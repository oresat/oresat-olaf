"""testing suite for bpe python module"""

import os
import unittest

import olaf.bpe
from .bin_check import bin_check
from .cfc import cfc
from .pixel_check import pixel_check


class Test_bpe(unittest.TestCase):
    """main module for BPE unittest"""
    def setUp(self):
        """
        min encode params = (name of file to be encoded, name of newly encoded file,
                                       width of image, height of image)
        min decode params = (name of encoded file to decode, name for the outfile)
        """

        source_file = "RR.raw"
        encoded_file = "RRencoded"
        decoded_file = "RR.out"

        self._infile = "img_files/raw/" + source_file
        self._compr_file = "img_files/encoded/" + encoded_file
        self._outfile = "img_files/decoded/" + decoded_file
        self._png_infile = "img_files/converted/" + source_file + ".png"
        self._png_outfile = "img_files/converted/" + decoded_file + ".png"

        self._width = 1024
        self._height = 1280
        # w and h (for encoding only - required)

        self._bpp = 14
        # for embbedded decoding (uncommon)
        # desired compression ratio (bits per pixel); default is 0

        self._bit_depth = 16
        # less common specs (for encoding only)
        # original # of bits of each pixel (encoding only) - must be <= 16; default is 8"""
        self._blocks_per_seg = 256
        # number of blocks in each segment - default is 256;
        # Required: 16 <= blocks_per_seg <= (max number of blocks of the image)"""
        self._is_big_endian = 1
        # indicates byte order of a pixel - either 1 or 0 (yes or no); default is 1"""
        self._is_lossless = 1
        # indicates type of transform - either 1 or 0 (yes or no); default is 1"""
        # END user-defined specs"""

        self._enc_data = bpe.encode_basearg(
            self._infile,
            self._compr_file,
            self._width,
            self._height,
            self._bpp,
            self._bit_depth,
        )
        self._enc_data = bpe.encode_fullarg(
            self._infile,
            self._compr_file,
            self._width,
            self._height,
            self._bpp,
            self._bit_depth,
            self._blocks_per_seg,
            self._is_big_endian,
            self._is_lossless,
        )

        self._dec_data = bpe.decode(self._compr_file, self._outfile)

    def test_bin_check(self):
        """binary check files"""
        self.assertEqual(self._enc_data, self._dec_data)
        bin_check(self._infile, self._outfile)

    def test_cfc(self):
        """create human readable files"""
        cfc(self._infile, self._width, self._height)
        cfc(self._outfile, self._width, self._height)

    def test_pixel_check(self):
        """pixel check human readable files"""
        cfc(self._infile, self._width, self._height)
        cfc(self._outfile, self._width, self._height)
        pixel_check(self._png_infile, self._png_outfile)

    def tearDown(self):
        """comment out if interested in keeping created files"""
        if os.path.isfile(self._compr_file):
            os.remove(self._compr_file)
        if os.path.isfile(self._outfile):
            os.remove(self._outfile)
        if os.path.isfile(self._png_infile):
            os.remove(self._png_infile)
        if os.path.isfile(self._png_outfile):
            os.remove(self._png_outfile)


if __name__ == "__main__":
    # unittest.main()
    unittest.main(verbosity=2)
