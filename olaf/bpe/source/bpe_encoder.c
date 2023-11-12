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

#include <sys/stat.h>
#include "global.h"


int ImageSize(StructCodingPara * );

short ImageRead(StructCodingPara *, int **);

int ImageSize(StructCodingPara * PtrStructCodingPara)
{
/*
Written by James R. Nau, 6-Oct-89

Attempt to find the size of an image in file pointed to by *file.
Number of rows (down), and the number of columns (across) is returned.
Uses a stat call to find the size of the file.  Then, attempts to find
a pertinent number of rows and columns that we normally use.  Currently

supported formats:

   row x column  size        Format

    128x128    16,384        Small Image
    320x200    64,000        IBM VGA Style
    256x256    65,536        Standard NASA Image (small)
    256x384    98,304        IVG Low-Res Image
    512x384   196,608        IVG High-Res Image
    512x512   262,144        Standard NASA Image (large)
    640x480   307,200        Super VGA (from GIF usually)
    720x480   345,600
    576x720   414,720	     JPEG images

Parameters:
         *file: pointer to filename containing image
          StructCodingPara->row_sizeow: pointer to the number of rows we decided on
       StructCodingPara->col_sizeolumn: pointer to number of columns we decided on

Return values:
        0: ok
       -1: Couldn't use stat function
       -2: Unknown image size
*/

   struct stat status;
   int res;
   UINT32 img_len;
   char buffer[BUFFER_LENGTH];

  // FILE *FF = fopen("spot.raw", "r");

   res = stat(PtrStructCodingPara->InputFile, &status);
   if (res != 0)
   {
		   return (-1);
   }
   img_len = status.st_size;

   // user did specify the image size.    
   if((PtrStructCodingPara->ImageRows > 0 ) && (PtrStructCodingPara->ImageWidth > 0)) 
   {
	   short temp = 
           PtrStructCodingPara->PtrHeader->Header.Part4.PixelBitDepth_4Bits;
	   if  ((temp == 0) || temp > 8) 
		   temp = 16;
	   else 
		   temp = 8;
	   
	   if (img_len == ((PtrStructCodingPara->ImageRows) * 
                   (PtrStructCodingPara->ImageWidth) * temp / 8)) // user defined 

       return BPE_OK;
	   else 
		   ErrorMsg(BPE_FILE_ERROR);
   } 	

   if (img_len == 16384L)       /* For BUD's images */
   {
      PtrStructCodingPara->ImageRows = 128;
      PtrStructCodingPara->ImageWidth = 128;
   }
   else if (img_len == 64000L)  /* IBM VGA Screen */
   {
      PtrStructCodingPara->ImageRows = 200;
      PtrStructCodingPara->ImageWidth = 320;
   }
   else if (img_len == 65536L)  /* Standard */
   {
      PtrStructCodingPara->ImageRows = 256;
      PtrStructCodingPara->ImageWidth = 256;
   }
   else if (img_len == 98304L)  /* Low-Res IVG images */
   {
      PtrStructCodingPara->ImageRows = 256;
      PtrStructCodingPara->ImageWidth = 384;
   }
   else if (img_len == 196608L) /* Hi-Res IVG images */
   {
      PtrStructCodingPara->ImageRows = 512;
      PtrStructCodingPara->ImageWidth = 384;
   }
   else if (img_len == 262144L) /* Standard, but large... */
   {
      PtrStructCodingPara->ImageRows = 512;
      PtrStructCodingPara->ImageWidth = 512;
   }
   else if (img_len == 307200L) /* SVGA Hi-Res from GIFs */
   {
      PtrStructCodingPara->ImageRows = 480;
      PtrStructCodingPara->ImageWidth = 640;
   }
   else if (img_len == 345600L) /* mpeg frame 720 x 480 */
   {
      PtrStructCodingPara->ImageRows = 720;
      PtrStructCodingPara->ImageWidth = 480;
   }
   else if (img_len == 414720L) /* jpeg test image 576 x 720 */
   {
      PtrStructCodingPara->ImageRows = 576;
      PtrStructCodingPara->ImageWidth = 720;	  
   }
   else if (img_len == 524288)
   {  
	   PtrStructCodingPara->ImageRows = 512;
	   PtrStructCodingPara->ImageWidth = 512;
	   PtrStructCodingPara->PtrHeader->Header.Part4.PixelBitDepth_4Bits = 0;
   }
   else
   {   
	   sprintf(buffer, "\nError: unknown image size: %ud\n", img_len);
	   DebugInfo(buffer);
	   ErrorMsg(BPE_FILE_ERROR);
   }

   if ((PtrStructCodingPara->ImageRows) * (PtrStructCodingPara->ImageWidth)
	   * (PtrStructCodingPara->PtrHeader->Header.Part4.PixelBitDepth_4Bits) / 8 != img_len)
   {
   	   sprintf(buffer, "\nError: incorrect image size: %ud\n", img_len);
	   DebugInfo(buffer);
	   ErrorMsg(BPE_FILE_ERROR);
   }
   return (BPE_OK);
}

