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
Email: hqwang@bigred.unl.edu, hqwang@eecomm.unl.edu

Your comment and suggestions are welcome. Please report bugs to me via email and I would greatly appreciate it. 
Nov. 3, 2006
*/ 

#include "global.h"

#define DEBUG
 
const char *BpeErrorMsg[] = {
"Success",         /* BPE_OK              0  */
"Error code 1: Bit stream end",		   /* BPE_STREAM_END    1  */
"Error code 2: File Error Msg",          /* BPE_FILE_ERROR   2*/
"Error code 3: Bitstream Error",        /* BPE_STREAM_ERROR  3 */
"Error code 4: Data ErrorMsg",          /* BPE_DATA_ERROR   4 */
"Error code 5: Memory allocation error", /* BPE_MEM_ERROR     5*/
"Error code 6: Decoding ErrorMsg",        /* BPE_BUF_ERROR     6 */
"Error code 7: Dynamical range ErrorMsg",/* BPE_VERSION_ERROR7*/
"Error code 8: Invalid Rate",         /* BPE_RATE_ERROR    8  */
"Rate  code 9: Cannot get the exact rate.",    /* BPE_RATE_UNREACHABLE 9 */
"Error code 10: Wavelet transform invalid.",  /*wavelet transform error 10 */ 
"Error code 11: Invalid image segment size.", /*BPE_IMAGE_SIZE_WRONG 11*/ 
"Error code 12: Scalling file open ErrorMsg or scales invalids.", /*invalid scales file 12 */ 
"Error code 13: Invalid header." ,/*invalid header file 13 */ 
"Error code 14: Invalid Coding Parameters.", /*Coding Parameters 14 */ 
"Error code 15: Pattern Coding Error." ,/*Coding Parameters  BPE_PATTERNING_CODING_ERROR 15 */
"Error code 16: Rice Coding Error.", /*Coding Parameters  BPE_RICING_CODING_ERROR 16 */
"Error code 17: Stage Coding Error." /*Coding Parameters  BPE_STAGE_CODING_ERROR 17 */};

void DebugInfo(char *m)
{
#ifdef DEBUG
	fprintf(stderr, "%s\n", m);
#endif
	return;
}

void ErrorMsg(int err)
{
	fprintf(stderr," %s\n", ERR_MSG(err)); 
	//fprintf(F_CodingInfo, "Failed %s\n ", ERR_MSG(err));
	//fclose(F_CodingInfo);
	exit(err);
}
