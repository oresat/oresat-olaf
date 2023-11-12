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


void HeaderInilization(StructCodingPara *Ptr)
{	
	// first part of the header. 
	Ptr->PtrHeader = (HeaderStruct *) calloc(sizeof(HeaderStruct), 1);
	Ptr->PtrHeader->Header.Part1.StartImgFlag = TRUE;	
	Ptr->PtrHeader->Header.Part1.EngImgFlg = FALSE;	//FALSE	
	Ptr->PtrHeader->Header.Part1.SegmentCount_8Bits = 0;
	Ptr->PtrHeader->Header.Part1.BitDepthAC_5Bits = 0;	
	Ptr->PtrHeader->Header.Part1.BitDepthDC_5Bits = 0;	
	Ptr->PtrHeader->Header.Part1.Part2Flag =TRUE; // 	FALSE; //
	Ptr->PtrHeader->Header.Part1.Part3Flag = 	TRUE;  //FALSE; //
	Ptr->PtrHeader->Header.Part1.Part4Flag =TRUE; //  FALSE; // 
	Ptr->PtrHeader->Header.Part1.PadRows_3Bits = 0;	
	Ptr->PtrHeader->Header.Part1.Reserved_5Bits = 0; 

    // 40963072 ;  //* 2; // in terms of byte
	Ptr->PtrHeader->Header.Part2.SegByteLimit_27Bits = 0;
    //indicate whether the compressed output stops. 
	Ptr->PtrHeader->Header.Part2.DCstop = FALSE; 
    // 5 bits
	Ptr->PtrHeader->Header.Part2.BitPlaneStop_5Bits = 0; 
    // 2 bits, transform input data quantization. 
	Ptr->PtrHeader->Header.Part2.StageStop_2Bits = 3; 
	if (Ptr->PtrHeader->Header.Part2.SegByteLimit_27Bits == 0)
		Ptr->PtrHeader->Header.Part2.UseFill = FALSE;
	else
		Ptr->PtrHeader->Header.Part2.UseFill = TRUE;
	Ptr->PtrHeader->Header.Part2.Reserved_4Bits = 0; // 4 bits
	
	Ptr->PtrHeader->Header.Part3.S_20Bits = 256; // Segment size in blocks
	Ptr->PtrHeader->Header.Part3.OptDCSelect = TRUE; // 1: optimum selection of k
	Ptr->PtrHeader->Header.Part3.OptACSelect = TRUE; // 1: optimum selection of k
	Ptr->PtrHeader->Header.Part3.Reserved_2Bits = 0;
	
    // true is integer FLOAT_WAVELET; //
	Ptr->PtrHeader->Header.Part4.DWTType = INTEGER_WAVELET;  

	Ptr->PtrHeader->Header.Part4.Reserved_2Bits = 0; //
    // 0: unsigned
	Ptr->PtrHeader->Header.Part4.SignedPixels = FALSE;
    //  if it is 0, pixel is of 16-bit. 
	Ptr->PtrHeader->Header.Part4.PixelBitDepth_4Bits = 8; 
    // image width
	Ptr->PtrHeader->Header.Part4.ImageWidth_20Bits = 2048;  
    // 1 do not transpose. 
	Ptr->PtrHeader->Header.Part4.TransposeImg = NOTRANSPOSE; 
    // codedword lenggth
	Ptr->PtrHeader->Header.Part4.CodewordLength_2Bits = 00; 
	Ptr->PtrHeader->Header.Part4.Reserved = 0;
    // 1, user defined weights used. TRUE; //
	Ptr->PtrHeader->Header.Part4.CustomWtFlag = FALSE; 
	Ptr->PtrHeader->Header.Part4.CustomWtHH1_2bits = 0;  
	Ptr->PtrHeader->Header.Part4.CustomWtHL1_2bits = 1;
	Ptr->PtrHeader->Header.Part4.CustomWtLH1_2bits = 1;
	Ptr->PtrHeader->Header.Part4.CustomWtHH2_2bits = 1;
	Ptr->PtrHeader->Header.Part4.CustomWtHL2_2bits = 2;
	Ptr->PtrHeader->Header.Part4.CustomWtLH2_2bits = 2;
	Ptr->PtrHeader->Header.Part4.CustomWtHH3_2bits = 2;
	Ptr->PtrHeader->Header.Part4.CustomWtHL3_2bits = 3;
	Ptr->PtrHeader->Header.Part4.CustomWtLH3_2bits = 3;
	Ptr->PtrHeader->Header.Part4.CustomWtLL3_2bits = 3;
/* customized test
	Ptr->PtrHeader->Header.Part4.CustomWtHH1_2bits = 0;
	Ptr->PtrHeader->Header.Part4.CustomWtHL1_2bits = 0;
	Ptr->PtrHeader->Header.Part4.CustomWtLH1_2bits = 0;
	Ptr->PtrHeader->Header.Part4.CustomWtHH2_2bits =0;
	Ptr->PtrHeader->Header.Part4.CustomWtHL2_2bits = 1;
	Ptr->PtrHeader->Header.Part4.CustomWtLH2_2bits = 1;
	Ptr->PtrHeader->Header.Part4.CustomWtHH3_2bits =1;
	Ptr->PtrHeader->Header.Part4.CustomWtHL3_2bits = 2;
	Ptr->PtrHeader->Header.Part4.CustomWtLH3_2bits = 2;
	Ptr->PtrHeader->Header.Part4.CustomWtLL3_2bits = 2;
*/ 
	Ptr->PtrHeader->Header.Part4.Reserved_11Bits = 0;
	////////////////////////////////////////////////////////////////////////////
    // initialize coding parameters to default values. 
	Ptr->ImageRows = 0; 
	Ptr->ImageWidth = 0;
    // default coding BitsPerPixel, bits per pixels
	Ptr->BitsPerPixel = 0;      
    // default byte order. little endian. For intel processor, don't change to 1. 	
	Ptr->PixelByteOrder = 0; 

	Ptr->Bits = (BitStream*)calloc(sizeof(BitStream), 1);
	Ptr->Bits->ByteBuffer_4Bytes = 0;
	Ptr->Bits->CodeWordAlighmentBits = 0;
	Ptr->Bits->SegBitCounter = 0;
	Ptr->Bits->TotalBitCounter = 0;
	Ptr->Bits->F_Bits = NULL; 
	Ptr->SegmentFull = FALSE;
	Ptr->RateReached = FALSE;
	strcpy(Ptr->CodingOutputFile, "");
	strcpy(Ptr->InputFile, "");
	//////////////////////////////////////////////////////////////////////////
	// these are to record the partial decoding positon.
	Ptr->DecodingStopLocations.BitPlaneStopDecoding = -1; // for find adjustment. 
	Ptr->DecodingStopLocations.BlockNoStopDecoding = -1;	
	Ptr->DecodingStopLocations.LocationFind = FALSE;
	Ptr->DecodingStopLocations.X_LocationStopDecoding = -1;
	Ptr->DecodingStopLocations.Y_LocationStopDecoding = -1;	
	Ptr->DecodingStopLocations.stoppedstage = 10;
	
	/////////////////////////////////////////////////////////////////////////
	if (Ptr->PtrHeader->Header.Part4.CodewordLength_2Bits == 0)
		Ptr->Bits->CodeWord_Length = 8;
	else if(Ptr->PtrHeader->Header.Part4.CodewordLength_2Bits == 1)
		Ptr->Bits->CodeWord_Length = 16;
	else if(Ptr->PtrHeader->Header.Part4.CodewordLength_2Bits == 2)
		Ptr->Bits->CodeWord_Length = 24;
	else if(Ptr->PtrHeader->Header.Part4.CodewordLength_2Bits == 3)
		Ptr->Bits->CodeWord_Length = 32;

	return;
}

