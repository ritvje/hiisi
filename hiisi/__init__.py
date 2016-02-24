# -*- coding: utf-8 -*-
import os.path
from hiisi import HiisiHDF
from odim import OdimPVOL, OdimCOMP
with open(os.path.join('hiisi','VERSION')) as version_file:
    __version__ = version_file.read().strip()