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
March 9, 2008
*/

//  Modified: Autumn 2023 for PSAS

#include "global.h"

#define VERSION "Last modified November 2023\n"
#define DEBUG
#ifndef DEBUG
#define DEBUG 
#endif

// Original program usage statement
void Usage()
{
	 fprintf(stderr, "/*******Bit Plane Encoder Using Wavelet Transform***/\n");
	 fprintf(stderr, VERSION);
	 fprintf(stderr, "bpe [-e]/[-d] [Input_file_name] [-o Output_file_name] "
             "[-r BitsPerPixel]\n");
	 fprintf(stderr, "\nParameters: \n");
	 fprintf(stderr, "[-e]: encoding filename; \n");
	 fprintf(stderr, "[-d]: decoding filename; \n");
	 fprintf(stderr, "[-o]: provide ouput file name. \n");
	 fprintf(stderr, "[-r]: bits per pixel for encoding. "
             "(by default it is 0 and encoded to the last bitplane\n");
	 fprintf(stderr, "[-w]: the number of pixels of each row. \n");
	 fprintf(stderr, "[-h]: the number of pixels of each column. \n");
	 fprintf(stderr, "[-b]: the number of bits of each pixel. By default it is 8.\n");
	 fprintf(stderr, "[-f]: byte order of a pixel, if it consists of more than "
             "one bytes.\n 0 means litttle endian, 1 means big endian. "
             "Default value is 0.\n");
     fprintf(stderr, "[-t]: wavelet transform. 1 is integer 9-7 DWT and "
                        "0 is floating 9-7 DWT. By default it is integer DWT\n");
     fprintf(stderr, "[-s]: the number of blocks in each segment. "
             "By default it is 256.\n");
	 fprintf(stderr, ""
             "eg 1: bpe -e sensin.img -o codes -r 1.0 -w 256 -h 256 -s 256  \n");
	 fprintf(stderr, "eg 2: bpe -d codes -o ss.img \n");
	 fprintf(stderr, "*********   Author: Hongqiang Wang *******************\n");
	 fprintf(stderr, "*********   Department of Electrical Engineering ******\n");
	 fprintf(stderr, "*********   University of Nebraska -Lincoln ********\n");
	 fprintf(stderr, "*********   March 9, 2008   *********************\n");
	 fprintf(stderr, "/****************************************************\n");
	return;
}

//Parameter Error Check
BOOL ParameterValidCheck(StructCodingPara *PtrCoding)
{
		if((PtrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits != 0) &&
                (PtrCoding->BitsPerPixel <= 0))
			return FALSE;

		if ((PtrCoding->ImageWidth < IMAGE_WIDTH_MIN) || 
                (PtrCoding->ImageWidth > IMAGE_WIDTH_MAX))
			return FALSE;

		if (PtrCoding->ImageRows < IMAGE_ROWS_MIN)
			return FALSE;
		
		if (PtrCoding->PtrHeader->Header.Part3.S_20Bits  < SEGMENT_S_MIN)
			return FALSE;

		if((PtrCoding->BitsPerPixel  < 0) || (PtrCoding->BitsPerPixel  >16))
			return FALSE;

	return TRUE;
}
/************************************************/
#ifndef DEBUG
#define DEBUG
#endif

