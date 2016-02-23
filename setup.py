# -*- coding: utf-8 -*-
import os.path

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

import sys

try:
    import numpy
except ImportError:
    print "Package requirements not fullfilled! numpy is missing"
try:
    import h5py
except ImportError:
    print "Package requirements not fullfilled! h5py is missing"

with open(os.path.join('hiisi','VERSION')) as version_file:
    version = version_file.read().strip()

setup(name='hiisi',
      version=version,
      description='Tools for easy handling of hdf5 files',
      author='Joonas Karjalainen',
      author_email='joonas.karjalainen@fmi.fi',
      url='https://github.com/karjaljo/hiisi',
      license='MIT',
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
        ],
      keywords='hdf5 hdf hiisi',
      packages=find_packages(exclude=['docs','tests*']),
      install_requires=['numpy','Cython','h5py'],
    )
