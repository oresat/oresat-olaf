Aaron Kiely
June-July 2008

This file describes the modifications I made to get the Nebraska CCSDS image compression software 
to run on my (PPC) Mac and to fix several bugs.  
My starting point is the Linux version of the Nebraska software (the file date for 
the Linux package is April 29, 2008).

In Part 1 I summarize bug fixes.  
In Part 2 I summarize changes that are either done primarily to get things working on a Mac, 
or for other reasons (like eliminating compiler warning errors).


Part 1: Bug Fixes
Note that most of these bugs should affect both PC and Mac implementations.

Bug when a segment consists of a single block
Decoding fails when the last segment consists of a single block.  

This can be demonstrated using a small 8-bit random noise image:

   bpe -e randimg8_48x24.raw -o testcomp.bpe -w 48 -h 24 -s 17
Presumably this affects Mac and PC implementations.

Here's the problem:

In several places, the parameter "gaggles" is used.  
This parameter is set to the number of values to be encoded, not counting a reference sample.  

Thus, it's equal to the number of values in the gaggle, except for the first gaggle, 
when it's one less than this number, and therefore it's set to zero when a segment consists of a single block.

But when gaggles is equal to zero, all of the following functions will return without doing anything, 
and thus encoding and decoding fail for a segment with a single block:

   ACGaggleEncoding, ACGaggleDecoding, DCGaggleDecoding, DCEncoder
These functions are called by:
  ACDepthEncoder, ACDepthDecoder, DCEntropyDecoder, DCEntropyEncoder

I've fixed this by rewriting all eight of the above functions.  
In the rewritten versions, the value of gaggles is always used to indicate the 
number of values in the gaggle.  The new code is also a bit shorter than the original.


Bug in coding additional bit planes of DC coefficients (section 4.3.3 of the recommendation):
The software is not properly handling encoding and decoding of DC bit planes described in sec. 4.3.3 of the standard.  
(These are the bit planes of DC coefficients coded after Rice coding of quantized coefficients, 
but BEFORE any of the AC coefficients are coded.)  
This affects Mac and PC implementations.  
In addition to not conforming to the specification, the decoder loses synchronization with the encoder, 
and so decoding can fail catastrophically, causing a segmentation fault.

(a) Encoding: For an integer DWT, in function DCEntropyEncoder, after calling DCEncoder (one or more times), 
it encodes q-WtLL3 bit planes, which is too many for some images.  
Instead, the number of DC bit planes encoded here should be
   q - max{BitDepthAC, WtLL3}.

(b) Decoding:  It looks like an attempt to decode section 4.3.3 bits was in file DC_EnDeCoding, function DCDeCoding, 
but it has been commented out.  
Instead, the decoding of section 4.3.3 bits seems to occur in file AC_BitPlaneCoding.c, function ACBpeDecoding.  
But this decoding appears AFTER calling function ACDepthDecoder, which is wrong.

To fix (a), in file DC_EnDeCoding.c, function DCEntropyEncoder, 
I've commented out a large chunk of source code and replaced it with a smaller chunk.

To fix (b), in file AC_BitPlaneCoding.c, function ACBpeDecoding, 
comment out large chunk of source code appearing right after 
	// 3.2 Family tree scaning sequence in a segment. 
I've added a chunk of source code near the end of the DC_EnDeCoding.c file, in function DCDeCoding, 
to handle decoding of section 4.3.3 bits.


Bug fix in AdjustOutput.c:
(This bug probably only affects Mac implementations.)
In the function 'AdjustOutPut' around line 50 of file AdjustOutput.c, change:
	*(*BlockCodingInfo[i].PtrBlockAddress) = DeConvTwosComp((DWORD32)(BlockCodingInfo[i].ShiftedDC + BlockCodingInfo[i].DecodingDCRemainder), PtrCoding->PtrHeader->Header.Part1.BitDepthDC_5Bits);

to: 
	*(*BlockCodingInfo[i].PtrBlockAddress) = DeConvTwosComp((DWORD32)((long int)BlockCodingInfo[i].ShiftedDC + (long int)BlockCodingInfo[i].DecodingDCRemainder), PtrCoding->PtrHeader->Header.Part1.BitDepthDC_5Bits);


Large Image Bug Fix:
If the number of segments is 2^15 or more, a segmentation fault can arise on decoding.  
This probably affects Mac and PC implementations.

In DCGaggleDecoding() (maybe elsewhere?), variable i is a short int.  
When the number of blocks exceeds 2^15-1, it overflows and points to a negative index.  
Should be able to fix this by just declaring it to be a long int.

File DC_EnDeCoding.c, function DCGaggleDeccoding, ~line 345, change
  short i = 0;
to
  long int i = 0;
Also, in File AC_BitPlaneCoding.c, function ACGaggleDecoding, ~line 388, change short i to long int i.
[It's possible that other overflow problems arise when the number of segments in an image 
or the number of blocks in a segment is very large.]


