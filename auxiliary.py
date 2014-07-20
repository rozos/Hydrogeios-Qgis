import ftools_utils
from qgis.core import *

def getFieldIndexByName(vlayer, name):
    """ Returns the index of the field named 'name' of the attribute table
    of the layer 'vlayer'. If no field with name 'name', returns -1 and 
    displays an error dialog."""
    try:
        fields= getFieldList(vlayer) 
        return [i for i in fields if i == name][0]
    except ValueError:
        #QtGui.QMessageBox.critical(None, 'Error', 'The field '+name+ 
        #                           ' not found', QtGui.QMessageBox.Yes)
        return -1



def getElementIndexByVal(alist, value):
    """Finds the indexes of the elements of the list 'alist' that are equal 
    to the value 'value'."""
    return [i for i in range(len(alist)) if alist[i]==value]    



def createPointLayer(path, filename, xList, yList, fieldnames, attrValues):
    """Creates a shapefile with points and populates its attribute table"""
