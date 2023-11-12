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

#define F_EXTPAD 4
#define D_EXTPAD 2

double const LowPassFilterInverse[] = {	 
-0.064538882629,
-0.040689417609,
0.418092273222,
0.788485616406,
0.418092273222,
-0.040689417609,
-0.064538882629
};

double const HighPassFilterInverse[] = {	 
	-0.037828455507,
0.023849465020,
0.110624404418,
0.377402855613,
-0.852698679009,
0.377402855613,
0.110624404418,
-0.023849465020,
-0.037828455507
};

static float *x_alloc = NULL;	//** temp work

//int FuncRounding(float input)
//{
//	int output = 0;
//	if (input > 0) 
//		output = (int)input;
//	else 
//	{
//		if (input != (int)input) 
//			output = (int)(input - 1);
//	}
//	return output;
//}


const float  LowPassFilter[] = {	
0.037828455507,
-0.023849465020,
-0.110624404418,
0.377402855613, 
0.852698679009,
0.377402855613, 
-0.110624404418,
-0.023849465020,
0.037828455507};

const float  HighPassFilter[] = {
-0.064538882629,
0.040689417609,
0.418092273222,
-0.788485616406,
0.418092273222,
0.040689417609,
-0.064538882629};


void forwardf97f(float *x_in, 
				 int N)
{
	int i;
	int n; 
	int half;
	float *x; 
	float *r;
	float *d;

	x = x_alloc + F_EXTPAD;

	memcpy(x,x_in,sizeof(float)*N);
	
	half = (N >> 1);  
	d = (float*)malloc(sizeof(float)*(half + 3));
	r = (float*)malloc(sizeof(float)*(half + 2));

	for(i = 1; i <= F_EXTPAD; i++) 
	{
		x[-i] = x[i];
		x[(N-1) + i] = x[(N-1) - i];
	}
	if( 1) 
	{
		float const *LPF = LowPassFilter + 4;
		float const *HPF = HighPassFilter + 3;

		for (n = 0; n < half; n++)
		{
			d[n] = 0;
			r[n] = 0;

			d[n]= (float)
				(  ( LPF[0] * x[2 * n] )
			+ 		(LPF[1]* ( x[2 * n -1] + x[2 * n + 1] ))
				+ (LPF[2] * (x[2 * n -2] + x[2 * n + 2]) )
				+ ( LPF[3] * (x[2 * n -3] + x[2 * n + 3]) )
				+ ( LPF[4] * (x[2 * n -4] + x[2 * n + 4])) );
			
			r[n] = (float)(
				(HPF[0] * x[2 * n + 1] )
			+ (HPF[1]  * ( x[2 * n ] + x[2 * n + 2]))
			+ ( HPF[2] * (x[2 * n -1] + x[2 * n + 3]))
			+ ( HPF[3] * (x[2 * n -2] + x[2 * n + 4]) ));

		}

	} 

	memcpy(x_in,d,sizeof(float)*half);
	memcpy(x_in+half,r,sizeof(float)*half);

    free(d);
    free(r);
}

