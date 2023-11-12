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

const int bit2_pattern[] = {0, 2, 1, 3};
const int bit3_pattern[] = {1, 4, 0, 5, 2, 6, 3, 7};
const int bit3_pattern_TranD[] = {0, 3, 0, 4, 1, 5, 2, 6};
const int bit4_pattern_TypeCi[] = {10, 1, 3, 6, 2, 5, 9, 12, 0, 8, 7, 13, 4, 14, 11, 15};
const int bit4_pattern_TypeHij_TranHi[] = {0, 1, 3, 6, 2, 5, 9, 11, 0, 8, 7, 12, 4, 13, 10, 14};


void PatternMapping(StrSymbolDetails *StrSymbol)
{	
	switch (StrSymbol->sym_len)
	{
	case 0: return;
	case 1: StrSymbol->sym_mapped_pattern = StrSymbol->sym_val;
		break;
	case 2:		
		StrSymbol->sym_mapped_pattern  = bit2_pattern[StrSymbol->sym_val];	
		break;
	case 3:
		if(StrSymbol->type == ENUM_TRAN_D)
			StrSymbol->sym_mapped_pattern  = bit3_pattern_TranD[StrSymbol->sym_val];	
		else 
			StrSymbol->sym_mapped_pattern  = bit3_pattern[StrSymbol->sym_val];	
		break;	
	case 4:	
		if (StrSymbol->type == ENUM_TYPE_CI)
			StrSymbol->sym_mapped_pattern  = bit4_pattern_TypeCi[StrSymbol->sym_val];
		else if ((StrSymbol->type == ENUM_TRAN_HI)||(StrSymbol->type == ENUM_TYPE_HIJ))
			StrSymbol->sym_mapped_pattern  = bit4_pattern_TypeHij_TranHi[StrSymbol->sym_val];	
		break;	
	default:
		ErrorMsg(BPE_PATTERNING_CODING_ERROR);//"Pattern mapping ErrorMsg occurs!\n");
	}
}

void DeMappingPattern(StrSymbolDetails *StrSymbol)
{

	UCHAR8 i;

	switch (StrSymbol->sym_len)
	{
	case 1: StrSymbol->sym_val = StrSymbol->sym_mapped_pattern;
		break;
	case 2:		
		for( i = 0; i < 4; i ++)
		{
			if(StrSymbol->sym_mapped_pattern == bit2_pattern[i])
			{
				StrSymbol->sym_val = i;
				break;
			}
		}
		break;
	case 3:
		if(StrSymbol->type == ENUM_TRAN_D)
		{
			for( i = 1; i < 8; i ++)
			{
				if(StrSymbol->sym_mapped_pattern == bit3_pattern_TranD[i])
				{
					StrSymbol->sym_val = i;
					break;
				}
			}
		}
		else
		{
			for( i = 0; i < 8; i ++)
			{
				if(StrSymbol->sym_mapped_pattern == bit3_pattern[i])
				{
					StrSymbol->sym_val = i;
					break;
				}
			}
		}
		break;	
	case 4:		 

		if (StrSymbol->type  == ENUM_TYPE_CI)
		{
			for( i = 0; i < 16 ; i ++)
			{
				if(StrSymbol->sym_mapped_pattern == bit4_pattern_TypeCi[i])
				{
					StrSymbol->sym_val = i;
					break;
				}
			}
		}
		else if ((StrSymbol->type  == ENUM_TRAN_HI)||(StrSymbol->type  == ENUM_TYPE_HIJ))
		{
			for( i = 1; i < 16 ; i ++)
			{
				if(StrSymbol->sym_mapped_pattern == bit4_pattern_TypeHij_TranHi[i])
				{
					StrSymbol->sym_val = i;
					break;
				}
			}
		}
		break;		
	default:
		ErrorMsg(BPE_PATTERNING_CODING_ERROR); 
	}	
}

void BitPlaneSymbolReset(StrSymbolDetails *SymbolStr) 
{
	SymbolStr->sign = 0;
	SymbolStr->sym_len = 0;
	SymbolStr->sym_mapped_pattern = 0;
	SymbolStr->sym_val = 0;						
	SymbolStr->type = 0;
} 


