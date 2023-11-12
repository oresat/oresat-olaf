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


void CoefficientsRescaling(int **transformed,
						   UINT32 Rows,
						   UINT32 Cols,
						   HeaderPart4 StrHead4)
{
	UINT32 i = 0; 
	UINT32 j = 0;
	short scales[10] = {0};
	
	if (StrHead4.CustomWtFlag == TRUE)
	{
		scales[0] = (1 << StrHead4.CustomWtHH1_2bits);		
		scales[1] = (1 << StrHead4.CustomWtHL1_2bits);
		scales[2] = (1 << StrHead4.CustomWtLH1_2bits);		
		scales[3] = (1 << StrHead4.CustomWtHH2_2bits);
		scales[4] = (1 << StrHead4.CustomWtHL2_2bits);		
		scales[5] = (1 << StrHead4.CustomWtLH2_2bits);
		scales[6] = (1 << StrHead4.CustomWtHH3_2bits);		
		scales[7] = (1 << StrHead4.CustomWtHL3_2bits);
		scales[8] = (1 << StrHead4.CustomWtLH3_2bits);		
		scales[9] = (1 << StrHead4.CustomWtLL3_2bits);
	}
	else
	{
		scales[0] = 1;		
		scales[1] = 2;
		scales[2] = 2;		
		scales[3] = 2;
		scales[4] = 4;		
		scales[5] = 4;
		scales[6] = 4;		
		scales[7] = 8;
		scales[8] = 8;		
		scales[9] = 8;
	}


// HH1 band. 
	for (i = (Rows>>1); i < Rows; i++)
		for(j = (Cols>>1); j < Cols; j++)
			transformed[i][j] = transformed[i][j] / scales[0];
	for (i = 0; i < (Rows>>1); i++)
		for(j = (Cols>>1); j < Cols; j++)
			transformed[i][j] = transformed[i][j] /  scales[1];
// LH1
	for (i = (Rows>>1); i < Rows; i++)
		for(j = 0; j < (Cols>>1); j++)
			transformed[i][j] = transformed[i][j] /  scales[2];

// HH2 band. 
	for (i = (Rows>>2); i < (Rows>>1); i++)
		for(j = (Cols>>2); j < (Cols>>1); j++)
			transformed[i][j] = transformed[i][j] /  scales[3];

// HL2
	for (i = 0; i < (Rows>>2); i++)
		for(j = (Cols>>2); j < (Cols>>1); j++)
			transformed[i][j] = transformed[i][j] /  scales[4];
// LH2

	for (i = (Rows>>2); i < (Rows>>1); i++)
		for(j = 0; j < (Cols>>2); j++)
			transformed[i][j] = transformed[i][j] /  scales[5];
// HH3 band. 
	for (i = (Rows>>3); i < (Rows>>2); i++)
		for(j = (Cols>>3); j < (Cols>>2); j++)
			transformed[i][j] = transformed[i][j] /  scales[6];

// HL3
	for (i = 0; i < (Rows>>3); i++)
		for(j = (Cols>>3); j < (Cols>>2); j++)
			transformed[i][j] = transformed[i][j] /  scales[7];	
// LH3
	for (i = (Rows>>3); i < (Rows>>2); i++)
		for(j = 0; j < (Cols>>3); j++)
			transformed[i][j] = transformed[i][j] /  scales[8];

// LL3
	for (i = 0; i < (Rows>>3); i++)
		for(j = 0; j < (Cols>>3); j++)
			transformed[i][j] = transformed[i][j] /  scales[9];
}  

