// work in progress
// implementation file for main_pybind.h
//


#include "main_pybind.h"

/*
void EncoderEngine(StructCodingPara * PtrCoding)
{
	int  **OriginalImage = NULL;
	int **TransformedImage = NULL;
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
		PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits = BLOCK_SIZE - (PtrCoding->ImageRows % BLOCK_SIZE);

	PtrCoding->PtrHeader->Header.Part4.ImageWidth_20Bits = PtrCoding->ImageWidth;
	
	if(PtrCoding->ImageWidth % BLOCK_SIZE != 0)
		PtrCoding->PadCols_3Bits = BLOCK_SIZE - (PtrCoding->ImageWidth % BLOCK_SIZE );

	// assign space for the original image

	OriginalImage = (int **)calloc(PtrCoding->ImageRows +	PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits, sizeof(int *));  
	
	for(i = 0; i < PtrCoding->ImageRows + PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits; i++)
		OriginalImage[i] = (int *)calloc(PtrCoding->ImageWidth + PtrCoding->PadCols_3Bits,sizeof(int));
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
		for(j = 0; j < PtrCoding->ImageWidth + PtrCoding->PadCols_3Bits; j++)
			OriginalImage[i + PtrCoding->ImageRows][j] = OriginalImage[PtrCoding->ImageRows - 1][j];
	}

	for(i = 0; i < PtrCoding->PadCols_3Bits ; i++)
	{
		for(j = 0; j < PtrCoding->ImageRows + PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits ; j++)
			OriginalImage[j][i + PtrCoding->ImageWidth] = OriginalImage[j][PtrCoding->ImageWidth - 1];
	}

	TransformedImage = (int **)calloc(PtrCoding->ImageRows +	PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits,sizeof(int *));  
	for(i = 0; i < PtrCoding->ImageRows+ PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits; i++)
   		TransformedImage[i] = (int *)calloc(PtrCoding->ImageWidth + PtrCoding->PadCols_3Bits, sizeof(int));	
	
	// Read the input image 

///////////////////////////////////////////////////////////////////////////////////////
// Allocate memory for coding of the input image 
	TotalBlocks =  (PtrCoding->ImageRows +	PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits) / BLOCK_SIZE *
		(PtrCoding->ImageWidth + PtrCoding->PadCols_3Bits )/ BLOCK_SIZE;	

	BlockString = (long **)calloc(TotalBlocks * BLOCK_SIZE,sizeof(long *));
	for(i = 0; i < TotalBlocks * BLOCK_SIZE; i++)
		BlockString[i] = (long *)calloc(BLOCK_SIZE,sizeof(long));

////////////////////////////////////////////////////////////////////////////////
	// Output the coding information into the the output. 
	if((PtrCoding->Bits->F_Bits = fopen(PtrCoding->CodingOutputFile, "wb")) == NULL)  // default name
		ErrorMsg(BPE_FILE_ERROR);
	
    //1.Transform
	DWT_(PtrCoding, OriginalImage, TransformedImage);
	
		BuildBlockString(TransformedImage, PtrCoding->ImageRows + PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits,
		PtrCoding->ImageWidth + PtrCoding->PadCols_3Bits, BlockString);
	for(i = 0; i < PtrCoding->ImageRows; i++)
		free(TransformedImage[i]);
	free(TransformedImage);

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

///////////////////////////////////////////////////////////////////////////
		BlockCodingInfo = (BitPlaneBits *)calloc(PtrCoding->PtrHeader->Header.Part3.S_20Bits,	sizeof(BitPlaneBits));
*/
        /********************************* 2. DC and AC encoding   *************************/	
