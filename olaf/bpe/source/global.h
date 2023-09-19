/* this header file defines global marco variabls and constans. Most c files
include this file*/

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
	DWORD32 SegBitCounter;
	DWORD32 TotalBitCounter;
	UINT32 ByteBuffer_4Bytes;
	UINT32 CodeWordAlighmentBits;
	UCHAR8 CodeWord_Length;
	FILE *F_Bits;
} BitStream;

typedef struct SYMBOLDETAILS
{ 
	UCHAR8 sym_val : 4;
	UCHAR8 sym_len : 4;
	UCHAR8 sym_mapped_pattern : 4;
	UCHAR8 sign : 4;	
	UCHAR8 type : 3;
}StrSymbolDetails;

typedef struct TYPEC
{ 
	UCHAR8 TypeC: 4;
}StrTypeC;

typedef struct TRANH
{ 
	UCHAR8 TranH: 4;
}StrTranH;

typedef struct TRANHI
{ 
	UCHAR8 TranH: 4;
}StrTranHI;

typedef struct TYPEHIJ
{ 
	StrTranHI TypeHij[4];
}StrTypeHij;

typedef struct PARENTREFINE
{
	UCHAR8 ParentRefSymbol : 4;
	UCHAR8 ParentSymbolLength: 2;
}ParentRefine;

typedef struct CHILDRENREF
{
	WORD16 ChildrenRefSymbol : 12;
	UCHAR8 ChildrenSymbolLength: 4;
}ChildrenRefine;

typedef struct GRANDCHILDREDREF
{
	WORD16 GrandChildrenRefSymbol : 16;
	UCHAR8 GrandChildrenSymbolLength: 5;
}GrandChildrenRefine;

typedef struct REFINEMENTBIT
{ 
	ParentRefine RefineParent;	
	ChildrenRefine RefineChildren;	
	GrandChildrenRefine RefineGrandChildren[3];
}StrRefine;

typedef struct PLANEHIT
{
	UCHAR8 TypeP : 3; // i = 0, 1, 2.
	UCHAR8 TranB : 1; // Ds = 1 or 0. 
	UCHAR8 TranD : 3; // i = 0, 1, 2.
	StrTypeC TypeCi[3];
	UCHAR8 TranGi : 3;	
	StrTranH TranHi[3];
	StrTypeHij TypeHij[3];
}PlaneHit;

typedef struct BLOCKBITSHIT
{ 
	// Block address
	long **PtrBlockAddress;
	float **PtrBlockAddressFloating;

	//Bit plane and block information. 
	UCHAR8 BitPlane : 5;
	long BlockIndex : 20;
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
	BOOL StartImgFlag : 1;  // 1 bits
	BOOL EngImgFlg : 1; // 1 bit
	UCHAR8 SegmentCount_8Bits : 8; //8 bits Senment count/ 
	UCHAR8 BitDepthDC_5Bits : 5; // 5 bits
	UCHAR8 BitDepthAC_5Bits : 5; // 5 bits
	BOOL Reserved : 1; // 1 bits
	BOOL Part2Flag : 1; // 1 bit
	BOOL Part3Flag : 1; // 1 bit
	BOOL Part4Flag : 1; //1 bit	
	UCHAR8 PadRows_3Bits : 3; // 3 bits replicate the last row so that new rows are integal of 8. 
	UCHAR8 Reserved_5Bits : 5; // 5 bits: 00000
}HeaderPart1;

typedef struct HEADER_STRUCTURE_PART2
{
	DWORD32 SegByteLimit_27Bits : 27; // 27 bits. 		
	BOOL DCstop : 1; //indicate whether the compressed output stops. 
	UCHAR8 BitPlaneStop_5Bits : 5; // 5 bits
	UCHAR8 StageStop_2Bits : 2; // 2 bits, transform input data quantication. 
	BOOL UseFill : 1;
	UCHAR8 Reserved_4Bits : 4; // 4 bits	
}HeaderPart2;


typedef struct HEADER_STRUCTURE_PART3
{
	DWORD32 S_20Bits : 20; //max number of blocks in a segment is limited to 2^20
	BOOL OptDCSelect : 1;
	BOOL OptACSelect : 1;
	UCHAR8 Reserved_2Bits : 2;
}HeaderPart3;

typedef struct HEADER_STRUCTURE_PART4
{
	BOOL DWTType : 1; 
	UCHAR8 Reserved_2Bits : 2; //
	BOOL SignedPixels : 1;
	UCHAR8 PixelBitDepth_4Bits : 4;
	DWORD32 ImageWidth_20Bits : 20; // maximum image width is limited 2^20
	BOOL TransposeImg : 1;
	UCHAR8 CodewordLength_2Bits : 2;
	BOOL Reserved : 1;
	BOOL CustomWtFlag : 1;
	UCHAR8 CustomWtHH1_2bits : 2;
	UCHAR8 CustomWtHL1_2bits : 2;
	UCHAR8 CustomWtLH1_2bits : 2;
	UCHAR8 CustomWtHH2_2bits : 2;
	UCHAR8 CustomWtHL2_2bits : 2;
	UCHAR8 CustomWtLH2_2bits : 2;
	UCHAR8 CustomWtHH3_2bits : 2;
	UCHAR8 CustomWtHL3_2bits : 2;
	UCHAR8 CustomWtLH3_2bits : 2;
	UCHAR8 CustomWtLL3_2bits : 2;
	WORD16 Reserved_11Bits : 11;
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
	UCHAR8 QuantizationFactorQ:6;
	UINT32 BlockCounter;
	UINT32 block_index;
	UCHAR8 N;
	BOOL SegmentFull; 
	HeaderStruct * PtrHeader; 
	UINT32 ImageRows; 
	UINT32 ImageWidth; 
	UCHAR8 PadCols_3Bits;
	UCHAR8 PixelByteOrder:1; // default byte order. 1 means LSB first. 
	char InputFile[100];	
	char CodingOutputFile[100];
} StructCodingPara;

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

//FILE *F_CodingInfo;

