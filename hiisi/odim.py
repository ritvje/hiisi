# -*- coding: utf-8 -*-
from hiisi import HiisiHDF
import h5py
import numpy as np
import re
import os
import string
"""
Odim is a module for handling radar data files that follow OPERA ODIM data scheme
More information about the Odim data scheme can be found:
http://www.eumetnet.eu/sites/default/files/OPERA2014_O4_ODIM_H5-v2.2.pdf
"""

class OdimPVOL(HiisiHDF):
    """
    Container for odim polar volumes    
    """
    def __init__(self, *args, **kwargs):
        super(OdimPVOL, self).__init__(*args, **kwargs)
        #if self.get_attr('product') != 'PVOL':
        #    raise Warning('The type of hdf5 file is not PVOL')
        self.elangles = {}
        self.quantities = []
        self.dataset = None
        try:
            self._set_elangles()
        except:
            pass

    @property
    def dataset(self):        
        return self[self._dataset][:]

    @dataset.setter
    def dataset(self, value):
        self._dataset = value
        
    def _set_elangles(self):
        """Sets the values of instance variable elangles.
        
        Method analyses the loaded file and checks what elevation angles it
        contains. Method creates a dictionary that contains uppercase letters
        as keys and elevation angles as values in acending order
        i.e. elagles={'A':0.3, 'B':0.5, C:'0.7', ...}
        """
        elevation_angles = self.get_attrs('elangle')
        elevation_angles = sorted(zip(*elevation_angles)[1])
        n_elangles = len(elevation_angles)
        self.elangles = dict(zip(list(string.ascii_uppercase[:n_elangles]), elevation_angles))
        
    def select_dataset(self, elangle, quantity):
        """
        Selects the matching dataset and returns its path.
        
        Parameters
        ----------
        elangle : str
            Upper case ascii letter defining the elevation angle
        quantity : str
            Name of the quantity e.g. DBZH, VRAD, RHOHV...
            
        Returns
        -------
        dataset : str
            Path of the matching dataset
            
        Examples
        --------
        Get the hdf5 path of the DBZH dataset at lowest elevation angle
        
        >>> pvol = odimPVOL('pvol.h5')
        >>> dataset = pvol.select_dataset('A', 'DBZH')
        >>> print(dataset)
        '/dataset1/data1/data'

        """
        elangle_path = None
        for x in self.get_attrs('elangle'):
            if x[1] == self.elangles[elangle]:
                elangle_path = x[0] 
                break
            
        if elangle_path is not None:
            dataset_root = re.search( '^/dataset[0-9]+/', elangle_path).group(0)
            
            quantity_path = None
            for x in self.get_attrs('quantity'):
                if x[1] == quantity:
                    if dataset_root in x[0]:
                        quantity_path = x[0]
                        break
                    
            if quantity_path is not None:
                dataset_path = re.search('^/dataset[0-9]+/data[0-9]/', quantity_path).group(0)            
                dataset_path = os.path.join(dataset_path, 'data')
                if isinstance(self[dataset_path], h5py.Dataset):
                    self.dataset = self[dataset_path].ref
                    return dataset_path
    
    def sector(self, start_ray, end_ray=None, start_distance=None, end_distance=None):
        """Slices a sector from selected dataset
        
        Parameters
        ----------
        start_ray : int
            Starting ray of of the slice first ray i 0
            
        Keywords
        --------
        end_ray : int
            End ray of the slice, if not given the slice is single ray
            
        start_distance : int
            Starting distance of the slice, if not defined sector starts form zero
        end_distance : int
            Ending distance of the slice, if not defined sector continues to the end
        Returns
        -------
        sector : ndarray
            Numpy array containing the sector values
            
        Examples
        --------
        Get one ray from the selected dataset
        
        >>> pvol = odimPVOL('pvol.h5')
        >>> pvol.select_dataset('A', 'DBZH')
        >>> ray = pvol.sector(10)

        Get sector from selected dataset, rays from 100 to 200
        at distances from 5 km to 10 km.
        
        >>> pvol = odimPVOL('pvol.h5')
        >>> pvol.select_dataset('A', 'DBZH')
        >>> sector = pvol.sector(100, 200, 5000, 10000)                
        """
        if self.dataset is None:
            raise ValueError('Dataset is not selected')

        # Validate parameter values        
        ray_max, distance_max = self.dataset.shape
        if start_ray > ray_max:
            raise ValueError('Value of start_ray is bigger than the number of rays')
        if start_ray < 0:
            raise ValueError('start_ray must be non negative')
            
        # Define the slicing indexes along the ray
        rscale = self.get_attr('rscale')
        if start_distance is None:
            start_index = 0
        else:
            start_index = int(start_distance / rscale)
        if end_distance is None:
            end_index = self.dataset.shape[1]
        else:
            end_index = int(end_distance / rscale) 
        
        if end_ray is None:
            sector = self.dataset[start_ray, start_index:end_index]
        else:
            if start_ray < end_ray:
                sector = self.dataset[start_ray:end_ray, start_index:end_index]
            else:
                sector1 = self.dataset[start_ray:, start_index:end_index]
                sector2 = self.dataset[:end_ray, start_index:end_index]
                sector = np.concatenate((sector1, sector2), axis=0)
        return sector
        
    def sub_volume(self, quantity, start_ray, end_ray, start_distance=None, end_distance=None, elangles=[]):
        """Slices a sub volume from the file
        
        Parameters
        ----------
        quantity : str
            sliced quantity
        start_ray : int
            starting ray of the sub volume
            
        Keywords
        --------
        end_ray : int
            ending ray of the sub volume
        start_distance : int
            start distance from the radar in meters
        end_distance : int 
            end distance from the radar in meters
        elangles : list
            list of elangles included in slicing, if left empty all the angles
            are included.
            
        Examples
        --------
        Get subvolume containing all the datapoints between rays 10 and 20 at
        all elevation angles
        
        >>> pvol = odimPVOL('pvol.h5')
        >>> pvol.sub_volume('DBZH', 10, 20)

        Get subvolume containing the datapoints between rays 10 and 20 from
        distances 5 km to 10 km at first two elevation angles
        
        >>> pvol = odimPVOL('pvol.h5')
        >>> pvol.sub_volume('DBZH', 10, 20, 5000, 10000, ['A', 'B'])
        
        """
        # Elangles are traversed from highest angle to lowest
        # and the size of the highest angle is used as limiting factor for the 
        # along the ray
        if elangles == []:
            elangles = self.elangles.keys()
        
        elangles = reversed(elangles)            
        self.select_dataset(elangles.next(), quantity)
        sub_volume = self.sector(start_ray, end_ray, start_distance, end_distance)

        height, width = sub_volume.shape
        
        for elangle in elangles:
            self.select_dataset(elangle, quantity)
            layer = self.sector(start_ray, end_ray, start_distance, end_distance)
            
            sub_volume = np.dstack((sub_volume, layer))
    
        return sub_volume


