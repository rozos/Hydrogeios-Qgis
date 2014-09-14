from PyQt4 import QtGui
from qgis.core import *
import os.path
import ftools_utils
import h_const
import h_utils
import h_surface




def doAll(path):
    """Calls all functions that create/initialize the layers of a Hydrogeios 
    Project."""
    if not initIrrigLayer(path):
        message="initIrrigLayer Failed. Continue?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No )
        if reply==QtGui.QMessageBox.No: return False
    if not initSubbasinLayer(path):
        message="initSubbasinLayer Failed. Continue?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No )
        if reply==QtGui.QMessageBox.No: return False
    if not h_utils.addShapeIdsToAttrTable(h_const.subbasLayerName,
                                          h_const.subbasFieldId)
        message="addSubbasinId Failed. Continue?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No )
        if reply==QtGui.QMessageBox.No: return False
    if not initGrdWatLayer(path):
        message="initGrdWatLayer Failed. Continue?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No )
        if reply==QtGui.QMessageBox.No: return False
    if not initSpringLayer(path):
        message="initSpringLayer Failed. Continue?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No )
        if reply==QtGui.QMessageBox.No: return False
    if not initBorehLayer(path):
        message="initBorehLayer Failed. Continue?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No )
        if reply==QtGui.QMessageBox.No: return False
    if not initRiverLayer(path):
        message="initRiverLayer Failed. Continue?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No )
        if reply==QtGui.QMessageBox.No: return False
    if not linkSubbasinRiver():
        message="linkSubbasinRiver Failed. Continue?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No )
        if reply==QtGui.QMessageBox.No: return False
    if not initAqueductLayer(path):
        message="initAqueductLayer Failed. Continue?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No )
        if reply==QtGui.QMessageBox.No: return False

    return True



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
    for fieldname,fieldtype in zip(fieldNames, fieldTypes):
        fieldIndex=h_utils.addFieldToAttrTable(layerName, fieldname, fieldtype)
        if fieldIndex==None:
            return False

    # Make sure the layer is loaded 
    ok=True
    if not h_utils.isShapefileLoaded(layerName):
        ok=h_utils.loadShapefileToCanvas(path, layerName+".shp")

    return ok



def createOutletsLayer(path):
    """ Create a new point layer with the end nodes of the rivers segments."""

    # Get outlets of river segments
    (endPntXs,endPntYs)= h_utils.getSegmentEndsCoords(h_const.riverLayerName,
                                                      "first")

    coordinates=zip(endPntXs, endPntYs)
    ok= h_utils.createPointLayer(path, h_const.outletLayerName, coordinates,
                          h_const.outletFieldNames, h_const.outletFieldTypes,
                          (endPntXs, endPntYs) )
    if not ok: return False

    # Make sure the layer is loaded 
    if not h_utils.isShapefileLoaded(h_const.outletLayerName):
        ok=h_utils.loadShapefileToCanvas(path, h_const.outletLayerName+".shp")

    return ok



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

    # Add id of polygons to attribute table
    ok=h_utils.addShapeIdsToAttrTable(h_const.subbasLayerName,
                                      h_const.subbasFieldId)
    if not ok: return False

    # Make sure the layer is loaded 
    if not h_utils.isShapefileLoaded(h_const.subbasLayerName):
        ok=h_utils.loadShapefileToCanvas(path, h_const.subbasLayerName+".shp")

    return ok



def initGrdWatLayer(path):
    """Initialize groundwater layer"""
    ok= initializeLayer(path, h_const.grdwatLayerName, h_const.grdwatGeomType,
                       h_const.grdwatFieldNames, h_const.grdwatFieldTypes)
    if not ok: return False

    # Add id of cells to attribute table
    ok=h_utils.addShapeIdsToAttrTable(h_const.grdwatLayerName,
                                      h_const.grdwatFieldId)

    return ok



def initSpringLayer(path):
    """Initialize spring layer"""
    ok= initializeLayer(path, h_const.springLayerName, h_const.springGeomType,
                       h_const.springFieldNames, h_const.springFieldTypes)
    if not ok: return False
    return True