void CodingOptions(StructCodingPara *PtrCoding, 
				   BitPlaneBits *BlockInfo,
				   UINT32 BlocksInGaggle, 
				   UCHAR8 Option[])
{

	DWORD32 BlockSeq = 0;	
	DWORD32 bitsCounter_2Bits[2] = {0};
	DWORD32 bitsCounter_3Bits[3] = {0};
	DWORD32 bitsCounter_4Bits[4] = {0};

	for ( BlockSeq = 0; BlockSeq < BlocksInGaggle; BlockSeq ++)		
	{
		UCHAR8 SymbolIndex = 0;
		if (BlockInfo[BlockSeq].BitMaxAC < PtrCoding->BitPlane)
			continue;		

		for(SymbolIndex = 0; SymbolIndex < MAX_SYMBOLS_IN_BLOCK; SymbolIndex ++)
		{		
			// 4.2 Pattern statistics and mapping. 
			if(BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].type == ENUM_NONE )
				continue;
			else if(BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_len == 1)
			{
				PatternMapping(&(BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex]) );
				continue;
			}			
			PatternMapping(&(BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex]));
		// 4.3 Entropy coding by truncated sample split code. 
		// 4.4 Truncated sample split code. 						
			if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_len == 2)
			{
				// try nk = 0 
				switch(BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern)   // code option 0;
				{
				case 0:
					bitsCounter_2Bits[0] ++;
					break;
				case 1:				
					bitsCounter_2Bits[0] += 2;
					break;
				case 2:				
					bitsCounter_2Bits[0] += 3;
					break;
				case 3:				
					bitsCounter_2Bits[0] += 3;
					break;
				default:
					ErrorMsg(BPE_PATTERNING_CODING_ERROR);
				}
				bitsCounter_2Bits[1] += 2;  //uncoded
			}
			else if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_len == 3)
			{
				// try option = 0 
				if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern <= 2)				
					bitsCounter_3Bits[0] +=  BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern + 1;

				else if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern <=5)					
					bitsCounter_3Bits[0] += 5;

				else if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern <=7)
					bitsCounter_3Bits[0] += 6;
				else
					ErrorMsg(BPE_PATTERNING_CODING_ERROR);

				// option  = 1;	
				if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern <= 1)				
					bitsCounter_3Bits[1] += 2;

				else if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern <= 3)					
					bitsCounter_3Bits[1] += 3;

				else if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern <= 7)
					bitsCounter_3Bits[1] += 4;
				else
					ErrorMsg(BPE_PATTERNING_CODING_ERROR);
				// option  = 3;	uncoded. 
				bitsCounter_3Bits[2] += 3;

			}
			else if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_len == 4)
			{
				// try nk = 0 

				if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern <= 3)				
					bitsCounter_4Bits[0] += BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern + 1;

				else if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern <= 7)					
					bitsCounter_4Bits[0] += 7;

				else if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern <= 15)
					bitsCounter_4Bits[0] += 8;
				else
					ErrorMsg(BPE_PATTERNING_CODING_ERROR);
				// nk = 1;	

				if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern <= 1)				
					bitsCounter_4Bits[1] +=  2;

				else if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern <= 3)					
					bitsCounter_4Bits[1] += 3;

				else if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern <= 5)
					bitsCounter_4Bits[1] += 4;
				
				else if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern <= 11)
					bitsCounter_4Bits[1] += 6;

				else if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern <= 15)
					bitsCounter_4Bits[1] += 7;
				else
					ErrorMsg(BPE_PATTERNING_CODING_ERROR);
				// nk = 2;	
				
				if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern <= 3)				
					bitsCounter_4Bits[2] +=  3;

				else if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern <= 7)					
					bitsCounter_4Bits[2] += 4;

				else if (BlockInfo[BlockSeq].SymbolsBlock[SymbolIndex].sym_mapped_pattern <= 15)
					bitsCounter_4Bits[2] += 5;			
				else
					ErrorMsg(BPE_PATTERNING_CODING_ERROR);

				//code option 3: uncoded. 
				bitsCounter_4Bits[3] += 4;
			}
		} 
	} 

	// now determine the coding ID. 
	// 4.5 Pattern selection.

	// 2-bit codeword
	if(	bitsCounter_2Bits[0] < bitsCounter_2Bits[1] )
		Option[0] = 0; // codes. 
	else
		Option[0] = 1; // no-coding

	// 3-bit codeword
	if((bitsCounter_3Bits[2] <= bitsCounter_3Bits[0]) &&
		(bitsCounter_3Bits[2] <= bitsCounter_3Bits[1]))
	{
		Option[1] = 3;
	}
	else if((bitsCounter_3Bits[0] <= bitsCounter_3Bits[1]) && 
		(bitsCounter_3Bits[0] <= bitsCounter_3Bits[2]))
	{
		Option[1] = 0;
	}
	else if((bitsCounter_3Bits[1]  <= bitsCounter_3Bits[0]) && 		
		(bitsCounter_3Bits[1]  <= bitsCounter_3Bits[2]))
	{
		Option[1] = 1;
	}
	// 4-bit codeword
	if((bitsCounter_4Bits[3]  <= bitsCounter_4Bits[1]) && 
		(bitsCounter_4Bits[3]  <= bitsCounter_4Bits[0])&& 
		(bitsCounter_4Bits[3]  <= bitsCounter_4Bits[2]))
	{
		Option[2] = 3;	
	}
	else if((bitsCounter_4Bits[0]  <= bitsCounter_4Bits[1]) && 
			(bitsCounter_4Bits[0]  <= bitsCounter_4Bits[2]) && 
			(bitsCounter_4Bits[0]  <= bitsCounter_4Bits[3]))
	{
		Option[2] = 0;
	}
	else if((bitsCounter_4Bits[1]  <= bitsCounter_4Bits[0]) && 
		(bitsCounter_4Bits[1]  <= bitsCounter_4Bits[2])&& 
		(bitsCounter_4Bits[1]  <= bitsCounter_4Bits[3]))
	{
		Option[2] = 1;
	}		
	else if((bitsCounter_4Bits[2]  <= bitsCounter_4Bits[1]) && 
		(bitsCounter_4Bits[2]  <= bitsCounter_4Bits[0])&& 
		(bitsCounter_4Bits[2]  <= bitsCounter_4Bits[3]))
	{
		Option[2] = 2;	
	}				
	return;
}

