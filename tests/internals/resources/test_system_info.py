import unittest

from olaf._internals.resources.system_info import SystemInfoResource, Subindex

from . import MockApp


class TestSystemInfoResource(unittest.TestCase):

    def setUp(self):

        self.app = MockApp()
        self.app.add_resource(SystemInfoResource())
        self.app.start()

    def tearDown(self):

        self.app.stop()

    def test_system_info(self):

        index = self.app.resource.index

        ''' TODO depends on system env
        self.assertNotEqual(self.app.sdo_read(index, Subindex.UPTIME.value), 0)

        self.assertNotEqual(self.app.sdo_read(index, Subindex.NUM_OF_CPUS.value), 0)
        self.assertNotEqual(self.app.sdo_read(index, Subindex.CPU_ARCH.value), 0)
        self.assertNotEqual(self.app.sdo_read(index, Subindex.CPU_GOV.value), 0)
        self.assertNotEqual(self.app.sdo_read(index, Subindex.CPU_FREQ.value), 0)

        self.app.sdo_read(index, Subindex.RPROC_ITER.value) = 0
        self.assertEqual(self.app.sdo_read(index, Subindex.RPROC_ITER.value), 0)
        self.app.sdo_read(index, Subindex.RPROC_ITER.value) = 1
        self.assertIn(self.app.sdo_read(index, Subindex.RPROC_ITER.value), [0, 1])

        rpocs = self.app.sdo_read(index, Subindex.NUM_OF_RPROCS.value)
        for i in range(rpocs):
            self.app.sdo_read(index, Subindex.RPROC_ITER.value) = i
            self.assertNotEqual(self.app.sdo_read(index, Subindex.RPROC_ITER.value), i)
            self.assertNotIn(self.app.sdo_read(index, Subindex.RPROC_NAME.value), [None, ''])
            self.assertNotIn(self.app.sdo_read(index, Subindex.RPROC_STATE.value), [None, ''])
        '''

        # just make sure nothing raises a exception

        self.app.sdo_read(index, Subindex.OS_DISTRO.value)
        self.app.sdo_read(index, Subindex.OS_NAME.value)
        self.app.sdo_read(index, Subindex.OS_KERNEL_VER.value)
        self.app.sdo_read(index, Subindex.HOSTNAME.value)

        self.app.sdo_read(index, Subindex.LOAD_AVG_1MIN.value)
        self.app.sdo_read(index, Subindex.LOAD_AVG_5MIN.value)
        self.app.sdo_read(index, Subindex.LOAD_AVG_15MIN.value)

        self.app.sdo_read(index, Subindex.RAM_TOTAL.value)
        self.app.sdo_read(index, Subindex.RAM_FREE.value)
        self.app.sdo_read(index, Subindex.RAM_SHARED.value)
        self.app.sdo_read(index, Subindex.RAM_BUFFERED.value)
        self.app.sdo_read(index, Subindex.RAM_PERCENT.value)

        self.app.sdo_read(index, Subindex.SWAP_TOTAL.value)
        self.app.sdo_read(index, Subindex.SWAP_FREE.value)
        self.app.sdo_read(index, Subindex.SWAP_PERCENT.value)

        # self.assertNotEqual(self.app.sdo_read(index, Subindex.PROCS.value), 0)

        self.app.sdo_read(index, Subindex.ROOT_PART_TOTAL.value)
        self.app.sdo_read(index, Subindex.ROOT_PART_FREE.value)
        self.app.sdo_read(index, Subindex.ROOT_PART_PERCENT.value)