void CoefficientsScaling(int **transformed,
			   int Rows,
			   int Cols,
			   HeaderPart4 StrHead4)
{
	int i;
	int j;
	short scales[10];
	
	if (StrHead4.CustomWtFlag == TRUE)
	{
		scales[0] = (1 << StrHead4.CustomWtHH1_2bits);				
		scales[1] = (1 << StrHead4.CustomWtHL1_2bits);
		scales[2] = (1 << StrHead4.CustomWtLH1_2bits);		
		scales[3] = (1 << StrHead4.CustomWtHH2_2bits);
		scales[4] = (1 << StrHead4.CustomWtHL2_2bits);		
		scales[5] = (1 << StrHead4.CustomWtLH2_2bits);
		scales[6] = (1 << StrHead4.CustomWtHH3_2bits);		
		scales[7] = (1 << StrHead4.CustomWtHL3_2bits);
		scales[8] = (1 << StrHead4.CustomWtLH3_2bits);		
		scales[9] = (1 << StrHead4.CustomWtLL3_2bits);
	}
	else
	{
		scales[0] = 1;		
		scales[1] = 2;
		scales[2] = 2;		
		scales[3] = 2;
		scales[4] = 4;		
		scales[5] = 4;
		scales[6] = 4;		
		scales[7] = 8;
		scales[8] = 8;		
		scales[9] = 8;
	}


// HH1 band. 
	for (i = (Rows>>1); i < Rows; i++)
		for(j = (Cols>>1); j < Cols; j++)
			transformed[i][j] = transformed[i][j] * scales[0];
	for (i = 0; i < (Rows>>1); i++)
		for(j = (Cols>>1); j < Cols; j++)
			transformed[i][j] = transformed[i][j] *  scales[1];
// LH1
	for (i = (Rows>>1); i < Rows; i++)
		for(j = 0; j < (Cols>>1); j++)
			transformed[i][j] = transformed[i][j] *  scales[2];

// HH2 band. 
	for (i = (Rows>>2); i < (Rows>>1); i++)
		for(j = (Cols>>2); j < (Cols>>1); j++)
			transformed[i][j] = transformed[i][j] *  scales[3];

// HL2
	for (i = 0; i < (Rows>>2); i++)
		for(j = (Cols>>2); j < (Cols>>1); j++)
			transformed[i][j] = transformed[i][j] *  scales[4];
// LH2

	for (i = (Rows>>2); i < (Rows>>1); i++)
		for(j = 0; j < (Cols>>2); j++)
			transformed[i][j] = transformed[i][j] *  scales[5];
// HH3 band. 
	for (i = (Rows>>3); i < (Rows>>2); i++)
		for(j = (Cols>>3); j < (Cols>>2); j++)
			transformed[i][j] = transformed[i][j] *  scales[6];

// HL3
	for (i = 0; i < (Rows>>3); i++)
		for(j = (Cols>>3); j < (Cols>>2); j++)
			transformed[i][j] = transformed[i][j] *  scales[7];	
// LH3
	for (i = (Rows>>3); i < (Rows>>2); i++)
		for(j = 0; j < (Cols>>3); j++)
			transformed[i][j] = transformed[i][j] *  scales[8];

// LL3
	for (i = 0; i < (Rows>>3); i++)
		for(j = 0; j < (Cols>>3); j++)
			transformed[i][j] = transformed[i][j] *  scales[9];
}     

void DWT_(StructCodingPara *PtrCoding,
		  int **imgin,
		  int **img_wav)
{
	int i = 0;
	int j = 0;
	int PadRows = 0;
	int PadCols = 0;

	PadRows = PtrCoding->ImageRows + PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits;
	PadCols = PtrCoding->ImageWidth+ PtrCoding->PadCols_3Bits;

	switch(PtrCoding->PtrHeader->Header.Part4.DWTType)
	{
	case FLOAT_WAVELET:			// floating 9-7	
		{
			float **f97_Transed; 
			f97_Transed = (float **)calloc(PadRows,sizeof(float *)); 
			for(i = 0; i < PadRows; i++)
			{
				f97_Transed[i] = (float *) calloc((PadCols ),sizeof(float));
				for(j = 0; j < PadCols; j++)
					f97_Transed[i][j] = (float)imgin[i][j];		
			}

			lifting_f97_2D(f97_Transed, PadRows, PadCols, 3, 0);

			for(i = 0; i < PadRows; i++)			
				for(j = 0; j < PadCols; j++)		
				{
					if( f97_Transed[i][j] >= 0)
						img_wav[i][j] = (int)(f97_Transed[i][j] + 0.5);
					else 
						img_wav[i][j] = (int)(f97_Transed[i][j] -0.5);

				}

			CoeffRegroupF97(f97_Transed, PtrCoding->ImageRows + 
                    PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits,
                    PtrCoding->ImageWidth + PtrCoding->PadCols_3Bits);

            for (i = 0; i < PadRows; ++i)
			    free(f97_Transed[i]);
			free(f97_Transed);
			break;
		}
	case INTEGER_WAVELET: // integer 9-7
		{
			for(i = 0; i < PadRows; i++)
				for(j = 0; j < PadCols; j++)
					img_wav[i][j] = (long)imgin[i][j];
				
			lifting_M97_2D(img_wav, PadRows, PadCols, 3, 0);
			CoefficientsScaling(img_wav, PadRows, PadCols, PtrCoding->PtrHeader->Header.Part4);
			break;
		}
	default:
		ErrorMsg(BPE_WAVELET_INVALID);
	}
	CoeffRegroup(img_wav, 
		PtrCoding->ImageRows + PtrCoding->PtrHeader->Header.Part1.PadRows_3Bits,
		PtrCoding->ImageWidth +  PtrCoding->PadCols_3Bits);
}


