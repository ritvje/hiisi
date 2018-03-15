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
    
    def getOperaComposite(self):
        return hiisi.OdimCOMP('test_data/T_PAAH21_C_EUOC_20160815114500.hdf', 'r')

    def tearDown(self):
        self.odim_file.close()
                    
    def test_select_dataset(self):
        self.assertEqual(self.odim_file.select_dataset('DBZH'), '/dataset1/data1/data')

    def test_select_dataset_no_dataset_found(self):
        self.assertIsNone(self.odim_file.select_dataset('NONEXISTING'))
        self.odim_file.select_dataset('DBZH')
        self.assertIsNone(self.odim_file.select_dataset('NONEXISTING'))

    def test_select_dataset_OPERA_composite(self):
        comp = self.getOperaComposite()
        dataset_path = comp.select_dataset('RATE')
        self.assertEqual(dataset_path, '/dataset1/data1/data')
        self.assertTrue(isinstance(comp[dataset_path], h5py.Dataset))
    
    def test_change_selected_dataset_OPERA_composite(self):
        comp = self.getOperaComposite()
        self.assertEqual(comp.select_dataset('RATE'), '/dataset1/data1/data')
        ds1 = comp.dataset[:]
        self.assertEqual(comp.select_dataset('QIND'), '/dataset2/data1/data')
        ds2 = comp.dataset[:]
        np.testing.assert_raises(AssertionError, np.testing.assert_array_equal, ds1, ds2)
        self.assertEqual(comp.select_dataset('RATE'), '/dataset1/data1/data')

    def test_select_dataset_no_dataset_found(self):
        comp = self.getOperaComposite()
        self.assertIsNone(comp.select_dataset('NONEXISTING'))
        comp.select_dataset('RATE')
        self.assertIsNone(comp.select_dataset('NONEXISTING'))

    def test_get_metadata_of_selected_dataset(self):
        comp = self.getOperaComposite()
        comp.select_dataset('RATE')
        self.assertEqual(comp.metadata['quantity'], 'RATE')
        comp.select_dataset('QIND')
        self.assertEqual(comp.metadata['quantity'], 'QIND')

if __name__=='__main__':
    unittest.main()