/*
        DCEncoding(PtrCoding, BlockString, BlockCodingInfo);

		if((PtrCoding->SegmentFull == FALSE) &&  // if (1) the segment is not full and (2) the DCstop is not true, continue AC coding. 
			// Otherwise jump to the codeline that update the header information, block counters, etc. 
			 ( !((PtrCoding->PtrHeader->Header.Part2.DCstop == TRUE) && (PtrCoding->PtrHeader->Header.Part1.Part2Flag == TRUE))))		
		{
			ACBpeEncoding(PtrCoding, BlockCodingInfo);	
			free(BlockCodingInfo) ;
	        // Update the bitstream struct. 	
		}

		if(PtrCoding->PtrHeader->Header.Part1.EngImgFlg == TRUE)
			break;	

		PtrCoding->BlockCounter += PtrCoding->PtrHeader->Header.Part3.S_20Bits;
		HeaderUpdate(PtrCoding->PtrHeader);	

		SegmentBufferFlushEncoder(PtrCoding);
		PtrCoding->SegmentFull = FALSE;
		
	}
*/
// ***************************  5. header information  *****************************//
/*    SegmentBufferFlushEncoder(PtrCoding);	
	for(i = 0; i < TotalBlocks * BLOCK_SIZE; i++)
		free(BlockString[i]);
	free(BlockString);
	return ; 
}

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

	
	PtrCoding->Bits = (BitStream *)calloc(sizeof(BitStream), 1);
	
	if((PtrCoding->Bits->F_Bits = fopen(PtrCoding->InputFile, "rb")) == NULL)  // default name
		ErrorMsg(BPE_FILE_ERROR);

	HeaderReadin(PtrCoding); // read first header. 	
	PtrCoding->ImageWidth = PtrCoding->PtrHeader->Header.Part4.ImageWidth_20Bits;	
	
	if(PtrCoding->ImageWidth % BLOCK_SIZE != 0)
		PtrCoding->PadCols_3Bits = BLOCK_SIZE - (PtrCoding->ImageWidth % 8 );
	else 
		PtrCoding->PadCols_3Bits  =  0;
	
	StrFreBlockString = (StructFreBlockString *)calloc(sizeof(StructFreBlockString), 1);
	StrFreBlockString->next = NULL;
	StrFreBlockString->previous = NULL;

	TotalBlocks = 0;
	for(;;)
	{		
		BitPlaneBits * BlockCodingInfo;
		BlockCodingInfo = (BitPlaneBits *)calloc(PtrCoding->PtrHeader->Header.Part3.S_20Bits,	sizeof(BitPlaneBits));
		TotalBlocks += PtrCoding->PtrHeader->Header.Part3.S_20Bits;

		StrFreBlockString->FreqBlkString = (long **)calloc(PtrCoding->PtrHeader->Header.Part3.S_20Bits * BLOCK_SIZE,sizeof(long *));
		for(i = 0; i < PtrCoding->PtrHeader->Header.Part3.S_20Bits * BLOCK_SIZE; i++)
			StrFreBlockString->FreqBlkString[i] = (long *)calloc(BLOCK_SIZE,sizeof(long));


		StrFreBlockString->FloatingFreqBlk  = (float **)calloc(PtrCoding->PtrHeader->Header.Part3.S_20Bits * BLOCK_SIZE,sizeof(float *));
		for(i = 0; i < PtrCoding->PtrHeader->Header.Part3.S_20Bits * BLOCK_SIZE; i++)
			StrFreBlockString->FloatingFreqBlk[i] = (float *)calloc(BLOCK_SIZE,sizeof(float));

		StrFreBlockString->Blocks = PtrCoding->PtrHeader->Header.Part3.S_20Bits;
		DCDeCoding(PtrCoding, StrFreBlockString, BlockCodingInfo);
		ACBpeDecoding(PtrCoding, BlockCodingInfo) ;	// This means the decoding process stops before segment limit. 
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
		tempStr = (StructFreBlockString *)calloc(sizeof(StructFreBlockString), 1);			
		(StrFreBlockString->next) = tempStr;
		tempStr->previous = StrFreBlockString;
		tempStr->next = NULL;
		StrFreBlockString = StrFreBlockString->next;
	}
*/
// ***************************  5. header information  *****************************//
/*
	PtrCoding->ImageRows = TotalBlocks * 64 /  (PtrCoding->ImageWidth + PtrCoding->PadCols_3Bits ); 

	imgout_integercase = (int **)calloc(PtrCoding->ImageRows,sizeof(int *)); 
	for(i = 0; i < PtrCoding->ImageRows; i++)
		imgout_integercase[i] = (int *)calloc((PtrCoding->ImageWidth + PtrCoding->PadCols_3Bits),sizeof(int));	

	imgout_floatingcase = (float **)calloc(PtrCoding->ImageRows,sizeof(float *)); 
	for(i = 0; i < PtrCoding->ImageRows; i++)
		imgout_floatingcase[i] = (float *)calloc((PtrCoding->ImageWidth + PtrCoding->PadCols_3Bits),sizeof(float));	

	while(StrFreBlockString->previous != NULL)
		StrFreBlockString = StrFreBlockString->previous;
	do{
		UINT32 F_x = 0;
		do
		{
			for( i = 0; i < BLOCK_SIZE; i++)
				for( j = 0; j < BLOCK_SIZE; j++)
				{
					imgout_integercase[X + i][Y + j] = StrFreBlockString->FreqBlkString[F_x + i][j];
					imgout_floatingcase[X + i][Y + j] =StrFreBlockString->FloatingFreqBlk[F_x + i][j];
				}
				
			Y += BLOCK_SIZE;

			if( Y >= PtrCoding->ImageWidth)
			{
				Y = 0;
				X += BLOCK_SIZE;
			}
			F_x += BLOCK_SIZE;
		}while (F_x <  StrFreBlockString->Blocks * BLOCK_SIZE);				
			
		StrFreBlockString = StrFreBlockString->next;
	}while(StrFreBlockString != NULL);
	
	if(PtrCoding->PtrHeader->Header.Part4.DWTType == INTEGER_WAVELET)
		DecodingOutputInteger(PtrCoding, imgout_integercase);
	else
		DecodingOutputFloating(PtrCoding, imgout_floatingcase);
	
	fclose(PtrCoding->Bits->F_Bits);
	free(imgout_integercase);
	return; 
}
*/

