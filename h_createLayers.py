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
    pass 

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

    # Add coordinates of polygon centroids to attribute table
    pass