Bug fix in file DC_EnDeCoding.c:
(There's a bug in the DPCM mapping.  This affects Mac and PC implementations.)
In function DPCM_DCMapper, around line 508, change:

		BlockInfo[0].ShiftedDC = -(short)(((~(BlockInfo[0].ShiftedDC - 1)) & Bits1));
to
		BlockInfo[0].ShiftedDC = -(short)( ((BlockInfo[0].ShiftedDC^Bits1) & Bits1) + 1 );

In function DPCM_DCMapper, around line 517, change:

			BlockInfo[i].ShiftedDC = -(short)((~(BlockInfo[i].ShiftedDC - 1)) & Bits1);
to
			BlockInfo[i].ShiftedDC = -(short)( ((BlockInfo[i].ShiftedDC^Bits1) & Bits1) + 1 );

In function DPCM_DCDeMapper, around line 761, change:

		BlockInfo[0].ShiftedDC = -(short)(((~(BlockInfo[0].ShiftedDC - 1)) & Bits1));
to
		BlockInfo[0].ShiftedDC = -(short)( ((BlockInfo[0].ShiftedDC^Bits1) & Bits1) + 1 );

In function DPCM_DCDeMapper, around line 769, change:

		if((float)BlockInfo[i].MappedDC / 2 == BlockInfo[i].MappedDC / 2)
		{
			diff_DC[i] = BlockInfo[i].MappedDC / 2;
			if(diff_DC[i] >= 0 && diff_DC[i] <= theta)
			{
				BlockInfo[i].ShiftedDC = diff_DC[i] + BlockInfo[i - 1].ShiftedDC;
				continue;
			}
		}
		else 
		{
			diff_DC[i] = -(long)(BlockInfo[i].MappedDC + 1) / 2 ;
			if(diff_DC[i] <= 0 && diff_DC[i] >= -theta)
			{
				BlockInfo[i].ShiftedDC = diff_DC[i] + BlockInfo[i - 1].ShiftedDC;
				continue;
			}
		}		
		diff_DC[i] = BlockInfo[i].MappedDC - theta;
		BlockInfo[i].ShiftedDC = diff_DC[i] + BlockInfo[i - 1].ShiftedDC;

		if(	(long)BlockInfo[i].ShiftedDC < X_Min || BlockInfo[i].ShiftedDC > X_Max)
		{
			diff_DC[i] = -diff_DC[i];
			BlockInfo[i].ShiftedDC = diff_DC[i] + BlockInfo[i - 1].ShiftedDC;
		}

to:
		if (BlockInfo[i].MappedDC > 2*theta) {
			if ((long int)BlockInfo[i - 1].ShiftedDC < 0)
				diff_DC[i] = BlockInfo[i].MappedDC - theta;
			else
				diff_DC[i] = theta - BlockInfo[i].MappedDC;
		} else {
			if((float)BlockInfo[i].MappedDC / 2 == BlockInfo[i].MappedDC / 2)
				diff_DC[i] = BlockInfo[i].MappedDC / 2;
			else
				diff_DC[i] = -(long)(BlockInfo[i].MappedDC + 1) / 2 ;
		}
		BlockInfo[i].ShiftedDC = diff_DC[i] + BlockInfo[i - 1].ShiftedDC;


Another bug fix
An image consisting of 15 blocks is not handled properly and a Segmentation Fault can arise.  
I believe that this affects PC and Mac implementations.  Here's the fix:

Change instances of 
    while(PtrCoding->PtrHeader->Header.Part3.S_20Bits - GaggleStartIndex >= gaggles)
to
    while(PtrCoding->PtrHeader->Header.Part3.S_20Bits >= gaggles + GaggleStartIndex)

This occurs in four places:
   File DC_EnDeCoding.c: DCEntropyEncoder ~ line 282, DCEntropyDecoder ~line 471
   File AC_BitPlaneCoding.c: ACDepthEncoder ~line 256, ACDepthDecoder ~line 571

In File AC_BitPlaneCoding.c change
	if (PtrCoding->PtrHeader->Header.Part3.S_20Bits < gaggles)
to
	if (PtrCoding->PtrHeader->Header.Part3.S_20Bits <= gaggles)

This occurs in two places: ~line 241 (function ACDepthEncoder), ~line 560 (function ACDepthDecoder).
[I also made the same change in file DC_EnDeCoding.c, function DCEntropyEncoder ~line 272, 
and function DCEntropyDecoder ~line 462.  I haven't confirmed that it was necessary here.]


And another Bug Fix:
Decompression can fail if the source image is all zeros.  
I believe that this affects PC and Mac implementations.  To fix this:

File DC_EnDeCoding.c, function DeConvTwosComp, ~line 51, change:
	if((leftmost >= sizeof(DWORD32) * 8) ||
		(leftmost == 0) || (leftmost == 1))
to
	if((leftmost >= sizeof(DWORD32) * 8) || (leftmost == 0))


Endian Bug Fix
The compressor and decompressor are supposed to use little-endian byte order by default.  
If big-endian is indicated, then swap the bytes on image input or output.

There are two bugs: (1) the byte swapping doesn't work, 
(2) the way endianness is actually treated is that the endianness (by default) 
matches the native computer's endianness, and "-f 1" causes bytes to be flipped.

I've modified the ImageRead function in bpe_encoder.c, and the ImageWrite and ImageWriteFloat functions in bpe_decoder.c.
I've defined a new variable "machineendianness" to indicate the endianness of the computer running the software.


Part 2: Other Modifications

I created a new makefile (the contents of the new makefile appear at the bottom of this file).

I commented out some of the statements printed during program execution (in main.c) 
and I eliminated the creation of informational files that report the status of encoding and decoding.  
If encoding or decoding fails, then an error message will still be returned, but no status file is created.  
If encoding or decoding works properly, then no message is printed, 
and no file is created except for the compressed or reconstructed image file.


Change some #includes:
  - Change each instance of #include <malloc.h> to #include <stdlib.h>.  
This occurs in files AC_BitPlaneCoding.c, CoeffGroup.c, bpe_decoder.c, lifting_97f.c

- Add #include <stdlib.h> near the beginning of AdjustOutput.c


Re-write an ambiguous line:
In functions 'DPCM_DCMapper' and 'DPCM_DCDeMapper', around lines 505 and 758 of file DC_EnDeCoding.c, change
		Bits1 = ((Bits1++)<<1);
to
		Bits1 = (Bits1<<1)+1;



Eliminate compiler warning messages via the following modifications:
- Comment out the following statement in function ACDepthDecoder around line 554 of AC_BitPlaneCoding.c:
	PtrCoding->PtrHeader->Header.Part3.S_20Bits;
(the statement had no effect, what was the intention?)

- In the function 'ACDepthEncoder' added the following lines (near line 231 of file AC_BitPlaneCoding.c):
		// added the following two lines to eliminate a compiler warning message
		Max_k = 0;
		ID_Length = 0;	

- In functions 'ImageWrite' and 'ImageWriteFloat' (around lines 154 and 325 of bpe_decoder.c), added parentheses

- In function 'ImageSize' (near lines 152, 160), changed %ld to %ud

- Added the following line to bpe_encoder.c:
  extern void DebugInfo(char *m);


Not strictly necessary, but clean up (and eliminate compiler warnings) 
by removing the following unused variables:

   in file AC_BitPlaneCoding.c:
      - variables {index, bit_num, counter} from function 'ACDepthEncoder' 
      - variable {temp_bit} from function 'ACGaggleDecoding'
   in file main.c:
      - variables {optind, k} from function 'main'
    in file StagesCodingGaggles.c:
      - variable {temp} from functions 'StagesDeCodingGaggles1' 'StagesDeCodingGaggles2' 'StagesDeCodingGaggles3' 
   in file bpe_decoder.c:
      - variables {counter, temp_code} from function 'DecoderEngine' 
   in file DC_EnDeCoding.c:
      - variable {counter} from 'DCEncoding'
      - variable {temp_bit} from 'DCGaggleDecoding'
      - variables {index, bit_num, counter} from function 'DCEntropyEncoder'
   in file PatternCoding.c:
      - variable SymbolIndex from function 'CodingOptions'


New makefile:
The makefile I wrote uses the -Wall option just to help me spot potential problems, 
but this could be turned off.  
It also deletes the *.o files generated during compilation, just to keep things cleaner.

Here's the contents of the makefile:

# My attempt to produce a working makefile for the CCSDS image compression software from U. Nebraska

# Compiler:
CC = gcc

BPEFLAGS = -O2 -c -Wall

BPEFILES = AC_BitPlaneCoding.c StagesCodingGaggles.c header.c AdjustOutput.c bitsIO.c lifting_97M.c BPEBlockCoding.c bpe_decoder.c lifting_97f.c CoeffGroup.c bpe_encoder.c main.c DC_EnDeCoding.c errorhandle.c ricecoding.c PatternCoding.c getopt.c waveletbpe.c

bpe: ${BPEFILES}

bpe: ${BPEFILES}
	${CC} ${BPEFLAGS} ${BPEFILES}
	${CC} *.o -o bpe -lm
	rm AC_BitPlaneCoding.o DC_EnDeCoding.o bpe_decoder.o header.o ricecoding.o AdjustOutput.o PatternCoding.o bpe_encoder.o lifting_97M.o waveletbpe.o BPEBlockCoding.o StagesCodingGaggles.o errorhandle.o lifting_97f.o CoeffGroup.o bitsIO.o getopt.o main.o
	


# Linker:
#LDFLAGS = -lm

# Default rule

