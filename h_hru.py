from PyQt4 import QtGui
from qgis.core import *
import os.path
import ftools_utils
import h_const
import h_utils



def createSubbasinHRU():
    """Use Subbasin polygons to intersect the HRU polygons to create a new 
    layer that links Subbasin with HRU."""

    # Check Subbasin is loaded
    if not h_utils.layerNameTypeOK(h_const.subbasLayerName, 
                                   h_const.subbasLayerType): 
        return False

    # Add to the attr. table of Subbasin a field that keeps the polys' ids
    ok=h_utils.addShapeIdsToField(h_const.subbasLayerName, 
                                  h_const.subbasHRUFieldSubId) 
    if not ok: return False
    
    # Add to the attr. table of HRU a field that keeps the polys' ids
    ok=h_utils.addShapeIdsToField(h_const.HRULayerName, 
                                  h_const.subbasHRUFieldHRUId) 
    if not ok: return False

    # Delete existing shapefile SubGroundHRU
    h_utils.delExistingLayer( path, h_const.subbasHRULayerName)

    # Intersect Subbasin with HRU
    pathFilename=os.path.join( path, h_const.subbasHRULayerName)
    overlayAnalyzer = QgsOverlayAnalyzer()
    ok=overlayAnalyzer.intersection( h_const.subbasLayerName,
                                     h_const.HRULayerName, 
                                     pathFilename+".shp" )
    if not ok: return False

    # Update the area values of the SubbasinHRU polygons in the attr. table
    ok= addMeasureToAttrTable( h_const.subbasHRULayerName,
                               h_const.subbasHRULayerType,
                               h_const.subbasHRUFieldArea)
    return ok



def createHRU(path, HRUrasterName, bandnum, rangeUpVals):
    """Takes the HRU raster and creates a layer with multipolygon shapes.
    The classification into miltipolygon shapes is based on the provide 
    ranges."""

    # Reclassify HRUraster (id of CN classes instead of CN values)
    ok=h_utils.reclassifyRaster(path, HRUrasterName, bandnum, 0, rangeUpVals, 
                                h_const.HRUreclasLayerName)
    if not ok: 
        message=HRUrasterName+ "  reclassification failed!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    # Turn HRUraster into vector
    ok=h_utils.createVectorFromRaster(path, h_const.HRUreclasLayerName+'.tif', 
                                      1, h_const.HRULayerName)
    if not ok: 
        message="Creation of " + h_const.HRUreclasLayerName + " failed!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    # Load HRU shapefile
    pathFilename=os.path.join(path, h_const.HRULayerName)
    h_utils.loadShapefileToCanvas(pathFilename+".shp")

    return True
