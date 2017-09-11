Hiisi
======
The main idea behind hiisi module is to make the handling of hdf5 files as
fluent as possible. Module contains higher level tools such as search and
write methods that are build on top of h5py_ module.

HiisiHDF expands h5py.File class forms the base of the module.
Using HiisiHDF file handle, users can search metadata from the file
without any prior knowledge of the file structure. In addition, HiisiHDF contains
methods for listing the datasets and groups in the file and a convenient method
for creating and expanding hdf5 files.
 
HiisiHDF can be used as such or it can be used as base class for creating more
specialized file handles for different types of data files. An example of custom
data file handle is the hiisi.odim module that contains file handles for reading
weather radar data files that follow the OPERA odim data format.

.. _h5py: http://www.h5py.org/

Examples
--------
Open hdf5 file::

    >>> from hiisi import HiisiHDF
    >>> h5f = HiisiHDF('data.h5', 'r')

Get a list of datasets::

    >>> for dataset in h5f.datasets():
            print(dataset)
    '/dataset1/data1/data'
    '/dataset1/data2/data'
    '/dataset2/data1/data'
    '/dataset2/data2/data'

Retrieve all instances of an attribute::

    >>> gen = h5f.attr_gen('elangle')
    >>> pair = gen.next()
    >>> print(pair.path)
    '/dataset1/where'
    >>> print(pair.value)
    0.5

Create a new hdf5 file with content::

    >>> h5f = HiisiHDF('newfile.h5', 'w')
    >>> filedict = {'/':{'attr1':'A'},
                    '/dataset1/data1/data':{'DATASET':np.zeros(100), 'quantity':'emptyarray'}, 'B':'b'}
    >>> h5f.create_from_filedict(filedict)

Find the names of the groups that contain an attribute with a certain value::

    >>> for result in h5f.search('quantity', 'DBZH'):
            print(result)
    '/dataset1/data2/what'
    '/dataset2/data2/what'
    '/dataset3/data2/what'
    '/dataset4/data2/what'
    '/dataset5/data2/what'
        
Find the names of the groups that contain a numerical attribute
with a certain value or a value that is within the given tolerance::

    >>> h5f.search('elangle', 0.5, tolerance=0.1)
    [u'/dataset1/where']


Installation
------------
Hiisi is dependent on **numpy** and **h5py** packages. If you have these dependencies already 
installed you can simply run ``pip install hiisi``.

Installing the dependencies and the package

.. code-block:: bash

    $ install pip
    $ pip install numpy
    $ pip install Cython
    $ pip install h5py
    $ pip install hiisi

License
-------
This code is licensed under the MIT open source license.

