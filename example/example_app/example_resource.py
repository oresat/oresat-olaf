from os import remove, listdir
from os.path import basename, dirname, join
from pathlib import Path
import cv2

import canopen
from loguru import logger

from olaf import Resource
from olaf import OreSatFileCache


class ExampleResource(Resource):

    # These values are magic numbers, don't change this signature unless you know what you're doing
    def __init__(self,
                 node: canopen.LocalNode,
                 fwrite_cache: OreSatFileCache,
                 tmp_dir: str = '/tmp/oresat/fwrite'):

        # Initting the node includes the on_loop delay rate.
        # 10.0 is the on_loop rate; it's something like self.delay
        # -1.0 = never looped; 0 means "no delay", constantly called; any positive value = seconds
        super().__init__(node, 'Fwrite', 10.0)

        # Define the index we're expecting for this resourece
        self.index = 0x1A0F #This is just an arbitrary OD index that isn't being used
        self.sub_test_write = 0x1 #Subindices for the read and write callbacks
        self.sub_test_read = 0x2

        # Set dir to current directory
        # This is for the image filepath we'll be snapping with the webcam
        self.dir = dirname(__file__)
        self.imageFile = join(self.dir, 'image1.jpeg')

        # Camera object
        self.cam = cv2.VideoCapture(0)

        # Register our callback functions
        node.add_read_callback(self.on_read)
        node.add_write_callback(self.on_write)

    # The on_loop tasks execute once every DELAY seconds, set at instantiation
    # This example resource is just snapping a picture from the system's webcam & printing to log.
    def on_loop(self):
        result, image = self.cam.read()
        ret = cv2.imwrite(self.imageFile, image)
        logger.info("Taking a picture!")


    # on_end gets called when the application using the resource coses
    # This example resource cleans up the camera object.
    def on_end(self):
        #turn off the camera
        self.cam.release()


    # on_read and on_write get triggered any time the OD is accessed... first check that
    # index + subindex match the desired value; if not, return immediately to lower overhead
    # Note that the OD does still get written to.
    # This example resource returns the last byte of the filepath, minus the suffix.
    # Currently looks like the resource framework won't allow bigger returns than 1 byte.
    def on_read(self, index: int, subindex: int, od: canopen.objectdictionary.Variable):

        ret = None

        if index != self.index:
            return ret

        if subindex == self.sub_test_read:
            logger.info('Image File Path = ' + self.imageFile)

            return self.__strToHex(self.imageFile[-9:-5])

    # The example resource takes a picture to the filename written when on_write is callbacked.
    def on_write(self, index, subindex, od, data):
        if index != self.index:
            return

        if subindex == self.sub_test_write:
            self.imageFile = join(self.dir, str(data))
            logger.info('Taking a picture, filename = ' + self.imageFile)
            result, image = self.cam.read()
            ret = cv2.imwrite(self.imageFile, image)
            return ret

    #Private helper function to convert the file name to hex for the CAN bus
    def __strToHex(self, in_text):
        hex_val = 0x0
        for chrs in in_text:
            hex_val = (hex_val << (8))
            hex_val = hex_val + ord(chrs)

        return hex_val