void Usage()                                                                    
{                                                                               
     fprintf(stderr, "/******************   Bit Plane Encoder Using Wavelet Transform    ************/\n");
     fprintf(stderr, "bpe [-e]/[-d] [Input_file_name] [-o Output_file_name] [-r BitsPerPixel]\n");
     fprintf(stderr, "\nParameters: \n");                                       
     fprintf(stderr, "[-e]: encoding filename; \n");                            
     fprintf(stderr, "[-d]: decoding filename; \n");                            
     fprintf(stderr, "[-o]: provide ouput file name. \n");                      
     fprintf(stderr, "[-r]: bits per pixel for encoding. (by default it is 0 and encoded to the last bitplane\n");
     fprintf(stderr, "[-w]: the number of pixels of each row. \n");             
     fprintf(stderr, "[-h]: the number of pixels of each column. \n");          
     fprintf(stderr, "[-b]: the number of bits of each pixel. By default it is 8.\n");
     fprintf(stderr, "[-f]: byte order of a pixel, if it consists of more than one bytes.\n 0 means litttle endian, 1 means big endian. Default value is 0.\n");
     fprintf(stderr, "[-t]: wavelet transform. 1 is integer 9-7 DWT and 0 is floating 9-7 DWT. By default it is integer DWT\n");
     fprintf(stderr, "[-s]: the number of blocks in each segment. By default it is 256.\n");
     fprintf(stderr, "eg 1: bpe -e sensin.img -o codes -r 1.0 -w 256 -h 256 -s 256  \n");
     fprintf(stderr, "eg 2: bpe -d codes -o ss.img \n");                        
     fprintf(stderr, "*************   Author: Hongqiang Wang  *******************************\n");
     fprintf(stderr, "*************   Department of Electrical Engineering    ********************\n");
     fprintf(stderr, "*************   University of Nebraska -Lincoln  **************************\n");
     fprintf(stderr, "*************   March 9, 2008   ******************************************\n");
     fprintf(stderr, "/*******************************************************************\n");
    return;                                                                     
}                                                                               

//Parameter Error Check                                                         
BOOL ParameterValidCheck(StructCodingPara *PtrCoding)                           
{                                                                               
    if((PtrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits != 0) &&( PtrCoding->BitsPerPixel <= 0 ))
        return FALSE;                                                       
                                                                            
    if ((PtrCoding->ImageWidth < IMAGE_WIDTH_MIN) || (PtrCoding->ImageWidth > IMAGE_WIDTH_MAX))
        return FALSE;                                                       
                                                                            
    if (PtrCoding->ImageRows < IMAGE_ROWS_MIN)                              
        return FALSE;                                                       
                                                                            
    if (PtrCoding->PtrHeader->Header.Part3.S_20Bits  < SEGMENT_S_MIN)       
        return FALSE;                                                       
                                                                            
    if((PtrCoding->BitsPerPixel  < 0) || (PtrCoding->BitsPerPixel  >16))    
        return FALSE;                                                       
                                                                                
    return TRUE;                                                                
}

