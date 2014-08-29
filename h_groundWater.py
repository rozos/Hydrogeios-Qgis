from PyQt4 import QtGui
from qgis.core import *
import math
import itertools
import ftools_utils
import h_const
import h_utils



def layerNameTypesOK():
    if not h_utils.layerNameTypeOK(h_const.grdwatLayerName, 
                                   h_const.grdwatLayerType):
        return False
    if not h_utils.layerNameTypeOK(h_const.springLayerName, 
                                   h_const.springLayerType):
        return False
    if not h_utils.layerNameTypeOK(h_const.borehLayerName, 
                                   h_const.borehLayerType):
        return False 
    return True



def nameGroundwaterCells():
    """Writes to the field NAME of the attribute table of groundwater the name
    of each cell (Cell 0, Cell 1, ...)."""

    if addFieldToAttrTable(h_const.grdwatLayerName, h_const.grdwatFieldName,
                           QVariant.String)==None: return False 
    ncells=h_utils.getLayerFeaturesCount(h_const.grdwatLayerName)
    values=["Cell "+str(i) for i in range(ncells)]

    return h_utils.setFieldAttrValues(h_const.grdwatLayerName, 
                                      h_const.grdwatFieldName, values)



def distanceBetweenGroundwaterCells():
    """Calculates the distance between all centroids of all groundwater cells.
    Returns a list with three lists: the ids of from/to cells and their 
    distance."""

    centroids=getPolyLayerCentroids(h_const.grdwatLayerName)
    if not centroids: return False

    x,y = 0,1
    iNodes=[]
    jNodes=[]
    distances=[]
    for i in range(len(centroids)):
        for j in range(len(centroids)):
            iNodes.append(i)
            jNodes.append(j)
            distances.append(math.hypot(centroids[i][x]-centroids[j][x],
                                       centroids[i][y]-centroids[j][y]) )
    return (iNodes, jNodes, distances)



def edgeBetweenGroundwaterCells():
    """Calculates the common edge between all groundwater cells.
    Returns a list with three lists: the ids of from/to cells and lenght of
    their common edge."""
    
    polygons=getLayerFeatures(h_const.grdwatLayerName)
    if not polygons: return False

    iNodes=[]
    jNodes=[]
    commonEdge=[]
    for polygonPair in  itertools.combinations(polygons, 2):
        if polygonPair[0].intersects(polygonPair[1]):
            iNodes.append(polygonPair[0].id())
            jNodes.append(polygonPair[1].id())
            intersection=polygonPair[0].intersection(polygonPair[1])
            commonEdge.append(intersection.geom.length())

    return (iNodes, jNodes, commonEdge)



def linkSpringToGroundwater():
    """Add in the GROUND_ID field of Spring layer the ids of Groundwater cells 
    that correspond to each spring."""
    grdwaterIdList=linkPointLayerPolygonLayer(h_const.springLayerName, 
                                      h_const.grdwatLayerName)
    if not grdwaterIdList: return False

    return setFieldAttrValues(h_const.springLayerName, 
                              h_const.springFieldGroundId, grdwaterIdList)



def linkSpringToSubbasinr(): 
    """Add in the SUB_ID field of the Spring layer the ids of Subbasin polygons 
    that correspond to each spring."""
    subbasIdList=linkPointLayerPolygonLayer(h_const.springLayerName,
                                      h_const.subbasLayerName)
    if not subbasIdList: return False

    return setFieldAttrValues(h_const.springLayerName, 
                              h_const.springFieldSubbasId, subbasIdList)



def linkBoreholeToGroundwater():
    """Add in the GROUND_ID field of the Borehole layer the ids of the 
    Groundwater cells that correspond to each borehole."""
    pass



def linkBoreholeToSubbasin():
    """Add in the SUB_ID field of the Borehole layer the ids of the Subbasin
    polygons that correspond to each borehole."""
    pass
