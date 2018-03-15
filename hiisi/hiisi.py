# -*- coding: utf-8 -*-
import h5py
import os
from collections import namedtuple
PathValue = namedtuple('PathValue', ['path', 'value'])


class HiisiHDF(h5py.File):
    """hdf5 file handle written on top of h5py.File.

    Module offers easy to use search, and write methods for handling
    HDF5 files.
    """
    CACHE = {'search_attribute':None,
             'dataset_paths':[],
             'group_paths':[],
             'attribute_paths':[]}

    def __init__(self, *args, **kwargs):
        super(HiisiHDF, self).__init__(*args, **kwargs)

    @staticmethod
    def _clear_cache():
        HiisiHDF.CACHE = {'search_attribute':None,
                          'dataset_paths':[],
                          'group_paths':[],
                          'attribute_paths':[]}

    @staticmethod
    def _is_dataset(name, obj):
        if isinstance(obj, h5py.Dataset):
            HiisiHDF.CACHE['dataset_paths'].append(obj.name)

    @staticmethod
    def _is_group(name, obj):
        if isinstance(obj, h5py.Group):
            HiisiHDF.CACHE['group_paths'].append(obj.name)

    @staticmethod
    def _find_attr_paths(name, obj):
        if HiisiHDF.CACHE['search_attribute'] in obj.attrs:
            HiisiHDF.CACHE['attribute_paths'].append(obj.name)

    @staticmethod
    def _is_attr_path(name, obj):
        if HiisiHDF.CACHE['search_attribute'] in obj.attrs:
            return obj.name

    def attr_exists(self, attr):
        """Returns True if at least on instance of the attribute is found
        """
        gen = self.attr_gen(attr)
        n_instances = len(list(gen))
        if n_instances > 0:
            return True
        else:
            return False

    def is_unique_attr(self, attr):
        """Returns true if only single instance of the attribute is found
        """
        gen = self.attr_gen(attr)
        n_instances = len(list(gen))
        if n_instances == 1:
            return True
        else:
            return False

    def datasets(self):
        """Method returns a list of dataset paths.

        Examples
        --------
        >>> for dataset in h5f.datasets():
                print(dataset)
        '/dataset1/data1/data'
        '/dataset1/data2/data'
        '/dataset2/data1/data'
        '/dataset2/data2/data'
        """
        HiisiHDF._clear_cache()
        self.visititems(HiisiHDF._is_dataset)
        return HiisiHDF.CACHE['dataset_paths']

    def groups(self):
        """Method returns a list of all goup paths
        
        Examples
        --------        
        >>> for group in h5f.groups():
                print(group)        
        '/'
        '/dataset1'
        '/dataset1/data1'
        '/dataset1/data2'
        """
        HiisiHDF._clear_cache()
        self.CACHE['group_paths'].append('/')
        self.visititems(HiisiHDF._is_group)
        return HiisiHDF.CACHE['group_paths']

    def attr_gen(self, attr):
        """Returns attribute generator that yields namedtuples containing
        path value pairs
        
        Parameters
        ----------
        attr : str
            Name of the search attribute

        Returns
        -------
        attr_generator : generator
            Returns a generator that yields named tuples with field names
            path and value.

        Examples
        --------
        >>> gen = h5f.attr_gen('elangle')
        >>> pair = next(gen)
        >>> print(pair.path)
        '/dataset1/where'
        >>> print(pair.value)
        0.5

        """
        HiisiHDF._clear_cache()
        HiisiHDF.CACHE['search_attribute'] = attr
        HiisiHDF._find_attr_paths('/', self['/']) # Check root attributes
        self.visititems(HiisiHDF._find_attr_paths)
        path_attr_gen = (PathValue(attr_path, self[attr_path].attrs.get(attr)) for attr_path in HiisiHDF.CACHE['attribute_paths'])
        return path_attr_gen


    def create_from_filedict(self, filedict):
        """
        Creates h5 file from dictionary containing the file structure.
        
        Filedict is a regular dictinary whose keys are hdf5 paths and whose
        values are dictinaries containing the metadata and datasets. Metadata
        is given as normal key-value -pairs and dataset arrays are given using
        'DATASET' key. Datasets must be numpy arrays.

        Datasets can be compressed by adding 'COMPRESSION' key to the
        dictionary that contains the 'DATASET'. Level of compression can
        be controlled with 'COMPRESSION_OPTS' key.
                
        Method can also be used to append existing hdf5 file. If the file is
        opened in read only mode, method does nothing.

        Parameters
        ----------
        file_dict : dict
            Nested dictionary containing the hdf5 file structure.
            Dictionary can contain reserved keys 'DATASET', 'COMPRESSION'
            and 'COMPRESSION_OPTS' that specify how dataset is written
            to the file.
            COMPRESSION can have values 'gzip', 'lzf' and 'szip'.
            COMPRESSION_OPTS can be optionally used with 'gzip' and it
            can have values at range 0-9, the default value is 4.

        Examples
        --------
        Create newfile.h5 and fill it with data and metadata

        >>> h5f = HiisiHDF('newfile.h5', 'w')
        >>> filedict = {'/':{'attr1':'A'},
                        '/dataset1/data1/data':{'DATASET':np.zeros(100), 'quantity':'emptyarray'}, 'B':'b'}
        >>> h5f.create_from_filedict(filedict)

        Create newfile.h5 with compressed datasets
        >>> h5f = HiisiHDF('newfile.h5', 'w')
        >>> filedict = {'/':{'attr1':'A'},
                        '/dataset1/data1/data':{'DATASET':np.zeros(100), 'COMPRESSION':'gzip', 'COMPRESSION_OPTS':9, 'quantity':'emptyarray'}, 'B':'b'}
        >>> h5f.create_from_filedict(filedict)

        """
        RESERVED_KEYS = ['DATASET', 'COMPRESSION', 'COMPRESSION_OPTS']

        if self.mode in ['r+','w', 'w-', 'x', 'a']:
            for h5path, path_content in filedict.iteritems():
                if path_content.has_key('DATASET'):
                    # If path exist, write only metadata
                    if h5path in self:
                        for key, value in path_content.iteritems():
                            if key not in RESERVED_KEYS:
                                self[h5path].attrs[key] = value
                    else:
                        try:
                            group = self.create_group(os.path.dirname(h5path))
                        except ValueError:
                            group = self[os.path.dirname(h5path)]
                            pass # This pass has no effect?

                        # extract compression parameters
                        compression = path_content.get('COMPRESSION')
                        if compression is not None:
                            compression_opts = path_content.get('COMPRESSION_OPTS')
                        
                        if compression is not None:
                            if compression_opts is not None:
                                new_dataset = group.create_dataset(os.path.basename(h5path), data=path_content['DATASET'], compression=compression, compression_opts=compression_opts)
                            else:
                                new_dataset = group.create_dataset(os.path.basename(h5path), data=path_content['DATASET'], compression=compression)
                        else:
                            new_dataset = group.create_dataset(os.path.basename(h5path), data=path_content['DATASET'])
                        for key, value in path_content.iteritems():
                            if key not in RESERVED_KEYS:
                                new_dataset.attrs[key] = value
                else:
                    try:  
                        group = self.create_group(h5path)
                    except ValueError:
                        group = self[h5path]
                    for key, value in path_content.iteritems():
                        group.attrs[key] = value

    def search(self, attr, value, tolerance=0):
        """Find paths with a key value match

        Parameters
        ----------
        attr : str
            name of the attribute
        value : str or numerical value
            value of the searched attribute
        
        Keywords
        --------
        tolerance : float
            tolerance used when searching for matching numerical
            attributes. If the value of the attribute found from the file
            differs from the searched value less than the tolerance, attributes
            are considered to be the same.

        Returns
        -------
        results : list
            a list of all matching paths

        Examples
        --------

        >>> for result in h5f.search('elangle', 0.5, 0.1):
                print(result)        
        '/dataset1/where'

        >>> for result in h5f.search('quantity', 'DBZH'):
                print(result)
        '/dataset1/data2/what'
        '/dataset2/data2/what'
        '/dataset3/data2/what'
        '/dataset4/data2/what'
        '/dataset5/data2/what'
        
        """
        found_paths = []
        gen = self.attr_gen(attr)
        for path_attr_pair in gen:
            # if attribute is numerical use numerical_value_tolerance in
            # value comparison. If attribute is string require exact match
            if isinstance(path_attr_pair.value, str):
                type_name = 'str'
            else:
                type_name = path_attr_pair.value.dtype.name
            if 'int' in type_name or 'float' in type_name:
                if abs(path_attr_pair.value - value) <= tolerance:
                    found_paths.append(path_attr_pair.path)
            else:
                if path_attr_pair.value == value:
                    found_paths.append(path_attr_pair.path)

        return found_paths

