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
Email: hqwang@bigred.unl.edu, hqwang@eecomm.unl.edu

Your comment and suggestions are welcome. Please report bugs to me via email and I would greatly appreciate it. 
Nov. 3, 2006
*/ 

#include "global.h"


short ImageWrite(StructCodingPara *StrPtr, int **image);

short ImageWrite(StructCodingPara *StrPtr,  int **image)
{
	UINT32 r = 0; 
	UINT32 i = 0;
	FILE *outfile = NULL;
	UCHAR8 machineendianness;  // indicates endian-ness of the computer -- bug fix (Kiely)
	unsigned long int bigendtest = 1;  //  bug fix (Kiely)
	
	if((outfile = fopen(StrPtr->CodingOutputFile,"wb")) == NULL)
		ErrorMsg(BPE_FILE_ERROR);
	
	StrPtr->ImageRows = StrPtr->ImageRows - StrPtr->PtrHeader->Header.Part1.PadRows_3Bits;

	if(StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits <= 8
		&& StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits != 0)
	{
		if(StrPtr->PtrHeader->Header.Part4.SignedPixels == FALSE) // unsigned image
		{	
			UCHAR8 *temp;		
			temp = (UCHAR8 *)calloc(sizeof(UCHAR8), StrPtr->ImageWidth);

			for(r = 0; r< StrPtr->ImageRows; r++)
			{
				for(i = 0; i < StrPtr->ImageWidth; i++)
				{
					image[r][i] = (image[r][i] > 0xFF)?0xFF :image[r][i] ;
					image[r][i] = (image[r][i] < 0)?0 :image[r][i] ;
					temp[i] = (UCHAR8)image[r][i];
				}
				fwrite(temp, StrPtr->ImageWidth, sizeof(char),outfile);	
			}
			free(temp);
		}
		else
		{
			char *temp;		
			temp = (char *)calloc(sizeof(char), StrPtr->ImageWidth);

			for(r=0; r< StrPtr->ImageRows; r++)
			{
				for(i = 0; i < StrPtr->ImageWidth; i++)
				{
					image[r][i] = (image[r][i] > 127)?127 :image[r][i] ;
					image[r][i] = (image[r][i] <-128 )?-128 :image[r][i] ;
					temp[i] = (char)image[r][i];
				}
				fwrite(temp, StrPtr->ImageWidth, sizeof(char),outfile);	
			}
			free(temp);
		}
	}
	else if(StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits == 0 ||
		StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits <= 15) // it is 16 bits
	{
		// machineendianness will be 1 if computer is big-endian, or 0 if little-endian
		const unsigned short MSBmask=0xFF00;  //  bug fix (Kiely)
		machineendianness = (((char *)&bigendtest)[0]==0);  //  bug fix (Kiely)

		if(StrPtr->PtrHeader->Header.Part4.SignedPixels == FALSE) // unsigned image
		{	
			WORD16 *temp_16;	

			WORD16 PixelMax;
			
			if (StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits == 0)
				PixelMax = (1 << 16) - 1;
			else
				PixelMax = (1 << StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits) - 1;

			
			temp_16 = (WORD16 *)calloc(sizeof(WORD16), StrPtr->ImageWidth);

			// if(StrPtr->PixelByteOrder == 1)
			if ( StrPtr->PixelByteOrder != machineendianness)  //  bug fix (Kiely)
				for(r = 0; r < StrPtr->ImageRows; r++)
				{
					for(i = 0; i < StrPtr->ImageWidth; i++)
					{
						image[r][i] = (image[r][i] > PixelMax) ? PixelMax : image[r][i];
						image[r][i] = (image[r][i] < 0) ? 0 : image[r][i];						
						image[r][i] = ((image[r][i] << 8) & MSBmask) + (image[r][i] >> 8) ;  //  bug fix (Kiely)
						temp_16[i] =(WORD16)image[r][i] ;
					}
					fwrite(temp_16, StrPtr->ImageWidth, sizeof(WORD16), outfile);
				}
			else
			{	
				for(r = 0; r < StrPtr->ImageRows; r++)
				{
					for(i = 0; i < StrPtr->ImageWidth; i++)
					{
						image[r][i] = (image[r][i] > PixelMax) ? PixelMax : image[r][i];
						image[r][i] = (image[r][i] < 0) ? 0 : image[r][i];
						temp_16[i] = (WORD16)image[r][i] ;
					}
					fwrite(temp_16, StrPtr->ImageWidth, sizeof(WORD16), outfile);
				}
			}
			free(temp_16);
		}
		else
		{
			short *temp_16 = (short *)calloc(sizeof(short), StrPtr->ImageWidth);
 
			WORD16 PixelMax = 0; 
			int PixelMin = 0;
			
			if (StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits == 0)
			{
				PixelMax = (1 << 15) - 1;
			}
			else
			{
				PixelMax = (1 << (StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits - 1)) - 1;
			}
			
			PixelMin = - PixelMax - 1;

			// if(StrPtr->PixelByteOrder == 1)
			if ( StrPtr->PixelByteOrder != machineendianness)  //  bug fix (Kiely)
			{
				for(r = 0; r < StrPtr->ImageRows; r++)
				{
					for(i = 0; i < StrPtr->ImageWidth; i++)
					{						
						image[r][i] = (image[r][i] > PixelMax) ? PixelMax : image[r][i];
						image[r][i] = (image[r][i] < PixelMin) ? PixelMin : image[r][i];
						image[r][i] = ((image[r][i] << 8) & MSBmask) + (image[r][i] >> 8);  //  bug fix (Kiely)
						temp_16[i] = (short)image[r][i] ;
					}
					fwrite(temp_16, StrPtr->ImageWidth, sizeof(short), outfile);
				}
			}
			else
			{	
				for(r = 0; r < StrPtr->ImageRows; r++)
				{
					for(i = 0; i < StrPtr->ImageWidth; i++)
					{
						
						image[r][i] = (image[r][i] > PixelMax) ? PixelMax : image[r][i];
						image[r][i] = (image[r][i] < PixelMin) ? PixelMin : image[r][i];
						temp_16[i] =(short)image[r][i] ;
					}
					fwrite(temp_16, StrPtr->ImageWidth, sizeof(short), outfile);
				}
			}
			free(temp_16);
		}
	}
	fclose(outfile);
	return BPE_OK;
}

 
void DecodingOutputInteger(StructCodingPara *PtrCP, int **imgout_integercase)
{	
	CoeffDegroup(imgout_integercase, PtrCP->ImageRows, 
                    PtrCP->ImageWidth + PtrCP->PadCols_3Bits);

	DWT_Reverse(imgout_integercase, PtrCP); 

	if (PtrCP->PtrHeader->Header.Part4.TransposeImg == TRANSPOSE)
	{
		UINT32 i = 0; 
		UINT32 j = 0;
		int **transposedimg = (int **)calloc(PtrCP->ImageRows,sizeof(int *)); 
		
		for(i = 0; i < PtrCP->ImageRows; i++)
			transposedimg[i] = (int *)calloc((PtrCP->ImageWidth),sizeof(int));	

		for( i = 0 ; i < PtrCP->ImageRows; i++)
			for(j = 0; j < PtrCP->ImageWidth; j++)
				transposedimg[j][i] = imgout_integercase[i][j];
			
		ImageWrite(PtrCP, transposedimg);
    }		
	else
		ImageWrite(PtrCP, imgout_integercase);
	
	return;	
}

