from PyQt4 import QtGui
from qgis.core import *
import ftools_utils
import h_const
import h_utils


def layerNamesTypesOK():
    if not h_utils.layerNameTypeOK(h_const.groundLayerName, 
                                   h_const.groundLayerType):
        return False
    if not h_utils.layerNameTypeOK(h_const.subbasLayerName, 
                                   h_const.subbasLayerType):
        return False
    if not h_utils.layerNameTypeOK(h_const.riverLayerName, 
                                   h_const.riverLayerType):
        return False


def createSubbasinHRU():
    """Use Subbasin polygons to intersect the HRU polygons to create a new 
    layer that links Subbasin with HRU."""
    pass



def createHRU():
    pass
