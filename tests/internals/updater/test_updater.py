"""Test the updater."""

from os import geteuid
from pathlib import Path

import pytest

from olaf._internals.updater import Updater, UpdaterState, is_update_archive

PATH = Path(__file__).resolve().parent / "test_files"
has_dpkg = Path("/usr/bin/dpkg").is_file()


@pytest.fixture
def updater(tmp_path: Path) -> Updater:
    return Updater(tmp_path / 'work', tmp_path / 'cache')


class TestUpdater:
    def test_is_update_archive(self) -> None:
        assert is_update_archive("gps_update_12346789.tar.xz")
        assert is_update_archive("star-tracker_update_12346789.tar.xz")

        assert not is_update_archive("gps_update_12346789")
        assert not is_update_archive("gps_update_12346789.tar")
        assert not is_update_archive("star-tracker_capture_12346789.tar.xz")

    def test_updater_default(self, updater: Updater) -> None:
        # properties defaults
        assert updater.status == UpdaterState.UPDATE_SUCCESSFUL
        assert updater.updates_cached == []
        assert updater.list_updates == "[]"
        assert updater.update_archive == ""
        assert updater.total_instructions == 0
        assert updater.instruction_index == 0
        assert updater.instruction_percent == 0
        assert updater.instruction_command == ""

    def test_add_update_archive(self, updater: Updater) -> None:
        updates_cached = len(updater.updates_cached)

        assert not updater.add_update_archive("invalid-file-path")
        assert len(updater.updates_cached) == updates_cached

        assert updater.add_update_archive(PATH / "test_update_1611940000.tar.xz")
        assert len(updater.updates_cached) == updates_cached + 1

        assert updater.add_update_archive(PATH / "test_update_1611941111.tar.xz")
        assert len(updater.updates_cached) == updates_cached + 2

        # add the same file (should override)
        assert updater.add_update_archive(PATH / "test_update_1611942222.tar.xz")
        assert updater.add_update_archive(PATH / "test_update_1611942222.tar.xz")
        assert updater.add_update_archive(PATH / "test_update_1611942222.tar.xz")
        assert len(updater.updates_cached) == updates_cached + 3

    @pytest.mark.skipif(not has_dpkg, reason="requires dpkg")
    def test_make_status_file(self, updater: Updater) -> None:
        status_archive = Path(updater.make_status_archive())
        assert status_archive.is_file()

    def test_archive_extraction(self, updater: Updater) -> None:
        updater._extract_update_archive(PATH / "test_update_1611940000.tar.xz")

    def test_read_instructions(self, updater: Updater) -> None:
        updater._extract_update_archive(PATH / "test_update_1611940000.tar.xz")
        updater._read_instructions()

    @pytest.mark.skipif(not has_dpkg or geteuid() != 0, reason="requires dpkg and root")
    def test_run_instructions(self, updater: Updater) -> None:
        updater._extract_update_archive(PATH / "test_update_1611940000.tar.xz")
        commands = updater._read_instructions()
        updater._run_instructions(commands)

    @pytest.mark.skipif(not has_dpkg or geteuid() != 0, reason="requires dpkg and root")
    def test_update(self, updater: Updater) -> None:
        updates_cached = updater.updates_cached
        assert updater.status == UpdaterState.UPDATE_SUCCESSFUL

        # add update archives
        assert updater.add_update_archive(PATH / "test_update_1611940000.tar.xz")
        assert updater.add_update_archive(PATH / "test_update_1611941111.tar.xz")
        assert updater.add_update_archive(PATH / "test_update_1611942222.tar.xz")
        assert updater.add_update_archive(PATH / "test_update_1611943333.tar.xz")
        assert len(updater.updates_cached) == len(updates_cached) + 4

        # valid updates
        updater.update()  # 0
        assert updater.status == UpdaterState.UPDATE_SUCCESSFUL
        updater.update()  # 1
        assert updater.status == UpdaterState.UPDATE_SUCCESSFUL
        assert len(updater.updates_cached) == len(updates_cached) + 2

        # valid updates that failed during update (missing dependency)
        updater.update()  # 2
        assert updater.status == UpdaterState.UPDATE_FAILED
        assert len(updater.updates_cached) == 0  # should clear cache on failure

        # add invalid update archives
        assert updater.add_update_archive(PATH / "test_update_1611943333.tar.xz")
        assert updater.add_update_archive(PATH / "test_update_1611944444.tar.xz")
        assert updater.add_update_archive(PATH / "test_update_1611945555.tar.xz")
        assert updater.add_update_archive(PATH / "test_update_1611946666.tar.xz")
        assert updater.add_update_archive(PATH / "test_update_1611947777.tar.xz")
        assert updater.add_update_archive(PATH / "test_update_1611948888.tar.xz")
        assert len(updater.updates_cached) == 6

        # invalid updates (failed during pre update)
        updater.update()  # 3
        assert updater.status == UpdaterState.PRE_UPDATE_FAILED
        updater.update()  # 4
        assert updater.status == UpdaterState.PRE_UPDATE_FAILED
        updater.update()  # 5
        assert updater.status == UpdaterState.PRE_UPDATE_FAILED
        updater.update()  # 6
        assert updater.status == UpdaterState.PRE_UPDATE_FAILED
        updater.update()  # 7
        assert updater.status == UpdaterState.PRE_UPDATE_FAILED
        updater.update()  # 8
        assert updater.status == UpdaterState.PRE_UPDATE_FAILED
        assert len(updater.updates_cached) == 0