short ImageWriteFloat(StructCodingPara *StrPtr, float **image)
{
	UINT32 r = 0; 
	UINT32 i = 0;
	FILE *outfile;
    // indicates endian-ness of the computer -- bug fix (Kiely)
	UCHAR8 machineendianness;  
	unsigned long int bigendtest = 1;  //  bug fix (Kiely)


	if((outfile = fopen(StrPtr->CodingOutputFile,"wb")) == NULL)
		ErrorMsg(BPE_FILE_ERROR);
	
	if(StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits <= 8
		&& StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits != 0)
	{
		if(StrPtr->PtrHeader->Header.Part4.SignedPixels == FALSE) // unsigned image
		{	
			UCHAR8 *temp = (UCHAR8 *)calloc(sizeof(UCHAR8), StrPtr->ImageWidth);

			for(r = 0; r < StrPtr->ImageRows; r++)
			{
				for(i = 0; i < StrPtr->ImageWidth; i++)
				{
					image[r][i] = (image[r][i] > 0xFF)?0xFF :image[r][i] ;
					image[r][i] = (image[r][i] < 0)?0 :image[r][i] ;
					temp[i] = (UCHAR8)image[r][i];
				}
				fwrite(temp, StrPtr->ImageWidth, sizeof(char),outfile);	
			}
			free(temp);
		}
		else
		{
			char *temp = (char *)calloc(sizeof(char), StrPtr->ImageWidth);

			for(r=0; r < StrPtr->ImageRows; r++)
			{
				for(i = 0; i < StrPtr->ImageWidth; i++)
				{
					image[r][i] = (image[r][i] > 127)?127 :image[r][i] ;
					image[r][i] = (image[r][i] <-128 )?-128 :image[r][i] ;
					temp[i] = (char)image[r][i];
				}
				fwrite(temp, StrPtr->ImageWidth, sizeof(char),outfile);	
			}
			free(temp);
		}
	}
	else if(StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits == 0 ||
		StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits <= 15) // it is 16 bits
	{
		// machineendianness will be 1 if computer is big-endian, or 0 if little-endian
		const unsigned short MSBmask=0xFF00;  //  bug fix (Kiely)
		machineendianness = (((char *)&bigendtest)[0]==0);  //  bug fix (Kiely)

		if(StrPtr->PtrHeader->Header.Part4.SignedPixels == FALSE) // unsigned image
		{	
			WORD16 PixelMax;
			WORD16 *temp_16 = (WORD16 *)calloc(sizeof(WORD16), StrPtr->ImageWidth);
			
			if (StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits == 0)
				PixelMax = (1 << 16) - 1;
			else
				PixelMax = (1 << StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits) - 1;

			// if(StrPtr->PixelByteOrder == 1)
			if ( StrPtr->PixelByteOrder != machineendianness)  //  bug fix (Kiely)
				for(r = 0; r < StrPtr->ImageRows; r++)
				{
					for(i = 0; i < StrPtr->ImageWidth; i++)
					{
						image[r][i] = (image[r][i] > PixelMax) ? PixelMax : image[r][i];
						image[r][i] = (image[r][i] < 0) ? 0 : image[r][i];
						image[r][i] = (float)((((int)(image[r][i])) << 8) & MSBmask) 
                            + (((int)(image[r][i])) >> 8);  //  bug fix (Kiely)
						temp_16[i] = (WORD16)image[r][i] ;
					}
					fwrite(temp_16, StrPtr->ImageWidth, sizeof(WORD16), outfile);
				}
			else
			{	
				for(r = 0; r < StrPtr->ImageRows; r++)
				{
					for(i = 0; i < StrPtr->ImageWidth; i++)
					{
						image[r][i] = (image[r][i] > PixelMax) ? PixelMax : image[r][i];
						image[r][i] = (image[r][i] < 0) ? 0 : image[r][i];
						temp_16[i] = (WORD16)image[r][i];
					}
					fwrite(temp_16, StrPtr->ImageWidth, sizeof(WORD16), outfile);
				}
			}
			free(temp_16);
		}	
		else  // signed image
		{
			short *temp_16 = (short *)calloc(sizeof(short), StrPtr->ImageWidth);
 
			WORD16 PixelMax = 0; 
			int PixelMin = 0;
			
			if (StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits == 0)
			{
				PixelMax = (1 << 15) - 1;
			}
			else
			{
				PixelMax = (1 << (StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits - 1)) - 1;
			}

			PixelMin = - PixelMax - 1;
			
			//if(StrPtr->PixelByteOrder == 1)
			if ( StrPtr->PixelByteOrder != machineendianness)  //  bug fix (Kiely)
				for(r = 0; r < StrPtr->ImageRows; r++)
				{
					for(i = 0; i < StrPtr->ImageWidth; i++)
					{						
						image[r][i] = (image[r][i] > PixelMax) ? PixelMax : image[r][i];
						image[r][i] = (image[r][i] < PixelMin) ? PixelMin : image[r][i]; 
						image[r][i] = (float)( ( ((int)(image[r][i])) << 8) & MSBmask ) + (((int)(image[r][i])) >> 8);  //  bug fix (Kiely)
						temp_16[i] = (short)image[r][i] ;
					}
					fwrite(temp_16, StrPtr->ImageWidth, sizeof(short), outfile);
				}
			else
			{	
				for(r = 0; r < StrPtr->ImageRows; r++)
				{
					for(i = 0; i < StrPtr->ImageWidth; i++)
					{						
						image[r][i] = (image[r][i] > PixelMax) ? PixelMax : image[r][i];
						image[r][i] = (image[r][i] < PixelMin) ? PixelMin : image[r][i];
						temp_16[i] =(short)image[r][i] ;
					}
					fwrite(temp_16, StrPtr->ImageWidth, sizeof(short), outfile);
				}
			}
			free(temp_16);
		}
	}
	fclose(outfile);
	return BPE_OK;
}