void RefBitsDe(StructCodingPara *PtrCoding, BitPlaneBits * BlockInfo)
{
	UINT32 BlockSeq;
	UCHAR8 i;
	UCHAR8 j;
	UCHAR8 k;
	UCHAR8 p;
	DWORD32 TempWord; 
	long ** block;
	UCHAR8 BitPlane = PtrCoding->BitPlane;

	PtrCoding->DecodingStopLocations.BlockNoStopDecoding = 0;

	for( BlockSeq = 0; BlockSeq < PtrCoding->PtrHeader->Header.Part3.S_20Bits; BlockSeq ++)
	{
		if (BlockInfo[BlockSeq].BitMaxAC < BitPlane)
			continue;
		// encoding TypeP first.

		block = BlockInfo[BlockSeq].PtrBlockAddress;

		if (BlockInfo[BlockSeq].RefineBits.RefineParent.ParentSymbolLength > 0)
		{
			if((PtrCoding->SegmentFull == TRUE) || (PtrCoding->RateReached == TRUE))
				return;

			for ( i = 0; i < 3; i++)
			{
				UCHAR8 temp_x = 0; 
				UCHAR8 temp_y = 0;
				if ((BlockInfo[BlockSeq].RefineBits.RefineParent.ParentRefSymbol &  (1 << (2 - i))) > 0) 
				{
					UCHAR8 code = 0;
					BitsRead(PtrCoding, &TempWord, 1);
					code = (UCHAR8) TempWord;
				    BlockInfo[BlockSeq].RefineBits.RefineParent.ParentSymbolLength --;
					temp_x = (i >= 1 ? 1 : 0);
					temp_y = (i != 1 ? 1 : 0);	
					if( code > 0) 
					{
						if (block[temp_x][temp_y] > 0)
							block[temp_x][temp_y] +=  (1 << (BitPlane - 1));
						else
							block[temp_x][temp_y] -=  (1 << (BitPlane - 1));
					} 
				}		
				if ((PtrCoding->DecodingStopLocations.BitPlaneStopDecoding != -1)
						&& (PtrCoding->RateReached == TRUE)
						&& (!PtrCoding->DecodingStopLocations.LocationFind))
				{
					PtrCoding->DecodingStopLocations.BlockNoStopDecoding = BlockSeq;
					PtrCoding->DecodingStopLocations.X_LocationStopDecoding = temp_x;						
					PtrCoding->DecodingStopLocations.Y_LocationStopDecoding = temp_y;
					PtrCoding->DecodingStopLocations.LocationFind = TRUE;
					return;
				}
			} 
			BlockInfo[BlockSeq].RefineBits.RefineParent.ParentRefSymbol = 0;
			BlockInfo[BlockSeq].RefineBits.RefineParent.ParentSymbolLength = 0;
		}

		if (BlockInfo[BlockSeq].RefineBits.RefineChildren.ChildrenSymbolLength > 0)
		{	
			
			if((PtrCoding->SegmentFull == TRUE) || (PtrCoding->RateReached == TRUE))
				break;		
			for ( k = 0; k < 3; k ++)
			{			
				UCHAR8 counter = 3;		
				UCHAR8 temp_x; 
				UCHAR8 temp_y;

				temp_x = (k >= 1 ? 1 : 0);
				temp_x *= 2;
				temp_y = (k != 1 ? 1 : 0);
				temp_y *= 2;
				
				for ( i = temp_x ; i < temp_x + 2; i ++)
					for ( j =temp_y; j < temp_y + 2; j ++)
					{						
						if ((BlockInfo[BlockSeq].RefineBits.RefineChildren.ChildrenRefSymbol & (1 << (8 - k * 4 + counter ))) > 0) 
						{
							UCHAR8 code = 0;
							BitsRead(PtrCoding,&TempWord, 1);
							code = (UCHAR8) TempWord;

							BlockInfo[BlockSeq].RefineBits.RefineChildren.ChildrenSymbolLength --;
							if(code > 0) 	
							{							
								if (block[i][j]  > 0)
									block[i][j]  +=  (1 << (BitPlane - 1));
								else
									block[i][j]  -=  (1 << (BitPlane - 1));
							}
						}
						counter --;				
						if ((PtrCoding->DecodingStopLocations.BitPlaneStopDecoding != -1)
							&& PtrCoding->RateReached == TRUE
							&& (!PtrCoding->DecodingStopLocations.LocationFind))
						{
							PtrCoding->DecodingStopLocations.BlockNoStopDecoding = BlockSeq;
							PtrCoding->DecodingStopLocations.X_LocationStopDecoding = i;						
							PtrCoding->DecodingStopLocations.Y_LocationStopDecoding = j;
							PtrCoding->DecodingStopLocations.LocationFind = TRUE;
							return;
						}
					}
			}
			// reset to 0			
			BlockInfo[BlockSeq].RefineBits.RefineChildren.ChildrenRefSymbol = 0;
			BlockInfo[BlockSeq].RefineBits.RefineChildren.ChildrenSymbolLength = 0;
		}

		// refinement Gi

		for( i = 0; i < 3; i ++)
		{
			if (BlockInfo[BlockSeq].RefineBits.RefineGrandChildren[i].GrandChildrenSymbolLength > 0)
			{
			  short refine_stop_point_counter = 0;
				if((PtrCoding->SegmentFull == TRUE) || (PtrCoding->RateReached == TRUE))
					break;
				for ( j = 0; j < 4; j ++)
				{	
					UCHAR8 temp_x; 
					UCHAR8 temp_y;
					UCHAR8 counter = 3;
					temp_x = (i >= 1 ? 1 : 0) * 4 + (j >= 2 ? 1 : 0) * 2;
					temp_y = (i != 1 ? 1 : 0) * 4 + (j % 2) * 2;
				
					for ( k = temp_x; k < temp_x + 2; k ++)
						for ( p = temp_y; p < temp_y + 2; p ++)
						{
							if ((BlockInfo[BlockSeq].RefineBits.RefineGrandChildren[i].GrandChildrenRefSymbol & (1 << (12 - j * 4 + counter ))) > 0) 
							{
								UCHAR8 code = 0;
								BitsRead(PtrCoding, &TempWord, 1);
								code = (UCHAR8) TempWord;

								BlockInfo[BlockSeq].RefineBits.RefineGrandChildren[i].GrandChildrenSymbolLength --;
								refine_stop_point_counter ++;
								if(code > 0) 
								{									
									if (block[k][p]  > 0)
										block[k][p]  +=  (1 << (BitPlane - 1));
									else
										block[k][p]  -=  (1 << (BitPlane - 1));
								} 
							}
							counter --;
							if ((PtrCoding->DecodingStopLocations.BitPlaneStopDecoding != -1)
									&& PtrCoding->RateReached == TRUE &&
									(!PtrCoding->DecodingStopLocations.LocationFind))
							{ 
	//						if (refine_stop_point_counter == PtrCoding->DecodingStopLocations.TotalBitsReadThisTime)
								{
								PtrCoding->DecodingStopLocations.BlockNoStopDecoding = BlockSeq;
								PtrCoding->DecodingStopLocations.X_LocationStopDecoding = k;						
								PtrCoding->DecodingStopLocations.Y_LocationStopDecoding = p;
								PtrCoding->DecodingStopLocations.LocationFind = TRUE;
								return;
								}
							}
						}
				}
			}
			BlockInfo[BlockSeq].RefineBits.RefineGrandChildren[i].GrandChildrenRefSymbol = 0;
			BlockInfo[BlockSeq].RefineBits.RefineGrandChildren[i].GrandChildrenSymbolLength = 0;			
		}

		if ((PtrCoding->DecodingStopLocations.BitPlaneStopDecoding != -1)
			&& PtrCoding->RateReached == TRUE)
		{
			PtrCoding->DecodingStopLocations.BlockNoStopDecoding = BlockSeq;
		}
	}
} 

