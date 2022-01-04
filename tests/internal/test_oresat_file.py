import os

import pytest

from oresat_linux_node.common.oresat_file import new_oresat_file, OreSatFile


def test_new_oresat_file():

    file = new_oresat_file('keyword', 'test', 100)
    assert file == 'test_keyword_100'

    file = new_oresat_file('keyword', 'test', 100, 'txt')
    assert file == 'test_keyword_100.txt'

    file = new_oresat_file('keyword', 'test', 100, '.txt')
    assert file == 'test_keyword_100.txt'

    assert new_oresat_file('test')


def test_oresat_file():

    name = 'name_test_12345.txt'
    file = OreSatFile(name)
    assert file.board == 'name'
    assert file.keyword == 'test'
    assert file.date == 12345.0
    assert file.extension == '.txt'
    assert file.name == name

    name = 'name_test_12345.tar.xz'
    file = OreSatFile(name)
    assert file.date == 12345.0
    assert file.extension == '.tar.xz'

    name = '/this/is/test/name_test_123'
    file = OreSatFile(name)
    assert file.board == 'name'
    assert file.keyword == 'test'
    assert file.date == 123.0
    assert file.extension == ''
    assert file.name == os.path.basename(name)

    with pytest.raises(ValueError):
        OreSatFile('nametest12345')

    with pytest.raises(ValueError):
        OreSatFile('__')

    with pytest.raises(ValueError):
        OreSatFile('__12345')

    with pytest.raises(ValueError):
        OreSatFile('_test_12345')

    with pytest.raises(ValueError):
        OreSatFile('name__12345')

    with pytest.raises(ValueError):
        OreSatFile('name_test_')

    assert OreSatFile('name_test_12345.txt') < OreSatFile('name_test_23456.txt')
    assert OreSatFile('name_test_23456.txt') > OreSatFile('name_test_12345.txt')
