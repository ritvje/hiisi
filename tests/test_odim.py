# -*- coding: utf-8 -*-
import unittest
import env
import h5py
from hiisi import odim
import numpy as np
import os

class Test(unittest.TestCase):
    
    def setUp(self):
        self.odim_file = OdimPVOL('test_data/201207292000_radar.raw.fivan.andre_ANDRE=FMI_DATA=ALL.h5', 'r')
        
    def tearDown(self):
        self.odim_file.close()
    """    
    def test__set_elangles(self):
        self.assertDictEqual(self.odim_file.elangles, {'A':0.5, 'B':0.7, 'C':1.5, 'D':3.0, 'E':5.0})
    
    def test__set_elangles_no_elangles(self):        
    """
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