void RefBitsEn(BitPlaneBits * BlockInfo,
			   StructCodingPara *PtrCoding)
{
	UINT32 i;
	UCHAR8 j;

	for( i = 0; i < PtrCoding->PtrHeader->Header.Part3.S_20Bits; i ++)
	{
		// encoding TypeP first.
		if (BlockInfo[i].RefineBits.RefineParent.ParentSymbolLength > 0)
		{
			BitsOutput(PtrCoding, 
					   BlockInfo[i].RefineBits.RefineParent.ParentRefSymbol, 
					   BlockInfo[i].RefineBits.RefineParent.ParentSymbolLength);
			// reset to 0:
			BlockInfo[i].RefineBits.RefineParent.ParentRefSymbol = 0;
			BlockInfo[i].RefineBits.RefineParent.ParentSymbolLength = 0;
		}

		if (BlockInfo[i].RefineBits.RefineChildren.ChildrenSymbolLength > 0)
		{
			BitsOutput(PtrCoding, 
					   BlockInfo[i].RefineBits.RefineChildren.ChildrenRefSymbol,
					   BlockInfo[i].RefineBits.RefineChildren.ChildrenSymbolLength);
			// reset to 0
			
			BlockInfo[i].RefineBits.RefineChildren.ChildrenRefSymbol = 0;
			BlockInfo[i].RefineBits.RefineChildren.ChildrenSymbolLength = 0;

		}
		for( j = 0; j < 3; j ++)
		{
			if (BlockInfo[i].RefineBits.RefineGrandChildren[j].GrandChildrenSymbolLength > 0)
				BitsOutput(PtrCoding, 
							BlockInfo[i].RefineBits.RefineGrandChildren[j].GrandChildrenRefSymbol,
							BlockInfo[i].RefineBits.RefineGrandChildren[j].GrandChildrenSymbolLength);

			BlockInfo[i].RefineBits.RefineGrandChildren[j].GrandChildrenRefSymbol = 0;
			BlockInfo[i].RefineBits.RefineGrandChildren[j].GrandChildrenSymbolLength = 0;			
		}
	}
	return;
}