/************************  Transform it to image ********************/
void DWT_Reverse(int **block, StructCodingPara *PtrCoding)
{
	UINT32 k = 0;
	UINT32 p = 0;
	UINT32 i = 0;

	if(PtrCoding->PtrHeader->Header.Part4.DWTType == FLOAT_WAVELET)
	{
		float **temp_f;
		temp_f = (float **)calloc(PtrCoding->ImageRows,sizeof(float *)); 		
		for(k = 0; k < PtrCoding->ImageRows; k ++)
			temp_f[k] = (float *) calloc(PtrCoding->ImageWidth + PtrCoding->PadCols_3Bits,sizeof(float)); 

		for( k = 0; k < PtrCoding->ImageRows; k ++)
			for( p = 0; p < PtrCoding->ImageWidth+ PtrCoding->PadCols_3Bits; p++)
				temp_f[k][p] = (float)block[k][p];	

		lifting_f97_2D(temp_f, PtrCoding->ImageRows, PtrCoding->ImageWidth, 3, 1);		
		for( k = 0; k < PtrCoding->ImageRows; k ++)
			for( p = 0; p < PtrCoding->ImageWidth+ PtrCoding->PadCols_3Bits; p++)
				block[k][p] = (long)temp_f[k][p];	

        for (i = 0; i < PtrCoding->ImageRows; ++i)
            free(temp_f[i]);
        free(temp_f);
	}
	else if(PtrCoding->PtrHeader->Header.Part4.DWTType == INTEGER_WAVELET)
	{
		CoefficientsRescaling(block, PtrCoding->ImageRows,
			PtrCoding->ImageWidth+ PtrCoding->PadCols_3Bits, PtrCoding->PtrHeader->Header.Part4);
		lifting_M97_2D(block, PtrCoding->ImageRows, PtrCoding->ImageWidth + PtrCoding->PadCols_3Bits, 3, 1);
	}
	return;
}

void DWT_ReverseFloating(float **block,  
				 StructCodingPara *PtrCoding)
{
	UINT32 k = 0;
	UINT32 p = 0;	
	UINT32 i = 0;	
    
	float **temp_f = (float **)calloc(PtrCoding->ImageRows,sizeof(float *)); 		
	for(k = 0; k < PtrCoding->ImageRows; k ++)
		temp_f[k] = (float *) calloc(PtrCoding->ImageWidth +PtrCoding->PadCols_3Bits,sizeof(float)); 

	for( k = 0; k < PtrCoding->ImageRows; k ++)
		for( p = 0; p < PtrCoding->ImageWidth; p++)
			temp_f[k][p] = (float)block[k][p];	

	lifting_f97_2D(temp_f, PtrCoding->ImageRows, PtrCoding->ImageWidth+  PtrCoding->PadCols_3Bits, 3, 1);		
	
	for( k = 0; k < PtrCoding->ImageRows; k ++)
		for( p = 0; p < PtrCoding->ImageWidth; p++)
		{
			if( temp_f[k][p] >= 0)
				block[k][p] = (float)(temp_f[k][p] + 0.5);		
			else
				block[k][p] = (float)(temp_f[k][p] - 0.5);		
		}	
    for (i = 0; i < PtrCoding->ImageRows; ++i)
        free(temp_f[i]);
    free(temp_f);
	return;
}
