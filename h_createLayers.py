from PyQt4 import QtGui
from qgis.core import *
import os.path
import ftools_utils
import h_const
import h_utils
import h_surface



def createOutletsLayer(path):
    """ Create a new point layer with the end nodes of the rivers segments."""

    # Get outlets of river segments
    riverSegments= h_utils.getLayerFeatures(h_const.riverLayerName)
    if not riverSegments: return False
    (endPntXs,endPntYs)= h_surface.getRiverJunctions(riverSegments)

    coordinates=zip(endPntXs, endPntYs)
    ok= h_utils.createPointLayer(path, h_const.outletLayerName, coordinates,
                          h_const.outletFieldNames, h_const.outletFieldTypes,
                          (endPntXs, endPntYs) )
    if not ok: return False

    # Make sure the layer is loaded 
    if not h_utils.isShapefileLoaded(h_const.outletLayerName):
        ok=h_utils.loadShapefileToCanvas(path, h_const.outletLayerName+".shp")

    return ok



def initializeLayer(path, layerName, layerType, fieldNames, fieldTypes):
    """Create a new empty layer with the given fields in attribute table or
    (if already there) make sure the attribute table has all required fields"""

    # If layer does not exist create one
    if not h_utils.shapefileExists(path, layerName): 
        # Initialize the list with name/type of attribute table fields
        fieldList = QgsFields()
        for fieldname,fieldtype in zip(fieldNames, fieldTypes):
            fieldList.append(QgsField(fieldname,fieldtype) )
        # Create an empty layer
        pathFilename=os.path.join(path, layerName)
        writer= QgsVectorFileWriter(pathFilename, "utf8", fieldList,
                                    layerType, None, "ESRI Shapefile")
        if writer.hasError() != QgsVectorFileWriter.NoError:
            message="Error creating shapefile "+filename
            QtGui.QMessageBox.critical(None,'Error',message,
                                       QtGui.QMessageBox.Ok)
            return False
        # Delete the writer to flush features to disk (optional)
        del writer

    # Make sure the layer is loaded
    layer=ftools_utils.getVectorLayerByName(layerName)
    if not layer:
        if not h_utils.loadShapefileToCanvas(path, layerName+".shp"):
            return False

    # Make sure all required fields are there
    res=True
    for fieldname,fieldtype in zip(fieldNames, fieldTypes):
        fieldIndex=h_utils.addFieldToAttrTable(layerName, fieldname, fieldtype)
        if fieldIndex==None:
            res=False
            break

    return res



def initIrrigLayer(path):
    """Initialize irrigation layer"""

    # Initialize layer
    ok= initializeLayer(path, h_const.irrigLayerName, h_const.irrigGeomType,
                       h_const.irrigFieldNames, h_const.irrigFieldTypes)
    if not ok: return False

    return True



def initSubbasinLayer(path):
    """Initialize subbasin layer"""

    # Initialize layer
    ok= initializeLayer(path, h_const.subbasLayerName, h_const.subbasGeomType,
                       h_const.subbasFieldNames, h_const.subbasFieldTypes)
    if not ok: return False

    # Add area of polygons to attribute table
    fieldIndex= h_utils.addMeasureToAttrTable(h_const.subbasLayerName, 
                                      h_const.subbasFieldArea)
    if fieldIndex==None: return False

    # Get centroids
    centroids=h_utils.getPolyLayerCentroids(h_const.subbasLayerName)
    if centroids==None: return False

    # Add coordinates of polygon centroids to attribute table
    xCoord=[]
    yCoord=[]
    for (x,y) in centroids:
        xCoord.append(x)
        yCoord.append(y)
    ok= h_utils.setFieldAttrValues(h_const.subbasLayerName,
                                   h_const.subbasFieldX, xCoord);
    if not ok: return False
    ok=h_utils.setFieldAttrValues(h_const.subbasLayerName,
                                   h_const.subbasFieldY, yCoord);
    if not ok: return False

    return True



def initGrdWatLayer(path):
    """Initialize groundwater layer"""
    ok= initializeLayer(path, h_const.grdwatLayerName, h_const.grdwatLayerType,
                       h_const.grdwatFieldNames, h_const.grdwatFieldTypes)
    if not ok: return False
    return True



def initSpringLayer(path):
    """Initialize spring layer"""
    ok= initializeLayer(path, h_const.springLayerName, h_const.springLayerType,
                       h_const.springFieldNames, h_const.springFieldTypes)
    if not ok: return False
    return True



def initBorehLayer(path):
    """Initialize boreholes layer"""
    ok= initializeLayer(path, h_const.borehLayerName, h_const.borehLayerType,
                       h_const.borehFieldNames, h_const.borehFieldTypes)
    if not ok: return False
    return True



def initRiverLayer(path):
    """Initialize river layer"""
    ok= initializeLayer(path, h_const.riverLayerName, h_const.riverLayerType,
                       h_const.riverFieldNames, h_const.riverFieldTypes)
    if not ok: return False 
    return True
