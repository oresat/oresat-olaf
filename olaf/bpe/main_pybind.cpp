// implementation file for pybind
                                                                              
#include "source/global.h"                                                      
#include <iostream>


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
     fprintf(stderr, "/************  Altered Sept 2023 for OreSat/PSAS  ******************\n");
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

//void command_flag_menu(int argc, char ** argv)
void command_menu()
{
    char i = 0;
    char p = 0;
    char pix_sign = 0;
    float bpp; //bits per pixel
    int value = 0;
    std::string infile_name = "";
    std::string outfile_name = "";
    const char* c_infile = nullptr; 
    const char* c_outfile = nullptr; 
    long TotalPixels = 0;
    char StringBuffer[100]  = {""};

    StructCodingPara *PtrCoding = NULL;

    BOOL BoolEnCoder = FALSE;
    BOOL BoolDeCoder = FALSE ;

    time_t  t0, t1; /* time_t  defined in <time.h> and <sys/types.h> as long */
    clock_t c0, c1; /* clock_t defined in <time.h> and <sys/types.h> as int */

    PtrCoding = (StructCodingPara *) calloc(sizeof(StructCodingPara), 1);       
    HeaderInilization(PtrCoding);  
    
    std::cout << "Enter input file: ";
    std::cin >> infile_name;
    c_infile = infile_name.c_str();
    strcpy(PtrCoding->InputFile, c_infile);
    
    std::cout << "\nEnter output file name: ";
    std::cin >> outfile_name; 
    c_outfile = outfile_name.c_str();
    strcpy(PtrCoding->CodingOutputFile, c_outfile);

    std::cout << "\nEnter [s] to switch pixels to signed (not typical): ";
    std::cin >> pix_sign;
    if (pix_sign=='s')
    {
            PtrCoding->PtrHeader->Header.Part4.SignedPixels = TRUE;
    }

    std::cout << "\nEnter bits/pixel (typically only for encoding),\n"
        << "If non-specified enter 0: ";
    std::cin >> bpp;
    if (bpp != 0)
    {
        PtrCoding->BitsPerPixel = (bpp);	
    }

    std::cout << "\nEncoding [e] or Decoding [d]?: ";
    std::cin >> i;
    while(i != 'd' && i != 'e')
    {
        std::cout << "Input error. Please try again: ";
        std::cin >> i;
    }
    if(i=='d')
    {
        BoolDeCoder = TRUE; // decoder
    }
    else if(i=='e')
    {
        BoolEnCoder = TRUE; // encoder.
        p = 0; 
        std::cout << "\nEnter parameter letter for encoding, then enter value,\n"
            << "Enter [q] when finished: ";
        do
        {
            std::cout << "Parameter letter: ";
            std::cin >> p;
            if (p=='q')
                break;
            std::cout << "Value: ";
            std::cin >> value;

            switch(p)
            {
                case 'h':  // row size
                    PtrCoding->ImageRows = UINT32(value); 
                    break;
                case 'w':   // col size
                    PtrCoding->ImageWidth = UINT32(value);
                    break;
                case 'f': // flip order. 0: little endian (LSB first) 
                    // usually for intel processor, it is 0, the default value. 
                    //, 1: big endian
                    // If it is 1, byte order will be changed later. 
                    PtrCoding->PixelByteOrder = UCHAR8(value);
                    break;	
                case 'b': // bit per pixel
            //		PtrCoding->PtrHeader->Header.Part4.PixelBitDepth_4Bits = atoi(StringBuffer) * 8;
                    PtrCoding->PtrHeader->Header.Part4.PixelBitDepth_4Bits = UCHAR8(value) % 16;
                    break;
                case 't':  // type of wavelet transform			
                    PtrCoding->PtrHeader->Header.Part4.DWTType = BOOL(value);
                    break;
                case 's':			
                    PtrCoding->PtrHeader->Header.Part3.S_20Bits  = DWORD32(value);
                    break;

                default:
                    break;
            }
        }while (p != 'q');
    }
    else
    {
        ErrorMsg(BPE_INVALID_CODING_PARAMETERS);
    }

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
