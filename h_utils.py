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
    nfeats=getLayerFeaturesCount(layerName)
    if nfeats!=featuresNum:
        message=layerName+" has not "+ str(featuresNum) + " features!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Yes)
        return False
    return True


def getFieldIndexByName(layerName, fieldname):
    """ Returns the index of the field named 'name' of the attribute table
    of the layer 'vlayer'. If no field with name 'name', returns -1 and 
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
    provider= getLayerProvider(layerName)
    if not provider: return False
    features= provider.getFeatures()
    return features



def getLayerFeaturesCount(layerName):
    provider= getLayerProvider(layerName)
    if not provider: return False
    return provider.freatureCount()



def createPointLayer(path, filename, xList, yList, fieldnames, attrValues):
    """Creates a shapefile with points and populates its attribute table"""

    # Check arguments
    if len(fieldnames) != len(attrValues):
        message="Field with name "+name+"not found!"
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
    j=0
    for name in fieldnames:
        layer.addAttribute(j,name)
        j=j+1
    i=0
    for x, y in zip(xList,yList):
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPoint(QgsPoint(x,y)))
        # Add values to attribute table
        j=0
        for name in fieldnames:
            if len(attrValues[j])>i:
                feat.addAttribute(j,name)
            j=i+1
        layer.dataProvider().addFeatures([feat])
        i=i+1
 
    # Write shapefile
    layer.commitChanges()
    QgsVectorFileWriter.writeAsVectorFormat(layer, path+filename, 
                                            "utf8", None, "ESRI Shapefile") 

    return True 



def addLengthToAtrrTable(layerName):
    pass


def addAreaToAtrrTable(layerName):
    pass
