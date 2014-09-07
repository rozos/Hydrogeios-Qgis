from PyQt4 import QtGui
from PyQt4.QtCore import QVariant
from qgis.core import *
import math
import itertools
import ftools_utils
import h_const
import h_utils
import h_geoprocess



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
    if not h_utils.layerNameTypeOK(h_const.riverLayerName, 
                                   h_const.riverLayerType):
        return False
    return True



def nameGroundwaterCells():
    """Writes to the field NAME of the attribute table of groundwater the name
    of each cell (Cell 0, Cell 1, ...)."""

    if h_utils.addFieldToAttrTable(h_const.grdwatLayerName, 
                               h_const.grdwatFieldName, QVariant.String)==None:
        return False 
    ncells=h_utils.getLayerFeaturesCount(h_const.grdwatLayerName)
    values=["Cell "+str(i) for i in range(ncells)]

    return h_utils.setFieldAttrValues(h_const.grdwatLayerName, 
                                      h_const.grdwatFieldName, values)



def distanceBetweenGroundwaterCells():
    """Calculates the distance between all centroids of all groundwater cells.
    Returns a list with three lists: the ids of from/to cells and their 
    distance."""

    centroids=h_utils.getPolyLayerCentroids(h_const.grdwatLayerName)
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
    
    polygons=h_utils.getLayerFeatures(h_const.grdwatLayerName)
    if not polygons: return False

    iNodes=[]
    jNodes=[]
    commonEdge=[]
    for polygonPair in  itertools.combinations(polygons, 2):
        geometryApolygon=polygonPair[0].geometry()
        geometryBpolygon=polygonPair[1].geometry()
        if geometryApolygon.intersects(geometryBpolygon):
            iNodes.append(polygonPair[0].id())
            jNodes.append(polygonPair[1].id())
            intersection=geometryApolygon.intersection(geometryBpolygon)
            commonEdge.append(intersection.length())

    return (iNodes, jNodes, commonEdge)



def linkSpringToGroundwater():
    """Add in the GROUND_ID field of Spring layer the ids of Groundwater cells 
    that correspond to each spring."""
    grdwaterIdList=h_utils.linkPointLayerToPolygonLayer(h_const.springLayerName,
                                      h_const.grdwatLayerName)
    if not grdwaterIdList: return False

    return h_utils.setFieldAttrValues(h_const.springLayerName, 
                              h_const.grdwatFieldId, grdwaterIdList)



def linkSpringToSubbasin(): 
    """Add in the SUB_ID field of the Spring layer the ids of Subbasin polygons 
    that correspond to each spring."""
    subbasIdList=h_utils.linkPointLayerToPolygonLayer(h_const.springLayerName,
                                      h_const.subbasLayerName)
    if not subbasIdList: return False

    return h_utils.setFieldAttrValues(h_const.springLayerName, 
                              h_const.subbasFieldId, subbasIdList)



def linkBoreholeToGroundwater():
    """Add in the GROUND_ID field of the Borehole layer the ids of the 
    Groundwater cells that correspond to each borehole."""
    grdwaterIdList=h_utils.linkPointLayerToPolygonLayer(h_const.borehLayerName, 
                                      h_const.grdwatLayerName)
    if not grdwaterIdList: return False

    return h_utils.setFieldAttrValues(h_const.borehLayerName, 
                              h_const.grdwatFieldId, grdwaterIdList)



def linkBoreholeToSubbasin():
    """Add in the SUB_ID field of the Borehole layer the ids of the Subbasin
    polygons that correspond to each borehole."""
    subbasIdList=h_utils.linkPointLayerToPolygonLayer(h_const.borehLayerName,
                                      h_const.subbasLayerName)
    if not subbasIdList: return False

    return h_utils.setFieldAttrValues(h_const.borehLayerName, 
                              h_const.borehFieldSubbasId, subbasIdList)



def createRiverGroundwater(path):
    """Use groundwater cells to clip the river segments to create a new layer
    that links River with Groundwater."""

    # Add to the attr. table of Groundwater a field that keeps the cells id
    ok=h_utils.addShapeIdsToField(h_const.grdwatLayerName, 
                                  h_const.grdwatFieldId) 
    if not ok: return False

    # Add to the attr. table of River a field that keeps the segments id
    ok=h_utils.addShapeIdsToField(h_const.riverLayerName, 
                                  h_const.riverFieldId)
    if not ok: return False

    # Delete existing shapefile
    h_utils.unloadLayer(h_const.riverGrdwatLayerName)
    if h_utils.shapefileExists(path, h_const.riverGrdwatLayerName ):
        ok=h_utils.delExistingShapefile( path, h_const.riverGrdwatLayerName )
        if not ok: return False

    # Intersect river with Groundwater
    ok=h_geoprocess.intersect( path, h_const.riverLayerName, 
                               h_const.grdwatLayerName, 
                               h_const.riverGrdwatLayerName )
    if not ok: return False

    # Load RiverGroundwater
    h_utils.loadShapefileToCanvas(path, h_const.riverGrdwatLayerName+ ".shp")

    # Update the length of the segments to the RiverGroundwater attr. table 
    ok= h_utils.addMeasureToAttrTable( h_const.riverGrdwatLayerName,
                                       h_const.riverGrdwatFieldLength )

    return ok
    
    

def createGroundwaterSubbasinHRU(path):
    """Use groundwater cells to intersect the subbasinHRU polygons to create a 
    new layer (SubGroundHRU) that links Groundwater with Subbasin-HRU ."""

    # Add to the attr. table of Groundwater a field that keeps the cells id
    ok=h_utils.addShapeIdsToField(h_const.grdwatLayerName, 
                                 h_const.grdwatFieldId) 
    if not ok: return False

    # Delete existing shapefile SubGroundHRU
    h_utils.unloadLayer(h_const.grdwatSubbasHRULayerName)
    if h_utils.shapefileExists(path, h_const.grdwatSubbasHRULayerName):
       ok=h_utils.delExistingShapefile( path, h_const.grdwatSubbasHRULayerName )
       if not ok: return False

    # Intersect Groundwater with SubbasinHRU
    ok=h_geoprocess.intersect( path, h_const.grdwatLayerName, 
                               h_const.subbasHRULayerName, 
                               h_const.grdwatSubbasHRULayerName)
    if not ok: return False

    # Load RiverGroundwater
    h_utils.loadShapefileToCanvas(path, h_const.grdwatSubbasHRULayerName+".shp")

    # Update the area values of the SubGroundHRU polygons in the attr. table
    ok= h_utils.addMeasureToAttrTable( h_const.grdwatSubbasHRULayerName,
                                       h_const.grdwatSubbasHRUFieldArea)
    return ok
