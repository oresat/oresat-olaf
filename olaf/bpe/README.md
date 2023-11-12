Kyle Klein for OreSat - September 2023
oresat.org - oresat@pdx.edu
kleinky@pdx.edu 


This program has been adapted from the University of Nebraska-Lincoln's 
    C language implementation of the CCSDS 122.0-B-2 Recommended Standard for 
    Image Data Compression. It has also been made to include code that allows 
    binding to Python using pybind.

Information on the original source program and its calling arguments for image 
    parameters can be found at the following website:
http://hyperspectral.unl.edu

Please note header comments for each file, as we have attempted to adapt the 
    source code to more modern capabilities while maintaining portability.

It should be possible to use the Makefile in the source directory to build the 
    bpe program without incorporating the extra code used to bind it to Python.

Note: The source program has a command line option to indicate if pixels are
    signed or unsigned. This option has been omitted from the python
    program; all operations assume the pixels are unsigned by default.
