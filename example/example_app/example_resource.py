from os import remove, listdir
from os.path import basename, dirname, join
from pathlib import Path
import cv2

import canopen
from loguru import logger

from olaf import Resource
from olaf import OreSatFileCache


class ExampleResource(Resource):

    def __init__(self,
                 node: canopen.LocalNode,
                 fwrite_cache: OreSatFileCache,
                 tmp_dir: str = '/tmp/oresat/fwrite'):

        # the -1.0 is the on_loop rate; it's something like self.delay
        # -1.0 = never looped; 0 means "no delay", constantly called; any positive value = seconds
        super().__init__(node, 'Fwrite', 10.0)

        # Define the index we're expecting for this resourece
        self.index = 0x1A0F #This looks like an unused mapping parameter?
        self.sub_test_write = 0x1
        self.sub_test_read = 0x2
        
        #set dir to current directory
        self.dir = dirname(__file__)
        self.imageFile = join(self.dir, 'image1.jpeg')
        
        #camera object
        self.cam = cv2.VideoCapture(0)

        node.add_read_callback(self.on_read)
        node.add_write_callback(self.on_write)

    def on_loop(self):
        result, image = self.cam.read()
        ret = cv2.imwrite(self.imageFile, image)
   

   # def on_start(self):
        #turn on the camera
   #     pass

    def on_end(self):
        #turn off the camera
        self.cam.release()
      



    # on_read / on_write get triggered any time the OD is accessed... first check that
    # index + subindex match the desired value; if not, return immediately to lower overhead
    def on_read(self, index: int, subindex: int, od: canopen.objectdictionary.Variable):
        # this can be a callback function to replace the value
        # i.e. if index = n && sub_index = m, return k
        # if another thread is trying to read the value at the specified location, this function is called
        ret = None 
        
        if index != self.index: 
            return ret
            
        if subindex == self.sub_test_read:
            logger.info('Image File Path = ' + self.imageFile)
            
            #TO DO: filepath strig to hex function goes here
            return 0x22
     

    def on_write(self, index, subindex, od, data):
        # i.e. if we write a 1 to an index + subindex, callback function takes a photo
        if index != self.index:
            return

        if subindex == self.sub_test_write:
            self.imageFile = join(self.dir, str(data))
            logger.info('Taking a picture, filename = ' + self.imageFile)
            result, image = self.cam.read()
            ret = cv2.imwrite(self.imageFile, image)
            return ret

