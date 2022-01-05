from setuptools import setup, find_packages

import oresat_linux_node as oln

with open('README.md', 'r') as f:
    long_description = f.read()

with open('requirements.txt', 'r') as f:
    requirements = f.readlines()

setup(
    name=oln.APP_NAME,
    version=oln.APP_VERSION,
    author=oln.APP_AUTHOR,
    license=oln.APP_LICENSE,
    description=oln.APP_DESCRIPTION,
    long_description=long_description,
    author_email=oln.APP_EMAIL,
    maintainer=oln.APP_AUTHOR,
    maintainer_email=oln.APP_EMAIL,
    url=oln.APP_URL,
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
)
