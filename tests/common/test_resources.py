import unittest

import canopen
from olaf import Node, Resource


class BadResource(Resource):

    def on_start(self):

        raise Exception('a random exception')

    def on_end(self):

        raise Exception('a random exception')


class TestResource(unittest.TestCase):

    def test_start_stop(self):
        '''All exception should be caught'''

        od = canopen.objectdictionary.eds.import_eds('olaf/_internals/data/oresat_app.eds', 0x10)
        node = Node(od, 'vcan0')

        good_res = Resource()
        bad_res = BadResource()

        good_res.start(node)
        bad_res.start(node)

        good_res.end()
        bad_res.end()
