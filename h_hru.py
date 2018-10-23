from PyQt5 import QtGui
from qgis.core import *
import os.path
import processing
import h_const
import h_utils
import h_initLayers


def doAll(path, CNrasterName, bandnum, tupleUpValues):
    """This function that calls all functions related to HRUs."""
    if not createHRU(path, CNrasterName, bandnum, tupleUpValues):
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



def createHRU(path, CNrasterName, bandnum, tupleUpValues):
    """Takes the HRU raster and creates a layer with multipolygon shapes.
    The classification into miltipolygon shapes is based on the provided
    ranges."""

    # Unload HRU
    HRULayerName=h_const.HRULayerName
    HRUunfixedLayerName=HRULayerName+'_u'
    h_utils.unloadShapefile(HRULayerName)
    h_utils.unloadShapefile(HRUunfixedLayerName)

    # Reclassify CNraster (id of CN classes instead of CN values)
    ok=h_utils.reclassifyRaster(path, CNrasterName, bandnum, 0, tupleUpValues,
                                h_const.HRUrasterLayerName)
#   CHECK WHAT HAPPENS WHEN PROVIDED tupleUpValues ARE OUTSIDE CN VALUES !!!
    if not ok:
        message=CNrasterName+ "  reclassification failed!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    # Turn HRUraster into vector
    ok=h_utils.createVectorFromRaster(path,h_const.HRUrasterLayerName+'.tif',1,
                                      HRUunfixedLayerName, h_const.HRUFieldId)
    if not ok:
        message="Creation of " + h_const.HRUrasterLayerName + " failed!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    # Fix HRU_u (unfixed)
    hrulayerpath=os.path.join(projectpath, HRULayerName+".shp")
    hruUnfixedlayerpath=os.path.join(projectpath, HRUunfixedLayerName+".shp")
    try:
        processing.run('qgis:fixgeometries', { 'INPUT': hruUnfixedlayerpath,
                       'OUTPUT': hrulayerpath} )
    except Exception as e:
        print(str(e))
        return False


    # Load undissolved HRU shapefile created from HRUraster
    h_utils.loadShapefileToCanvas(path, HRULayerName)

    # Delete pogyons generated from non-data pixels
    filterExpr=h_const.HRUFieldId+ "<0"
    listIds=h_utils.getQueryShapeIds(HRULayerName, filterExpr)
    if listIds==False:
        message="Delete non-data of " + HRULayerName+ " failed!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False
    if listIds!=[]:
        ok=h_utils.delSpecificShapes(HRULayerName, listIds)
        if not ok: return False

    return True
