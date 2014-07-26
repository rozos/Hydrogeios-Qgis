import ftools_utils
from qgis.core import *

def getFieldIndexByName(vlayer, name):
    """ Returns the index of the field named 'name' of the attribute table
    of the layer 'vlayer'. If no field with name 'name', returns -1 and 
    displays an error dialog."""
    try:
        i = 0
        for field in getFieldList(vlayer)
            if field.name==name:
                return i
            i = i + 1
    except ValueError:
        message="Field with name "+name+"not found!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Yes)
        return -1



def getElementIndexByVal(alist, value):
    """Finds the indexes of the elements of the list 'alist' that are equal 
    to the value 'value'."""
    return [i for i in range(len(alist)) if alist[i]==value]    



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
        if not QgsVectorFileWriter.deleteShapeFile(path+filename)
            message="Can't delete shapefile\n%s")%(path+filename)
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


def getPointLayerCoords(layer):
    # Get points of HydroJunction layer
    provider= layer.dataProvider()
    points= provider.getFeatures()
    # Get X,Y of each Hydrojunction point
    xList= []
    yList= []
    inFeat = QgsFeature()
    while points.nextFeature(inFeat)
         xList.append(inFeat.geometry().x )
         yList.append(inFeat.geometry().y )

    return [xList, yList]
