from PyQt5.QtWidgets import *
from qgis.core import *
import os.path
import h_const
import h_utils
import h_topology




def doAll(prjpath):
    """Calls all functions that create/initialize the layers of a Hydrogeios 
    Project."""
    if not initIrrigLayer(prjpath):
        message="initIrrigLayer Failed. Continue?"
        reply=QMessageBox.question(None, 'Delete', message,
                                   QMessageBox.Yes|QMessageBox.No )
        if reply==QMessageBox.No: return False
    if not initSubbasinLayer(prjpath):
        message="initSubbasinLayer Failed. Continue?"
        reply=QMessageBox.question(None, 'Delete', message,
                                   QMessageBox.Yes|QMessageBox.No )
        if reply==QMessageBox.No: return False
    if not h_utils.addShapeIdsToAttrTable(h_const.subbasLayerName,
                                          h_const.subbasFieldId):
        message="addSubbasinId Failed. Continue?"
        reply=QMessageBox.question(None, 'Delete', message,
                                   QMessageBox.Yes|QMessageBox.No )
        if reply==QMessageBox.No: return False
    if not initGrdWatLayer(prjpath):
        message="initGrdWatLayer Failed. Continue?"
        reply=QMessageBox.question(None, 'Delete', message,
                                   QMessageBox.Yes|QMessageBox.No )
        if reply==QMessageBox.No: return False
    if not initSpringLayer(prjpath):
        message="initSpringLayer Failed. Continue?"
        reply=QMessageBox.question(None, 'Delete', message,
                                   QMessageBox.Yes|QMessageBox.No )
        if reply==QMessageBox.No: return False
    if not initBorehLayer(prjpath):
        message="initBorehLayer Failed. Continue?"
        reply=QMessageBox.question(None, 'Delete', message,
                                   QMessageBox.Yes|QMessageBox.No )
        if reply==QMessageBox.No: return False
    if not initRiverLayer(prjpath):
        message="initRiverLayer Failed. Continue?"
        reply=QMessageBox.question(None, 'Delete', message,
                                   QMessageBox.Yes|QMessageBox.No )
        if reply==QMessageBox.No: return False
    if not initAqueductLayer(prjpath):
        message="initAqueductLayer Failed. Continue?"
        reply=QMessageBox.question(None, 'Delete', message,
                                   QMessageBox.Yes|QMessageBox.No )
        if reply==QMessageBox.No: return False
    if not createRiverexitnodeLayer(prjpath):
        message="initRiverexitnodeLayer Failed. Continue?"
        reply=QMessageBox.question(None, 'Delete', message,
                                   QMessageBox.Yes|QMessageBox.No )
        if reply==QMessageBox.No: return False
    if not linkSubbasinRiver():
        message="linkSubbasinRiver Failed. Continue?"
        reply=QMessageBox.question(None, 'Delete', message,
                                   QMessageBox.Yes|QMessageBox.No )
        if reply==QMessageBox.No: return False

    return True



def initializeLayer(prjpath, layerName, wkbtype, fieldNames, fieldTypes):
    """Create a new empty layer with the given fields in attribute table or
    (if already there) make sure the attribute table has all required fields"""

    # If layer does not exist create one
    if not h_utils.shapefileExists(prjpath, layerName): 
        pathFilename=os.path.join(prjpath, layerName)
        writer= QgsVectorFileWriter(pathFilename, "utf8", QgsFields(), wkbtype,
                       QgsCoordinateReferenceSystem(h_const.projectcrs), 
                       "ESRI Shapefile")
        if writer.hasError() != QgsVectorFileWriter.NoError:
            message="Error creating shapefile "+ layerName
            QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
            return False
        # Delete the writer to flush features to disk (optional)
        del writer

    # Make sure all required fields are there
    if not h_utils.addFieldsToAttrTable(prjpath, layerName, fieldTypes, 
                                        fieldNames):
        return False

    return True



