from ftools_utils import *
from qgis.core import *
from PyQt4 import QtGui

def layerNameTypeOK(layerName, layerType):
    """This function checks if the type of a layer is what is supposed to be"""
    layer=getVectorLayerByName(layerName)
    if layer==None:
        message=layerName + "  not loaded!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Yes)
        return False
    if riverLayer.type() != layerType:
        message=layerName + " is not a "+ str(layerType) + " layer!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Yes)
        return False
    return True



def layerFeaturesNumberOK(layerName, featuresNum):
    """This function checks if the number of features in a shapefile equals to
    the expected number of features."""
    nfeats=getLayerFeaturesCount(layerName)
    if nfeats!=featuresNum:
        message=layerName+" has not "+ str(featuresNum) + " features!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Yes)
        return False
    return True



def getFieldIndexByName(layerName, fieldname):
    """ Returns the index of the field named 'name' of the attribute table
    of the layer 'vlayer'. If no field with name 'name', returns False and 
    displays an error dialog."""
    provider.getLayerProvider(layerName)
    if provider:
        i = 0
        fieldsList=provider.fields()
        for field in fieldsList:
            if field.name==fieldname:
                return i
            i = i + 1
    if not provider:
        message=layerName+" not found!"
    else:
        message="Field with name "+fieldname+"not found!"
    QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Yes)
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
         xList.append(inFeat.geometry().x )
         yList.append(inFeat.geometry().y )

    return [xList, yList]



def getLayerProvider(layerName):
    """This function returns the dataprovider of a loaded layer""" 
    layer=getVectorLayerByName(layerName)
    if layer==None:
        message=layerName + "  not loaded!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Yes)
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
    return provider.freatureCount()



def getMinFeatureMeasure(layerName, layerType):
    """This function returns the area/length of the smallest polygon/line of 
    a shapefile."""
    # Check that type is what is supposed to be
    if not layerNameTypeOK(layerName, layerType): return False

    # Get features
    features= getLayerFeatures(layerName)
    if not features: return False

    # Loop to find smalest polygon
    inFeat= QgsFeature()
    minfeature=0
    while polygons.nextFeature(inFeat):
        if layerType==QGis.Polygon: minfeature=min(minfeature, inFeat.area())
        if layerType==QGis.Line: minfeature=min(minfeature, inFeat.length())

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



def getCellValue(layerName, x, y):
    """Returns the value of the cell of the layerName raster mape that has
    coordinates x,y"""
    rlayer=getRasterlayerByName(layerName)
    if rlayer==None:
        message=layerName + "  not loaded!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Yes)
        return False 
    return rlayer.identify(QgsPoint(x,y) )



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
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Yes)
        return False

    # Delete existing layer
    check = QFile(path+filename)
    if check.exists():
        if not QgsVectorFileWriter.deleteShapeFile(path+filename):
            message=("Can't delete shapefile\n%s")%(path+filename)
            QtGui.QMessageBox.warning(None,'Error',message, 
                                      QtGui.QMessageBox.Yes) 
            return False

    # Add points to layer
    layer=QgsVectorLayer()
    layer.startEditing()
    provider=layer.dataProvider()
    provider.addAttributes(zip(fieldNames, fieldTypes))
    for i, x, y in zip( range(0,len(xList)), xList, yList ):
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPoint(QgsPoint(x,y)))
        # Add values to attribute table
        for j in range(0, len(fieldNames)):
            if len(attrValues[j])>i: feat.addAttribute(j,attrValues[j][i])
        provider.addFeatures([feat])
 
    # Write shapefile
    layer.commitChanges()
    QgsVectorFileWriter.writeAsVectorFormat(layer, path+filename, 
                                            "utf8", None, "ESRI Shapefile") 

    return True 



def addMeasureToAtrrTable(layerName, layerType, fieldname):
    """Add area/length of each feature to the attribute table of a 
    polygon/line shapefile"""
    # Check that type is what is supposed to be
    if not layerNameTypeOK(layerName, layerType): return False
    
    # Get provider and features
    provider= getLayerProvider(layerName)
    features= getLayerFeatures(layerName)
    if not features: return False

    # Check if the fieldname already exists and if not add one
    fieldIndex=getFieldIndexByName(layerName, fieldname)
    if not fieldIndex:
        res = provider.addAttributes( [ QgsField(fieldname,QVariant.Double) ] )
        if not res: 
            message="Could not add a field to layer" + layerName 
            QtGui.QMessageBox.warning(None,'Error',message, 
                                      QtGui.QMessageBox.Yes) 
            return False
        fieldIndex=getFieldIndexByName(layerName, fieldname)

    # Add area/length to attribute table
    inFeat= QgsFeature()
    while polygons.nextFeature(inFeat):
        if layerType==QGis.Polygon: 
            inFeat.changeAttributeValue(fieldIndex, inFeat.area() )
        if layerType==QGis.Line:
            inFeat.changeAttributeValue(fieldIndex, inFeat.length() )

    # All went OK
    return True
