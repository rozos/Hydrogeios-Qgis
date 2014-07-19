import ftools_utils
from qgis.core import *

def getFieldIndexByName(vlayer, name):
    try:
        fields= getFieldList(vlayer) 
        return [i for i in fields if i == name][0]
    except ValueError:
        #QtGui.QMessageBox.critical(None, 'Error', 'The field '+name+ 
        #                           ' not found', QtGui.QMessageBox.Yes)
        return -1
