from PyQt4 import QtGui
from qgis.core import *
#from qgis.analysis import QgsOverlayAnalyzer
import os.path
import h_geoprocess
import h_const
import h_utils



def createSubbasinHRU(path):
    """Use Subbasin polygons to intersect the HRU polygons to create a new
    layer that links Subbasin with HRU."""

    # Delete existing shapefile SubGroundHRU
    h_utils.unloadLayer(h_const.subbasHRULayerName)
    if h_utils.shapefileExists(path, h_const.subbasHRULayerName):
        ok=h_utils.delExistingShapefile( path, h_const.subbasHRULayerName)
        if not ok: return False

    # Check Subbasin and HRU are loaded and get their layers
    if not h_utils.layerNameTypeOK(h_const.subbasLayerName,
                                   h_const.subbasLayerType) or \
       not h_utils.layerNameTypeOK(h_const.HRULayerName,
                                   h_const.HRULayerType):
        return False
    subbasLayer=ftools_utils.getVectorLayerByName(h_const.subbasLayerName)
    HRULayer=ftools_utils.getVectorLayerByName(h_const.HRULayerName)

    # Intersect Subbasin with HRU
    ok = h_geoprocess.intersect( path, h_const.subbasLayerName, 
                                 h_const.HRULayerName,
                                 h_const.subbasHRULayerName)
    if not ok: return False

    # Load SubbasinHRU
    h_utils.loadShapefileToCanvas(path, h_const.subbasHRULayerName + ".shp")

    # Update the area values of the SubbasinHRU polygons in the attr. table
    ok= h_utils.addMeasureToAttrTable( h_const.subbasHRULayerName,
                                       h_const.subbasHRUFieldArea)
    return ok



def createHRU(path, CNrasterName, bandnum, rangeUpVals):
    """Takes the HRU raster and creates a layer with multipolygon shapes.
    The classification into miltipolygon shapes is based on the provide
    ranges."""

    # Reclassify CNraster (id of CN classes instead of CN values)
    if h_utils.isShapefileLoaded(h_const.HRULayerName):
	h_utils.unloadLayer(h_const.HRULayerName)
    ok=h_utils.reclassifyRaster(path, CNrasterName, bandnum, 0, rangeUpVals,
                                h_const.HRUrasterLayerName)
    if not ok:
        message=CNrasterName+ "  reclassification failed!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    # Turn HRUraster into vector
    ok=h_utils.createVectorFromRaster(path, h_const.HRUrasterLayerName+'.tif',
                                      1, h_const.HRULayerName)
    if not ok:
        message="Creation of " + h_const.HRUrasterLayerName + " failed!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    # Load HRU shapefile
    h_utils.loadShapefileToCanvas(path, h_const.HRULayerName + ".shp")

    # Delete pogyons generated from non-data pixels
    filterExpr=h_const.HRUFieldId + "<0"
    listIds=h_utils.getQueryShapeIds(h_const.HRULayerName, filterExpr)
    if not listIds: return False
    if listIds!=[]:
        ok=h_utils.delSpecificShapes(h_const.HRULayerName, listIds)
        if not ok: return False

    return True
