# -*- coding: utf-8 -*-
import unittest
import env
import h5py
import hiisi
import numpy as np
import os

class Test(unittest.TestCase):
    
    def setUp(self):
        self.odim_file = hiisi.OdimPVOL('test_data/pvol.h5', 'r')
        
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
 
    def test_sector_valid_indexes(self):
        filedict = {'/dataset1/data1/data':{'DATASET':np.arange(10*10).reshape((10,10))},
                    '/dataset1/where':{'elangle':0.5, 'rscale':500},
                    '/dataset1/data1/what':{'quantity':'DBZH'}
                    }        
        
        with hiisi.OdimPVOL('test_pvol.h5', 'w') as pvol:
            pvol.create_from_filedict(filedict)
            pvol._set_elangles()
            pvol.select_dataset('A', 'DBZH')
            # Single ray slice
            np.testing.assert_array_equal(pvol.sector(0, 0), np.arange(10).reshape(1, 10)) 
            # Multiple rays slice
            np.testing.assert_array_equal(pvol.sector(0, 1), np.arange(20).reshape((2, 10)))
            # Multiple rays, start distance given
            comparison_array = np.array([[4,  5,  6,  7,  8,  9],
                                         [14, 15, 16, 17, 18, 19]])
            np.testing.assert_array_equal(pvol.sector(0, 1, 2000, units='m'), comparison_array)
            np.testing.assert_array_equal(pvol.sector(0, 1, 4), comparison_array)
            # Multiple rays, start and end distances given
            comparison_array = np.array([[4,  5,  6,  7],
                                         [14, 15, 16, 17]])
            np.testing.assert_array_equal(pvol.sector(0, 1, 2000, 4000, units='m'), comparison_array)
            np.testing.assert_array_equal(pvol.sector(0, 1, 4, 8), comparison_array)
            # Start slice bigger than end slice i.e. slice from 359->
            comparison_array = np.array([[80, 81, 82, 83, 84, 85, 86, 87, 88, 89],
                                         [90, 91, 92, 93, 94, 95, 96, 97, 98, 99],
                                            [ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9],
                                            [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]])

            np.testing.assert_array_equal(pvol.sector(8, 1), comparison_array)           
                        
            
    def test_sector_invalid_indexes(self):
        filedict = {'/dataset1/data1/data':{'DATASET':np.arange(10*10).reshape((10,10))},
                    '/dataset1/where':{'elangle':0.5, 'rscale':500},
                    '/dataset1/data1/what':{'quantity':'DBZH'}
                    }        
        
        with hiisi.OdimPVOL('test_pvol.h5', 'w') as pvol:
            pvol.create_from_filedict(filedict)
            pvol._set_elangles()
            pvol.select_dataset('A', 'DBZH')
            
            # 
    '''        
    def test_volume_slice(self):
        
        dataset1 = np.arange(10*10).reshape((10,10))
        dataset2 = np.arange(10*10).reshape((10,10))[:,:8] * 10
        dataset3 = np.arange(10*10).reshape((10,10))[:,:6] * 100
        
        layer1 = np.array([[ 0,  100,  200,  300,  400,  500],
                             [1000, 1100, 1200, 1300, 1400, 1500],
                            [2000, 2100, 2200, 2300, 2400, 2500],
                            [3000, 3100, 3200, 3300, 3400, 3500]])
        layer2 = np.array([[  0,  10,  20,  30,  40,  50],
                             [100, 110, 120, 130, 140, 150],
                            [200, 210, 220, 230, 240, 250],
                            [300, 310, 320, 330, 340, 350]]) 
        layer3 = np.array([[ 0,  1,  2,  3,  4,  5],
                             [10, 11, 12, 13, 14, 15],
                            [20, 21, 22, 23, 24, 25],
                            [30, 31, 32, 33, 34, 35]])
        comparison_array = np.dstack((layer1, layer2, layer3))
               
        filedict = {'/dataset1/data1/data':{'DATASET':dataset1},
                    '/dataset1/where':{'elangle':0.5, 'rscale':500},
                    '/dataset1/data1/what':{'quantity':'DBZH'},
                    '/dataset2/data1/data':{'DATASET':dataset2},
                    '/dataset2/where':{'elangle':0.7, 'rscale':500},
                    '/dataset2/data1/what':{'quantity':'DBZH'},
                    '/dataset3/data1/data':{'DATASET':dataset3},
                    '/dataset3/where':{'elangle':1.5, 'rscale':500},
                    '/dataset3/data1/what':{'quantity':'DBZH'},
                    }
        with hiisi.OdimPVOL('test_pvol.h5', 'w') as pvol:
            pvol.create_from_filedict(filedict)
            pvol._set_elangles()
            volume_slice = pvol.volume_slice('DBZH', 0, 3)
            np.testing.assert_array_equal(volume_slice, comparison_array)            
    '''                         
        
        
if __name__=='__main__':
    unittest.main()