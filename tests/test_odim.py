# -*- coding: utf-8 -*-
import unittest
import env
import h5py
import hiisi
import numpy as np
import os

class Test(unittest.TestCase):
    
    def setUp(self):
        self.odim_file = OdimPVOL('test_data/pvol.h5', 'r')
        
    def tearDown(self):
        self.odim_file.close()
        
    def test__set_elangles(self):
        self.odim_file._set_elangles()
        comparison_dict = {'A':self.odim_file['/dataset1/where'].attrs['elangle'],
                           'B':self.odim_file['/dataset2/where'].attrs['elangle'],
                            'C':self.odim_file['/dataset3/where'].attrs['elangle'],
                            'D':self.odim_file['/dataset4/where'].attrs['elangle'],
                            'E':self.odim_file['/dataset5/where'].attrs['elangle']
                            }
        self.assertDictEqual(self.odim_file.elangles, comparison_dict)
    
    def test__set_elangles_no_elangles(self):        
        with hiisi.OdimPVOL('empty_file.h5') as pvol:
            self.assertDictEqual(pvol.elangles, {})
            
    def test_select_dataset(self):
        self.assertEqual(self.odim_file.select_dataset('A', 'DBZH'), '/dataset1/data2/data')
        self.assertEqual(self.odim_file.select_dataset('B', 'VRAD'), '/dataset2/data3/data')
        self.assertEqual(self.odim_file.select_dataset('E', 'RHOHV'), '/dataset5/data7/data')
        
    def test_select_dataset_no_dataset_found(self):
        self.assertIsNone(self.odim_file.select_dataset('X', 'DBZH'))
        self.assertIsNone(self.odim_file.select_dataset('A', 'XXXX'))
    """
        
    def test_get_dataset(self):
        dataset_path = self.odim_file.get_dataset('A', 'DBZH')        
        self.assertEqual(dataset_path, '/dataset1/data1/data')        
    """
    
    def test_OdimPVOL_create_from_filedict(self):
        dataset1 = np.arange(9).reshape(3,3)
        dataset2 = np.ones_like(dataset1)   
        with odim.OdimPVOL('test.h5', 'w') as pvol:
            d = {'/what':{'date':'20151212'},
                 '/dataset1/data1/data':{'A':1, 'B':'b', 'DATASET':dataset1},
                 '/dataset1/data2/data':{'C':1, 'D':'b', 'DATASET':dataset2}}
            pvol.create_from_filedict(d)
    
        with odim.OdimPVOL('test.h5', 'r') as pvol:
            self.assertEqual('20151212' , pvol['/what'].attrs['date'])
            self.assertEqual(1, pvol['/dataset1/data1/data'].attrs['A'])
            self.assertEqual('b', pvol['/dataset1/data1/data'].attrs['B'] )
            np.testing.assert_array_equal(dataset1, pvol['/dataset1/data1/data'][:])
            self.assertEqual(1, pvol['/dataset1/data2/data'].attrs['C'])
            self.assertEqual('b', pvol['/dataset1/data2/data'].attrs['D'])
            np.testing.assert_array_equal(dataset2, pvol['/dataset1/data2/data'][:])
            
    def test_OdimPVOL_get_dataset_no_match(self):    
        dataset_path = self.odim_file.get_dataset(elangle='A', quantity='TESTQUANTITY' )
        self.assertEqual(None, dataset_path)
        
            
        
if __name__=='__main__':
    unittest.main()