# -*- coding: utf-8 -*-
import unittest
import env
import h5py
import hiisi
import numpy as np
import os

class Test(unittest.TestCase):
    
    def setUp(self):
        self.odim_file = hiisi.OdimCOMP('test_data/comp.h5', 'r')
        
    def tearDown(self):
        self.odim_file.close()
                    
    def test_select_dataset(self):
        self.assertEqual(self.odim_file.select_dataset('DBZH'), '/dataset1/data1/data')
        
    def test_select_dataset_no_dataset_found(self):
        self.assertIsNone(self.odim_file.select_dataset('NONEXISTING'))
 
        
if __name__=='__main__':
    unittest.main()