short ImageRead(StructCodingPara *StrPtr, int **image)
{
	UINT32 r = 0;
	UINT32 i = 0;
	FILE *infile = NULL;
    // indicates endian-ness of the computer -- bug fix (Kiely)
	UCHAR8 machineendianness;  
	unsigned long int bigendtest = 1;  //  bug fix (Kiely)

	infile = fopen(StrPtr->InputFile,"rb");
	if (infile == NULL)
	{
        char buf[40];
        strcpy(buf, "Error: Unable to read the image file!\n\0");
		DebugInfo(buf);			
		ErrorMsg(BPE_FILE_ERROR);
	}

	if (StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits <= 8
		&& StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits != 0)
	{			
		if(StrPtr->PtrHeader->Header.Part4.SignedPixels == FALSE) // unsigned image
		{
			UCHAR8 *temp;
			temp = (UCHAR8 *)calloc(sizeof(UCHAR8), StrPtr->ImageWidth);
			for(r = 0; r < StrPtr->ImageRows;  r++)
			{
				fread(temp, StrPtr->ImageWidth, sizeof(char),infile);	
				for(i = 0; i < StrPtr->ImageWidth; i++)
					image[r][i] = temp[i];
			}
			free(temp);
		}
		else
		{
			char *temp;
			temp = (char *)calloc(sizeof(char), StrPtr->ImageWidth);	
			for(r = 0; r < StrPtr->ImageRows;  r++)
			{
				fread(temp, StrPtr->ImageWidth, sizeof(char),infile);	
				for(i = 0; i < StrPtr->ImageWidth; i++)
					image[r][i] = temp[i];
			}
			free(temp);
		}
	}	
	else if(StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits == 0 ||
		StrPtr->PtrHeader->Header.Part4.PixelBitDepth_4Bits <= 15) // it is 16 bits
	{
		if(StrPtr->PtrHeader->Header.Part4.SignedPixels == FALSE) // unsigned image
		{
			WORD16 *temp_16;
			temp_16 = (WORD16 *)calloc(sizeof(WORD16), StrPtr->ImageWidth);
			for(r=0; r<StrPtr->ImageRows; r++)
			{
				fread(temp_16, StrPtr->ImageWidth, sizeof(short),infile);	
				for(i = 0; i <  StrPtr->ImageWidth; i++)
				{
					//image[r][i] = ((temp_16[i] & 0x00FF) << 8) + ((temp_16[i] & 0xFF00) >> 8);
					image[r][i] = temp_16[i];
				}
			}			
			free(temp_16);
		}
		else
		{
			short *temp_16;
			temp_16 = (short *)calloc(sizeof(short), StrPtr->ImageWidth);
			for(r=0; r<StrPtr->ImageRows; r++)
			{
				fread(temp_16, StrPtr->ImageWidth, sizeof(short),infile);	
				for(i = 0; i <  StrPtr->ImageWidth; i++)
					image[r][i] = temp_16[i];
			}			
			free(temp_16);
		}

		/* --- Begin bug fix (Kiely) --- */
		// machineendianness will be 1 if computer is big-endian, or 0 if little-endian
		machineendianness = (((char *)&bigendtest)[0]==0);

		// swap pixel byte order if computer and image endianness do not match
		if ( StrPtr->PixelByteOrder != machineendianness)
		{
			const unsigned short MSBmask=0xFF00;
			for(r = 0; r <  StrPtr->ImageRows; r++)
			{
				for (i = 0; i <  StrPtr->ImageWidth; i ++)
					image[r][i] = (image[r][i]>>8) + ((image[r][i]<<8) & MSBmask) ;
			}
		}
		/* --- End bug fix (Kiely) --- */
	}
	else
		ErrorMsg(BPE_FILE_ERROR);

	fclose(infile);
	return BPE_OK;
}

