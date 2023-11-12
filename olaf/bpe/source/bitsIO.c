/*
Bit plane encoder
Please note:
(1)	Before you download and use the program, you must read and agree the license agreement carefully. 
(2)	We supply the source code and program WITHOUT ANY WARRANTIES. The users will be responsible 
        for any loses or damages caused by the use of the source code and the program. 

Author: 
Hongqiang Wang
Department of Electrical Engineering
University of Nebraska-Lincoln
Nov. 3, 2006
*/ 

#include "global.h"

void OutputCodeWord(StructCodingPara * Ptr)
{

	Ptr->Bits->CodeWordAlighmentBits ++;
	Ptr->Bits->SegBitCounter++;
	Ptr->Bits->TotalBitCounter ++;

	if ( Ptr->Bits->CodeWordAlighmentBits == Ptr->Bits->CodeWord_Length)
	{
		if(Ptr->Bits->CodeWord_Length == 8)
		{
			UCHAR8 temp;
/*			if( Ptr->Bits->TotalBitCounter  >= 8 * 0x5)
			Ptr->Bits->TotalBitCounter  = Ptr->Bits->TotalBitCounter ;
*/		
			temp = (UCHAR8)Ptr->Bits->ByteBuffer_4Bytes;
			putc(temp, Ptr->Bits->F_Bits);	

		}
		else if(Ptr->Bits->CodeWord_Length == 16)
		{
			WORD16 temp;					
			temp = (WORD16)Ptr->Bits->ByteBuffer_4Bytes;
			fwrite(&temp, 1, sizeof(WORD16), Ptr->Bits->F_Bits);  //Bug?
		}
		else if(Ptr->Bits->CodeWord_Length == 24)
		{
			WORD16 temp;							
			temp = (WORD16)Ptr->Bits->ByteBuffer_4Bytes & 0xFF;
			putc(temp, Ptr->Bits->F_Bits);
			
			temp = (WORD16)Ptr->Bits->ByteBuffer_4Bytes & 0xFF00;
			putc(temp, Ptr->Bits->F_Bits);
			
			temp = (WORD16)Ptr->Bits->ByteBuffer_4Bytes & 0xFF0000;
			putc(temp, Ptr->Bits->F_Bits);
		}
		else if(Ptr->Bits->CodeWord_Length == 32)
		{
			UINT32 temp;					
			temp = (UINT32)Ptr->Bits->ByteBuffer_4Bytes;
			fwrite(&temp, 1, sizeof(UINT32), Ptr->Bits->F_Bits); //Bug?
		}				
		Ptr->Bits->CodeWordAlighmentBits = 0;
	}
}

void BitsOutput(StructCodingPara *Ptr, DWORD32 bit, int length)
{
	short i;
//	short CodeWord_Length; 
	UCHAR8 temp_bits;
	if(length == 0)	
		return;
	if(Ptr->SegmentFull == TRUE)
		return;
	
	// determine if there is limitation on the total number of bytes output in this segment. 
	// first check if Part 2 of the header is available. 

	if((Ptr->PtrHeader->Header.Part2.SegByteLimit_27Bits != 0))
	{
		// means that there might be a limitation on the total number of bits.
		if(Ptr->Bits->SegBitCounter + (UINT32)length >= Ptr->PtrHeader->Header.Part2.SegByteLimit_27Bits * 8)  
		{
			short RemainderBits = 0;
			Ptr->SegmentFull = TRUE;
			RemainderBits = (short)(Ptr->PtrHeader->Header.Part2.SegByteLimit_27Bits 
                                                * 8 - Ptr->Bits->SegBitCounter);

			for (i = RemainderBits - 1; i >= 0; i --)
			{
				temp_bits = (UCHAR8) (0x01 & (bit >> (length - 1)));
				length--;
//				Ptr->Bits->SegBitCounter++;
//				Ptr->Bits->TotalBitCounter ++;
				Ptr->Bits->ByteBuffer_4Bytes <<= 1;
				Ptr->Bits->ByteBuffer_4Bytes += temp_bits;
				OutputCodeWord(Ptr);	
			}		
			return;
		}
	}
	
// determine the Codeword length by the hearder part 4. 	
	if(length > 32)
	{
		int tt = length - 32;

		Ptr->Bits->ByteBuffer_4Bytes <<= tt; 
		OutputCodeWord(Ptr);	
		length = 32;
	}

	for (i = length - 1; i >= 0; i --)
	{
		temp_bits = (UCHAR8) (0x01 & (bit >> i));
		Ptr->Bits->ByteBuffer_4Bytes <<= 1;
		Ptr->Bits->ByteBuffer_4Bytes += temp_bits;
		OutputCodeWord(Ptr);	
	}

	return;
}

