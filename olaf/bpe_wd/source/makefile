# CCSDS image compression standard makefile for usage compiling as C code 
# adapted from Dr Aaron Kiley's work for UNL
# Kyle Klein for OreSat - August 2023 - kleinky@pdx.edu

# Currently raises warnings

# Compiler:
#CC = gcc

BPEFLAGS = -O2 -c -Wall

BPEFILES = AC_BitPlaneCoding.c StagesCodingGaggles.c header.c AdjustOutput.c bitsIO.c lifting_97M.c BPEBlockCoding.c bpe_decoder.c lifting_97f.c CoeffGroup.c bpe_encoder.c bpe_main.c DC_EnDeCoding.c errorhandle.c ricecoding.c PatternCoding.c waveletbpe.c

bpe: ${BPEFILES}
	${CC} ${BPEFLAGS} ${BPEFILES}
	${CC} *.o -o bpe -lm
	rm AC_BitPlaneCoding.o DC_EnDeCoding.o bpe_decoder.o header.o ricecoding.o AdjustOutput.o PatternCoding.o bpe_encoder.o lifting_97M.o waveletbpe.o BPEBlockCoding.o StagesCodingGaggles.o errorhandle.o lifting_97f.o CoeffGroup.o bitsIO.o bpe_main.o

# Linker:
LDFLAGS = -lm

