from ftools_utils import *
from qgis.core import *
from PyQt4 import QtGui
import os.path

def layerNameTypeOK(layerName, layerType):
    """This function checks if the type of a layer is what is supposed to be"""
    layer=getVectorLayerByName(layerName)
    if layer==None:
        message=layerName + "  not loaded!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False
    if layer.geometryType() != layerType:
        message=layerName + " is not a type "+ str(layerType) + " layer!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False
    return True



def layerFeaturesNumberOK(layerName, featuresNum):
    """This function checks if the number of features in a shapefile equals to
    the expected number of features."""
    nfeats=getLayerFeaturesCount(layerName)
    if nfeats!=featuresNum:
        message=layerName+" has not "+ str(featuresNum) + " features!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False
    return True



def getFieldIndexByName(layerName, fieldname):
    """Returns the index of the field named 'name' of the attribute table
    of the layer 'vlayer'. If no field with name 'name', returns False and 
    displays an error dialog."""
    provider=getLayerProvider(layerName)
    if provider:
        i = 0
        fieldsList=provider.fields()
        for field in fieldsList:
            if field.name()==fieldname:
                return i
            i = i + 1
    #else:
    #    return False

    # No field with this name found
    #message="Field with name "+str(fieldname)+" not found!"
    #QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
    return False



def getElementIndexByVal(alist, value):
    """Finds the indexes of the elements of the list 'alist' that are equal 
    to the value 'value'."""
    return [i for i in range(len(alist)) if alist[i]==value]    



def getPointLayerCoords(layerName):
    """This function returns the coordinates of a point layer."""
    # Check if it is a point layer
    if not layerNameTypeOK(layerName, QGis.Point): return False

    # Get points of HydroJunction layer
    points= getLayerFeatures(layerName)
    if points==None: return [False, False]

    # Get X,Y of each Hydrojunction point
    xList= []
    yList= []
    inFeat = QgsFeature()
    while points.nextFeature(inFeat):
         xList.append(inFeat.geometry().asPoint().x() )
         yList.append(inFeat.geometry().asPoint().y() )

    return [xList, yList]



def getLayerProvider(layerName):
    """This function returns the dataprovider of a loaded layer""" 
    layer=getVectorLayerByName(layerName)
    if layer==None:
        message=layerName + "  not loaded!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False 
    provider= layer.dataProvider()

    return provider



def getLayerFeatures(layerName):
    """This function returns the features of a shapefile."""
    provider= getLayerProvider(layerName)
    if not provider: return False
    features= provider.getFeatures()
    return features



def getLayerFeaturesCount(layerName):
    """This function returns the number of features of a shapefile."""
    provider= getLayerProvider(layerName)
    if not provider: return False
    return provider.featureCount()



def getMinFeatureMeasure(layerName, layerType):
    """This function returns the area/length of the smallest polygon/line of 
    a shapefile."""
    # Check that type is what is supposed to be
    if not layerNameTypeOK(layerName, layerType): return False

    # Return 0 if it is point layer
    if layerType==QGis.Point: return 0

    # Get features
    features= getLayerFeatures(layerName)
    if not features: return False

    # Loop to find smalest polygon
    inFeat= QgsFeature()
    minfeature=1e12 # An arbitrary large number
    while features.nextFeature(inFeat):
        if layerType==QGis.Polygon: 
            minfeature=min(minfeature, inFeat.geometry().area() )
        if layerType==QGis.Line: 
            minfeature=min(minfeature, inFeat.geometry().length() )

    return minfeature



def getRasterlayerByName(layerName):
    """Returns a raster layer given its name"""
    layermap = QgsMapLayerRegistry.instance().mapLayers()
    for name, layer in layermap.iteritems():
        if layer.type() == QgsMapLayer.RasterLayer and layer.name()==layerName:
            if layer.isValid():
                return layer
            else:
                return None