def createOutletsLayer(prjpath):
    """Create a new point layer with the end nodes of the rivers segments."""

    # Get outlets of river segments
    endPnts= h_utils.getSegmentPoints(h_const.riverLayerName, "first")

    ok= h_utils.createPointLayer(prjpath, h_const.outletLayerName, endPnts,
                          h_const.outletFieldNames, h_const.outletFieldTypes,
                          (endPntXs, endPntYs) )
    if not ok: return False

    # Make sure the layer is loaded 
    if not h_utils.isLayerLoaded(h_const.outletLayerName):
        ok=h_utils.loadShapefileToCanvas(prjpath, h_const.outletLayerName)

    return ok



def initIrrigLayer(prjpath):
    """Initialize irrigation layer"""

    # Initialize layer
    ok= initializeLayer(prjpath, h_const.irrigLayerName, h_const.irrigWkbType,
                       h_const.irrigFieldNames, h_const.irrigFieldTypes)
    if not ok: return False

    return True



def initSubbasinLayer(prjpath):
    """Initialize subbasin layer"""

    # Initialize layer
    ok= initializeLayer(prjpath, h_const.subbasLayerName, h_const.subbasWkbType,
                       h_const.subbasFieldNames, h_const.subbasFieldTypes)
    if not ok:
        print("Failed to initialize layer!")
        return False

    # Add area of polygons to attribute table
    fieldIndex= h_utils.addMeasureToAttrTable(h_const.subbasLayerName, 
                                      h_const.subbasFieldArea)
    if fieldIndex==None: 
        print("Failed to add area to attribute table!")
        return False

    # Get centroids
    centroids=h_utils.getPolyLayerCentroids(h_const.subbasLayerName)
    if centroids==None: 
        print("Failed to get centroids!")
        return False

    # Add coordinates of polygon centroids to attribute table
    xCoord=[]
    yCoord=[]
    for (x,y) in centroids:
        xCoord.append(x)
        yCoord.append(y)
    ok= h_utils.setFieldAttrValues(h_const.subbasLayerName,
                                   h_const.subbasFieldX, xCoord);
    if not ok:
        print("Failed to add X coordinates!")
        return False
    ok=h_utils.setFieldAttrValues(h_const.subbasLayerName,
                                   h_const.subbasFieldY, yCoord);
    if not ok:
        print("Failed to add Y coordinates!")
        return False

    # Add id of polygons to attribute table
    ok=h_utils.addShapeIdsToAttrTable(h_const.subbasLayerName,
                                      h_const.subbasFieldId)
    if not ok:
        print("Failed to add Ids.")
        return False

    # Make sure the layer is loaded 
    if not h_utils.isLayerLoaded(h_const.subbasLayerName):
        ok=h_utils.loadShapefileToCanvas(prjpath, h_const.subbasLayerName)

    return ok



def initGrdWatLayer(prjpath):
    """Initialize groundwater layer"""
    ok= initializeLayer(prjpath, h_const.grdwatLayerName, h_const.grdwatWkbType,
                       h_const.grdwatFieldNames, h_const.grdwatFieldTypes)
    if not ok: return False

    # Add id of cells to attribute table
    ok=h_utils.addShapeIdsToAttrTable(h_const.grdwatLayerName,
                                      h_const.grdwatFieldId)

    return ok



def initSpringLayer(prjpath):
    """Initialize spring layer"""
    ok= initializeLayer(prjpath, h_const.springLayerName, h_const.springWkbType,
                       h_const.springFieldNames, h_const.springFieldTypes)
    if not ok: return False
    return True



def initBorehLayer(prjpath):
    """Initialize boreholes layer"""
    ok= initializeLayer(prjpath, h_const.borehLayerName, h_const.borehWkbType,
                       h_const.borehFieldNames, h_const.borehFieldTypes)
    if not ok: return False
    return True



def initRiverLayer(prjpath):
    """Initialize river layer"""
    ok= initializeLayer(prjpath, h_const.riverLayerName, h_const.riverWkbType,
                       h_const.riverFieldNames, h_const.riverFieldTypes)
    if not ok: return False 

    # Add id of segments to attribute table
    ok=h_utils.addShapeIdsToAttrTable(h_const.riverLayerName,
                                      h_const.riverFieldId)
    if not ok: return False 

    # Add length of segments to attribute table
    ok=h_utils.addMeasureToAttrTable(h_const.riverLayerName,
                                      h_const.riverFieldLength)

    return ok



