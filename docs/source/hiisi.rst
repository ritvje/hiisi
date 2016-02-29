Hiisi
======
The main idea behind hiisi module is to make the handling of hdf5 -files as
fluent as possible. Module contains higher level tools such as search and
write methods that are build on top of h5py module.

HiisiHDF file handle is built of top of h5py.File class and it forms the base of
the module. HiisiHDF makes it possible to search metadata from the file
without any prior knowledge of the structure of the file. In addition, it contains
methods for listing the datasets and groups of the file and a conveinient method
for creating new hdf5 files and for expanding files that already contain data.

File creation method uses nested dictionaries, referred to as filedicts, for saving
the hdf5-file structure. The keys of the outer layer of the filedict are the group
and dataset paths. The value of each path is a dictionary containing the related
metadata. If the path contains a dataset, a key 'DATASET' is used to indicate the data array.
 
HiisiHDF can be used as such or it can be used as base class for creating more
specialized file handles for different types of data files. An example of custom
data file handle is the hiisi.odim module that contains file handles for reading
weather radar data files that follow the OPERA odim data format.

.. automodule:: hiisi.hiisi

.. autoclass:: HiisiHDF
   :members:
