# -*- coding: utf-8 -*-
import os.path
from hiisi import HiisiHDF
from odim import OdimPVOL, OdimCOMP
from pkg_resources import get_distribution, DistributionNotFound
__version__ = get_distribution('hiisi').version

try:
    _dist = get_distribution('hiisi')
    # Normalize case for Windows systems
    dist_loc = os.path.normcase(_dist.location)
    here = os.path.normcase(__file__)
    if not here.startswith(os.path.join(dist_loc, 'hiisi')):
        # not installed, but there is another version that *is*
        raise DistributionNotFound
except DistributionNotFound:
    __version__ = 'Please install this project with setup.py'
else:
    __version__ = _dist.version