void SegmentBufferFlushEncoder(StructCodingPara *StrCoding) // flush codes and reset
{	
	if(StrCoding->Bits->CodeWordAlighmentBits != 0)
	{
		int shift = 0;
		shift = StrCoding->Bits->CodeWord_Length - 
                            StrCoding->Bits->CodeWordAlighmentBits;
		BitsOutput(StrCoding, 0, shift);
	}
	if((StrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits != 0)
            && (StrCoding->SegmentFull == FALSE) 
            && StrCoding->PtrHeader->Header.Part2.UseFill == TRUE)
	{
		while(StrCoding->SegmentFull == FALSE)
		{
			BitsOutput(StrCoding, 0, 8);
		}
	}
	StrCoding->Bits->SegBitCounter = 0;
	StrCoding->Bits->ByteBuffer_4Bytes = 0;
	StrCoding->Bits->CodeWordAlighmentBits = 0;
	return;
}
// if it is 1, means LSB first, 0 means MSB first
// extern char InputFile[BUFFER_LENGTH],  CodingOutputFile[BUFFER_LENGTH];

void BuildBlockString(int **TransformedImage, int ImageRows, int ImageWidth, 
                                                            long **BlockString)
{
	int i = 0;
	int j = 0; 
	int k = 0; 
	int p = 0;
	int BlockRow = 0;
	int BlockCol = 0;
	int counter = 0;
	UINT32 TotalBlocks = 0;
	
	BlockRow = ImageRows / BLOCK_SIZE;
	BlockCol = ImageWidth / BLOCK_SIZE;

///////////////////////////////////////////////////////////////////////////////
/* Allocate memory for coding of the input image */
	TotalBlocks = BlockRow * BlockCol;
	for(i = 0; i < BlockRow; i ++)
		for ( j= 0; j < BlockCol; j++)
		{
			for ( k= 0; k < BLOCK_SIZE; k ++)
			{
				for (p = 0; p < BLOCK_SIZE; p ++)
                {
					BlockString[counter][p] = 
					TransformedImage[i*BLOCK_SIZE + k][j*BLOCK_SIZE + p];
                }
                counter ++;
			}
		}
	return;
}

