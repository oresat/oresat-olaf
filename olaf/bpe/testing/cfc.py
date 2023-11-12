# simple program to convert raw cfc images to viewable file types

import os
import sys
import numpy as np
import cv2


def cfc(infile, columns, rows):
    path = os.path.split(infile)                                     
    appnd = path[1]                                                         
    newpath = os.path.split(path[0])                                        
    fout = newpath[0] + '/converted/' + appnd 
    outfile = fout + '.png'
    
    with open(infile, 'rb') as f:
        raw = f.read()
    # reshape() parameters are for end image dimensions
    data = np.frombuffer(raw, dtype=np.uint16).reshape(columns, rows)
    # override with a copy that is mutable
    data = np.copy(data)  
    # manipulate image for displaying
    data //= 64  # scale 14-bits to 8-bits
    data = data.astype(np.uint8)
    data = np.invert(data)  # invert black/white values
    cv2.imwrite(outfile, data)

# if calling from command line: python cfc.py <infile> <columns> <rows>
if __name__ == "__main__":
    infile = sys.argv[1]
    columns = sys.argv[2]
    rows = sys.argv[3]
    cfc(infile, columns, rows)