#define HEADER_INCLUDED
void HeaderOutput(StructCodingPara *PtrCoding)
{
#ifndef HEADER_INCLUDED
	return;
#endif
	BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part1.StartImgFlag, 1);
	BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part1.EngImgFlg, 1);	
	BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part1.SegmentCount_8Bits, 8);
	BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part1.BitDepthDC_5Bits, 5);
	BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part1.BitDepthAC_5Bits, 5);		
	BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part1.Reserved , 1);	
	BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part1.Part2Flag , 1);	
	BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part1.Part3Flag , 1);	
	BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part1.Part4Flag , 1);

	// 24 bits already, 3 bytes

	if(PtrCoding->PtrHeader->Header.Part1.EngImgFlg == TRUE)
	{
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits, 3);
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part1.Reserved_5Bits, 5);
	}
	if(PtrCoding->PtrHeader->Header.Part1.Part2Flag == TRUE)
	{		
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits, 27);		
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part2.DCstop, 1); //indicate whether the compressed output stops. 
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part2.BitPlaneStop_5Bits, 5);
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part2.StageStop_2Bits, 2);
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part2.UseFill , 1);
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part2.Reserved_4Bits , 4); // 4 bits
	}

	if(PtrCoding->PtrHeader->Header.Part1.Part3Flag == TRUE)
	{
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part3.S_20Bits, 20);
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part3.OptDCSelect, 1);
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part3.OptACSelect, 1);
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part3.Reserved_2Bits, 2);
	}

	if(PtrCoding->PtrHeader->Header.Part1.Part4Flag == TRUE)
	{
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.DWTType, 1);  // true is integer
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.Reserved_2Bits, 2);
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.SignedPixels, 1);// 0: unsigned
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.PixelBitDepth_4Bits, 4); // 
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.ImageWidth_20Bits, 20);
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.TransposeImg , 1);
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.CodewordLength_2Bits, 2);
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.Reserved, 1);
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.CustomWtFlag, 1);
		if(PtrCoding->PtrHeader->Header.Part4.CustomWtFlag == FALSE)
		{
			BitsOutput(PtrCoding, 0, 8);			
			BitsOutput(PtrCoding, 0, 8);					
			BitsOutput(PtrCoding, 0, 4);
		}		
		else
		{
			BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.CustomWtHH1_2bits, 2);
			BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.CustomWtHL1_2bits, 2);
			BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.CustomWtLH1_2bits, 2);
			BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.CustomWtHH2_2bits, 2);
			BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.CustomWtHL2_2bits, 2);
			BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.CustomWtLH2_2bits, 2);
			BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.CustomWtHH3_2bits, 2);
			BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.CustomWtHL3_2bits, 2);
			BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.CustomWtLH3_2bits, 2);
			BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.CustomWtLL3_2bits, 2);
		}
		BitsOutput(PtrCoding, PtrCoding->PtrHeader->Header.Part4.Reserved_11Bits, 11);
	}
}

