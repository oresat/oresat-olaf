"""Test the OreSat file class."""

from pathlib import Path

import pytest

from olaf.common.oresat_file import OreSatFile, new_oresat_file


class TestOreSatFile:
    def test_new_oresat_file(self) -> None:
        file = new_oresat_file("keyword", "test", 100)
        assert file == "test_keyword_100000"

        file = new_oresat_file("keyword", "test", 100, "txt")
        assert file == "test_keyword_100000.txt"

        file = new_oresat_file("keyword", "test", 100, ".txt")
        assert file == "test_keyword_100000.txt"

        assert new_oresat_file("test") is not None

    def test_oresat_file(self) -> None:
        name = "name_test_12345.txt"
        file = OreSatFile(name)
        assert file.card == "name"
        assert file.keyword == "test"
        assert file.date == 12.345
        assert file.extension == ".txt"
        assert file.name == name

        name = "name_test_12345.tar.xz"
        file = OreSatFile(name)
        assert file.date == 12.345
        assert file.extension == ".tar.xz"

        path = Path("/this/is/test/name_test_123")
        file = OreSatFile(path)
        assert file.card == "name"
        assert file.keyword == "test"
        assert file.date == 0.123
        assert file.extension == ""
        assert file.name == path.name

        for name in [
            "nametest12345",
            "__",
            "__12345",
            "_test_12345",
            "name__12345",
            "name_test_",
        ]:
            with pytest.raises(ValueError, match='invalid'):
                OreSatFile(name)

        assert OreSatFile("name_test_12345.txt") < OreSatFile("name_test_23456.txt")
        assert OreSatFile("name_test_23456.txt") > OreSatFile("name_test_12345.txt")
