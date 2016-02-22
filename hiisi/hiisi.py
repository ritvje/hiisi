# -*- coding: utf-8 -*-
import h5py
import os
from collections import namedtuple
__version__ = '0.0.1'
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
        """Returns True if atleast on instance of attribute is found
        """
        gen = self.attr_gen(attr)
        n_instances = len(list(gen))
        if n_instances > 0:
            return True
        else:
            return False

    def is_unique_attr(self, attr):
        """Returns true if only single instance of attribute is found
        """
        gen = self.attr_gen(attr)
        n_instances = len(list(gen))
        if n_instances == 1:
            return True
        else:
            return False

    def list_datasets(self):
        """Method goes trough the hdf5 file and retrurns a
        list of all dataset paths.

        Examples
        --------

        >>> h5f = HiisiHDF('data.h5')
        >>> print(h5f.get_dataset_paths())
        ['/dataset1/data1/data', '/dataset1/data2/data', ...]

        """
        HiisiHDF._clear_cache()
        self.visititems(HiisiHDF._is_dataset)
        return HiisiHDF.CACHE['dataset_paths']

    def list_groups(self):
        """Method returns the list of all goup paths
        """
        HiisiHDF._clear_cache()
        self.CACHE['group_paths'].append('/') #Every hdf5 file has a root
        self.visititems(HiisiHDF._is_group)
        return HiisiHDF.CACHE['group_paths']


    def attr_gen(self, attr):
        """Returns attribute generator that yields namedtuples containing
        path value pairs

        Examples
        --------

        gen = h5f.attr_gen('elangle')
        print(gen.next().value)
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
        Creates h5 file from dictionary that contains the groups, datasets
        and metadata. Method can also be used to append existing hdf5 file.
        If the file is opened in read only mode, method does nothing.

        Examples
        --------
        Create newfile.h5 and fill it with data and metadata

        >>> h5f = HiisiHDF('newfile.h5', 'w')
        >>> filedict = {'/':{'attr1':'A'},
                        '/dataset1/data1/data':{'DATASET':np.zeros(100), 'quantity':'emptyarray'}, 'B':'b'}
        >>> h5f.create_from_filedict(filedict)

        """
        if self.mode in ['r+','w', 'w-', 'x', 'a']:
            for h5path, path_content in filedict.iteritems():
                if path_content.has_key('DATASET'):
                    # If path exist, write only metadata
                    if h5path in self:
                        for key, value in path_content.iteritems():
                            if key != 'DATASET':
                                self[h5path].attrs[key] = value
                    else:
                        try:
                            group = self.create_group(os.path.dirname(h5path))
                        except ValueError:
                            group = self[os.path.dirname(h5path)]
                            pass # This pass has no effect?
                        new_dataset = group.create_dataset(os.path.basename(h5path), data=path_content['DATASET'])
                        for key, value in path_content.iteritems():
                            if key != 'DATASET':
                                new_dataset.attrs[key] = value
                else:
                    try:  
                        group = self.create_group(h5path)
                    except ValueError:
                        group = self[h5path]
                    for key, value in path_content.iteritems():
                        group.attrs[key] = value

    def search(self, attr, value, tolerance=0):
        """
        1. Find paths with a key value match

        Parameters
        ----------
        search_dict : dict
            Dictionary containing the search keys and values
        numerical : float
            tolerance used when searching for matching numerical
            attributes. If the value of the attribute found from the file
            differs from the searched value less than the tolerance, attributes
            are considered to be the same.

        Returns
        -------
        list_of_paths : list of strings
            List of corresponding paths

        Examples
        --------

        >>> h5f = HiisiHDF('data.h5')
        >>> h5f.search('elangle', 0.5, 0.1)
        [u'/dataset1/where']

        >>> h5f = HiisiHDF('data.h5')
        >>> h5f.search('quantity', 'DBZH')
        [u'/dataset1/data2/what',
         u'/dataset2/data2/what',
         u'/dataset3/data2/what',
         u'/dataset4/data2/what',
         u'/dataset5/data2/what']

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

    '''
    # These methods require more development and are left out for now

    def search_dataset(self, search_dict, start_path='/', sibling_groups=[]):
        """
        Finds dataset whose path contains all the key/value pairs in the dict
        returns None if nothing is found. Keyword sibling_groups is a list of
        approved group names that are also searched, for example in ODIM files
        the sibling paths would be how, what, where.

        Parameters
        ----------
        search_dict : dictionary
            Dictionary containing the key value pairs used in the search
        start_path : str
            Where to start the search, default value is '/'
        sibling_groups : list
            List of group names that are included in the search

        Returns
        -------
        matching datasets : set
            Returns a set containing the paths of all matching datasets

        Examples
        --------

        >>> h5f = HiisiHDF('newfile.h5', 'w')
        >>> print(h5f.get_dataset({'quantity':'DBZH', 'elangle':'0.7'},
                                  sibling_paths=['how', 'what', 'where']))
        '/dataset2/data2/data'

        """
        #For example, if sibling paths are defined ['how', 'what', 'where'] the 
        #search goes like this. Note if search path doesn't exist the search
        #continues.

        #1. list all dataset paths

        #2. search paths for matching key value pairs and add the path of the
        #dataset to dictionary if positive match is found.

        #first level:
        #/dataset1/data1/data
        #/dataset1/data1/data/how
        #/dataset1/data1/data/what
        #/dataset1/data1/data/where

        #move to second level and search paths:
        #/dataset1/data1
        #/dataset1/data1/how
        #/dataset1/data1/what
        #/dataset1/data1/where

        #move to third level and search paths:
        #/dataset1
        #/dataset1/how
        #/dataset1/what
        #/dataset1/where

        #move to fourth level and searh paths:
        #/
        #/how
        #/what
        #/where

        #3. Go trough the result dictionary and select the dataset paths whose
        #search trees contain all the matching search values.

        search_results_dict = dict(zip(search_dict.keys(), [[] for x in range(len(search_dict.keys()))]))
        dataset_paths = self.get_dataset_paths()
        for key, value in search_dict.iteritems():
            for dataset_path in dataset_paths:
                search_point = self[dataset_path]

                while search_point.name != '/':
                    try:
                        if str(search_point.attrs[key]) == str(value):
                            search_results_dict[key].append(dataset_path)
                    except KeyError:
                        pass
                    for sibling_group in sibling_groups:
                        try:
                            sibling_group_path = os.path.join(search_point.name, sibling_group)
                            if str(self[sibling_group_path].attrs[key]) == str(value):
                                search_results_dict[key].append(dataset_path)     
                        except:
                            pass

                    search_point = search_point.parent

        for k, v in search_results_dict.iteritems():
            if v == []:
                print("k was not found anywhere on the file")

        matching_values = set(search_results_dict.values()[0]).intersection(*search_results_dict.values())
        return  matching_values


    def search_dict(self, search_dict, numerical_tolerance=0):
        """
        1. Find paths with a key value match
 
        Parameters
        ----------
        search_dict : dict
            Dictionary containing the search keys and values
        numerical_tolerance : float
            Numerical tolerance used when searching for matching float
            attributes. If the attribute value found from the file is within 
            the tolerance values are regarded the same. 
        """
        found_paths = {}
        for attr, value in search_dict.iteritems():
            gen = self.attr_gen(attr)
            for path_attr_pair in gen:
                print path_attr_pair
                # if attribute is numerical use numerical_value_tolerance in
                # value comparison. If attribute is string require exact match
                dtype_name = path_attr_pair.value.dtype.name   
                if 'int' in dtype_name or 'float' in dtype_name:
                    if abs(path_attr_pair.value - value) <= numerical_tolerance:                    
                        if attr not in found_paths.keys():
                            found_paths[attr] = [path_attr_pair.path]
                        else:
                            found_paths[attr].append(path_attr_pair.path)
                else:
                    if path_attr_pair.value == value:
                        if attr not in found_paths.keys():
                            found_paths[attr] = [path_attr_pair.path]
                        else:
                            found_paths[attr].append(path_attr_pair.path)

        if search_dict.keys() != found_paths.keys():
            return None
        else:
            return found_paths
    '''