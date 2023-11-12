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

static int *x_alloc = NULL;	//** temp work

void forwardf97M(int *x_in, 
				 int N)
{
	int i; 
	int n;
	int half;
	int *x;
	int	*r;
	int *d;
	int *temp_0;
	int *temp_1;
	double temp; 

	x = x_alloc + F_EXTPAD;
	memcpy(x,x_in,sizeof(int)*N);
	for(i=1;i<=F_EXTPAD;i++) 
	{
		x[-i] = x[i];
		x[(N-1) + i] = x[(N-1) - i];
	}

	half = (N>>1);  	
	d = (int*)malloc(sizeof(int)*(half + 1));
	temp_0 = d;

	for (n=half + 1;n > 0; n--) 
	{
		temp = (-1.0/16 * (x[-4] + x[2]) + 9.0/16 * (x[-2] + x[0]) + 0.5);
		if (temp > 0) 
			temp = (int)temp;
		else 
		{
			if (temp != (int)temp) 
				temp = (int)(temp - 1);
		}

		*d++ = x[-1] - (int)temp;
		x += 2;
	}
	d = temp_0;
	r = (int*)malloc(sizeof(int)*(half));
	temp_1 = r;
	x = x_alloc + F_EXTPAD;
	for (n=half;n> 0; n--) 
	{
		temp = -.25 * (d[0] + d[1]) +.5;
		if (temp > 0) 
			temp = (int)temp;
		else 
		{
			if (temp != (int)temp) 
				temp = (int)(temp - 1);
		}

		*r++ = x[0] - (int)(temp);
		x+=2;
		d++;
	}
	d = temp_0;
	r = temp_1;
	memcpy(x_in,r, sizeof(int)*half);
	memcpy(x_in + half,d+1, sizeof(int)*half);	
	
	free(d);
	free(r);
}

void inversef97M(int *x, int N)
{
	//r is the low pass and d is the high pass. 
	int i; 
	int n;
	int half;
	int *r;
	int *d; 
	int *d0;
	int *r0;
	int *temp;
	int *temp_1;
	int *temp_0;
	int *x_0;
	int *x_1 ;

	temp = x;
	half = N/2;
	r = x_alloc + D_EXTPAD;  
	d = x_alloc + D_EXTPAD + half+D_EXTPAD+  D_EXTPAD+D_EXTPAD;  
	memcpy(r,x,half*sizeof(int));
	memcpy(d,x+half,half*sizeof(int));

	x_0 = (int*)malloc(sizeof(int)*(half + 3));
	temp_0 = x_0;

	x_1 = (int*)malloc(sizeof(int)*(half + 2));
	temp_1 = x_1;

	d0 = d;
	r0 = r;
	
	for(i=1;i<=D_EXTPAD;i++) 
	{
		if(half <=1)
		{
			r[(half-1)+i] = r[half - i];
			r[-i] = r[i] =  r[half - i];
		}
		else
		{
			r[-i] = r[i];
			r[(half-1)+i] = r[half - i];
		}
		d[-i] = d[i -1];
		d[(half-1)+i] = d[half - i - 1];
	}
 
	for (n = half + 3; n--;) 
	{
		double rounding = (-1.0/4 * (d[-1] + d[-2]) + 0.5);

		if (rounding > 0) 
			rounding = (int)rounding;
		else 
		{
			if (rounding != (int)rounding) 
				rounding = (int)(rounding - 1);
		}

		*x_0++ = r[-1] + (int) rounding;		
		d++; 
		r++;
	}
	
	x_0 = temp_0;
	d = d0;
	r = r0;

	for (n = half; n--;) 
	{
		double rounding;

		rounding = (-1.0/16 * (x_0[0] + x_0[3]) + 9.0/16 * (x_0[1] + x_0[2]) + 0.5);
		if (rounding > 0) 
			rounding = (int)rounding;
		else 
		{
			if (rounding != (int)rounding) 
				rounding = (int)(rounding - 1);
		}

		*x_1++ = d[0] + (int) rounding;

		x_0++; 
		d++;
	}
	
	x_0 = temp_0 + 1;
	x_1 = temp_1;

	for (n = 0; n < half; n ++)
	{
		*x++ = x_0[n];
		*x++ = x_1[n];
	}
	free(temp_0);
	free(x_1);
}

void lifting_M97_2D(int **rows,
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
	int *buffer;
	int *rows_ptr;

    /* Check the dimensions for compatability. */

    if ((ImgCols%(1 << levels)) || (ImgRows%(1 << levels)) ) {
		ErrorMsg(BPE_FILE_ERROR);
	}

	if ( (x_alloc = (int*)malloc(sizeof(int)*(ImgCols+ImgRows+F_EXTPAD+F_EXTPAD))) == NULL )  {
		ErrorMsg(BPE_MEM_ERROR); 
	}
	else
	{
		for ( i = 0; i < ImgCols+ImgRows+F_EXTPAD+F_EXTPAD; i ++)
			x_alloc[i] = 0;
	}
  
    /* Allocate a work array (for transposing columns) */
    
   	if ( (buffer = (int*)calloc(ImgRows, sizeof(int))) == NULL ) {
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
			h = (ImgRows >> l);
      
			/* Rows. */
	
			for (y = 0; y < h; y++)
				forwardf97M(rows[y], w);
    
			/* Columns. */
	
			rows_ptr = rows[0];
			for (x = 0; x < w; x++) 
			{
				for (y = 0; y < h; y++) 
					buffer[y] = rows[y][x];
				forwardf97M(buffer, h);
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
				inversef97M(buffer, h);
				for (y = 0; y < h; y++) 
					rows[y][x] = buffer[y];
//				rows_ptr ++;
			}

			/* Rows. */
	
			for (y = 0; y < h; y++)
				inversef97M(rows[y], w);
    	}
	}
	free(x_alloc); x_alloc = NULL;
	free(buffer);
}
