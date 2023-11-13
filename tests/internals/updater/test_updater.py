"""Test the updater."""

import shutil
import tempfile
import unittest
from os import geteuid, remove
from os.path import abspath, dirname, isfile

from olaf._internals.updater import Updater, UpdaterState, is_update_archive

PATH = dirname(abspath(__file__)) + "/test_files"


class TestUpdater(unittest.TestCase):
    """Test the updater."""

    @classmethod
    def setUpClass(cls):
        """generate temp dirs for tests"""
        cls._work_dir = tempfile.mkdtemp()
        cls._cache_dir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        """clean up temp dirs after tests"""
        shutil.rmtree(cls._work_dir)
        shutil.rmtree(cls._cache_dir)

    def setUp(self):
        """clean up cache dir before tests"""
        shutil.rmtree(self._cache_dir, ignore_errors=True)

    def test_is_update_archive(self):
        """Test the is_update_archive method works."""

        self.assertTrue(is_update_archive("gps_update_12346789.tar.xz"))
        self.assertTrue(is_update_archive("star-tracker_update_12346789.tar.xz"))

        self.assertFalse(is_update_archive("gps_update_12346789"))
        self.assertFalse(is_update_archive("gps_update_12346789.tar"))
        self.assertFalse(is_update_archive("star-tracker_capture_12346789.tar.xz"))

    def test_updater_default(self):
        """Test updater class defaults when no updates are cached."""
        updater = Updater(self._work_dir, self._cache_dir)

        # properties defaults
        self.assertEqual(updater.status, UpdaterState.UPDATE_SUCCESSFUL)
        self.assertEqual(updater.updates_cached, [])
        self.assertEqual(updater.list_updates, "[]")
        self.assertEqual(updater.update_archive, "")
        self.assertEqual(updater.total_instructions, 0)
        self.assertEqual(updater.instruction_index, 0)
        self.assertEqual(updater.instruction_percent, 0)
        self.assertEqual(updater.instruction_command, "")

    def test_add_update_archive(self):
        """Test adding an update archive to the updater."""

        updater = Updater(self._work_dir, self._cache_dir)
        updates_cached = len(updater.updates_cached)

        self.assertFalse(updater.add_update_archive("invalid-file-path"))
        self.assertEqual(len(updater.updates_cached), updates_cached)

        self.assertTrue(updater.add_update_archive(PATH + "/test_update_1611940000.tar.xz"))
        self.assertEqual(len(updater.updates_cached), updates_cached + 1)

        self.assertTrue(updater.add_update_archive(PATH + "/test_update_1611941111.tar.xz"))
        self.assertEqual(len(updater.updates_cached), updates_cached + 2)

        # add the same file (should override)
        self.assertTrue(updater.add_update_archive(PATH + "/test_update_1611942222.tar.xz"))
        self.assertTrue(updater.add_update_archive(PATH + "/test_update_1611942222.tar.xz"))
        self.assertTrue(updater.add_update_archive(PATH + "/test_update_1611942222.tar.xz"))
        self.assertEqual(len(updater.updates_cached), updates_cached + 3)

    @unittest.skipUnless(isfile("/usr/bin/dpkg"), "requires dpkg")
    def test_make_status_file(self):
        """Test making in a status file."""

        updater = Updater(self._work_dir, self._cache_dir)

        status_archive = updater.make_status_archive()
        self.assertTrue(isfile(status_archive))

        # clean up
        remove(status_archive)

    def test_archive_extraction(self):
        """Test archive exxtraction."""

        updater = Updater(self._work_dir, self._cache_dir)
        updater._extract_update_archive(PATH + "/test_update_1611940000.tar.xz")

    def test_read_instructions(self):
        """Test reading the instructions file."""

        updater = Updater(self._work_dir, self._cache_dir)
        updater._extract_update_archive(PATH + "/test_update_1611940000.tar.xz")
        updater._read_instructions()

    @unittest.skipUnless(isfile("/usr/bin/dpkg") and geteuid() == 0, "requires dpkg and root")
    def test_run_instructions(self):
        """Test running the instructions."""

        updater = Updater(self._work_dir, self._cache_dir)
        updater._extract_update_archive(PATH + "/test_update_1611940000.tar.xz")
        commands = updater._read_instructions()
        updater._run_instructions(commands)

    @unittest.skipUnless(isfile("/usr/bin/dpkg") and geteuid() == 0, "requires dpkg and root")
    def test_update(self):
        """Test running updates."""

        updater = Updater(self._work_dir, self._cache_dir)
        updates_cached = updater.updates_cached
        self.assertEqual(updater.status, UpdaterState.UPDATE_SUCCESSFUL)

        # add update archives
        self.assertTrue(updater.add_update_archive(PATH + "/test_update_1611940000.tar.xz"))
        self.assertTrue(updater.add_update_archive(PATH + "/test_update_1611941111.tar.xz"))
        self.assertTrue(updater.add_update_archive(PATH + "/test_update_1611942222.tar.xz"))
        self.assertTrue(updater.add_update_archive(PATH + "/test_update_1611943333.tar.xz"))
        self.assertEqual(updater.updates_cached, updates_cached + 4)

        # valid updates
        updater.update()  # 0
        self.assertEqual(updater.status, UpdaterState.UPDATE_SUCCESSFUL)
        updater.update()  # 1
        self.assertEqual(updater.status, UpdaterState.UPDATE_SUCCESSFUL)
        self.assertEqual(updater.updates_cached, updates_cached + 2)

        # valid updates that failed during update (missing dependency)
        updater.update()  # 2
        self.assertEqual(updater.status, UpdaterState.UPDATE_FAILED)
        self.assertEqual(updater.updates_cached, 0)  # should clear cache on failure

        # add invalid update archives
        self.assertTrue(updater.add_update_archive(PATH + "/test_update_1611943333.tar.xz"))
        self.assertTrue(updater.add_update_archive(PATH + "/test_update_1611944444.tar.xz"))
        self.assertTrue(updater.add_update_archive(PATH + "/test_update_1611945555.tar.xz"))
        self.assertTrue(updater.add_update_archive(PATH + "/test_update_1611946666.tar.xz"))
        self.assertTrue(updater.add_update_archive(PATH + "/test_update_1611947777.tar.xz"))
        self.assertTrue(updater.add_update_archive(PATH + "/test_update_1611948888.tar.xz"))
        self.assertEqual(updater.updates_cached, 6)

        # invalid updates (failed during pre update)
        updater.update()  # 3
        self.assertEqual(updater.status, UpdaterState.PRE_UPDATE_FAILED)
        updater.update()  # 4
        self.assertEqual(updater.status, UpdaterState.PRE_UPDATE_FAILED)
        updater.update()  # 5
        self.assertEqual(updater.status, UpdaterState.PRE_UPDATE_FAILED)
        updater.update()  # 6
        self.assertEqual(updater.status, UpdaterState.PRE_UPDATE_FAILED)
        updater.update()  # 7
        self.assertEqual(updater.status, UpdaterState.PRE_UPDATE_FAILED)
        updater.update()  # 8
        self.assertEqual(updater.status, UpdaterState.PRE_UPDATE_FAILED)
        self.assertEqual(updater.updates_cached, 0)
