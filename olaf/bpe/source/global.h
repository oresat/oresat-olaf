// ```This global.h file DOES NOT have bit colons for any struct members.
//
// main header file for source code that has been altered
// -bit colons were removed due to compilation issues
// -reformatted source code to include function declarations here 
//      instead of using externs
// -function declarations for pybind have been included at EOF 

#pragma once

#ifndef _INCL_GUARD
#define _INCL_GUARD

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdio.h>
#include <stdlib.h>   
#include <time.h>     
#include <ctype.h>        
#include <unistd.h>
#include <string.h>      
#include <math.h>     


#define BUFFER_LENGTH 150
#define TRUE 1
#define FALSE 0
#define MAX_SYMBOLS_IN_BLOCK 22

#define INTEGER_WAVELET 1
#define FLOAT_WAVELET 0
#define GAGGLE_SIZE 16

#define NOTRANSPOSE 0
#define TRANSPOSE 1

typedef unsigned char UCHAR8;
typedef unsigned int UINT32;
typedef unsigned long DWORD32;
typedef unsigned short WORD16;
typedef unsigned char BOOL;
 
typedef signed int SINT;
typedef signed char SCHAR;
typedef signed long SLONG;
typedef double DOUBLE4;

#define ERR_MSG(err) BpeErrorMsg[err]
#define AMPLITUDE(a) ((a) >=0 ? (a): -(a))

#define BPE_OK            0
#define BPE_STREAM_END    1
#define BPE_FILE_ERROR   (2)
#define BPE_STREAM_ERROR (3)
#define BPE_DATA_ERROR   (4)
#define BPE_MEM_ERROR    (5)
#define BPE_BLOCKSCAN_CODING_ERROR    (6)
#define BPE_DYNAMICAL_RANGE_ERROR (7)
#define BPE_RATE_ERROR    (8)  
#define BPE_RATE_UNREACHABLE (9)
#define BPE_WAVELET_INVALID (10)
#define BPE_IMAGE_SIZE_WRONG (11)
#define BPE_SCALLING_FILE_ERROR (12)
#define BPE_INVALID_HEADER (13)
#define BPE_INVALID_CODING_PARAMETERS (14)
#define BPE_PATTERNING_CODING_ERROR (15) 
#define BPE_RICE_CODING_ERROR (16) 
#define BPE_STAGE_CODING_ERROR (17) 

#define	ENUM_NONE 0
#define	ENUM_TYPE_P 1
#define	ENUM_TRAN_B 2// Ds = 1 or 0.
#define	ENUM_TRAN_D 3 // i = 0, 1, 2.
#define	ENUM_TYPE_CI 4 
#define	ENUM_TRAN_GI 5
#define	ENUM_TRAN_HI 6 // i = 0, 1, 2. j = 0, 1, 2, 3; four bits
#define	ENUM_TYPE_HIJ 7

#define BLOCK_SIZE 8
#define NEGATIVE_SIGN 1
#define POSITIVE_SIGN 0

#define the_max(a,b) (((a) > (b)) ? (a) : (b))
#define the_min(a,b) (((a) < (b)) ? (a) : (b))

#define SIGN(var) ((var < 0) ? NEGATIVE_SIGN : POSITIVE_SIGN)

// restrictions on the coding parameters
#define IMAGE_WIDTH_MAX (1 << 20)
#define IMAGE_WIDTH_MIN 17
#define IMAGE_ROWS_MIN 17
#define SEGMENT_S_MIN 16
#define SEGMENT_S_MAX (1 << 20)
#define SEGBYTE_MAX (1 << 27)
#define DCDEPTH_MAX (1 << 5)
#define ACDEPTH_MAX (1 << 5)
//////////////////////////////////////////////////////////////////////////////

typedef struct BITSTREAM
{
	DWORD32 SegBitCounter;
	DWORD32 TotalBitCounter;
	UINT32 ByteBuffer_4Bytes;
	UINT32 CodeWordAlighmentBits;
	UCHAR8 CodeWord_Length;
	FILE *F_Bits;
} BitStream;

typedef struct SYMBOLDETAILS
{ 
	UCHAR8 sym_val;
	UCHAR8 sym_len;
	UCHAR8 sym_mapped_pattern;
	UCHAR8 sign;	
	UCHAR8 type;
}StrSymbolDetails;

