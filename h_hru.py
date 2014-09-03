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



def createHRU(path, HRUraster, rangeUpVals):
    """Takes the HRU raster and creates a layer with multipolygon shapes.
    The classification into miltipolygon shapes is based on the provide 
    ranges."""

    # Del the existing (if any) output shapefile
    ok=h_utils.delExistingShapefile(path, HRULayerName)
    if not ok: return False

    # Reclassify HRUraster (id of CN classes instead of CN values)
    reclassifyRaster(path, HRUraster, band, rangeUpVals, h_const.HRUreclasName)

    # Turn HRUraster into vector
    ok=h_utils.createVectorFromRaster(path, h_const.HRUreclasName, 1, 
                                      h_const.HRULayerName)
    # Load HRU shapefile
    pathFilename=os.path.join(path, h_const.HRULayerName)
    h_utils.loadShapefileToCanvas(pathFilename+".shp")

    return ok