short BitsRead(StructCodingPara *Ptr, DWORD32 *bit, short length)
{
	UCHAR8 i; 
	*bit = 0;

	if((length == 0) || (Ptr->SegmentFull == TRUE))
	{
		*bit = 0;
		return BPE_OK;
	}

	if(Ptr->RateReached == TRUE)
	{
		*bit = 0;
		return BPE_OK;
	}

	if (Ptr->SegmentFull != TRUE)
	{
		for (i = 0; i < length; i ++)
		{
			if (Ptr->Bits->CodeWordAlighmentBits == 0)
			{
				Ptr->Bits->ByteBuffer_4Bytes = getc(Ptr->Bits->F_Bits) ; 
				Ptr->Bits->CodeWordAlighmentBits = 8;
			}			
			(*bit) <<= 1;
			(*bit) += (UCHAR8) ((Ptr->Bits->ByteBuffer_4Bytes >> (Ptr->Bits->CodeWordAlighmentBits - 1)) & 0x01);
			Ptr->Bits->CodeWordAlighmentBits --;
			Ptr->Bits->SegBitCounter++;
			Ptr->Bits->TotalBitCounter ++;

			// for embedded decoding rate control
			if((Ptr->Bits->SegBitCounter >= Ptr->DecodingAllowedBitsSizeInSegment)
                    && Ptr->DecodingAllowedBitsSizeInSegment != 0)
			{
				UINT32 CurrentTotalBytes =  (Ptr->Bits->SegBitCounter + 
					Ptr->Bits->CodeWordAlighmentBits) / 8;

				Ptr->RateReached = TRUE;
				Ptr->DecodingStopLocations.BitPlaneStopDecoding = Ptr->BitPlane - 1;
				Ptr->DecodingStopLocations.TotalBitsReadThisTime = i + 1;
				(*bit) <<= (length - i - 1);	
				while(CurrentTotalBytes < Ptr->PtrHeader->Header.Part2.SegByteLimit_27Bits)
				{
					getc(Ptr->Bits->F_Bits);
					CurrentTotalBytes++;
				}
				Ptr->SegmentFull = TRUE;
				return BPE_OK;
			}
			// end of rate control. 		
		}
	}
	return BPE_OK;
}

//void SegmentBufferFlushEncoder(StructCodingPara *StrCoding) // flush codes and reset
//{
//	
//	if(StrCoding->Bits->CodeWordAlighmentBits != 0)
//	{
//		int shift = 0;
//		shift = StrCoding->Bits->CodeWord_Length - StrCoding->Bits->CodeWordAlighmentBits;
//		BitsOutput(StrCoding, 0, shift);
//	}
//
//	if((StrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits != 0)
//		&& (StrCoding->SegmentFull == FALSE) 
//		&& StrCoding->PtrHeader->Header.Part2.UseFill == TRUE)
//	{
//		while(StrCoding->SegmentFull == FALSE)
//		{
//			BitsOutput(StrCoding, 0, 8);
//		}
//	}
//	
//	StrCoding->Bits->SegBitCounter = 0;
//	StrCoding->Bits->ByteBuffer_4Bytes = 0;
//	StrCoding->Bits->CodeWordAlighmentBits = 0;
//	return;
//}
