import unittest

import canopen
from oresat_od_db.oresat0_5 import GPS_OD
from olaf import Node, Resource


class BadResource(Resource):

    def on_start(self):

        raise Exception('a random exception')

    def on_end(self):

        raise Exception('a random exception')


class TestResource(unittest.TestCase):

    def test_start_stop(self):
        '''All exception should be caught'''

        od = GPS_OD
        node = Node(od, 'vcan0')

        good_res = Resource()
        bad_res = BadResource()

        good_res.start(node)
        bad_res.start(node)

        good_res.end()
        bad_res.end()
