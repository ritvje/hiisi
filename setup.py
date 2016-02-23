# -*- coding: utf-8 -*-
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

setup(name='hiisi',
      version='0.0.3',
      description='Tools for easy handling of hdf5 files',
      author='Joonas Karjalainen',
      author_email='joonas.karjalainen@fmi.fi',
      url='https://github.com/karjaljo/hiisi',
      license='MIT',
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
        ],
      keywords='hdf5 hdf hiisi',
      packages=find_packages(exclude=['docs','tests*']),
      install_requires=['numpy','Cython','h5py'],
    )