typedef struct TYPEC
{ 
	UCHAR8 TypeC;
}StrTypeC;

typedef struct TRANH
{ 
	UCHAR8 TranH;
}StrTranH;

typedef struct TRANHI
{ 
	UCHAR8 TranH;
}StrTranHI;

typedef struct TYPEHIJ
{ 
	StrTranHI TypeHij[4];
}StrTypeHij;

typedef struct PARENTREFINE
{
	UCHAR8 ParentRefSymbol;
	UCHAR8 ParentSymbolLength;
}ParentRefine;

typedef struct CHILDRENREF
{
	WORD16 ChildrenRefSymbol;
	UCHAR8 ChildrenSymbolLength;
}ChildrenRefine;

typedef struct GRANDCHILDREDREF
{
	WORD16 GrandChildrenRefSymbol;
	UCHAR8 GrandChildrenSymbolLength;
}GrandChildrenRefine;

typedef struct REFINEMENTBIT
{ 
	ParentRefine RefineParent;	
	ChildrenRefine RefineChildren;	
	GrandChildrenRefine RefineGrandChildren[3];
}StrRefine;

typedef struct PLANEHIT
{
	UCHAR8 TypeP; // i = 0, 1, 2.
	UCHAR8 TranB; // Ds = 1 or 0. 
	UCHAR8 TranD; // i = 0, 1, 2.
	StrTypeC TypeCi[3];
	UCHAR8 TranGi;	
	StrTranH TranHi[3];
	StrTypeHij TypeHij[3];
}PlaneHit;

typedef struct BLOCKBITSHIT
{ 
	// Block address
	long **PtrBlockAddress;
	float **PtrBlockAddressFloating;

	//Bit plane and block information. 
	UCHAR8 BitPlane;
	long BlockIndex;
	// DC and AC_max information
	DWORD32 MappedDC;
	DWORD32 ShiftedDC;
	WORD16 DCRemainder; 
	float DecodingDCRemainder;
	WORD16 BitMaxAC;	
	WORD16 MappedAC;
	// status information ( hit history)
	//bit plane hit information.
	PlaneHit StrPlaneHitHistory;
	// code information. 
	StrSymbolDetails SymbolsBlock[MAX_SYMBOLS_IN_BLOCK];
	// refinement bits
	StrRefine RefineBits;

} BitPlaneBits;

//#define DEFAULT_DWORD 100000;

typedef struct HEADER_STRUCTURE_PART1
  {
	BOOL StartImgFlag;  // 1 bits
	BOOL EngImgFlg; // 1 bit
	UCHAR8 SegmentCount_8Bits; //8 bits Senment count/ 
	UCHAR8 BitDepthDC_5Bits; // 5 bits
                   //         
	UCHAR8 BitDepthAC_5Bits; // 5 bits
	BOOL Reserved; // 1 bits
	BOOL Part2Flag; // 1 bit
	BOOL Part3Flag; // 1 bit
	BOOL Part4Flag; //1 bit	
	UCHAR8 PadRows_3Bits; // 3 bits replicate the last row so that new rows are integal of 8. 
	UCHAR8 Reserved_5Bits; // 5 bits: 00000
}HeaderPart1;

typedef struct HEADER_STRUCTURE_PART2
{
	DWORD32 SegByteLimit_27Bits; // 27 bits. 		
	BOOL DCstop; //indicate whether the compressed output stops. 
	UCHAR8 BitPlaneStop_5Bits; // 5 bits
	UCHAR8 StageStop_2Bits; // 2 bits, transform input data quantication. 
	BOOL UseFill;
	UCHAR8 Reserved_4Bits; // 4 bits	
}HeaderPart2;

typedef struct HEADER_STRUCTURE_PART3
{
	DWORD32 S_20Bits; //max number of blocks in a segment is limited to 2^20
	BOOL OptDCSelect;
	BOOL OptACSelect;
	UCHAR8 Reserved_2Bits;
}HeaderPart3;

