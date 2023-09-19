# A simple program to convert raw cfc images to viewable file types
# Kyle Klein, Ryan Medick for OreSat - August 2023 - kleinky@pdx.edu


import numpy as np
import cv2

in_file = 'desena.img'
out_file = 'desena.png'

# specify image file to convert in first open() parameter
with open(in_file, 'rb') as f:
    raw = f.read()

# reshape() parameters are for end image dimensions

# data = np.frombuffer(raw, dtype=np.uint16).reshape(1024, 1280)
data = np.frombuffer(raw, dtype=np.uint16).reshape(128, 256)

data = np.copy(data)  # make the data editable

# manipulate image for disaplaying
data //= 64  # scale 14-bits to 8-bits
data = data.astype(np.uint8)
data = np.invert(data)  # invert black/white values

# first parameter is end image file name
cv2.imwrite(out_file, data)
