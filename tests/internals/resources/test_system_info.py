import unittest

from olaf._internals.resources.system_info import SystemInfoResource, Subindex

from . import MockApp


class TestSystemInfoResource(unittest.TestCase):
    def setUp(self):
        self.app = MockApp()
        self.node = self.app.node
        self.app.add_resource(SystemInfoResource)
        self.app.start()

        self.info_sdo = self.node.sdo[self.app.resource.index]

    def tearDown(self):
        self.app.stop()

    def test_system_info(self):

        '''
        self.assertNotEqual(self.info_sdo[Subindex.UPTIME.value].phys, 0)

        self.assertNotEqual(self.info_sdo[Subindex.NUM_OF_CPUS.value].phys, 0)
        self.assertNotEqual(self.info_sdo[Subindex.CPU_ARCH.value].phys, 0)
        self.assertNotEqual(self.info_sdo[Subindex.CPU_GOV.value].phys, 0)
        self.assertNotEqual(self.info_sdo[Subindex.CPU_FREQ.value].phys, 0)

        self.info_sdo[Subindex.RPROC_ITER.value].phys = 0
        self.assertEqual(self.info_sdo[Subindex.RPROC_ITER.value].phys, 0)
        self.info_sdo[Subindex.RPROC_ITER.value].phys = 1
        self.assertIn(self.info_sdo[Subindex.RPROC_ITER.value].phys, [0, 1])

        rpocs = self.info_sdo[Subindex.NUM_OF_RPROCS.value].phys
        for i in range(rpocs):
            self.info_sdo[Subindex.RPROC_ITER.value].phys = i
            self.assertNotEqual(self.info_sdo[Subindex.RPROC_ITER.value].phys, i)
            self.assertNotIn(self.info_sdo[Subindex.RPROC_NAME.value].phys, [None, ''])
            self.assertNotIn(self.info_sdo[Subindex.RPROC_STATE.value].phys, [None, ''])
        '''

        # just make sure nothing raises a exception

        self.info_sdo[Subindex.OS_DISTRO.value].phys
        self.info_sdo[Subindex.OS_NAME.value].phys
        self.info_sdo[Subindex.OS_KERNEL_VER.value].phys
        self.info_sdo[Subindex.HOSTNAME.value].phys

        self.info_sdo[Subindex.LOAD_AVG_1MIN.value].phys
        self.info_sdo[Subindex.LOAD_AVG_5MIN.value].phys
        self.info_sdo[Subindex.LOAD_AVG_15MIN.value].phys

        self.info_sdo[Subindex.RAM_TOTAL.value].phys
        self.info_sdo[Subindex.RAM_FREE.value].phys
        self.info_sdo[Subindex.RAM_SHARED.value].phys
        self.info_sdo[Subindex.RAM_BUFFERED.value].phys
        self.info_sdo[Subindex.RAM_PERCENT.value].phys

        self.info_sdo[Subindex.SWAP_TOTAL.value].phys
        self.info_sdo[Subindex.SWAP_FREE.value].phys
        self.info_sdo[Subindex.SWAP_PERCENT.value].phys

        # self.assertNotEqual(self.info_sdo[Subindex.PROCS.value].phys, 0)

        self.info_sdo[Subindex.ROOT_PART_TOTAL.value].phys
        self.info_sdo[Subindex.ROOT_PART_FREE.value].phys
        self.info_sdo[Subindex.ROOT_PART_PERCENT.value].phys