void DecodingOutputFloating(StructCodingPara *PtrCP, float **imgout_floatingcase)
{	
	CoeffDegroupFloating(imgout_floatingcase, PtrCP->ImageRows, PtrCP->ImageWidth + PtrCP->PadCols_3Bits);

	DWT_ReverseFloating(imgout_floatingcase, PtrCP); 

	if (PtrCP->PtrHeader->Header.Part4.TransposeImg == TRANSPOSE)
	{
		UINT32 i = 0;
		UINT32 j = 0;
		float **transposedimg = (float **)calloc(PtrCP->ImageRows,sizeof(float *)); 
		
		for(i = 0; i < PtrCP->ImageRows; i++)
			transposedimg[i] = (float *)calloc((PtrCP->ImageWidth),sizeof(float));	

		for( i = 0 ; i < PtrCP->ImageRows; i ++)
			for(j = 0; j < PtrCP->ImageWidth; j++)
				transposedimg[j][i] = imgout_floatingcase[i][j];
			
		ImageWriteFloat(PtrCP, transposedimg);
    }		
	else
		ImageWriteFloat(PtrCP, imgout_floatingcase);

	return;	
}
///////////////////////////////////////////////////////////////////////////////

void TempCoeffOutput(FILE *fdc,
					 FILE * fac, 
					 BitPlaneBits *BlockCodingInfo,
					 StructCodingPara * PtrCoding)
{
	UINT32 i;	
	int totalbytes_counter = 0;

	for(i = 0; i < PtrCoding->PtrHeader->Header.Part3.S_20Bits; i ++)
	{
		int m, n;
//test			
		fwrite(&(BlockCodingInfo[i].PtrBlockAddress[0][0]), 1,sizeof(long), fdc);

		for(m = 0; m < 8; m++)
			for(n = 0; n < 8; n++)
			{
				totalbytes_counter += 4;
				fwrite(&(BlockCodingInfo[i].PtrBlockAddress[m][n]), 1,sizeof(long), fac);
			}

	}
}