void HeaderReadin(StructCodingPara *PtrCoding)
{
	DWORD32 Byte; 

	BitsRead(PtrCoding, &Byte, 1);
	PtrCoding->PtrHeader->Header.Part1.StartImgFlag = (BOOL)Byte;

	BitsRead(PtrCoding, &Byte, 1);
	PtrCoding->PtrHeader->Header.Part1.EngImgFlg = (BOOL)Byte;

	BitsRead(PtrCoding, &Byte, 8);
	PtrCoding->PtrHeader->Header.Part1.SegmentCount_8Bits = (UCHAR8)Byte;

	BitsRead(PtrCoding, &Byte, 5);
	PtrCoding->PtrHeader->Header.Part1.BitDepthDC_5Bits = (UCHAR8)Byte;

	BitsRead(PtrCoding, &Byte, 5);
	PtrCoding->PtrHeader->Header.Part1.BitDepthAC_5Bits = (UCHAR8)Byte;

	BitsRead(PtrCoding, &Byte, 1);
	PtrCoding->PtrHeader->Header.Part1.Reserved = (UCHAR8)Byte;

	BitsRead(PtrCoding, &Byte, 1);
	PtrCoding->PtrHeader->Header.Part1.Part2Flag = (BOOL)Byte;
	
	BitsRead(PtrCoding, &Byte, 1);
	PtrCoding->PtrHeader->Header.Part1.Part3Flag= (BOOL)Byte;	

	BitsRead(PtrCoding,&Byte, 1);
	PtrCoding->PtrHeader->Header.Part1.Part4Flag= (BOOL)Byte;

	if((PtrCoding->PtrHeader->Header.Part1).EngImgFlg == TRUE)
	{
		BitsRead(PtrCoding, &Byte, 3);
		PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits= (UCHAR8)Byte;
		BitsRead(PtrCoding, &Byte, 5);
		PtrCoding->PtrHeader->Header.Part1.Reserved_5Bits= (UCHAR8)Byte;
	}

	if(PtrCoding->PtrHeader->Header.Part1.Part2Flag == TRUE)
	{		
		BitsRead(PtrCoding, &Byte, 27);
		PtrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits = Byte;

		BitsRead(PtrCoding, &Byte, 1);
		PtrCoding->PtrHeader->Header.Part2.DCstop = (BOOL)Byte; //indicate whether the compressed output stops. 
		
		BitsRead(PtrCoding, &Byte, 5);
		PtrCoding->PtrHeader->Header.Part2.BitPlaneStop_5Bits = (UCHAR8)Byte;
		
		BitsRead(PtrCoding, &Byte, 2);
		PtrCoding->PtrHeader->Header.Part2.StageStop_2Bits = (UCHAR8)Byte;
		
		BitsRead(PtrCoding, &Byte, 1);
		PtrCoding->PtrHeader->Header.Part2.UseFill = (BOOL)Byte;
		
		BitsRead(PtrCoding, &Byte, 4);
		PtrCoding->PtrHeader->Header.Part2.Reserved_4Bits = (UCHAR8)Byte; // 4 bits
	}

	if((PtrCoding->PtrHeader->Header.Part1).Part3Flag == TRUE)
	{
		BitsRead(PtrCoding, &Byte, 20);
		PtrCoding->PtrHeader->Header.Part3.S_20Bits = Byte;
		if(PtrCoding->BitsPerPixel != 0)
		{
			PtrCoding->DecodingAllowedBitsSizeInSegment = 
                        (DWORD32)(PtrCoding->BitsPerPixel * 
                        PtrCoding->PtrHeader->Header.Part3.S_20Bits * 64);

			if (PtrCoding->DecodingAllowedBitsSizeInSegment > 
                    (PtrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits  << 3))
				PtrCoding->DecodingAllowedBitsSizeInSegment = 
                    (PtrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits << 3);
		}
		else
		{
			PtrCoding->DecodingAllowedBitsSizeInSegment = 0;
			if(PtrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits  != 0)
            {
				PtrCoding->DecodingAllowedBitsSizeInSegment = 
                    (PtrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits << 3);
            }
        }

		BitsRead(PtrCoding, &Byte, 1);
		PtrCoding->PtrHeader->Header.Part3.OptDCSelect = (BOOL)Byte;
		
		BitsRead(PtrCoding, &Byte, 1);
		PtrCoding->PtrHeader->Header.Part3.OptACSelect = (BOOL)Byte;

		BitsRead(PtrCoding, &Byte, 2);
		PtrCoding->PtrHeader->Header.Part3.Reserved_2Bits = (UCHAR8)Byte;
	}
	else
	{
		PtrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits = 0;  //even user specify a rate, in this case, there is no rate control.
	}

	if((PtrCoding->PtrHeader->Header.Part1).Part4Flag == TRUE)
	{
		BitsRead(PtrCoding, &Byte, 1);
		PtrCoding->PtrHeader->Header.Part4.DWTType = (BOOL)Byte;
		BitsRead(PtrCoding, &Byte, 2);
			PtrCoding->PtrHeader->Header.Part4.Reserved_2Bits = (UCHAR8)Byte;
		BitsRead(PtrCoding, &Byte, 1);
			PtrCoding->PtrHeader->Header.Part4.SignedPixels = (BOOL)Byte;
		BitsRead(PtrCoding, &Byte, 4);
			PtrCoding->PtrHeader->Header.Part4.PixelBitDepth_4Bits = (UCHAR8)Byte;
		BitsRead(PtrCoding, &Byte, 20);
			PtrCoding->PtrHeader->Header.Part4.ImageWidth_20Bits = (DWORD32)Byte;
		BitsRead(PtrCoding, &Byte, 1);
			PtrCoding->PtrHeader->Header.Part4.TransposeImg  = (BOOL)Byte;
		BitsRead(PtrCoding, &Byte, 2);
			PtrCoding->PtrHeader->Header.Part4.CodewordLength_2Bits = (UCHAR8)Byte;

		if (PtrCoding->PtrHeader->Header.Part4.CodewordLength_2Bits == 00)
			PtrCoding->Bits->CodeWord_Length = 8;
		else if(PtrCoding->PtrHeader->Header.Part4.CodewordLength_2Bits == 01)
			PtrCoding->Bits->CodeWord_Length = 16;
		else if(PtrCoding->PtrHeader->Header.Part4.CodewordLength_2Bits == 2)
			PtrCoding->Bits->CodeWord_Length = 24;
		else if(PtrCoding->PtrHeader->Header.Part4.CodewordLength_2Bits == 3)
			PtrCoding->Bits->CodeWord_Length = 32;

		BitsRead(PtrCoding, &Byte, 1);
			PtrCoding->PtrHeader->Header.Part4.Reserved = (BOOL)Byte;
		BitsRead(PtrCoding, &Byte, 1);
			PtrCoding->PtrHeader->Header.Part4.CustomWtFlag = (BOOL)Byte;
		if(Byte == TRUE) 
		{
			BitsRead(PtrCoding, &Byte, 2);
				PtrCoding->PtrHeader->Header.Part4.CustomWtHH1_2bits = (UCHAR8)Byte;
			BitsRead(PtrCoding, &Byte, 2);
				PtrCoding->PtrHeader->Header.Part4.CustomWtHL1_2bits = (UCHAR8)Byte;
			BitsRead(PtrCoding, &Byte, 2);
				PtrCoding->PtrHeader->Header.Part4.CustomWtLH1_2bits = (UCHAR8)Byte;
			BitsRead(PtrCoding, &Byte, 2);
				PtrCoding->PtrHeader->Header.Part4.CustomWtHH2_2bits = (UCHAR8)Byte;
			BitsRead(PtrCoding, &Byte, 2);
				PtrCoding->PtrHeader->Header.Part4.CustomWtHL2_2bits = (UCHAR8)Byte;
			BitsRead(PtrCoding, &Byte, 2);
				PtrCoding->PtrHeader->Header.Part4.CustomWtLH2_2bits = (UCHAR8)Byte;
			BitsRead(PtrCoding, &Byte, 2);
				PtrCoding->PtrHeader->Header.Part4.CustomWtHH3_2bits = (UCHAR8)Byte;
			BitsRead(PtrCoding, &Byte, 2);
				PtrCoding->PtrHeader->Header.Part4.CustomWtHL3_2bits = (UCHAR8)Byte;
			BitsRead(PtrCoding, &Byte, 2);
				PtrCoding->PtrHeader->Header.Part4.CustomWtLH3_2bits = (UCHAR8)Byte;
			BitsRead(PtrCoding, &Byte, 2);
			PtrCoding->PtrHeader->Header.Part4.CustomWtLL3_2bits = (UCHAR8)Byte;
		}
		else
		{
			BitsRead(PtrCoding, &Byte, 20);
		}
		BitsRead(PtrCoding, &Byte, 11);
		PtrCoding->PtrHeader->Header.Part4.Reserved_11Bits  = (WORD16)Byte;
	}
	PtrCoding->DecodingStopLocations.BitPlaneStopDecoding = -1;
	PtrCoding->DecodingStopLocations.BlockNoStopDecoding = -1;	
	PtrCoding->DecodingStopLocations.LocationFind = FALSE;
	PtrCoding->DecodingStopLocations.X_LocationStopDecoding = -1;
	PtrCoding->DecodingStopLocations.Y_LocationStopDecoding  = -1;
}

