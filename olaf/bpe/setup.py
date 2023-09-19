from pathlib import Path

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

import bpe

bpe_module = Pybind11Extension(
    "bpe"
)

setup(
    name='bpe_module',
    version=0.1,
)