class OdimCOMP(HiisiHDF):
    """
    Container class for odim composite files
    """
    def __init__(self, *args, **kwargs):
        super(OdimCOMP, self).__init__(*args, **kwargs)            
        if self.get_attr('object') != 'COMP':
            raise ValueError('Given data file is not ODIM composite')
        self._dataset = None
        
    @property
    def dataset(self):        
        return self[self._dataset][:]

    @dataset.setter
    def dataset(self, value):
        self._dataset = value
    
    def select_dataset(self, quantity):
        """
        Selects the matching dataset and returns its path.
        
        Parameters
        ----------
        quantity : str
            name of the quantity
            
        Examples
        --------
        Select DBZH composite        
        
        >>> comp = OdimCOMP('comp.h5')
        >>> dataset = comp.select_dataset('DBZH')
        >>> print(dataset)
        >>> '/dataset1/data1/data'
        
        """
        quantity_path = None
        for x in self.get_attrs('quantity'):
            if x[1] == quantity:
                quantity_path = x[0]
        
        if quantity_path is not None:
            dataset_path = re.search( '^/dataset[0-9]+/data[0-9]+/', quantity_path).group(0)
            dataset_path = os.path.join(dataset_path, 'data')   
            if isinstance(self[dataset_path], h5py.Dataset):
                self.dataset = self[dataset_path].ref
                return dataset_path        
                     
                     
class OdimVPR(HiisiHDF):
    """
    Container class for odim vpr files
    """
    #TODO: implementation
    def __init__(self, *args, **kwargs):
        super(OdimVPR, self).__init__(*args, **kwargs)            
        if self.get_attr('object') != 'VPR':
            raise ValueError('Given data file is not VPR composite')
        self._dataset = None


class OdimRHI(HiisiHDF):
    """
    Container class for odim rhi files
    """
    #TODO: implementation
    def __init__(self, *args, **kwargs):
        super(OdimRHI, self).__init__(*args, **kwargs)            
        if self.get_attr('object') != 'RHI':
            raise ValueError('Given data file is not RHI composite')
        self._dataset = None
    

            