int main(int argc, char **argv)
{
	char i = 0;
	long TotalPixels = 0;
	char StringBuffer[100]  = {""};

	StructCodingPara *PtrCoding = NULL;

	BOOL BoolEnCoder = FALSE;
	BOOL BoolDeCoder = FALSE ;		
	
	time_t  t0, t1; /* time_t  defined in <time.h> and <sys/types.h> as long */
	clock_t c0, c1; /* clock_t defined in <time.h> and <sys/types.h> as int */
	 
    // included (optional) file from source code; most likely buggy if used
	//F_CodingInfo = NULL;

	PtrCoding = (StructCodingPara*)calloc(sizeof(StructCodingPara), 1);
	HeaderInilization(PtrCoding); 

	while((i = getopt(argc,argv,"e:d:o:r:h:w:b:f:t:s:g:"))!=EOF)
	{
		switch (i)
		{
		case 'e':
			BoolEnCoder = TRUE; // encoder. 
			strcpy(PtrCoding->InputFile, optarg);
			break;
		case 'd':
			BoolDeCoder = TRUE; // decoder
			strcpy(PtrCoding->InputFile, optarg);
			break;
		case 'o':
			strcpy(PtrCoding->CodingOutputFile,optarg);
			break;
		case 'r':   // coding BitsPerPixel, bits per pixels
			strcpy(StringBuffer,optarg);
			PtrCoding->BitsPerPixel = (float)atof(StringBuffer);	
			break;
		case 'h':  // row size
			strcpy(StringBuffer, optarg);
			PtrCoding->ImageRows = atoi(StringBuffer); 
			break;
		case 'w':   // col size
			strcpy(StringBuffer, optarg);
			PtrCoding->ImageWidth = atoi(StringBuffer);
			break;
		case 'f': // flip order. 0: little endian (LSB first) 
			// usually for intel processor, it is 0, the default value. 
			//, 1: big endian
            // If it is 1, byte order will be changed later. 
			strcpy(StringBuffer, optarg);
			PtrCoding->PixelByteOrder = atoi(StringBuffer);
			break;	
		case 'b': // bit per pixel
			strcpy(StringBuffer, optarg);			
		    //PtrCoding->PtrHeader->Header.Part4.PixelBitDepth_4Bits = i
            //                                          atoi(StringBuffer) * 8;
			PtrCoding->PtrHeader->Header.Part4.PixelBitDepth_4Bits = 
                                                        atoi(StringBuffer) % 16;
			break;
		case 't':  // type of wavelet transform			
			strcpy(StringBuffer, optarg);
			PtrCoding->PtrHeader->Header.Part4.DWTType = atoi(StringBuffer);
			break;
		case 'g':  // signed pixels or not		
			strcpy(StringBuffer, optarg);
			PtrCoding->PtrHeader->Header.Part4.SignedPixels = atoi(StringBuffer);
			if(PtrCoding->PtrHeader->Header.Part4.SignedPixels > 0)
				PtrCoding->PtrHeader->Header.Part4.SignedPixels = TRUE;
			else
				PtrCoding->PtrHeader->Header.Part4.SignedPixels= FALSE;
			break;
		case 's':			
			strcpy(StringBuffer, optarg);
			PtrCoding->PtrHeader->Header.Part3.S_20Bits  = atoi(StringBuffer);
			break;

		default:
			Usage();
			strcpy(StringBuffer, "CodingInfo.txt");		
			ErrorMsg(BPE_INVALID_CODING_PARAMETERS);
		}
	}
	///////////////// Validate coding parameters //////////////////////////////
	if((BoolEnCoder && BoolDeCoder) ||
	((!BoolEnCoder) && (!BoolDeCoder)) ||
    // strcmp returns 0 if both strings are identical. 
	(strcmp(PtrCoding->CodingOutputFile, "") == 0) ||	
	(strcmp(PtrCoding->InputFile, "") == 0))
	{
		strcat(StringBuffer, "En.txt");		
        Usage();
		ErrorMsg(BPE_INVALID_CODING_PARAMETERS);		
	}
	///////////////////////////////////////////////////////////////////////////
	if (BoolEnCoder == TRUE)
	{
		//store information to a text file. 
		strcpy(StringBuffer, PtrCoding->CodingOutputFile); 
		strcat(StringBuffer, "En.txt");		
        
		if ((PtrCoding->BitsPerPixel != 0) && 
                PtrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits == 0)
        {
            PtrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits = 
                PtrCoding->BitsPerPixel * 
                PtrCoding->PtrHeader->Header.Part3.S_20Bits * 64/8;
        }

		//check validility of the input parameters. 
		if (ParameterValidCheck(PtrCoding) == FALSE)
			ErrorMsg(BPE_INVALID_CODING_PARAMETERS);		

		// record the encoding time. 
		t0 = time(NULL);
		c0 = clock();	
    	EncoderEngine(PtrCoding);
		c1 = clock();
		t1 = time(NULL);

		TotalPixels = PtrCoding->ImageRows *  PtrCoding->ImageWidth;
	}
	///////////////////////////////////////////////////////////////////////////	
	else if (BoolDeCoder == TRUE)
	{				
		short TotalBitsPerpixel = 0;			
		//store information to a text file. 
		strcpy(StringBuffer, PtrCoding->CodingOutputFile); 
		strcat(StringBuffer, ".txt");

		if(PtrCoding->BitsPerPixel < 0)
			ErrorMsg(BPE_INVALID_CODING_PARAMETERS);

		// record the decoding time. 
		t0 = time(NULL);
		c0 = clock();
		DecoderEngine(PtrCoding);
		c1 = clock();
		t1 = time(NULL);


		TotalBitsPerpixel = PtrCoding->PtrHeader->Header.Part4.PixelBitDepth_4Bits;
		if(TotalBitsPerpixel == 0)
			TotalBitsPerpixel = 16;

		TotalPixels = PtrCoding->ImageRows *  PtrCoding->ImageWidth;
	}
	fclose(PtrCoding->Bits->F_Bits);
	free(PtrCoding->Bits);
	free(PtrCoding->PtrHeader);
	free(PtrCoding);

	return 0;
}
