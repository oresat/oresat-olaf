# A simple program to convert raw cfc images to viewable file types


import numpy as np
import cv2

# specify image in and out file
filenm = 'RR.raw'
in_file = '../imgs_raw/' + filenm
out_file = 'imgs_conv/' + (filenm + '.png')

# specify image file to convert in first open() parameter
with open(in_file, 'rb') as f:
    raw = f.read()

# reshape() parameters are for end image dimensions

# RR test dimensions
data = np.frombuffer(raw, dtype=np.uint16).reshape(1024, 1280)

# example dimensions
#data = np.frombuffer(raw, dtype=np.uint16).reshape(128, 256)

data = np.copy(data)  # make the data editable

# manipulate image for displaying
data //= 64  # scale 14-bits to 8-bits
data = data.astype(np.uint8)
data = np.invert(data)  # invert black/white values

# first parameter is end image file name
cv2.imwrite(out_file, data)
