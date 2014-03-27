#############################################################################
### import
import flickrapi ###http://stuvel.eu/flickrapi
import xml.etree.ElementTree as ET
import urllib2

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import subprocess
import Image
from math import *
import os
import itertools
import random
#from termcolor import colored
import time
import subprocess
#############################################################################
############################################################################# ### declare global parameters here
###
np.set_printoptions(suppress=True);
np.set_printoptions(precision=4);
np.set_printoptions(threshold=np.nan);
np.set_printoptions(linewidth=500);
largenum = float(100000000);
smallnum = 1/largenum;
#############################################################################
############################################################################# ### declare functions here
def geoDistance(strlat1, strlon1, strlat2, strlon2):
    lat1 = float(strlat1);
    lon1 = float(strlon1);
    lat2 = float(strlat2);
    lon2 = float(strlon2);
    deg2rad = np.pi/180;
    rad2deg = 180/np.pi;
    if((lat1 == lat2) and (lon1 == lon2)):
        return 0;
    #endif
    distance = (np.sin(deg2rad*lat1) * np.sin(deg2rad*lat2)) + (np.cos(deg2rad*lat1) * np.cos(deg2rad*lat2) * np.cos(deg2rad*(lon1 - lon2)));
    distance = (rad2deg * (np.arccos(distance))) * 69.09 * 1.60934;
    distance = round(distance, 2);
    return distance;
#endfor
#############################################################################
##http://zips.sourceforge.net/
#def calcDist(strlat1, strlon1, strlat2, strlon2):
#    lat_A = float(strlat1);
#    long_A = float(strlon1);
#    lat_B = float(strlat2);
#    long_B = float(strlon2);
#    distance = (sin(radians(lat_A)) *
#                sin(radians(lat_B)) +
#                cos(radians(lat_A)) *
#                cos(radians(lat_B)) *
#                cos(radians(long_A - long_B)))
#    
#    distance = (degrees(acos(distance))) * 69.09
#    return distance
##enddef
#############################################################################
def myprint(a, verboselevel, color=""):
    if(verboselevel == 1):
        if(color == ""):
            print a;
        else:
            print colored(a, color);
        #endif
    #endif
#enddef
#############################################################################
#############################################################################