void HeaderUpdate(HeaderStruct * HeaderStr)
{
	if(HeaderStr->Header.Part1.StartImgFlag == TRUE)
		HeaderStr->Header.Part1.StartImgFlag = FALSE;
	HeaderStr->Header.Part1.BitDepthAC_5Bits = 0;	
	HeaderStr->Header.Part1.BitDepthDC_5Bits = 0;
	HeaderStr->Header.Part1.SegmentCount_8Bits ++;

	//for test 4
	HeaderStr->Header.Part1.Part2Flag = FALSE;
	HeaderStr->Header.Part1.Part3Flag = FALSE;
	HeaderStr->Header.Part1.Part4Flag = FALSE;

	if(HeaderStr->Header.Part1.Part2Flag == TRUE)  // it has part 2. 
	{
        // maxmimum number of bits, including the bytes used for the header. 
		HeaderStr->Header.Part2.SegByteLimit_27Bits = 1000000; 
		HeaderStr->Header.Part2.BitPlaneStop_5Bits ++;
		HeaderStr->Header.Part2.StageStop_2Bits ++;
		HeaderStr->Header.Part2.UseFill ++;		
	}

	if(HeaderStr->Header.Part1.Part3Flag == TRUE)  // it has part 3. 
		// Part 3 can be changed within the application. 
	{
		HeaderStr->Header.Part3.S_20Bits = 1000;
		HeaderStr->Header.Part3.OptDCSelect ++;
		HeaderStr->Header.Part3.OptACSelect ++;
	}
	
	if(HeaderStr->Header.Part1.Part4Flag == TRUE)  // Part 4 may not be changed
		// within a particular application. 
	{
		HeaderStr->Header.Part4.DWTType = INTEGER_WAVELET;
	}

	if (HeaderStr->Header.Part3.S_20Bits < 16)
		ErrorMsg(BPE_INVALID_HEADER);
}