typedef struct HEADER_STRUCTURE_PART4
{
	BOOL DWTType; 
	UCHAR8 Reserved_2Bits; //
	BOOL SignedPixels;
	UCHAR8 PixelBitDepth_4Bits;
	DWORD32 ImageWidth_20Bits; // maximum image width is limited 2^20
	BOOL TransposeImg;
	UCHAR8 CodewordLength_2Bits;
	BOOL Reserved;
	BOOL CustomWtFlag;
	UCHAR8 CustomWtHH1_2bits;
	UCHAR8 CustomWtHL1_2bits;
	UCHAR8 CustomWtLH1_2bits;
	UCHAR8 CustomWtHH2_2bits;
	UCHAR8 CustomWtHL2_2bits;
	UCHAR8 CustomWtLH2_2bits;
	UCHAR8 CustomWtHH3_2bits;
	UCHAR8 CustomWtHL3_2bits;
	UCHAR8 CustomWtLH3_2bits;
	UCHAR8 CustomWtLL3_2bits;
	WORD16 Reserved_11Bits;
}HeaderPart4;
	
typedef struct HEADER
{
	HeaderPart1 Part1; 	 
	HeaderPart2 Part2;	 
	HeaderPart3 Part3;	 
	HeaderPart4 Part4;
}StructHeader;

typedef union HEADERUNION { 
	StructHeader Header;
	long Field[5];
}HeaderStruct;

typedef struct STR_STOPLOCATION { 
	char BitPlaneStopDecoding; // for find adjustment. 
	long BlockNoStopDecoding;
	short TotalBitsReadThisTime; 
	BOOL LocationFind;
	char X_LocationStopDecoding;
	char Y_LocationStopDecoding;
	unsigned char stoppedstage;
}StrStopLocation;

typedef struct CODINGPARAMETERS
{
	BitStream *Bits;
	UCHAR8 BitPlane;
	float BitsPerPixel;      // default coding BitsPerPixel, bits per pixels
	DWORD32 DecodingAllowedBitsSizeInSegment;      // for decoding purpose. 
	BOOL RateReached;
	StrStopLocation DecodingStopLocations;
	UCHAR8 QuantizationFactorQ;
	UINT32 BlockCounter;
	UINT32 block_index;
	UCHAR8 N;
	BOOL SegmentFull; 
	HeaderStruct * PtrHeader; 
	UINT32 ImageRows; 
	UINT32 ImageWidth; 
	UCHAR8 PadCols_3Bits;
	UCHAR8 PixelByteOrder; // default byte order. 1 means LSB first. 
	char InputFile[100];	
	char CodingOutputFile[100];
}StructCodingPara;

typedef struct BLOCKSTRING
{
	long **FreqBlkString;
	float ** FloatingFreqBlk;
	UINT32 Blocks;
	struct BLOCKSTRING *next;
	struct BLOCKSTRING *previous;
}StructFreBlockString;

void ErrorMsg(int err);
void BitsOutput(StructCodingPara *, 	DWORD32 ,  int );
short BitsRead(StructCodingPara *,   DWORD32 *,  short );

// included (optional) file from source code; most likely buggy if used 
//FILE * F_CodingInfo = NULL;

// extern functions
void BlockScanEncode(StructCodingPara *PtrCoding, BitPlaneBits *BlockInfo);
void StagesEnCoding(StructCodingPara *PtrCoding, BitPlaneBits *BlockInfo);
void StagesDeCoding(StructCodingPara *PtrCoding, BitPlaneBits *BlockInfo);
long DeConvTwosComp(DWORD32 complement, UCHAR8 leftmost);
void AdjustOutPut(StructCodingPara * PtrCoding, BitPlaneBits * BlockCodingInfo);
void CoeffDegroup(int **img_wav, UINT32 rows, UINT32 cols);
void CoeffDegroupFloating(float **img_wav, UINT32 rows, UINT32 cols);
void HeaderReadin(StructCodingPara *PtrCoding); 
void DWT_Reverse(int **block,  StructCodingPara *PtrCoding);
void DWT_ReverseFloating(float **block, StructCodingPara *PtrCoding);
short DCDeCoding(StructCodingPara *PtrCoding, StructFreBlockString *StrBlocks,
                                            BitPlaneBits *BlockInfo);
