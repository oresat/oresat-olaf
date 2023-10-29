'''Test the Resource class.'''
import unittest

import canopen
from oresat_configs import OreSatConfig, OreSatId, NodeId
from olaf import Node, Resource


class BadResource(Resource):
    '''Bad Resource for testing.'''

    def on_start(self):

        raise Exception('a random exception')

    def on_end(self):

        raise Exception('a random exception')


class TestResource(unittest.TestCase):
    '''Test the Resource class.'''

    def test_start_stop(self):
        '''All exception should be caught'''

        od = OreSatConfig(OreSatId.ORESAT0).od_db[NodeId.GPS]
        node = Node(od, 'vcan0')

        good_res = Resource()
        bad_res = BadResource()

        good_res.start(node)
        bad_res.start(node)

        good_res.end()
        bad_res.end()
