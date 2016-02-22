# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys

try:
    import numpy
except ImportError:
    print "Package requirements not fullfilled! numpy is missing"
try:
    import h5py
except ImportError:
    print "Package requirements not fullfilled! h5py is missing"

setup(name='hiisi',
      version='0.0.1',
      description='Tools for easy handling of hdf5 files',
      author='Joonas Karjalainen',
      author_email='joonas.karjalainen@fmi.fi',
      url='https://github.com/karjaljo/hiisi.git',
      packages=['hiisi'],
      install_requires=['numpy', 'h5py'],
    )
