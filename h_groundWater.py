from PyQt4 import QtGui
from qgis.core import *
import ftools_utils
import h_const
import h_utils



def nameGroundwaterCells():
    """Writes to the field NAME of the attribute table of groundwater the name
    of each cell (Cell 0, Cell 1, ...)."""
    pass



def distanceBetweenGroundwaterCells():
    """Calculates the distance between all centroids of all groundWater cells.
    Returns a list with three lists: the ids of from/to cells and their 
    distance."""
    pass



def edgeBetweenGroundwaterCells():
    """Calculates the common edge between all groundWater cells.
    Returns a list with three lists: the ids of from/to cells and lenght of
    their common edge."""
    pass



def linkPolygonLayerToPointLayer(polyLayername, pointLayername, idfield): 
    """Find the polygons of the polyLayername to which each point of 
    pointLayername corresponds to. Write to the idfield of pointLayerName 
    attribute table the id of the corresponding polygon"""
    pass