// Main encode function
void EncoderEngine(StructCodingPara * PtrCoding)
{
	int  **OriginalImage = NULL;
	int **TransformedImage = NULL;
    int img_param = 0;
    int array_param = 0;
	long **BlockString = NULL;
	UINT32 TotalBlocks = 0;
	UINT32 i = 0;
	UINT32 j = 0;
	UCHAR8 TempPaddedRows = 0;

	BitPlaneBits *BlockCodingInfo;
	// check to see if the file size are correct or not. 
	if (ImageSize(PtrCoding) == BPE_FILE_ERROR)
		ErrorMsg(BPE_FILE_ERROR);

	// determine the last rows we need to replicate.
	if(PtrCoding->ImageRows % BLOCK_SIZE != 0)
		PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits = 
                            BLOCK_SIZE - (PtrCoding->ImageRows % BLOCK_SIZE);

	PtrCoding->PtrHeader->Header.Part4.ImageWidth_20Bits = PtrCoding->ImageWidth;
	
	if(PtrCoding->ImageWidth % BLOCK_SIZE != 0)
		PtrCoding->PadCols_3Bits = BLOCK_SIZE - (PtrCoding->ImageWidth % BLOCK_SIZE );

	// assign space for the original image
    img_param = PtrCoding->ImageRows + PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits;
    array_param = PtrCoding->ImageWidth + PtrCoding->PadCols_3Bits;
	
    OriginalImage = (int**)calloc(img_param, sizeof(int *));  
	for(i = 0; i < img_param; i++)
    {
        OriginalImage[i] = (int*)calloc(array_param, sizeof(int));
    }
		// assign memeory for the transformed image	
		// The OriginalImage matrix is to store the original image and 
	//TransformedImage stores the transformed values. 

	// read into the original image. 
	if ((i = ImageRead(PtrCoding, OriginalImage)) != BPE_OK)
		ErrorMsg(BPE_FILE_ERROR);

	// replicate the last rows and cols if the number of rows
	// and columns are not integal of 8. 

	for(i = 0; i < PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits ; i++)
	{
		for(j = 0; j < array_param; j++)
			OriginalImage[i + PtrCoding->ImageRows][j] = OriginalImage[PtrCoding->ImageRows - 1][j];
	}

	for(i = 0; i < PtrCoding->PadCols_3Bits ; i++)
	{
		for(j = 0; j < img_param; j++)
			OriginalImage[j][i + PtrCoding->ImageWidth] = OriginalImage[j][PtrCoding->ImageWidth - 1];
	}

	TransformedImage = (int **)calloc(img_param, sizeof(int *));  
	for(i = 0; i < img_param; i++)
    {
   		TransformedImage[i] = (int *)calloc(array_param, sizeof(int));	
    }
	/* Read the input image */

///////////////////////////////////////////////////////////////////////////////////////
/* Allocate memory for coding of the input image */
	TotalBlocks =  (PtrCoding->ImageRows +	PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits) / BLOCK_SIZE *
		(PtrCoding->ImageWidth + PtrCoding->PadCols_3Bits )/ BLOCK_SIZE;	

	BlockString = (long **)calloc(TotalBlocks * BLOCK_SIZE,sizeof(long *));
	for(i = 0; i < TotalBlocks * BLOCK_SIZE; i++)
		BlockString[i] = (long *)calloc(BLOCK_SIZE,sizeof(long));

////////////////////////////////////////////////////////////////////////////////
	// Output the coding information into the the output. 
    //
	if((PtrCoding->Bits->F_Bits = fopen(PtrCoding->CodingOutputFile, "wb")) == NULL)  // default name
		ErrorMsg(BPE_FILE_ERROR);
	
	/****************************     1. Transform       *************************/
	DWT_(PtrCoding, OriginalImage, TransformedImage);

    BuildBlockString(TransformedImage, PtrCoding->ImageRows + 
            PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits,
            PtrCoding->ImageWidth + PtrCoding->PadCols_3Bits, 
            BlockString);
	
	TempPaddedRows = PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits;
	PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits = 0;
	for(;PtrCoding->BlockCounter < TotalBlocks; )
	{	
		//////////////////////////////////////////////////////////////////////
		// update the information of header. 

		if (PtrCoding->BlockCounter + PtrCoding->PtrHeader->Header.Part3.S_20Bits == TotalBlocks)
		{
			PtrCoding->PtrHeader->Header.Part1.EngImgFlg = TRUE;
			PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits = TempPaddedRows;
		}
		else if (PtrCoding->BlockCounter + PtrCoding->PtrHeader->Header.Part3.S_20Bits > TotalBlocks)
		{			
			// This part may handle the situation where the number of blocks in the last packet is not exactly the one specified. 
			// For example: if totalblocks = 128, PtrCoding->PtrHeader->Header.Part3.S_20Bits = 10, so in the last packet, 
			// only 8 blocks left, so we need to specify exactly 8 blocks are left in the last packet and part3 may need to be enabled
			PtrCoding->PtrHeader->Header.Part1.EngImgFlg = TRUE;
			PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits = TempPaddedRows;
			PtrCoding->PtrHeader->Header.Part1.Part3Flag = TRUE; 
			PtrCoding->PtrHeader->Header.Part3.S_20Bits = TotalBlocks - PtrCoding->BlockCounter;
			
			PtrCoding->PtrHeader->Header.Part1.Part2Flag = TRUE; 
			PtrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits = PtrCoding->BitsPerPixel * PtrCoding->PtrHeader->Header.Part3.S_20Bits * 64/8;
		}

		BlockCodingInfo = (BitPlaneBits *)calloc(PtrCoding->PtrHeader->Header.Part3.S_20Bits,	sizeof(BitPlaneBits));
//********************************* 2. DC and AC encoding   *************************/	
		DCEncoding(PtrCoding, BlockString, BlockCodingInfo);

        // if (1) the segment is not full and (2) the DCstop is not true, continue AC coding. 
        // Otherwise jump to the codeline that update the header information, block counters, etc. 
		if((PtrCoding->SegmentFull == FALSE) &&  
			 ( !((PtrCoding->PtrHeader->Header.Part2.DCstop == TRUE) && 
                 (PtrCoding->PtrHeader->Header.Part1.Part2Flag == TRUE))))		
		{
			ACBpeEncoding(PtrCoding, BlockCodingInfo);	
	        // Update the bitstream struct. 	
		}

		free(BlockCodingInfo) ;

		if(PtrCoding->PtrHeader->Header.Part1.EngImgFlg == TRUE)
			break;	

		PtrCoding->BlockCounter += PtrCoding->PtrHeader->Header.Part3.S_20Bits;
		HeaderUpdate(PtrCoding->PtrHeader);	

		SegmentBufferFlushEncoder(PtrCoding);
		PtrCoding->SegmentFull = FALSE;
	}
    // free allocated memory
    SegmentBufferFlushEncoder(PtrCoding);	
    for(i = 0; i < TotalBlocks * BLOCK_SIZE; i++)
    {
		free(BlockString[i]);
    }
    free(BlockString);
    for(i = 0; i < img_param; i++)
    {
		free(TransformedImage[i]);
    }
    free(TransformedImage);
	for(i = 0; i < img_param; i++)
    {
        free(OriginalImage[i]);
    }
    free(OriginalImage);
	
	return; 
}
