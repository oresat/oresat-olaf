from os import remove, listdir
from os.path import basename
from pathlib import Path

import canopen
from loguru import logger

from olaf import Resource
from ..common.oresat_file_cache import OreSatFileCache


class ExampleResource(Resource):

    def __init__(self,
                 node: canopen.LocalNode,
                 fwrite_cache: OreSatFileCache,
                 tmp_dir: str = '/tmp/oresat/fwrite'):

        # the -1.0 is the on_loop rate; it's something like self.delay
        # -1.0 = never looped; 0 means "no delay", constantly called; any positive value = seconds
        super().__init__(node, 'Fwrite', -1.0)

        # Define the index we're expecting for this resourece
        self.index = 0x1A0F #This looks like an unused mapping parameter?
        self.sub_test_write = 0x1
        self.sub_test_read = 0x2


    def on_loop(self):
        #take a picture every N
        pass

    def on_start(self):
        #turn on the camera
        pass

    def on_end(self):
        #turn off the camera
        pass


    # on_read / on_write get triggered any time the OD is accessed... first check that
    # index + subindex match the desired value; if not, return immediately to lower overhead
    def on_read(self, index: int, subindex: int, od: canopen.objectdictionary.Variable):
        # this can be a callback function to replace the value
        # i.e. if index = n && sub_index = m, return k
        # if another thread is trying to read the value at the specified location, this function is called
        pass

    def on_write(self, index, subindex, od, data):
        # i.e. if we write a 1 to an index + subindex, callback function takes a photo