def getCellValue(layerName, coords, band):
    """Returns the value of the cell of the layerName raster mape that has
    coordinates x,y"""
    message=""
    if len(coords)!=2:
        message="A pair of two numbers only is required for coordinates!"
    else:
        rlayer=getRasterlayerByName(layerName)
        if rlayer==None: message=layerName + "  not loaded or not a raster!"
        elif band<1 or band>rlayer.bandCount():
            message=layerName + "  has not that many bands!"
    if len(message)>0:
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    identity=rlayer.dataProvider().identify( QgsPoint(coords[0], coords[1]),  
                                           QgsRaster.IdentifyFormatValue )
    return identity.results()[band]



def createPointLayer(path, filename, xList, yList, fieldNames, fieldTypes,
                     attrValues):
    """Creates a shapefile with points and populates its attribute table"""

    # Check arguments
    message=""
    if len(fieldNames) != len(attrValues):
        message="Number of field names <> number of attribute columns!"
    if len(fieldNames) != len(fieldTypes):
        message="Number of field names <> number of field types!"
    if len(xList) != len(yList):
        message="Number of x values <> number of y values!"
    if len(message)!=0:
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    # Delete existing layer
    pathFilename=os.path.join(path, filename)
    fileExists= os.path.isfile(pathFilename+".shp")
    if fileExists:
        message="Shapefile "+filename+" alredy there. Delete?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
        if reply==QtGui.QMessageBox.No: return False
        if not QgsVectorFileWriter.deleteShapeFile(pathFilename):
            message=("Can't delete shapefile\n%s")%(pathFilename)
            QtGui.QMessageBox.warning(None,'Error',message,QtGui.QMessageBox.Ok)
            return False

    # Create empty point layer and add attribute fields
    fieldList = QgsFields()
    for i,j in zip(fieldNames, fieldTypes):
        fieldList.append(QgsField(i,j) )
    writer= QgsVectorFileWriter(pathFilename, "utf8", fieldList,
                                QGis.WKBPoint, None, "ESRI Shapefile")
    if writer.hasError() != QgsVectorFileWriter.NoError:
        message="Error creating shapefile "+filename
        QtGui.QMessageBox.warning(None,'Error',message,QtGui.QMessageBox.Ok)
        return False

    # Add points to layer
    for i, x, y in zip( range(0,len(xList)), xList, yList ):
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPoint(QgsPoint(x,y)))
        # Add values to attribute table
        rowValues=[]
        for j in range(0, len(fieldNames)):
            if len(attrValues[j])>i: rowValues.append(attrValues[j][i])
            else: rowValues.append(None)
            feat.setAttributes(rowValues)
        writer.addFeature(feat)
 
    # Delete the writer to flush features to disk (optional)
    del writer
    


def addMeasureToAttrTable(layerName, layerType, fieldname):
    """Add area/length of each feature to the attribute table of a 
    polygon/line shapefile"""
    # Check that type is what is supposed to be
    if not layerNameTypeOK(layerName, layerType): return False
    
    # Turn on editing, get provider and features
    layer=getVectorLayerByName(layerName)
    if not layer: return False
    layer.startEditing()
    provider= getLayerProvider(layerName)
    features= getLayerFeatures(layerName)

    # Check if the fieldname already exists and if not add one
    fieldIndex=getFieldIndexByName(layerName, fieldname)
    if not fieldIndex:
        res = provider.addAttributes( [ QgsField(fieldname,QVariant.Double) ] )
        if not res: 
            message="Could not add a field to layer" + str(layerName)
            QtGui.QMessageBox.warning(None,'Error',message,QtGui.QMessageBox.Ok)
            return False
        layer.updateFields()
        fieldIndex=getFieldIndexByName(layerName, fieldname)
        pass

    # Add area/length to attribute table
    inFeat= QgsFeature()
    while features.nextFeature(inFeat):
        if layerType==QGis.Polygon: 
            res=layer.changeAttributeValue(inFeat.id(), fieldIndex, 
                                       inFeat.geometry().area() )
        if layerType==QGis.Line:
            res=layer.changeAttributeValue(inFeat.id(), fieldIndex, 
                                       inFeat.geometry().length() )

    # Save changes
    layer.commitChanges()
    return res
