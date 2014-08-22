from PyQt4 import QtGui
from qgis.core import *
import ftools_utils
import h_const

def createOutletsLayer(path):
    """ Create a new point layer with the end nodes of the rivers segments."""

    # Get River segments
    riverSegments= h_utils.getLayerFeatures(h_const.riverLayerName)
    if not riverSegments: return False

    # Get outlet of river segments
    inFeat1 = QgsFeature()
    frstnode=0
    x,y = 0,1
    endPntXs= []
    endPntYs= []
    while riverSegments.nextFeature(inFeat1):
        nodes=inFeat1.geometry().asPolyline()
        endPntXs.append( nodes[frstnode][x] )
        endPntYs.append( nodes[frstnode][y] )
    
    coordinates=zip(endPntXs, endPntYs)
    res= createPointLayer(path, h_const.outletLayerName, coordinates,
                          h_const.outletFieldNames, h_const.outletFieldTypes,
                          attrValues)
    return res



def initilizeLayer(path, layerName, layerType, fieldNames, fieldTypes):
    """Create a new empty layer with the given fields in attribute table or
    (if already there) make sure the attribute table has all required fields"""

    # Check if file exists
    pathFilename=os.path.join(path, layerName)
    fileExists= os.path.isfile(pathFilename+".shp")

    # If layer does not exist create one
    if not fileExists: 
        # Initialize the list with name/type of attribute table fields
        fieldList=[]
        for fieldname,fieldtype in zip(fieldNames, fieldTypes):
            fieldList.append(QgsField(fieldname,fieldtype) )
        # Create an empty layer
        writer= QgsVectorFileWriter(pathFilename, "utf8", fieldList,
                                    layertype, None, "ESRI Shapefile")
        if writer.hasError() != QgsVectorFileWriter.NoError:
            message="Error creating shapefile "+filename
            QtGui.QMessageBox.critical(None,'Error',message,
                                       QtGui.QMessageBox.Ok)
            return False
        # Delete the writer to flush features to disk (optional)
        del writer

    # Make sure the layer is loaded
    if not ftools_utils.addShapeToCanvas(pathFilename):
        message="Error loading output shapefile:\n%s"  %(pathFilename)
        QtGui.QMessageBox.critical(None, 'Error', message,QtGui.QMessageBox.Ok)
        return False

    # Make sure all required fields are there
    res=True
    for fieldname,fieldtype in (fieldNames, fieldTypes):
        ok=addFieldToAttrTable(layername, fieldname, fieldtype)
        if not ok:
            res=False
            break

    return res



def initIrrigLayer(path):
    """Initialize irrigation layer"""

    # Initialize layer
    ok= initilizeLayer(path, h_const.irrigLayerName, h_const.irrigLayerType,
                       h_const.irrigFieldNames, h_const.irrigFieldTypes)
    if not ok: return False

    return True



def initSubbasinLayer(path):
    """Initialize subbasin layer"""

    # Initialize layer
    ok= initilizeLayer(path, h_const.subbasLayerName, h_const.subbasLayerType,
                       h_const.subbasFieldNames, h_const.subbasFieldTypes)
    if not ok: return False

    # Add area of polygons to attribute table
    ok= addMeasureToAttrTable(h_const.subbasLayerName, h_const.subbasLayerType,
                              h_const.subbasFieldNameArea)
    if not ok: return False

    # Get centroids
    centroids=getPolyLayerCentroids(h_const.subbasLayerName)
    if not centroids: return False

    # Add coordinates of polygon centroids to attribute table
    xCoord=[]
    yCoord=[]
    for (x,y) in centroids:
        xCoord.append(x)
        yCoord.append(y)
    ok= h_utils.setFieldAttrValues(h_const.subbasLayerName,
                                   h_const.subbasFieldNameX, xCoord);
    if not ok: return False
    ok=h_utils.setFieldAttrValues(h_const.subbasLayerName,
                                   h_const.subbasFieldNameY, yCoord);
    if not ok: return False

    return True



def initGrdWatLayer(path):
    """Initialize groundwater layer"""
    ok= initilizeLayer(path, h_const.grdwatLayerName, h_const.grdwatLayerType,
                       h_const.grdwatFieldNames, h_const.grdwatFieldTypes)
    if not ok: return False
    return True



def initSpringLayer(path):
    """Initialize spring layer"""
    ok= initilizeLayer(path, h_const.springLayerName, h_const.springLayerType,
                       h_const.springFieldNames, h_const.springFieldTypes)
    if not ok: return False
    return True



def initBorehLayer(path):
    """Initialize boreholes layer"""
    ok= initilizeLayer(path, h_const.borehLayerName, h_const.borehLayerType,
                       h_const.borehFieldNames, h_const.borehFieldTypes)
    if not ok: return False
    return True



def initBorehLayer(path):
    """Initialize river layer"""
    ok= initilizeLayer(path, h_const.riverLayerName, h_const.riverLayerType,
                       h_const.riverFieldNames, h_const.riverFieldTypes)
    if not ok: return False 
    return True
