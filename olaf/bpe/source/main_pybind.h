// Header file including global.h plus binding declarations


#include <string.h>                                                             
#include <stdlib.h>                                                             
#include <time.h>                                                               
#include <ctype.h>                                                              
#include <unistd.h> 
#include <stdio.h>

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

#define max(a,b)    (((a) > (b)) ? (a) : (b))
#define min(a,b)    (((a) < (b)) ? (a) : (b))
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
	unsigned long SegBitCounter;
	unsigned long TotalBitCounter;
	unsigned int ByteBuffer_4Bytes;
	unsigned int CodeWordAlighmentBits;
	unsigned char CodeWord_Length;
	FILE *F_Bits;
} BitStream;

typedef struct SYMBOLDETAILS
{ 
	unsigned char sym_val : 4;
	unsigned char sym_len : 4;
	unsigned char sym_mapped_pattern : 4;
	unsigned char sign : 4;	
	unsigned char type : 3;
}StrSymbolDetails;

typedef struct TYPEC
{ 
	unsigned char TypeC: 4;
}StrTypeC;

typedef struct TRANH
{ 
	unsigned char TranH: 4;
}StrTranH;

typedef struct TRANHI
{ 
	unsigned char TranH: 4;
}StrTranHI;

typedef struct TYPEHIJ
{ 
	StrTranHI TypeHij[4];
}StrTypeHij;

typedef struct PARENTREFINE
{
	unsigned char ParentRefSymbol : 4;
	unsigned char ParentSymbolLength: 2;
}ParentRefine;

typedef struct CHILDRENREF
{
	unsigned short ChildrenRefSymbol : 12;
	unsigned char ChildrenSymbolLength: 4;
}ChildrenRefine;

typedef struct GRANDCHILDREDREF
{
	unsigned short GrandChildrenRefSymbol : 16;
	unsigned char GrandChildrenSymbolLength: 5;
}GrandChildrenRefine;

typedef struct REFINEMENTBIT
{ 
	ParentRefine RefineParent;	
	ChildrenRefine RefineChildren;	
	GrandChildrenRefine RefineGrandChildren[3];
}StrRefine;

typedef struct PLANEHIT
{
	unsigned char TypeP : 3; // i = 0, 1, 2.
	unsigned char TranB : 1; // Ds = 1 or 0. 
	unsigned char TranD : 3; // i = 0, 1, 2.
	StrTypeC TypeCi[3];
	unsigned char TranGi : 3;	
	StrTranH TranHi[3];
	StrTypeHij TypeHij[3];
}PlaneHit;

typedef struct BLOCKBITSHIT
{ 
	// Block address
	long **PtrBlockAddress;
	float **PtrBlockAddressFloating;

	//Bit plane and block information. 
	unsigned char BitPlane : 5;
	long BlockIndex : 20;
	// DC and AC_max information
	unsigned long MappedDC;
	unsigned long ShiftedDC;
	unsigned short DCRemainder; 
	float DecodingDCRemainder;
	unsigned short BitMaxAC;	
	unsigned short MappedAC;
	// status information ( hit history)
	//bit plane hit information.
	PlaneHit StrPlaneHitHistory;
	// code information. 
	StrSymbolDetails SymbolsBlock[MAX_SYMBOLS_IN_BLOCK];
	// refinement bits
	StrRefine RefineBits;

} BitPlaneBits;

//#define DEFAULT_DWORD 100000;


/////////////////////////////////////////

typedef struct HEADER_STRUCTURE_PART1
  {
	unsigned char StartImgFlag;  // 1 bits
	unsigned char EngImgFlg; // 1 bit
	unsigned char SegmentCount_8Bits; //8 bits Senment count/ 
	unsigned char BitDepthDC_5Bits; // 5 bits
	unsigned char BitDepthAC_5Bits; // 5 bits
	unsigned char Reserved; // 1 bits
	unsigned char Part2Flag; // 1 bit
	unsigned char Part3Flag; // 1 bit
	unsigned char Part4Flag; //1 bit	
	unsigned char PadRows_3Bits; // 3 bits replicate the last row so that new rows are integal of 8. 
	unsigned char Reserved_5Bits; // 5 bits: 00000
}HeaderPart1;