def initAqueductLayer(prjpath):
    """Initialize aqueduct layer"""
    ok= initializeLayer(prjpath, h_const.aquedLayerName, h_const.aquedWkbType,
                       h_const.aquedFieldNames, h_const.aquedFieldTypes)
    if not ok: return False 

    return ok



def createRiverexitnodeLayer(prjpath):
    """Initialize/create Riverexitnode layer"""

    # Get outlets of river segments
    duplpoints= h_utils.getSegmentPoints(h_const.riverLayerName, "first")
    if duplpoints==False or duplpoints==None: 
        print("No start node found!")
        return False

    # Create a point layer with the river segment outlets
    riverexitnodeLayerName=h_const.riverexitnodeLayerName
    h_utils.unloadShapefile(riverexitnodeLayerName)
    points=list(set(duplpoints))
    ok= h_utils.createPointLayer(prjpath, riverexitnodeLayerName, points, 
                                 h_const.riverexitnodeFieldNames, 
                                 h_const.riverexitnodeFieldTypes, ([], [], [],))
    if not ok: return False

    # Load river exit, add Ids to attr. table, and unload
    if not h_utils.isLayerLoaded(riverexitnodeLayerName):
        ok=h_utils.loadShapefileToCanvas(prjpath, riverexitnodeLayerName)
        if not ok: return False

    ok= h_utils.addShapeIdsToAttrTable(h_const.riverexitnodeLayerName, 
                                       h_const.riverexitnodeFieldId)
    if ok: 
        h_utils.unloadShapefile(riverexitnodeLayerName)
        return ok
    else:
        return False



def linkSubbasinRiver():
    """This function finds for each subbasin the corresponding river_id
    of the primary river segment """

    # Make sure River and Subbasin layers are OK
    if not h_utils.layerNameTypeOK(h_const.riverLayerName, 
                                                    h_const.riverGeomType) or \
       not h_utils.layerNameTypeOK(h_const.subbasLayerName, 
                                                     h_const.subbasGeomType):
        print("River or Subbasin layers not OK!")
        return False

    # Check that number of river segments euqals the number of subbasins
    subbasCount= h_utils.getLayerFeaturesCount(h_const.subbasLayerName)
    if not h_utils.layerFeaturesNumberOK(h_const.riverLayerName, subbasCount): 
        print("River segments not equal to Subbasin polygons!")
        return False 

    # Get coordinates of river segments mid-nodes
    rivInpNodes= h_utils.getSegmentPoints(h_const.riverLayerName, "mid")
    if rivInpNodes==None: 
        print("Failed to get coordinates of river segments mid-nodes!")
        return False

    # Loop through every river input node
    rivsId = [None] * subbasCount
    inFeat = QgsFeature()
    for rivid, strtNode in zip( range(0,len(rivInpNodes)), rivInpNodes ):
        # Loop through every subbasin polygon
        foundStart= False
        subbPolygons= h_utils.getLayerFeatures(h_const.subbasLayerName)
        i=0
        while subbPolygons.nextFeature(inFeat):
            # Find if this point belongs to this subbasin 
            if inFeat.geometry().contains(strtNode):
                if not foundStart:
                    foundStart= True
                else:
                    message="Polygons of Subbasin overlap!"
                    QMessageBox.critical(None,'Error',message, QMessageBox.Yes)
                    return False 
                # Record the river_id
                rivsId[i]= rivid
            i= i+1

        if not foundStart:
            message="The start of a river segment is outside of the subbasin!"
            QMessageBox.critical(None,'Error',message, QMessageBox.Yes)
            return False 

    # Save edits
    res=h_utils.setFieldAttrValues(h_const.subbasLayerName,
                                   h_const.riverFieldId, rivsId)
    return res