void StagesEnCoding(StructCodingPara *PtrCoding, BitPlaneBits *BlockInfo)
{
	// try various options for the 2-bit, 3-bit, and 4 bit coding. 
	UCHAR8 BlocksInLastGaggle = 0;
	DWORD32 TotalGaggles; 
	DWORD32 GaggleIndex = 0;
	UCHAR8 **CodeOptionsAllGaggles;	
	UCHAR8 BlocksInGaggle = 0;
	UINT32 BlockStartIndex = 0;
	BOOL **OptionHitFlag;

	BlocksInLastGaggle = (UCHAR8) (PtrCoding->PtrHeader->Header.Part3.S_20Bits % GAGGLE_SIZE) ;
	TotalGaggles = PtrCoding->PtrHeader->Header.Part3.S_20Bits / GAGGLE_SIZE;
	// bit length is equal to 1, nk = 0;

	if( BlocksInLastGaggle!= 0) 
		TotalGaggles++;
	CodeOptionsAllGaggles = (UCHAR8 **)calloc(TotalGaggles, sizeof(UCHAR8 *)) ;
	OptionHitFlag = (BOOL **) calloc(TotalGaggles, sizeof(BOOL *)) ;

	// 4.1 Pattern values.  

	for (GaggleIndex = 0; GaggleIndex < TotalGaggles; GaggleIndex ++)	
	{
		BlockStartIndex = GaggleIndex * GAGGLE_SIZE;
		CodeOptionsAllGaggles[GaggleIndex] = (UCHAR8 *)calloc(3, sizeof(UCHAR8)) ;
		OptionHitFlag[GaggleIndex] =  (BOOL *)calloc(3, sizeof(BOOL)) ;
		OptionHitFlag[GaggleIndex][0] = FALSE;		
		OptionHitFlag[GaggleIndex][1] = FALSE;		
		OptionHitFlag[GaggleIndex][2] = FALSE;
		BlocksInGaggle = (UCHAR8)((BlockStartIndex + GAGGLE_SIZE < PtrCoding->PtrHeader->Header.Part3.S_20Bits) ? 
						 GAGGLE_SIZE : (PtrCoding->PtrHeader->Header.Part3.S_20Bits - BlockStartIndex)) ;

		CodingOptions(PtrCoding, &(BlockInfo[BlockStartIndex]) , BlocksInGaggle, (CodeOptionsAllGaggles[GaggleIndex]));
		
		StagesEnCodingGaggles1(PtrCoding, &(BlockInfo[BlockStartIndex]) , 
			BlocksInGaggle, (CodeOptionsAllGaggles[GaggleIndex]), OptionHitFlag[GaggleIndex] );
	}

	for (GaggleIndex = 0; GaggleIndex < TotalGaggles; GaggleIndex ++)	
	{ 
		BlockStartIndex = GaggleIndex * GAGGLE_SIZE;
		BlocksInGaggle = (UCHAR8) ((BlockStartIndex + GAGGLE_SIZE < PtrCoding->PtrHeader->Header.Part3.S_20Bits) ? 
							GAGGLE_SIZE : (PtrCoding->PtrHeader->Header.Part3.S_20Bits - BlockStartIndex))  ;
		StagesEnCodingGaggles2(PtrCoding, &(BlockInfo[BlockStartIndex]) ,
			BlocksInGaggle, (CodeOptionsAllGaggles[GaggleIndex]), OptionHitFlag[GaggleIndex] );
	}
	for (GaggleIndex = 0; GaggleIndex < TotalGaggles; GaggleIndex ++)	
	{
		BlockStartIndex = GaggleIndex * GAGGLE_SIZE;
		BlocksInGaggle = (UCHAR8) ((BlockStartIndex + GAGGLE_SIZE < PtrCoding->PtrHeader->Header.Part3.S_20Bits) ? 
							GAGGLE_SIZE : (PtrCoding->PtrHeader->Header.Part3.S_20Bits - BlockStartIndex)) ;
		StagesEnCodingGaggles3(PtrCoding, &(BlockInfo[BlockStartIndex]) , 
			BlocksInGaggle, (CodeOptionsAllGaggles[GaggleIndex]), OptionHitFlag[GaggleIndex] );
	}
	RefBitsEn(BlockInfo, PtrCoding);		

    int i = 0;
    for(i = 0; i < TotalGaggles; i++)                                   
        free(CodeOptionsAllGaggles[i]);
    free(CodeOptionsAllGaggles);
    for(i = 0; i < TotalGaggles; i++)                                   
        free(OptionHitFlag[i]);
    free(OptionHitFlag);
    
    return;
}

