"""Test the OreSat file cache class."""

from itertools import chain
from pathlib import Path

import pytest

from olaf.common.oresat_file_cache import OreSatFileCache


class TestOreSatFileCache:
    def test_non_existing_dir(self, tmp_path: Path) -> None:
        dir_name = tmp_path / "delete_me"
        result = OreSatFileCache(dir_name)
        assert result._dir == str(dir_name.absolute()) + "/"
        assert result.dir == str(dir_name.absolute())
        assert not result._data
        assert result._lock
        assert len(result) == 0

    def test_non_existing_file(self, tmp_path: Path) -> None:
        dir_name = tmp_path / "delete_me.txt"
        result = OreSatFileCache(dir_name)
        assert result._dir == str(dir_name.absolute()) + "/"
        assert result.dir == str(dir_name.absolute())
        assert not result._data
        assert result._lock
        assert len(result) == 0

    def test_existing_dir(self, tmp_path: Path) -> None:
        result = OreSatFileCache(tmp_path)
        assert result._dir == str(tmp_path.absolute()) + "/"
        assert result.dir == str(tmp_path.absolute())
        assert not result._data
        assert result._lock
        assert len(result) == 0

    def test_existing_file(self, tmp_path: Path) -> None:
        dir_name = tmp_path / "existing_file.xyz"
        dir_name.touch()
        with pytest.raises(FileExistsError):
            OreSatFileCache(dir_name)

    def test_add_good(self, tmp_path: Path) -> None:
        result = OreSatFileCache(tmp_path / "good_cache")

        for name in ("good_file_12345.txt", "good_file_12345.tar.xz", "good_file_123"):
            path = tmp_path / name
            path.touch()
            result.add(path, consume=True)
            assert not path.exists()

        for name in ("good_file_67890.txt", "good_file_67890.tar.xz", "good_file_678"):
            path = tmp_path / name
            path.touch()
            result.add(path, consume=False)
            assert path.exists()

        with pytest.raises(FileNotFoundError):
            result.add(tmp_path / "bad_path_123.txt")

    def test_add_bad(self, tmp_path: Path) -> None:
        # TEST: populate directory with BAD file name conventions
        result = OreSatFileCache(tmp_path / "bad_cache")
        for name in ["bad_file_.txt", "bad_file_1a2b3c.tar.xz", "badfile12345"]:
            path = tmp_path / name
            path.touch()
            with pytest.raises(ValueError, match=r"invalid|convert"):
                result.add(path)

    def test_remove(self, tmp_path: Path) -> None:
        # TEST: populate remove_cache with files and delete files
        result = OreSatFileCache(tmp_path / "remove_cache")
        for name in ("remove_file_12345.txt", "remove_file_12345.tar.xz", "remove_file_123"):
            path = tmp_path / name
            path.touch()
            result.add(path, consume=True)
            result.remove(name)
            assert not Path(result._dir, name).exists()

        # try remove non-existing file
        result.remove("remove_file_03152022.xyz")

    def test_peek(self, tmp_path: Path) -> None:
        # TEST: Get the oldest file name or returns empty string if none
        result = OreSatFileCache(tmp_path / "peek_cache")

        file1 = tmp_path / "pop_file_12345.txt"
        file2 = tmp_path / "pop_file_67890.txt"

        file1.touch()
        file2.touch()

        result.add(file1, consume=True)
        result.add(file2, consume=True)

        assert result.peek() == file1.name

    def test_pop_empty(self, tmp_path: Path) -> None:
        # TEST: Pop an empty cache
        result = OreSatFileCache(tmp_path / "pop_cache")
        assert result.pop("/phony/path/null") == ""

    def test_pop(self, tmp_path: Path) -> None:
        # TEST: Pop oldest file in cache via Move
        result = OreSatFileCache(tmp_path / "pop_cache")

        file1 = tmp_path / "pop_file_12345.txt"
        file2 = tmp_path / "pop_file_67890.txt"

        file1.touch()
        file2.touch()

        result.add(file1, consume=True)
        result.add(file2, consume=True)

        dest_path = result.pop(tmp_path, copy=False)
        assert Path(dest_path) == file1
        assert not Path(result._dir, file1.name).exists()
        assert file1.exists()

        dest_path = result.pop(tmp_path, copy=True)
        assert Path(dest_path) == file2
        assert Path(result._dir, file2.name).exists()
        assert file2.exists()

    def test_get(self, tmp_path: Path) -> None:
        # TEST: Get file from cache and move it to a specific directory
        result = OreSatFileCache(tmp_path / "get_cache")

        for name in (tmp_path / "get_file_999.txt", tmp_path / "get_file_111.txt"):
            name.touch()
            result.add(name, consume=True)

        dest_path = result.get("get_file_111.txt", tmp_path, copy=True)
        assert Path(dest_path) == tmp_path / "get_file_111.txt"
        assert Path(result._dir, "get_file_111.txt").exists()
        assert (tmp_path / "get_file_111.txt").exists()

        dest_path = result.get("get_file_999.txt", tmp_path, copy=False)
        assert Path(dest_path) == tmp_path / "get_file_999.txt"
        assert not Path(result._dir, "get_file_999.txt").exists()
        assert (tmp_path / "get_file_999.txt").exists()

        # Raises: FileNotFoundError when filename is not in cache
        with pytest.raises(FileNotFoundError):
            result.get("get_file_777.txt", tmp_path)

        with pytest.raises(FileNotFoundError):
            result.get("__get_file__", tmp_path)

        with pytest.raises(FileNotFoundError):
            result.get("getFile123", tmp_path)

    def test_files(self, tmp_path: Path) -> None:
        # TEST: populate cache with files by keyword, then return using keyword filter
        result = OreSatFileCache(tmp_path / "files_cache")

        alpha = ["files_alpha_123", "files_alpha_456.txt", "files_alpha_789.tar.xz"]
        beta = ["files_beta_123", "files_beta_456.txt", "files_beta_789.tar.xz"]
        gamma = ["files_gamma_000", "files_gamma_000", "files_gamma_000"]

        for name in chain(alpha, beta, gamma):
            path = tmp_path / name
            path.touch()
            result.add(path, consume=True)

        for file, name in zip(result.files("alpha"), alpha):
            assert file.name == name

        for file, name in zip(result.files("beta"), beta):
            assert file.name == name

        for file, name in zip(result.files("gamma"), gamma):
            assert file.name == name

        assert len(result.files("gamma")) == 1  # duplicate files are overwritten via add()

    def test_clear(self, tmp_path: Path) -> None:
        dir_name = tmp_path / "clear_cache"
        result = OreSatFileCache(dir_name)

        file_name = tmp_path / "clear_file_123.txt"
        file_name.touch()
        result.add(file_name, consume=True)
        assert len(result) == 1

        result.clear()
        assert result.dir == str(dir_name.absolute())
        assert not any(Path(result._dir).iterdir())