void command_flag_menu()
{
    char i = 0;
    long TotalPixels = 0;
    char StringBuffer[100]  = {""};

    StructCodingPara *PtrCoding = NULL;

    BOOL BoolEnCoder = FALSE;
    BOOL BoolDeCoder = FALSE ;

    time_t  t0, t1; /* time_t  defined in <time.h> and <sys/types.h> as long */
    clock_t c0, c1; /* clock_t defined in <time.h> and <sys/types.h> as int */

    PtrCoding = (StructCodingPara *) calloc(sizeof(StructCodingPara), 1);       
    HeaderInilization(PtrCoding);  

    

	do
    {
        char choice = 0;
        fgets(&choice, 1, stdin);
        scanf(&choice, "%d", &i);
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
	//		PtrCoding->PtrHeader->Header.Part4.PixelBitDepth_4Bits = atoi(StringBuffer) * 8;
			PtrCoding->PtrHeader->Header.Part4.PixelBitDepth_4Bits = atoi(StringBuffer) % 16;
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
			/*
			if ((F_CodingInfo = fopen(StringBuffer,"w")) == NULL) 
			{
				fprintf(stderr, "Cannot creat coding information file. \n");
				exit(0);
			}
			*/
			ErrorMsg(BPE_INVALID_CODING_PARAMETERS);
		}
    }while(!EOF);

    if((BoolEnCoder && BoolDeCoder) ||
    ((!BoolEnCoder) && (!BoolDeCoder)) ||
    (strcmp(PtrCoding->CodingOutputFile, "") == 0) ||   // strcmp returns 0 if both stri    ngs are identical.
    (strcmp(PtrCoding->InputFile, "") == 0))
    {
        strcat(StringBuffer, "En.txt");
        /*
        if ((F_CodingInfo = fopen(StringBuffer,"w")) == NULL)
        {
            fprintf(stderr, "Cannot creat coding information file. \n");
            exit(0);
        }
        */
        Usage();
        ErrorMsg(BPE_INVALID_CODING_PARAMETERS);
    } 
    if (BoolEnCoder == TRUE)
    {                                                                           
        //store information to a text file.                                     
        strcpy(StringBuffer, PtrCoding->CodingOutputFile);                      
        strcat(StringBuffer, "En.txt");                                         
        /*                                                                      
        if ((F_CodingInfo = fopen(StringBuffer,"w")) == NULL)                   
        {                                                                       
            fprintf(stderr, "Cannot creat coding information file. \n");        
            exit(0);                                                            
        }                                                                       
        */                                                                      
                                                                                
        if((PtrCoding->BitsPerPixel != 0) && PtrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits == 0)
        {
            PtrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits = 
                (PtrCoding->BitsPerPixel * PtrCoding->PtrHeader->Header.Part3.S_20Bits * 64/8);
        }                                                                    

        //check validility of the input parameters.                             
        if (ParameterValidCheck(PtrCoding) == FALSE)                            
        {
            ErrorMsg(BPE_INVALID_CODING_PARAMETERS);                            
        // DebugInfo( "\tBegin to encode...\n");                                
        }

        // record the encoding time.                                            
        t0 = time(NULL);                                                        
        c0 = clock();                                                           
        EncoderEngine(PtrCoding);                                               
        c1 = clock();                                                           
        t1 = time(NULL);                                                        
                                                                                
        // DebugInfo( "\tEncoding Success!\n");                                 
        // fprintf (stderr, "\telapsed CPU time:        %f\n", (float) (c1 - c0)/CLOCKS_PER_SEC);       
                                                                                
        TotalPixels = PtrCoding->ImageRows *  PtrCoding->ImageWidth;            
        // fprintf(F_CodingInfo, "Success! %f ", (float) PtrCoding->Bits->TotalBitCounter/ TotalPixels);
    }

    else if (BoolDeCoder == TRUE)
    {                                                                           
        short TotalBitsPerpixel = 0;                                            
        //store information to a text file.                                     
        strcpy(StringBuffer, PtrCoding->CodingOutputFile);                      
        strcat(StringBuffer, ".txt");                                           
                                                                                
        /*                                                                      
        if ((F_CodingInfo = fopen(StringBuffer,"w")) == NULL)                   
        {                                                                       
            fprintf(stderr, "Cannot creat coding information file. \n");        
            exit(0);                                                            
        }                                                                       
        */                                                                      
                                                                                
        if(PtrCoding->BitsPerPixel < 0)                                         
        {
            ErrorMsg(BPE_INVALID_CODING_PARAMETERS);                            
        }

        // DebugInfo( "\tBegin to decode...\n");                                
        // record the decoding time.                                            
        t0 = time(NULL);                                                        
        c0 = clock();                                                           
        DecoderEngine(PtrCoding);                                               
        c1 = clock();                                                           
        t1 = time(NULL);                                                        
                                                                                
        // DebugInfo( "\tDecoding Success!\n");                                 
        // fprintf (stderr, "\telapsed CPU time:        %f\n", (float) (c1 - c0)/CLOCKS_PER_SEC);
                                                                                
        TotalBitsPerpixel = PtrCoding->PtrHeader->Header.Part4.PixelBitDepth_4Bits;
        if(TotalBitsPerpixel == 0)                                              
        {
            TotalBitsPerpixel = 16;                                             
        }    

        TotalPixels = PtrCoding->ImageRows *  PtrCoding->ImageWidth;            
        
        /*                                                                      
        fprintf(F_CodingInfo, "%s %f  %d  %d  %d", "Success!", (float) PtrCoding->Bits->TotalBitCounter/ TotalPixels, 
            PtrCoding->ImageRows, PtrCoding->ImageWidth, TotalBitsPerpixel);    
        */                                                                      
    }         
    free(PtrCoding);
}