void StagesDeCoding(StructCodingPara *PtrCoding, BitPlaneBits *BlockInfo)
{
	// try various options for the 2-bit, 3-bit, and 4 bit coding. 
	UCHAR8 BlocksInLastGaggle = 0;
	DWORD32 TotalGaggles; 
	DWORD32 GaggleIndex = 0;
	UCHAR8 **CodeOptionsAllGaggles;	
	UCHAR8 BlocksInGaggle = 0;
	UINT32 BlockStartIndex = 0;
	BOOL **OptionHitFlag;

    DWORD32 free_count = 0;

	BlocksInLastGaggle = (UCHAR8) (PtrCoding->PtrHeader->Header.Part3.S_20Bits % GAGGLE_SIZE) ;
	TotalGaggles = PtrCoding->PtrHeader->Header.Part3.S_20Bits / GAGGLE_SIZE;
	// bit length is equal to 1, nk = 0;
	if( BlocksInLastGaggle!= 0) 
		TotalGaggles++;
	CodeOptionsAllGaggles = (UCHAR8 **)calloc(TotalGaggles, sizeof(UCHAR8 *)); //BUG
	OptionHitFlag = (BOOL **) calloc(TotalGaggles, sizeof(BOOL *)); //BUG
	PtrCoding->DecodingStopLocations.BlockNoStopDecoding = 0;

	// 4.1 Pattern values.  
	for (GaggleIndex = 0; GaggleIndex < TotalGaggles; GaggleIndex ++)	
	{
		BlockStartIndex = GaggleIndex * GAGGLE_SIZE;
		CodeOptionsAllGaggles[GaggleIndex] = (UCHAR8 *)calloc(3, sizeof(UCHAR8));//BUG
		OptionHitFlag[GaggleIndex] =  (BOOL *)calloc(3, sizeof(BOOL));//BUG
        free_count = GaggleIndex;
		OptionHitFlag[GaggleIndex][0] = FALSE;		
		OptionHitFlag[GaggleIndex][1] = FALSE;		
		OptionHitFlag[GaggleIndex][2] = FALSE;
		BlocksInGaggle = (UCHAR8)((BlockStartIndex + GAGGLE_SIZE < PtrCoding->PtrHeader->Header.Part3.S_20Bits) ? 
						 GAGGLE_SIZE : (PtrCoding->PtrHeader->Header.Part3.S_20Bits - BlockStartIndex)) ;
		StagesDeCodingGaggles1(PtrCoding, &(BlockInfo[BlockStartIndex]) , 
			BlocksInGaggle, (CodeOptionsAllGaggles[GaggleIndex]), OptionHitFlag[GaggleIndex] );
		
		if ((PtrCoding->DecodingStopLocations.BitPlaneStopDecoding != -1)
			&& PtrCoding->RateReached == TRUE)
		{
			PtrCoding->DecodingStopLocations.BlockNoStopDecoding+=GaggleIndex * 16;
			PtrCoding->DecodingStopLocations.stoppedstage = 1;	

            int i = 0;
            for(i = 0; i <= free_count; i++)                                   
            {
                free(CodeOptionsAllGaggles[i]);
                free(OptionHitFlag[i]);
            }
            free(CodeOptionsAllGaggles);
            free(OptionHitFlag);
			
            return;
		}
	}
	for (GaggleIndex = 0; GaggleIndex < TotalGaggles; GaggleIndex ++)	
	{
		BlockStartIndex = GaggleIndex * GAGGLE_SIZE;
		BlocksInGaggle = (UCHAR8) ((BlockStartIndex + GAGGLE_SIZE < PtrCoding->PtrHeader->Header.Part3.S_20Bits) ? 
							GAGGLE_SIZE : (PtrCoding->PtrHeader->Header.Part3.S_20Bits - BlockStartIndex))  ;
		StagesDeCodingGaggles2(PtrCoding, &(BlockInfo[BlockStartIndex]) ,
			BlocksInGaggle, (CodeOptionsAllGaggles[GaggleIndex]), OptionHitFlag[GaggleIndex] );
		
		if ((PtrCoding->DecodingStopLocations.BitPlaneStopDecoding != -1)
			&& PtrCoding->RateReached == TRUE)
		{
			PtrCoding->DecodingStopLocations.BlockNoStopDecoding += GaggleIndex * 16;			
			PtrCoding->DecodingStopLocations.stoppedstage = 2;

            int i = 0;
            for(i = 0; i <= free_count; i++)                                   
            {
                free(CodeOptionsAllGaggles[i]);
                free(OptionHitFlag[i]);
            }
            free(CodeOptionsAllGaggles);
            free(OptionHitFlag);
			
			return;
		}
	}

	if( PtrCoding->RateReached == TRUE)
	{
		PtrCoding->DecodingStopLocations.stoppedstage = 2;

        int i = 0;
        for(i = 0; i <= free_count; i++)                                   
        {
            free(CodeOptionsAllGaggles[i]);
            free(OptionHitFlag[i]);
        }
        free(CodeOptionsAllGaggles);
        free(OptionHitFlag);
			
		return;
	}

	for (GaggleIndex = 0; GaggleIndex < TotalGaggles; GaggleIndex ++)	
	{
		BlockStartIndex = GaggleIndex * GAGGLE_SIZE;
		BlocksInGaggle = (UCHAR8) ((BlockStartIndex + GAGGLE_SIZE < PtrCoding->PtrHeader->Header.Part3.S_20Bits) ? 
							GAGGLE_SIZE : (PtrCoding->PtrHeader->Header.Part3.S_20Bits - BlockStartIndex)) ;

        //
		StagesDeCodingGaggles3(PtrCoding, &(BlockInfo[BlockStartIndex]), 
                            BlocksInGaggle, (CodeOptionsAllGaggles[GaggleIndex]), 
                                                OptionHitFlag[GaggleIndex] );
		
		if ((PtrCoding->DecodingStopLocations.BitPlaneStopDecoding != -1)
			&& PtrCoding->RateReached == TRUE)
		{
			PtrCoding->DecodingStopLocations.BlockNoStopDecoding += GaggleIndex * 16;
			PtrCoding->DecodingStopLocations.stoppedstage = 3;

            int i = 0;
            for(i = 0; i <= free_count; i++)                                   
            {
                free(CodeOptionsAllGaggles[i]);
                free(OptionHitFlag[i]);
            }
            free(CodeOptionsAllGaggles);
            free(OptionHitFlag);
			
			return;
		}
	}

	if( PtrCoding->RateReached == TRUE) 
	{
		PtrCoding->DecodingStopLocations.stoppedstage = 3;

        int i = 0;
        for(i = 0; i <= free_count; i++)                                   
        {
            free(CodeOptionsAllGaggles[i]);
            free(OptionHitFlag[i]);
        }
        free(CodeOptionsAllGaggles);
        free(OptionHitFlag);
			
		return;
	}
	RefBitsDe(PtrCoding, BlockInfo);

	if( PtrCoding->RateReached == TRUE)
	{		
		PtrCoding->DecodingStopLocations.stoppedstage = 4;

        int i = 0;
        for(i = 0; i <= free_count; i++)                                   
        {
            free(CodeOptionsAllGaggles[i]);
            free(OptionHitFlag[i]);
        }
        free(CodeOptionsAllGaggles);
        free(OptionHitFlag);
			
		return;
	}

    int i = 0;
    for(i = 0; i <= free_count; i++)                                   
    {
        free(CodeOptionsAllGaggles[i]);
        free(OptionHitFlag[i]);
    }
    free(CodeOptionsAllGaggles);
    free(OptionHitFlag);

	return;
}
