# pixel_check.py: 
#  a simple program for comparing/checking each pixel in identical images
# **currently has only been tested on PNG image type
# adapted from:
#  https://stackoverflow.com/questions/62285511/use-numpy-to-quickly-iterate-over-pixels
# (program utilizes PIL)

import sys
import numpy as np
from PIL import Image


def pixel_check(file1, file2):
    image1 = Image.open(file1)
    image2 = Image.open(file2)

    im1 = (image1).load()
    im2 = (image2).load()

    height, width = np.shape(image1)
    # as alternative, next line can help with:  'ValueError: too many values to unpack'
    #height, width, _ = np.shape(image1)

    # comparison loop
    for i in range(width):
        for j in range(height):
            pixel_val1 = im1[i, j]
            pixel_val2 = im2[i, j]
            if pixel_val1 != pixel_val2:
                print(f"Found pixel {pixel_val2} at {i, j} does not match")

    print('scan complete')

# if calling from command line: python pixel_check.py <file1> <file2>
if __name__ == '__main__':
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    pixel_check(file1, file2)