void SegmentBufferFlushDecoder(StructCodingPara *StrCoding) // flush codes and reset
{
	
	if((StrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits != 0)
		&&(StrCoding->SegmentFull == FALSE) && StrCoding->PtrHeader->Header.Part2.UseFill == TRUE)
	{
		DWORD32 temp = 0;
		while(StrCoding->SegmentFull == FALSE)
		{
			BitsRead(StrCoding, &temp, 8);
		}
	}
	
	StrCoding->Bits->TotalBitCounter  +=  StrCoding->Bits->CodeWordAlighmentBits;
	StrCoding->Bits->SegBitCounter = 0;
	StrCoding->Bits->ByteBuffer_4Bytes = 0;
	StrCoding->Bits->CodeWordAlighmentBits = 0;
	return;
}


// Main decode function
void DecoderEngine(StructCodingPara * PtrCoding)
{
	UINT32 i = 0;
	UINT32 j = 0;
	UINT32 X = 0;
	UINT32 Y = 0;
	UINT32 TotalBlocks = 0;

	int **imgout_integercase = NULL;
	float **imgout_floatingcase = NULL;
	StructFreBlockString * StrFreBlockString = NULL;
	StructFreBlockString *tempStr = NULL;
	
    // default name
	if((PtrCoding->Bits->F_Bits = fopen(PtrCoding->InputFile, "rb")) == NULL)  
    {
		ErrorMsg(BPE_FILE_ERROR);
    }

	HeaderReadin(PtrCoding); // read first header. 	
                             
	PtrCoding->ImageWidth = PtrCoding->PtrHeader->Header.Part4.ImageWidth_20Bits;	
	
	if(PtrCoding->ImageWidth % BLOCK_SIZE != 0)
    {
        PtrCoding->PadCols_3Bits = BLOCK_SIZE - (PtrCoding->ImageWidth % 8 );
    }
    else 
    {
        PtrCoding->PadCols_3Bits  =  0;
    }

	StrFreBlockString = (StructFreBlockString*)calloc(sizeof(StructFreBlockString), 1);
	StrFreBlockString->next = NULL;
	StrFreBlockString->previous = NULL;

	TotalBlocks = 0;
	for(;;)
	{		
		BitPlaneBits * BlockCodingInfo;
		BlockCodingInfo = 
            (BitPlaneBits *)calloc(PtrCoding->PtrHeader->Header.Part3.S_20Bits, 
                                                            sizeof(BitPlaneBits));
		TotalBlocks += PtrCoding->PtrHeader->Header.Part3.S_20Bits;

		StrFreBlockString->FreqBlkString = 
            (long **)calloc(PtrCoding->PtrHeader->Header.Part3.S_20Bits * BLOCK_SIZE, sizeof(long *));
		
        for(i = 0; i < PtrCoding->PtrHeader->Header.Part3.S_20Bits * BLOCK_SIZE; i++)
        {
            StrFreBlockString->FreqBlkString[i] = 
                (long *)calloc(BLOCK_SIZE, sizeof(long));
        }
		StrFreBlockString->FloatingFreqBlk = 
            (float **)calloc(PtrCoding->PtrHeader->Header.Part3.S_20Bits * BLOCK_SIZE, sizeof(float *));

		for(i = 0; i < PtrCoding->PtrHeader->Header.Part3.S_20Bits * BLOCK_SIZE; i++)
        {
            StrFreBlockString->FloatingFreqBlk[i] = 
                (float *)calloc(BLOCK_SIZE, sizeof(float));
        }
		StrFreBlockString->Blocks = PtrCoding->PtrHeader->Header.Part3.S_20Bits;
		
        DCDeCoding(PtrCoding, StrFreBlockString, BlockCodingInfo);
        
        // This means the decoding process stops before segment limit. 
		ACBpeDecoding(PtrCoding, BlockCodingInfo) ;	

		AdjustOutPut(PtrCoding, BlockCodingInfo);

	//	TempCoeffOutput(fdc, fac, BlockCodingInfo, PtrCoding);
    	
        free(BlockCodingInfo);
        SegmentBufferFlushDecoder(PtrCoding);
		PtrCoding->SegmentFull = FALSE;
		PtrCoding->RateReached = FALSE;
		PtrCoding->DecodingStopLocations.BitPlaneStopDecoding = 0;
		PtrCoding->BlockCounter += PtrCoding->PtrHeader->Header.Part3.S_20Bits;
		
        if(PtrCoding->PtrHeader->Header.Part1.EngImgFlg == TRUE)
			break;
	
        if (PtrCoding->PtrHeader->Header.Part1.EngImgFlg != TRUE)
			HeaderReadin(PtrCoding); // read second header. 
                                     
		tempStr = (StructFreBlockString*)calloc(sizeof(StructFreBlockString), 1);			
		(StrFreBlockString->next) = tempStr;
		tempStr->previous = StrFreBlockString;
		tempStr->next = NULL;
		StrFreBlockString = StrFreBlockString->next;
	}
	// ***********************  5. header information  **********************//

	PtrCoding->ImageRows = TotalBlocks * 64 /  (PtrCoding->ImageWidth + PtrCoding->PadCols_3Bits ); 

	imgout_integercase = (int **)calloc(PtrCoding->ImageRows,sizeof(int *)); 
	for(i = 0; i < PtrCoding->ImageRows; i++)
    {	
        imgout_integercase[i] = (int *)calloc((PtrCoding->ImageWidth + 
                                        PtrCoding->PadCols_3Bits),sizeof(int));	
    }
	imgout_floatingcase = (float **)calloc(PtrCoding->ImageRows,sizeof(float *)); 
	for(i = 0; i < PtrCoding->ImageRows; i++)
    {
		imgout_floatingcase[i] = (float *)calloc((PtrCoding->ImageWidth + 
                                        PtrCoding->PadCols_3Bits),sizeof(float));	
    }
	while(StrFreBlockString->previous != NULL)
    {
        StrFreBlockString = StrFreBlockString->previous;
    }

    StructFreBlockString * tail = NULL;
	do
    {
		UINT32 F_x = 0;
		do
		{
			for( i = 0; i < BLOCK_SIZE; i++)
				for( j = 0; j < BLOCK_SIZE; j++)
				{
					imgout_integercase[X + i][Y + j] = 
                        StrFreBlockString->FreqBlkString[F_x + i][j];
					imgout_floatingcase[X + i][Y + j] = 
                        StrFreBlockString->FloatingFreqBlk[F_x + i][j];
				}
			Y += BLOCK_SIZE;
			if( Y >= PtrCoding->ImageWidth)
			{
				Y = 0;
				X += BLOCK_SIZE;
			}
			F_x += BLOCK_SIZE;
		}while (F_x <  StrFreBlockString->Blocks * BLOCK_SIZE);				

        if (StrFreBlockString->next == NULL)                                    
        {                                                                       
            tail = StrFreBlockString;                                           
        } 

        StrFreBlockString = StrFreBlockString->next;

    }while(StrFreBlockString != NULL);

	if(PtrCoding->PtrHeader->Header.Part4.DWTType == INTEGER_WAVELET)
		DecodingOutputInteger(PtrCoding, imgout_integercase);
	else
		DecodingOutputFloating(PtrCoding, imgout_floatingcase);
	
/////////////////////////////////////////////////////    
    for(i = 0; i < PtrCoding->ImageRows; i++)
    {    
        free(imgout_integercase[i]);
    }
    free(imgout_integercase);

    for(i = 0; i < PtrCoding->ImageRows; i++)
    {    
        free(imgout_floatingcase[i]);
    }
    free(imgout_floatingcase);

    StrFreBlockString = tail;

    // free blockstring data structure memory
	while(StrFreBlockString->previous != NULL)
    {
        for(i = 0; i < PtrCoding->PtrHeader->Header.Part3.S_20Bits * BLOCK_SIZE; i++)
        {    
            free(StrFreBlockString->FloatingFreqBlk[i]);
        }
        free(StrFreBlockString->FloatingFreqBlk);

        for(i = 0; i < PtrCoding->PtrHeader->Header.Part3.S_20Bits * BLOCK_SIZE; i++)
        {
            free(StrFreBlockString->FreqBlkString[i]);
        }
        free(StrFreBlockString->FreqBlkString);
        tempStr = StrFreBlockString->previous;
        free(StrFreBlockString);
		StrFreBlockString = tempStr; 
    }

    for(i = 0; i < PtrCoding->PtrHeader->Header.Part3.S_20Bits * BLOCK_SIZE; i++)
    {    
        free(StrFreBlockString->FloatingFreqBlk[i]);
    }
    free(StrFreBlockString->FloatingFreqBlk);

    for(i = 0; i < PtrCoding->PtrHeader->Header.Part3.S_20Bits * BLOCK_SIZE; i++)
    {
        free(StrFreBlockString->FreqBlkString[i]);
    }
    free(StrFreBlockString->FreqBlkString);
    free(StrFreBlockString);
	
    return; 
}