//attempted separate functions
/*
void main_encode()
{                                                                           
    //store information to a text file.                                     
    strcpy(StringBuffer, PtrCoding->CodingOutputFile);                      
    strcat(StringBuffer, "En.txt");                                         
    *//*                                                                      
    if ((F_CodingInfo = fopen(StringBuffer,"w")) == NULL)                   
    {                                                                       
        fprintf(stderr, "Cannot creat coding information file. \n");        
        exit(0);                                                            
    }                                                                       
    *//*                                                                      
                                                                            
    if((PtrCoding->BitsPerPixel != 0) && PtrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits == 0)
    {
        PtrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits = 
            (PtrCoding->BitsPerPixel * PtrCoding->PtrHeader->Header.Part3.S_20Bits * 64/8);
    }                                                                    

    //check validility of the input parameters.                             
    if (ParameterValidCheck(PtrCoding) == FALSE)                            
    {
        ErrorMsg(BPE_INVALID_CODING_PARAMETERS);                            
    // DebugInfo( "\tBegin to encode...\n");                                
    }

    // record the encoding time.                                            
    t0 = time(NULL);                                                        
    c0 = clock();                                                           
    EncoderEngine(PtrCoding);                                               
    c1 = clock();                                                           
    t1 = time(NULL);                                                        
                                                                            
    // DebugInfo( "\tEncoding Success!\n");                                 
    // fprintf (stderr, "\telapsed CPU time:        %f\n", (float) (c1 - c0)/CLOCKS_PER_SEC);       
                                                                            
    TotalPixels = PtrCoding->ImageRows *  PtrCoding->ImageWidth;            
    // fprintf(F_CodingInfo, "Success! %f ", (float) PtrCoding->Bits->TotalBitCounter/ TotalPixels);
}


void main_decode()                                               
{                                                                           
    short TotalBitsPerpixel = 0;                                            
    //store information to a text file.                                     
    strcpy(StringBuffer, PtrCoding->CodingOutputFile);                      
    strcat(StringBuffer, ".txt");                                           
                                                                            
    *//*                                                                      
    if ((F_CodingInfo = fopen(StringBuffer,"w")) == NULL)                   
    {                                                                       
        fprintf(stderr, "Cannot creat coding information file. \n");        
        exit(0);                                                            
    }                                                                       
    *//*                                                                      
                                                                            
    if(PtrCoding->BitsPerPixel < 0)                                         
    {
        ErrorMsg(BPE_INVALID_CODING_PARAMETERS);                            
    }

    // DebugInfo( "\tBegin to decode...\n");                                
    // record the decoding time.                                            
    t0 = time(NULL);                                                        
    c0 = clock();                                                           
    DecoderEngine(PtrCoding);                                               
    c1 = clock();                                                           
    t1 = time(NULL);                                                        
                                                                            
    // DebugInfo( "\tDecoding Success!\n");                                 
    // fprintf (stderr, "\telapsed CPU time:        %f\n", (float) (c1 - c0)/CLOCKS_PER_SEC);
                                                                            
    TotalBitsPerpixel = PtrCoding->PtrHeader->Header.Part4.PixelBitDepth_4Bits;
    if(TotalBitsPerpixel == 0)                                              
    {
        TotalBitsPerpixel = 16;                                             
    }    

    TotalPixels = PtrCoding->ImageRows *  PtrCoding->ImageWidth;            
    
    //fprintf(F_CodingInfo, "%s %f  %d  %d  %d", "Success!", (float) PtrCoding->Bits->TotalBitCounter/ TotalPixels, 
    //    PtrCoding->ImageRows, PtrCoding->ImageWidth, TotalBitsPerpixel);    
                                                                          
}         
*/
