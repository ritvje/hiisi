# -*- coding: utf-8 -*-
import os
import re
import io

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages
'''
try:
    import numpy
except ImportError:
    print "Package requirements not fullfilled! numpy is missing"
try:
    import h5py
except ImportError:
    print "Package requirements not fullfilled! h5py is missing"
'''

# This function is copied from https://github.com/pypa/pip/blob/1.5.6/setup.py#L33
def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()
# This function is copied from https://github.com/pypa/pip/blob/1.5.6/setup.py#L33
def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(name='hiisi',
      version=find_version("hiisi", "__init__.py"),
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
      keywords='hdf5 hdf hiisi weather radar odim',
      packages=find_packages(exclude=['docs','tests*']),
      #install_requires=['numpy','Cython','h5py'],
    )
