// implementation file for pybind
                                                                              
#include "source/global.h"                                                      
#include <iostream>


// Original program information
void Usage()                                                                    
{                                                                               
     fprintf(stderr, "/*****   Bit Plane Encoder Using Wavelet Transform    ***/\n");
     fprintf(stderr, "bpe [-e]/[-d] [Input_file_name] [-o Output_file_name] "
             "[-r BitsPerPixel]\n");
     fprintf(stderr, "\nParameters: \n");                                       
     fprintf(stderr, "[-e]: encoding filename; \n");                            
     fprintf(stderr, "[-d]: decoding filename; \n");                            
     fprintf(stderr, "[-o]: provide ouput file name. \n");                      
     fprintf(stderr, "[-w]: the number of pixels of each row. \n");             
     fprintf(stderr, "[-h]: the number of pixels of each column. \n");          
     fprintf(stderr, "[-r]: bits per pixel for encoding. "
             "(by default it is 0 and encoded to the last bitplane\n");
     fprintf(stderr, "[-b]: the number of bits of each pixel. By default it is 8.\n");
     fprintf(stderr, "[-f]: byte order of a pixel, if it consists of more than one bytes.\n" 
             "0 means little endian, 1 means big endian. Default value is 0.\n");
     fprintf(stderr, "[-t]: wavelet transform. 1 is integer 9-7 DWT "
             "and 0 is floating 9-7 DWT. By default it is integer DWT\n");
     fprintf(stderr, "[-s]: the number of blocks in each segment. By default it is 256.\n");
     fprintf(stderr, "eg 1: bpe -e sensin.img -o codes -r 1.0 -w 256 -h 256 -s 256  \n");
     fprintf(stderr, "eg 2: bpe -d codes -o ss.img \n");                        
     fprintf(stderr, "**********  Author: Hongqiang Wang  *****************\n");
     fprintf(stderr, "**********  Department of Electrical Engineering ****\n");
     fprintf(stderr, "**********  University of Nebraska -Lincoln  ********\n");
     fprintf(stderr, "**********  March 9, 2008   *************************\n");
     fprintf(stderr, "/****************************************************\n");
     fprintf(stderr, "/*****  Altered Sept 2023 for OreSat/PSAS  **********\n");
     fprintf(stderr, "/****************************************************\n");
    return;                                                                     
}                                                                               

// Parameter Error Check                                                         
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

// need to verify appropriate means of setting default params
void encode_basearg(char* c_infile, char * c_outfile, const UINT32 w, 
                const UINT32 h, const float bpp = 0, const UINT32 bit_depth = 8)
{
    const UINT32 blocks_per_seg = 256;
    const BOOL is_big_endian = 0;
    const BOOL is_lossless = 1;
    
    encode_fullarg(c_infile, c_outfile, w, h, bpp, bit_depth, blocks_per_seg, 
                                        is_big_endian, is_lossless); 
}

void encode_fullarg(char * c_infile, char* c_outfile, const UINT32 w, 
                    const UINT32 h, const float bpp = 0, const UINT32 bit_depth = 8, 
                    const UINT32 blocks_per_seg = 256, const BOOL is_big_endian = 1, 
                    const BOOL is_lossless = 1)
{                                                                           
    long TotalPixels = 0;
    char StringBuffer[100]  = {""};
    StructCodingPara *PtrCoding = NULL;
    time_t  t0, t1; /* time_t  defined in <time.h> and <sys/types.h> as long */
    clock_t c0, c1; /* clock_t defined in <time.h> and <sys/types.h> as int */
    
    PtrCoding = (StructCodingPara*)calloc(sizeof(StructCodingPara), 1);       
    HeaderInilization(PtrCoding);  

    strcpy(PtrCoding->InputFile, c_infile);
    strcpy(PtrCoding->CodingOutputFile, c_outfile);
    PtrCoding->ImageRows = h; 
    PtrCoding->ImageWidth = w;
    PtrCoding->BitsPerPixel = bpp;	
    PtrCoding->PtrHeader->Header.Part4.PixelBitDepth_4Bits = bit_depth % 16;
    //store information to a text file.                                     
    strcpy(StringBuffer, PtrCoding->CodingOutputFile);                      
    strcat(StringBuffer, "En.txt");                                         
                                                                            
    if((PtrCoding->BitsPerPixel != 0) && PtrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits == 0)
    {
        PtrCoding->PtrHeader->Header.Part2.SegByteLimit_27Bits = 
            (PtrCoding->BitsPerPixel * PtrCoding->PtrHeader->Header.Part3.S_20Bits * 64/8);
    }                                                                    
    //check validility of the input parameters.                             
    if (ParameterValidCheck(PtrCoding) == FALSE)                            
    {
        ErrorMsg(BPE_INVALID_CODING_PARAMETERS);                            
    }
    // record the encoding time.                                            
    t0 = time(NULL);                                                        
    c0 = clock();                                                           
    EncoderEngine(PtrCoding);                                               
    c1 = clock();                                                           
    t1 = time(NULL);      
    TotalPixels = PtrCoding->ImageRows * PtrCoding->ImageWidth;            

    fclose(PtrCoding->Bits->F_Bits);
    free(PtrCoding->Bits);
    free(PtrCoding->PtrHeader);
    free(PtrCoding);

    return;
}

//////// need to include bpp cases for embedded decoding?
void decode(char* c_infile, char* c_outfile)
{                                                                           
    long TotalPixels = 0;
    char StringBuffer[100]  = {""};
    StructCodingPara *PtrCoding = NULL;
    time_t  t0, t1; /* time_t  defined in <time.h> and <sys/types.h> as long */
    clock_t c0, c1; /* clock_t defined in <time.h> and <sys/types.h> as int */

    PtrCoding = (StructCodingPara *) calloc(sizeof(StructCodingPara), 1);       
    HeaderInilization(PtrCoding);  

    strcpy(PtrCoding->InputFile, c_infile);
    strcpy(PtrCoding->CodingOutputFile, c_outfile);

    short TotalBitsPerpixel = 0;               
    //store information to a text file.                                     
    strcpy(StringBuffer, PtrCoding->CodingOutputFile);                      
    strcat(StringBuffer, ".txt");                                           
                                                                            
    if(PtrCoding->BitsPerPixel < 0)                                         
    {
        ErrorMsg(BPE_INVALID_CODING_PARAMETERS);                            
    }
    t0 = time(NULL);                                                        
    c0 = clock();                                                           
    DecoderEngine(PtrCoding);                                               
    c1 = clock();                                                           
    t1 = time(NULL);                                                        
                                                                            
    TotalBitsPerpixel = PtrCoding->PtrHeader->Header.Part4.PixelBitDepth_4Bits;
    if(TotalBitsPerpixel == 0)                                              
    {
        TotalBitsPerpixel = 16;                                             
    }    
    TotalPixels = PtrCoding->ImageRows *  PtrCoding->ImageWidth;            

    fclose(PtrCoding->Bits->F_Bits);
    free(PtrCoding->Bits);
    free(PtrCoding->PtrHeader);
    free(PtrCoding);

    return;
}         