def initBorehLayer(path):
    """Initialize boreholes layer"""
    ok= initializeLayer(path, h_const.borehLayerName, h_const.borehGeomType,
                       h_const.borehFieldNames, h_const.borehFieldTypes)
    if not ok: return False
    return True



def initRiverLayer(path):
    """Initialize river layer"""
    ok= initializeLayer(path, h_const.riverLayerName, h_const.riverGeomType,
                       h_const.riverFieldNames, h_const.riverFieldTypes)
    if not ok: return False 

    # Add id of segments to attribute table
    ok=h_utils.addShapeIdsToAttrTable(h_const.riverLayerName,
                                      h_const.riverFieldId)
    return ok



def initAqueductLayer(path):
    """Initialize aqueduct layer"""
    ok= initializeLayer(path, h_const.aquedLayerName, h_const.aquedGeomType,
                       h_const.aquedFieldNames, h_const.aquedFieldTypes)
    if not ok: return False 

    return ok



def linkSubbasinRiver():
    """This function finds for each subbasin the corresponding river_id,
    node_id of the primary river segment """

    # Make sure River/Hydrojunction layers are OK
    if not h_utils.layerNameTypeOK(h_const.riverLayerName, 
                                                    h_const.riverLayerType) or \
       not h_utils.layerNameTypeOK(h_const.hydroJncLayerName, 
                                                 h_const.hydroJncLayerType) or \
       not h_utils.layerNameTypeOK(h_const.subbasLayerName, 
                                                     h_const.subbasLayerType):

        return False

    # Get coords of hydrojunction layer points
    [hydrojuncXlist, hydrojuncYlist]= \
                          h_utils.getPointLayerCoords(h_const.hydroJncLayerName)

    # Check that number of river segments euqals the number of subbasins
    riversNum= h_utils.getLayerFeaturesCount(h_const.riverLayerName)
    if not h_utils.layerFeaturesNumberOK(h_const.subbasLayerName, riversNum): 
        return False 

    # Get coordinates of river segments' first nodes
    rivSrtNodeXlist, rivSrtNodeYlist = \
                    h_utils.getSegmentEndsCoords(h_const.riverLayerName, "last")
    rivEndNodeXlist, rivEndNodeYlist = \
                   h_utils.getSegmentEndsCoords(h_const.riverLayerName, "first")

    # Find to which subbasin each segment start belongs to
    subassCount= h_utils.getLayerFeaturesCount(h_const.subbasLayerName)
    rivIds = [None] * subassCount
    nodeIds = [None] * subassCount

    inFeat = QgsFeature()
    for rivid, strNodeX, strNodeY, endNodeX, endNodeY, in zip( \
               range(0,len(rivSrtNodeXlist)), rivSrtNodeXlist, rivSrtNodeYlist,\
                                              rivEndNodeXlist, rivEndNodeYlist):
        # Obtain a new iterator, reset found-flag, reset i index
        foundStart= False
        subbPolygons= h_utils.getLayerFeatures(h_const.subbasLayerName)
        i=0
        # Find in which subbasin this point belongs to
        while subbPolygons.nextFeature(inFeat):
            if inFeat.geometry().contains(QgsPoint(strNodeX,strNodeY)):
                if not foundStart:
                    foundStart= True
                else:
                    message="Polygons of Subbasin overlap!"
                    QtGui.QMessageBox.critical(None,'Error',message, 
                                                QtGui.QMessageBox.Yes)
                    return False 
                # Prepare the list with node_id and river_id of this polygon
                rivIds[i]= rivid
                k=h_utils.getElementIndexByVal( \
                     zip(hydrojuncXlist, hydrojuncYlist), (endNodeX, endNodeY) )
                nodeIds[i]= k[0]
            i= i+1

        if not foundStart:
            message="The start of a river segment is outside of the subbasin!"
            QtGui.QMessageBox.critical(None,'Error',message, 
                                        QtGui.QMessageBox.Yes)
            return False 

    # Save edits
    res=h_utils.setFieldAttrValues(h_const.subbasLayerName,
                                   h_const.riverFieldId, rivIds)
    if not res: return False
    res=h_utils.setFieldAttrValues(h_const.subbasLayerName,
                                   h_const.subbasFieldRivNode, nodeIds)
    return res