void ACBpeDecoding(StructCodingPara *PtrCoding, BitPlaneBits *BlockCodingInfo);
void DWT_(StructCodingPara *, int **, int **);
void HeaderUpdate(HeaderStruct * );
void DCEncoding(StructCodingPara *,	   long **,   BitPlaneBits *);
void ACBpeEncoding(StructCodingPara *,  BitPlaneBits *);
void DebugInfo(char *m);
// char InputFile[BUFFER_LENGTH],  CodingOutputFile[BUFFER_LENGTH];
void EncoderEngine(StructCodingPara * PtrCoding);
void DecoderEngine(StructCodingPara * PtrCoding);
void HeaderInilization(StructCodingPara *Ptr);
void HeaderOutput(StructCodingPara *PtrCoding);
void StagesEnCodingGaggles1(StructCodingPara *PtrCoding, BitPlaneBits *BlockInfo, 
        UCHAR8 BlocksInGaggles, UCHAR8 Option[], BOOL FlagCodeOptionOutput[]); 

void StagesEnCodingGaggles2(StructCodingPara *PtrCoding, BitPlaneBits *BlockInfo, 
        UCHAR8 BlocksInGaggles, UCHAR8 Option[], BOOL FlagCodeOptionOutput[]);
                                                         
void StagesEnCodingGaggles3(StructCodingPara *PtrCoding, BitPlaneBits *BlockInfo,
        UCHAR8 BlocksInGaggles, UCHAR8 Option[], BOOL FlagCodeOptionOutput[]);

void StagesDeCodingGaggles1(StructCodingPara *PtrCoding, BitPlaneBits *BlockCodingInfo,
        UCHAR8 BlocksInGaggles, UCHAR8 *CodeOptionsAllGaggles, 
        BOOL *FlagCodeOptionOutput);
                                                                                
void StagesDeCodingGaggles2(StructCodingPara *PtrCoding, BitPlaneBits *BlockCodingInfo,
        UCHAR8 BlocksInGaggles, UCHAR8 *CodeOptionsAllGaggles, 
        BOOL *FlagCodeOptionOutput);
                                                                                
void StagesDeCodingGaggles3(StructCodingPara *PtrCoding, BitPlaneBits *BlockCodingInfo, 
        UCHAR8 BlocksInGaggles, UCHAR8 *CodeOptionsAllGaggles, 
        BOOL *FlagCodeOptionOutput);

void RiceCoding(short InputVal,short BitLength, UCHAR8 *Option, 
                                                StructCodingPara *PtrCoding); 
void BitPlaneSymbolReset(StrSymbolDetails *SymbolStr);
void RiceDecoding(DWORD32 *decoded, short BitLength, UCHAR8 *splitOption, 
                                                        StructCodingPara *Ptr);
void DeMappingPattern(StrSymbolDetails *StrSymbol);
void CoeffRegroupF97(float **TransformedImage, UINT32 rows, UINT32 cols);   
void CoeffRegroup(int **TransformedImage, UINT32 rows, UINT32 cols);
void DWT_f97_2D(float **rows, UINT32 ImgCols, UINT32 ImgRows, 
                                                    UINT32 levels, BOOL inverse);     
void lifting_M97_2D(int **rows, UINT32 ImgCols, UINT32 ImgRows, 
                                                    UINT32 levels, BOOL inverse);
void lifting_f97_2D(float **rows, UINT32 ImgCols, UINT32 ImgRows, 
                                                    UINT32 levels, BOOL inverse); 

// for bpe_encoder.c
void EncoderEngine(StructCodingPara * PtrCoding);
// for bpe_decoder.c
void DecoderEngine(StructCodingPara * PtrCoding);
// for header.c
void HeaderInilization(StructCodingPara * Ptr);

// adapted from source_main.c
void Usage();
BOOL ParameterValidCheck(StructCodingPara *PtrCoding);

// pybind functions
void command_menu();
void encode_basearg(char * c_infile, char * c_outfile, const UINT32 w, 
                        const UINT32 l, const float bpp, const UINT32 bit_depth);

void encode_fullarg(char * c_infile, char* c_outfile, const UINT32 w, 
                        const UINT32 l, const float bpp, const UINT32 bit_depth,
                        const UINT32 blocks_per_seg, const BOOL is_big_endian, 
                        const BOOL is_lossless);

void decode(char* c_infile, char* c_outfile);

#ifdef __cplusplus
}
#endif

#endif // _INCL_GUARD
