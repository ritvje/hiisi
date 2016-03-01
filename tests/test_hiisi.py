# -*- coding: utf-8 -*-
import unittest
import env
import hiisi
import h5py
import numpy as np
import uuid
import os


class Test(unittest.TestCase):
    
    def setUp(self):
        self.unique_attr_path = None
        self.unique_attr_value = None
        self.reoccuring_attr_paths = []
        self.reoccuring_attr_items = []
        self.dataset_paths = []
        self.group_paths = ['/']
        self.data_filename = 'hiisi_test_data.h5'

        self.create_hdf5_test_data()
        self.h5file = hiisi.hiisi.HiisiHDF(self.data_filename, 'r')
        print('run setUp')
        
        
    def create_hdf5_test_data(self):
        """Creates random hdf5 file for testing
        """
        n_branches = 3
        n_datasets = 3
        unique_attr = uuid.uuid1().hex
        reoccuring_attr = [uuid.uuid1().hex for x in range(n_branches)]
        dataset_data = np.zeros((3,3))
        h5f = h5py.File(self.data_filename, 'w')
        
        for i in range(n_branches):
            group_path = '/branch{}'.format(i)
            self.group_paths.append(group_path)
            branch = h5f.create_group(group_path)
            branch.attrs['reoccuring_attr'] = reoccuring_attr[i]
            self.reoccuring_attr_paths.append(branch.name)
            self.reoccuring_attr_items.append((branch.name, reoccuring_attr[i]))
            for j in range(n_datasets):
                dataset_name='/branch{}/data{}/dataset'.format(i, j)
                self.group_paths.append('/branch{}/data{}'.format(i, j))
                dataset = h5f.create_dataset(dataset_name, data=np.int8(dataset_data), dtype='int8')
                self.dataset_paths.append(dataset.name)                    
                if i==1 and j==1:
                    dataset.attrs['unique_attr'] = unique_attr
                    self.unique_attr_path = dataset.name
                    self.unique_attr_value = unique_attr
        
        h5f.close()
        
    def tearDown(self):
        os.remove(self.data_filename)
                         
    def test_is_unique_attribute_true(self):
        self.assertTrue(self.h5file.is_unique_attr('unique_attr'))
        
    def test_is_unique_attribute_false(self):
        self.assertFalse(self.h5file.is_unique_attr('reoccuring_attr'))
        self.assertFalse(self.h5file.is_unique_attr('not_existing_attr'))
        
    def test_attr_exists_true(self):
        self.assertTrue(self.h5file.attr_exists('unique_attr'))        
            
    def test_attr_exists_false(self):
        self.assertFalse(self.h5file.attr_exists('not_existing_attr'))    

    def test_datasets(self):
        self.assertItemsEqual(list(self.h5file.datasets()), self.dataset_paths)
        
    def test_datasets_no_datasets_found(self):
        with hiisi.HiisiHDF('tmp.h5', 'w') as h5f:
            self.assertItemsEqual(list(h5f.datasets()), [])
        os.remove('tmp.h5')
        
    def test_groups(self):
        self.assertItemsEqual(list(self.h5file.groups()), self.group_paths)
        
    def test_groups_no_groups_found(self):
        with hiisi.HiisiHDF('tmp.h5', 'w') as h5f:
            self.assertItemsEqual(h5f.groups(), ['/'])
        os.remove('tmp.h5')

    def test_attr_gen(self):
        attr_gen = self.h5file.attr_gen('reoccuring_attr')
        attr_items = []     
        for i in attr_gen:
            attr_items.append((i.path, i.value))
        self.assertListEqual(attr_items, self.reoccuring_attr_items)

    def test_attr_gen_no_match(self):
        attr_gen = self.h5file.attr_gen('not_existing_attr')        
        with self.assertRaises(StopIteration):
            attr_gen.next()
            
    def test_create_from_filedict_new_file(self):
        filename = 'create_from_filedict_test.h5'
        with hiisi.HiisiHDF(filename, 'w') as h5f:
            file_dict = {}
            file_dict['/'] = {'A':1, 'B':2}
            file_dict['/dataset1/data1/data'] = {'DATASET':np.arange(9).reshape((3,3)), 'C':'c'}
            file_dict['/dataset1/data1/what'] = {'D':123}
            h5f.create_from_filedict(file_dict)        

        with hiisi.HiisiHDF(filename, 'r') as h5f:      
            self.assertEqual(h5f['/'].attrs['A'], 1)
            self.assertEqual(h5f['/'].attrs['B'], 2)
            self.assertEqual(h5f['/dataset1/data1/data'].attrs['C'], 'c')
            np.testing.assert_array_equal(h5f['/dataset1/data1/data'][:], np.arange(9).reshape((3,3)))
            self.assertEqual(h5f['/dataset1/data1/what'].attrs['D'], 123)
        os.remove(filename)

    
    def test_create_from_filedict_append_new_goup(self):
        filename = 'create_from_filedict_test.h5'
        # Create the file
        with hiisi.HiisiHDF(filename, 'w') as h5f:
            file_dict = {}
            file_dict['/'] = {'A':1, 'B':2}
            file_dict['/dataset1/data1/data'] = {'DATASET':np.arange(9).reshape((3,3)), 'C':'c'}
            file_dict['/dataset1/data1/what'] = {'D':123}
            h5f.create_from_filedict(file_dict)        

        # Append the file created above
        with hiisi.HiisiHDF(filename) as h5f:
            h5f.create_from_filedict({'/added_group':{'attr1':1}})
            
        # Check the results
        with hiisi.HiisiHDF(filename, 'r') as h5f:      
            self.assertEqual(h5f['/'].attrs['A'], 1)
            self.assertEqual(h5f['/'].attrs['B'], 2)
            self.assertEqual(h5f['/dataset1/data1/data'].attrs['C'], 'c')
            np.testing.assert_array_equal(h5f['/dataset1/data1/data'][:], np.arange(9).reshape((3,3)))
            self.assertEqual(h5f['/dataset1/data1/what'].attrs['D'], 123)
            self.assertEqual(h5f['/added_group'].attrs['attr1'], 1)
            
        os.remove(filename)
        
    def test_create_from_filedict_modify_existing_content(self):
        filename = 'create_from_filedict_test.h5'
        # Create the file
        with hiisi.HiisiHDF(filename, 'w') as h5f:
            file_dict = {}
            file_dict['/'] = {'A':1, 'B':2}
            file_dict['/dataset1/data1/data'] = {'DATASET':np.arange(9).reshape((3,3)), 'C':'c'}
            file_dict['/dataset1/data1/what'] = {'D':123}
            h5f.create_from_filedict(file_dict)        

        # Append the file created above
        with hiisi.HiisiHDF(filename) as h5f:
            h5f.create_from_filedict({'/dataset1/data1/data':{'C':'new_value'}})
            
        # Check the results
        with hiisi.HiisiHDF(filename, 'r') as h5f:      
            self.assertEqual(h5f['/'].attrs['A'], 1)
            self.assertEqual(h5f['/'].attrs['B'], 2)
            self.assertEqual(h5f['/dataset1/data1/data'].attrs['C'], 'new_value')
            np.testing.assert_array_equal(h5f['/dataset1/data1/data'][:], np.arange(9).reshape((3,3)))
            self.assertEqual(h5f['/dataset1/data1/what'].attrs['D'], 123)
            
        os.remove(filename)
           
    def test_search_no_match(self):
        self.assertListEqual([], self.h5file.search('madeupkey', 'xyz'))
            
    def test_search_single_match(self):
        self.assertListEqual([self.unique_attr_path], self.h5file.search('unique_attr', self.unique_attr_value))
            
    def test_search_multiple_matches(self):
        filename = 'test_search_multiple_matches.h5'
        with hiisi.HiisiHDF(filename) as h5f:
            groups = ['/group1', '/group2', '/basegroup/group1']
            for g in groups:
                group = h5f.create_group(g)
                group.attrs['attribute']  = 'attribute'
            
        with hiisi.HiisiHDF(filename) as h5f:
            self.assertListEqual(sorted(groups), sorted(h5f.search('attribute', 'attribute')))
        os.remove(filename)
            
    def test_search_numerical_attribute_within_tolerance(self):
        filename = 'test_search_numerical_attribute.h5'
        with hiisi.HiisiHDF(filename) as h5f:
            group = h5f.create_group('/group1')
            group.attrs['attribute']  = 7.3
            group = h5f.create_group('/group2')
            group.attrs['attribute']  = 0.1001
            group = h5f.create_group('/basegroup/group1')        
            group.attrs['attribute']  = 0.5245

        with hiisi.HiisiHDF(filename) as h5f:        
            self.assertListEqual(['/basegroup/group1'], h5f.search('attribute', 0.5, 0.1))
        os.remove(filename)

    def test_search_numerical_attribute_outside_tolerance(self):            
        filename = 'test_search_numerical_attribute.h5'
        with hiisi.HiisiHDF(filename) as h5f:
            group = h5f.create_group('/group1')
            group.attrs['attribute']  = 7.3
            group = h5f.create_group('/group2')
            group.attrs['attribute']  = 0.1001
            group = h5f.create_group('/basegroup/group1')        
            group.attrs['attribute']  = 0.5245

        with hiisi.HiisiHDF(filename) as h5f:        
            self.assertListEqual([], h5f.search('attribute', 7, 0.1))
        os.remove(filename)
        
    
if __name__=='__main__':
    unittest.main()       