void inversef97f(float *x, int N)
{

	//r is the low pass and d is the high pass.
	int i; 
	int n;
	int half;
	
	float *r;
	float *d;
/*
	half = N/2;

	r = x_alloc + D_EXTPAD;  
	d = x_alloc + D_EXTPAD + half+D_EXTPAD+D_EXTPAD;  
	memcpy(r,x,half*sizeof(float));
	memcpy(d,x+half,half*sizeof(float));

	for(i=1;i<=D_EXTPAD;i++) {
		r[-i] = r[i];
		r[(half-1)+i] = r[half - i];
		d[-i] = d[i-1];
		d[(half-1)+i] = d[(half-1) - i];
	}
 
	for (n = half; n--;) {

		*x++ = (float)(0.788485616406 * r[0] - 0.040689417609 * ( r[1] + r[-1] )
		     - 0.023849465020 * (d[1] + d[-2]) + 0.377402855613 * (d[0] + d[-1]));

		*x++ = (float)(0.418092273222 * (r[1] + r[0]) - 0.064538882629 * (r[2] + r[-1])
		     - 0.037828455507 * (d[2] + d[-2]) + 0.110624404418 * (d[1] + d[-1]) - 0.852698679009 * d[0]);

		d++; r++;
	}

*/ 
	half = N/2;

	r = x_alloc + D_EXTPAD;  
	d = x_alloc + D_EXTPAD + half+D_EXTPAD+D_EXTPAD;  
	memcpy(r,x,half*sizeof(float));
	memcpy(d,x+half,half*sizeof(float));

	for(i=1;i<=D_EXTPAD;i++) {
		r[-i] = r[i];
		r[(half-1)+i] = r[half - i];
		d[-i] = d[i-1];
		d[(half-1)+i] = d[(half-1) - i];
	}
 
	for (n = half; n--;) {

		*x++ = (float)(0.788486 * r[0] - 0.0406894 * ( r[1] + r[-1] )
		     - 0.023849 * (d[1] + d[-2]) + 0.377403 * (d[0] + d[-1]));

		*x++ = (float)(0.418092 * (r[1] + r[0]) - 0.0645389 * (r[2] + r[-1])
		     - 0.037829 * (d[2] + d[-2]) + 0.110624 * (d[1] + d[-1]) - 0.852699 * d[0]);

		d++; r++;
	}

}

void lifting_f97_2D(float **rows,
					UINT32 ImgRows, 
					UINT32 ImgCols, 
					UINT32 levels, 
					BOOL inverse)
{
	int x;
	int y;
	int w;
	int h;
	int l;
	int i;//yw,
	float *buffer;
	float *rows_ptr;

    /* Check the dimensions for compatability. */

    if (ImgCols%(1 << levels) || ImgRows%(1 << levels)) {
		ErrorMsg(BPE_FILE_ERROR);
	}

	if ( (x_alloc = (float*)malloc(sizeof(float)*(ImgCols+ImgRows+F_EXTPAD+F_EXTPAD))) == NULL )  {
		ErrorMsg(BPE_MEM_ERROR); 
	}
	else
	{
		for ( i = 0; i < ImgCols+ImgRows+F_EXTPAD+F_EXTPAD; i ++)
			x_alloc[i] = 0;
	}
  
    /* Allocate a work array (for transposing columns) */
    
   	if ( (buffer = (float*)calloc(ImgRows, sizeof(float))) == NULL ) {
		ErrorMsg(BPE_MEM_ERROR); 
	}
	else
	{
		for ( i = 0; i < ImgRows; i ++)
			buffer[i] = 0;
	}

    /* Compute the rowslet transform. */
  
	if ( !inverse ) { /* forward transform. */

		for (l = 0; l < levels; l++) {
			w = (ImgCols >> l);
			h =  (ImgRows>> l);
      
			/* Rows. */
	
			for (y = 0; y < h; y++)
			{
	//			fprintf(stderr, "%d\n", y);
				forwardf97f(rows[y], w);
    
			}
			/* Columns. */ 
	
			rows_ptr = rows[0];
			for (x = 0; x < w; x++) 
			{
				for (y = 0; y < h; y++) 
					buffer[y] = rows[y][x];
				forwardf97f(buffer, h);
				for (y = 0; y < h; y++) 
					rows[y][x] = buffer[y];
//				rows_ptr ++;
			}
		}

    } else {

		for (l = levels-1; l >= 0; l--) {
			w = (ImgCols >> l);
			h = (ImgRows >> l);

			/* Columns. */	
			rows_ptr = rows[0];
			for (x = 0; x < w; x++) 
			{
				for (y = 0; y < h; y++) 
					buffer[y] = rows[y][x];
				inversef97f(buffer, h);
				for (y = 0; y < h; y++) 
					rows[y][x] = buffer[y];
//				rows_ptr ++;
			}

			/* Rows. */
	
			for (y = 0; y < h; y++)
				inversef97f(rows[y], w);
    	}
	}
	free(x_alloc); x_alloc = NULL;
	free(buffer);
}