typedef struct HEADER_STRUCTURE_PART2
{
	unsigned long SegByteLimit_27Bits; // 27 bits. 		
	unsigned char DCstop; //indicate whether the compressed output stops. 
	unsigned char BitPlaneStop_5Bits; // 5 bits
	unsigned char StageStop_2Bits; // 2 bits, transform input data quantication. 
	unsigned char UseFill;
	unsigned char Reserved_4Bits; // 4 bits	
}HeaderPart2;


typedef struct HEADER_STRUCTURE_PART3
{
	unsigned long S_20Bits; //max number of blocks in a segment is limited to 2^20
	unsigned char OptDCSelect;
	unsigned char OptACSelect;
	unsigned char Reserved_2Bits;
}HeaderPart3;

typedef struct HEADER_STRUCTURE_PART4
{
	unsigned char DWTType; 
	unsigned char Reserved_2Bits; //
	unsigned char SignedPixels;
	unsigned char PixelBitDepth_4Bits;
	unsigned long ImageWidth_20Bits; // maximum image width is limited 2^20
	unsigned char TransposeImg;
	unsigned char CodewordLength_2Bits;
	unsigned char Reserved;
	unsigned char CustomWtFlag;
	unsigned char CustomWtHH1_2bits;
	unsigned char CustomWtHL1_2bits;
	unsigned char CustomWtLH1_2bits;
	unsigned char CustomWtHH2_2bits;
	unsigned char CustomWtHL2_2bits;
	unsigned char CustomWtLH2_2bits;
	unsigned char CustomWtHH3_2bits;
	unsigned char CustomWtHL3_2bits;
	unsigned char CustomWtLH3_2bits;
	unsigned char CustomWtLL3_2bits;
	unsigned short Reserved_11Bits;
}HeaderPart4;
	
typedef struct HEADER
{
	HeaderPart1 Part1; 	 
	HeaderPart2 Part2;	 
	HeaderPart3 Part3;	 
	HeaderPart4 Part4;
}StructHeader;

typedef union HEADERUNION { 
	long Field[5];
	StructHeader Header;
}HeaderStruct;


/////////////////////////////////////

typedef struct STR_STOPLOCATION { 
	char BitPlaneStopDecoding; // for find adjustment. 
	long BlockNoStopDecoding;
	short TotalBitsReadThisTime; 
	unsigned char LocationFind;
	char X_LocationStopDecoding;
	char Y_LocationStopDecoding;
	unsigned char stoppedstage;
}StrStopLocation;


/////////////////////
typedef struct CODINGPARAMETERS
{
	BitStream *Bits;
	unsigned char BitPlane;
	float BitsPerPixel;      // default coding BitsPerPixel, bits per pixels
	unsigned long DecodingAllowedBitsSizeInSegment;      // for decoding purpose. 
	unsigned char RateReached;
	StrStopLocation DecodingStopLocations;
	unsigned char QuantizationFactorQ;
	unsigned int BlockCounter;
	unsigned int block_index;
	unsigned char N;
	unsigned char SegmentFull; 
	HeaderStruct * PtrHeader; 
	unsigned int ImageRows; 
	unsigned int ImageWidth; 
	unsigned char PadCols_3Bits;
	unsigned char PixelByteOrder; // default byte order. 1 means LSB first. 
	char InputFile[100];	
	char CodingOutputFile[100];
}StructCodingPara;
////////////////

typedef struct BLOCKSTRING
{
	long **FreqBlkString;
	float ** FloatingFreqBlk;
	unsigned int Blocks;
	struct BLOCKSTRING *next;
	struct BLOCKSTRING *previous;
}StructFreBlockString;


void ErrorMsg(int err);
void BitsOutput(StructCodingPara *, 	unsigned long ,  int );
short BitsRead(StructCodingPara *,   unsigned long *,  short );

//FILE *F_CodingInfo;
 
//for bpe_encoder.c                                                             
void EncoderEngine(StructCodingPara * PtrCoding);                               
//for bpe_decoder.c                                                             
void DecoderEngine(StructCodingPara * PtrCoding);                               
//for header.c                                                                  
void HeaderInilization(StructCodingPara *Ptr);                                  
                                                                                
//adapted from bpe_main.c                                                       
void Usage();                                                                   
unsigned char ParameterValidCheck(StructCodingPara *PtrCoding);                          
void command_flag_menu();                                                       
//void main_encode();                                                           
//void main_decode(); 
