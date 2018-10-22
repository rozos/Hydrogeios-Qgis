from PyQt5 import QtGui
from qgis.core import *
#from qgis.analysis import QgsOverlayAnalyzer
import os.path
import processing
import h_const
import h_utils
import h_initLayers


def doAll(path, CNrasterName, bandnum, rangeUpVals):
    """This function that calls all functions related to HRUs."""
    if not createHRU(path, CNrasterName, bandnum, rangeUpVals):
        message="createHRU Failed. Continue?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No )
        if reply==QtGui.QMessageBox.No: return False
    if not createSubbasinHRU(path):
        message="createSubbasinHRU Failed. Continue?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No )
        if reply==QtGui.QMessageBox.No: return False

    return True



def createSubbasinHRU(projectpath):
    """Use Subbasin polygons to intersect the HRU polygons to create a new
    layer that links Subbasin with HRU."""

    # Delete existing shapefile SubbasinHRU
    h_utils.unloadShapefile(h_const.subbasHRULayerName)
    if h_utils.shapefileExists(projectpath, h_const.subbasHRULayerName):
        ok=h_utils.delExistingShapefile(projectpath, h_const.subbasHRULayerName)
        if not ok: return False

    # Check Subbasin and HRU types
    if not h_utils.layerNameTypeOK(h_const.subbasLayerName,
                                   h_const.subbasGeomType) or \
       not h_utils.layerNameTypeOK(h_const.HRULayerName,
                                   h_const.HRUGeomType):
        return False

    # Fix HRU geometries
    hrulayername=os.path.join(projectpath, h_const.HRULayerName+".shp")
    hrufixedlayername=os.path.join(projectpath, "HRU_f.shp")
    try:
        processing.run('qgis:fixgeometries', { 'INPUT': hrulayername,
                       'OUTPUT': hrufixedlayername } )
    except Exception as e:
        print(str(e))
        return False

    # Intersect Subbasin with HRU
    subbasinlayername=os.path.join(projectpath, h_const.subbasLayerName+".shp")
    outlayername=os.path.join(projectpath, h_const.subbasHRULayerName+".shp")
    try:
        processing.run('qgis:intersection', { 'INPUT': subbasinlayername,
                       'INPUT_FIELDS': [], 'OUTPUT': outlayername,
                       'OVERLAY': hrufixedlayername, 'OVERLAY_FIELDS': [] } )
    except Exception as e:
        print(str(e))
        return False

    # Update the area values of the SubbasinHRU polygons in the attr. table
    h_utils.loadShapefileToCanvas(projectpath, h_const.subbasHRULayerName)
    ok= h_utils.addMeasureToAttrTable( h_const.subbasHRULayerName,
                                       h_const.subbasHRUFieldArea)
    h_utils.unloadShapefile(h_const.subbasHRULayerName)

    return ok



def createHRU(path, CNrasterName, bandnum, rangeUpVals):
    """Takes the HRU raster and creates a layer with multipolygon shapes.
    The classification into miltipolygon shapes is based on the provided
    ranges."""

    # Unload HRU and HRUundis
    #HRUundLayerName=h_const.HRULayerName+"_undis"
    HRUundLayerName=h_const.HRULayerName
    h_utils.unloadShapefile(HRUundLayerName)
    #h_utils.unloadShapefile(h_const.HRULayerName)

    # Reclassify CNraster (id of CN classes instead of CN values)
    ok=h_utils.reclassifyRaster(path, CNrasterName, bandnum, 0, rangeUpVals,
                                h_const.HRUrasterLayerName)
#   CHECK WHAT HAPPENS WHEN PROVIDED rangeUpVals ARE OUTSIDE CN VALUES !!!
    if not ok:
        message=CNrasterName+ "  reclassification failed!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    # Turn HRUraster into vector
    ok=h_utils.createVectorFromRaster(path,h_const.HRUrasterLayerName+'.tif',1,
                                      HRUundLayerName, h_const.HRUundisFieldId)
    if not ok:
        message="Creation of " + h_const.HRUrasterLayerName + " failed!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    # Load undissolved HRU shapefile created from HRUraster
    h_utils.loadShapefileToCanvas(path, HRUundLayerName)

    # Delete pogyons generated from non-data pixels
    filterExpr=h_const.HRUundisFieldId+ "<0"
    listIds=h_utils.getQueryShapeIds(HRUundLayerName, filterExpr)
    if listIds==False:
        message="Delete non-data of " + HRUundLayerName+ " failed!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False
    if listIds!=[]:
        ok=h_utils.delSpecificShapes(HRUundLayerName, listIds)
        if not ok: return False

    # Dissolve undissolved HRU layer
    #ok=geoprocess.dissolve(path, HRUundLayerName, h_const.HRULayerName,
    #                       useField=h_const.HRUFieldId)
    #if not ok:
    #    message="Dissolving of " + h_const.HRUundLayerName+ " failed!"
    #    QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
    #    return False

    # Initialize dissolved HRU layer
    #ok=h_initLayers.initializeLayer(path, h_const.HRULayerName, 
    #        h_const.HRULayerType, h_const.HRUFieldNames, h_const.HRUFieldTypes)
    #if not ok: return False

    # Unload undissolved HRU layer
    #h_utils.unloadShapefile(HRUundLayerName)

    # Add area to HRU attribute table
    #ok=h_utils.addMeasureToAttrTable(h_const.HRULayerName,h_const.HRUFieldArea)
    #if not ok: return False

    # Add HRU id to attribute table
    #ok=h_utils.addShapeIdsToAttrTable(h_const.HRULayerName, h_const.HRUFieldId)
    #if not ok: return False

    return True
