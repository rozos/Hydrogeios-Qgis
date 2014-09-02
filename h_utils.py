from qgis.core import *
from PyQt4 import QtGui
from PyQt4.QtCore import QVariant
import ftools_utils
import os.path
import h_const



def packInteger(num, order):
    """Packs an integer number, ranging from 0 to 15, into a binary 
    structure that can hold up to 7 integers.
     1111 1111 1111 1111 1111 1111 1111
     |                             |
     |                             `-> First (order 1) number packed here
     `-> Seventh (order 7) number packed here."""
    if (order < 1) or (order > 7):
        return None

    if (num > 15) or (num < 0):
        return None

    return num * iround(2 ^ (4 * (order - 1)))



def unpackInteger(num, order):
    """Unpacks the integer that was packed into the binary structure described
    above."""

    if (order < 1) or (order > 7):
        return None

    if (num > 268435455) or (num < 0):
        return None

    return (num & 15 * 2 ^ (4 * (order - 1))) / 2 ^ (4 * (order - 1))



def iround(x):
    """iround(number) -> integer Round a number to the nearest integer."""
    y = round(x) - .5
    return int(y) + (y > 0)



def floatsEqual(afloat, bfloat, exponent):
    """Returns true if float numbers are close enough (enough is defined by
    the power."""
    precision=1./pow(10,exponent)
    if type(afloat) in (tuple, list): 
        valuelen=len(afloat)
        if valuelen!=len(bfloat): return None
    else: 
        return abs(afloat-bfloat) <= precision
    equal= True
    for i in range(valuelen):
        equal=equal and ( abs(afloat[i]-bfloat[i]) <= precision )
    return equal



def loadShapefileToCanvas(pathFilename):
    """Wraps the ftools function. It displayes an error message if something
    goes wrong."""

    if not ftools_utils.addShapeToCanvas(pathFilename):
        message="Error loading output shapefile "+pathFilename
        QtGui.QMessageBox.critical(None, 'Error', message,QtGui.QMessageBox.Ok)
        return False
    return True



def layerNameTypeOK(layerName, layerType):
    """This function checks if the type of a layer is what is supposed to be"""
    layer=ftools_utils.getVectorLayerByName(layerName)
    if not layer:
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



def getFieldIndexByName(layerName, fieldName):
    """Returns the index of the field named 'name' of the attribute table
    of the layer 'vlayer'. If no field with name 'name', returns None and 
    displays an error dialog."""
    provider=getLayerProvider(layerName)
    if provider:
        i = 0
        fieldsList=provider.fields()
        for field in fieldsList:
            if field.name()==fieldName:
                return i
            i = i + 1
    else:
        return None

    # No field with this name found
    message="Field with name "+str(fieldName)+" not found in layer " +\
             str(layerName)
    QtGui.QMessageBox.warning(None,'Error',message, QtGui.QMessageBox.Ok)
    return None



def getElementIndexByVal(alist, value):
    """Finds the indexes of the elements of the list 'alist' that are equal 
    to the value 'value'."""
    return [i for i in range(len(alist)) if floatsEqual(alist[i],value,h_const.precise)]    



def getPointLayerCoords(layerName):
    """This function returns the coordinates of a point layer."""
    # Check if it is a point layer
    if not layerNameTypeOK(layerName, QGis.Point): return None

    # Get points of HydroJunction layer
    points= getLayerFeatures(layerName)
    if points==None: return [None, None]

    # Get X,Y of each Hydrojunction point
    xList= []
    yList= []
    inFeat = QgsFeature()
    while points.nextFeature(inFeat):
         xList.append(inFeat.geometry().asPoint().x() )
         yList.append(inFeat.geometry().asPoint().y() )

    return (xList, yList)



def getPolyLayerCentroids(layerName):
    """Get centroids of a polygon layer."""

    # Make sure this is a polygon layer
    if not layerNameTypeOK(layerName, QGis.Polygon):
        return None

    # Get polygons of layerName
    polygons= getLayerFeatures(layerName)
    if not polygons: return None

    coords= []
    inFeat=QgsFeature()
    while polygons.nextFeature(inFeat):
        centrpoint = inFeat.geometry().centroid().asPoint()
        coords.append( (centrpoint.x(), centrpoint.y()) )

    return coords 



def getLayerProvider(layerName):
    """This function returns the dataprovider of a loaded layer""" 
    layer=ftools_utils.getVectorLayerByName(layerName)
    if not layer:
        message=layerName + "  not loaded!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return None
    provider= layer.dataProvider()

    return provider



def getLayerFeatures(layerName):
    """This function returns the features of a shapefile."""
    provider= getLayerProvider(layerName)
    if not provider: return None
    features= provider.getFeatures()
    return features



def getLayerFeaturesCount(layerName):
    """This function returns the number of features of a shapefile."""
    provider= getLayerProvider(layerName)
    if not provider: return None
    return provider.featureCount()



def getMinFeatureMeasure(layerName, layerType):
    """This function returns the area/length of the smallest polygon/line of 
    a shapefile."""
    # Check that type is what is supposed to be
    if not layerNameTypeOK(layerName, layerType): return None

    # Return 0 if it is point layer
    if layerType==QGis.Point: return 0

    # Get features
    features= getLayerFeatures(layerName)
    if not features: return None

    # Loop to find smalest polygon
    inFeat= QgsFeature()
    minfeature=1e12 # An arbitrary large number
    while features.nextFeature(inFeat):
        if layerType==QGis.Polygon: 
            minfeature=min(minfeature, inFeat.geometry().area() )
        if layerType==QGis.Line: 
            minfeature=min(minfeature, inFeat.geometry().length() )

    return minfeature



def getCellValue(layerName, coords, band):
    """Returns the value of the cell of the layerName raster mape that has
    coordinates x,y"""
    message=""
    if len(coords)!=2:
        message="A pair of two numbers only is required for coordinates!"
    else:
        rlayer=getRasterLayerByName(layerName)
        if rlayer==None: message=layerName + "  not loaded or not a raster!"
        elif band<1 or band>rlayer.bandCount():
            message=layerName + "  has not that many bands!"
    if len(message)>0:
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return None

    identity=rlayer.dataProvider().identify( QgsPoint(coords[0], coords[1]),  
                                           QgsRaster.IdentifyFormatValue )
    return identity.results()[band]



def getFieldAttrValues(layerName, fieldName):
    """Gets all values of a field of the attribute table."""
    features=getLayerFeatures(layerName)
    if not features:return None
    fieldIndex=getFieldIndexByName(layerName, fieldName)
    if fieldIndex==None:return None

    values= []
    inFeat= QgsFeature()
    while features.nextFeature(inFeat):
        attribs=inFeat.attributes()
        values.append(attribs[fieldIndex])

    return values



def createPointLayer(path, filename, coords, fieldNames, fieldTypes,
                     attrValues):
    """Creates a shapefile with points and populates its attribute table"""

    # Check arguments
    message=""
    if len(fieldNames) != len(attrValues):
        message="Number of field names <> number of attribute columns!"
    if len(fieldNames) != len(fieldTypes):
        message="Number of field names <> number of field types!"
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
            message="Can't delete shapefile "+pathFilename
            QtGui.QMessageBox.critical(None,'Err',message,QtGui.QMessageBox.Ok)
            return False

    # Create empty point layer and add attribute fields
    fieldList = QgsFields()
    for i,j in zip(fieldNames, fieldTypes):
        fieldList.append(QgsField(i,j) )
    writer= QgsVectorFileWriter(pathFilename, "utf8", fieldList,
                                QGis.WKBPoint, None, "ESRI Shapefile")
    if writer.hasError() != QgsVectorFileWriter.NoError:
        message="Error creating shapefile "+filename
        QtGui.QMessageBox.critical(None,'Error',message,QtGui.QMessageBox.Ok)
        return False

    # Add points to layer
    for i, xy in zip( range(0,len(coords)), coords):
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPoint(QgsPoint(xy[0],xy[1])))
        # Add values to attribute table
        rowValues=[]
        for j in range(0, len(fieldNames)):
            if len(attrValues[j])>i: rowValues.append(attrValues[j][i])
            else: rowValues.append(None)
            feat.setAttributes(rowValues)
        writer.addFeature(feat)
 
    # Delete the writer to flush features to disk (optional)
    del writer
    return True



def createDBF(path, filename, fieldNames, fieldTypes, values):
    """Creates a new dbf file (or updates an existing) with the values provided
    in the values list (this is a list of lists in case of many fields."""

    # Check validity of arguments' length
    numvalues=len(fieldNames)
    if numvalues!=len(fieldTypes) or numvalues==0:
        message="addFieldToDBF arguments error!"
        QtGui.QMessageBox.critical(None, 'Error', message,QtGui.QMessageBox.Ok)
        return False

    # Create the list with the coordinates of dummy points
    coords=zip([0]*numvalues, [0]*numvalues)

    # Create dummy shapefile to create the required dbf file
    ok=createPointLayer(path, filename, coords, fieldNames, fieldTypes, values)

    return ok



def addFieldToAttrTable(layerName, fieldName, fieldType):
    """Add a fieldName to attribute table of layerName. Returns the index
    off added field"""

    # Get layer and enable editing
    layer=ftools_utils.getVectorLayerByName(layerName)
    if not layer: return None

    layer.startEditing()

    # Get dataprovider
    provider=getLayerProvider(layerName)

    # Check if the fieldName already exists and if not add one
    fieldIndex=getFieldIndexByName(layerName, fieldName)
    if fieldIndex!=None:
        # Make sure fieldName is fieldType
        field=provider.fields()[fieldIndex]
        if field.type() != fieldType:
            message="Field " + str(fieldName) + " already in layer " + \
                    str(layerName) + " but not of expected type!"
            QtGui.QMessageBox.critical(None,'Err',message,QtGui.QMessageBox.Ok)
            return None
    else:
        message="Field "+str(fieldName)+" is added to the layer "+str(layerName)
        QtGui.QMessageBox.warning(None,'Info',message,QtGui.QMessageBox.Ok)
        ok = provider.addAttributes( [ QgsField(fieldName,fieldType) ] )
        if not ok: 
            message="Could not add a field to layer" + str(layerName)
            QtGui.QMessageBox.critical(None,'Err',message,QtGui.QMessageBox.Ok)
            return None
        layer.updateFields()
        fieldIndex=getFieldIndexByName(layerName, fieldName)

    # Save changes and return field index
    layer.commitChanges()
    return fieldIndex



def addShapeIdToField(layerName, fieldName):
    """Add to the attribute table of a layer a field that keeps the ids of the 
       shapes"""
    ok=addFieldToAttrTable(layerName,fieldName, QVariant.Int)
    if not ok: return False
    values=range(getLayerFeaturesCount(layerName))
    return setFieldAttrValues(layerName,fieldName, values)
    
    

def setFieldAttrValues(layerName, fieldName, values):
    """Sets all values of a field of the attribute table."""

    # Get features of layer
    features= getLayerFeatures(layerName)
    if not features: return False

    # Get the index of fieldName
    fieldIndex=getFieldIndexByName(layerName, fieldName)
    if fieldIndex==None: return False

    # Start editing layer
    layer=ftools_utils.getVectorLayerByName(layerName)
    layer.startEditing()

    # Set the values of the fieldName of the attribute table
    i=0
    inFeat=QgsFeature()
    while features.nextFeature(inFeat):
        inFeat.setAttribute(fieldIndex, values[i])
        layer.updateFeature(inFeat)
        i=i+1
        if i>=len(values): break

    # Save edits
    layer.commitChanges()
    return True



def addMeasureToAttrTable(layerName, layerType, fieldName):
    """Add area/length of each feature to the attribute table of a 
    polygon/line shapefile"""
    # Check that type is what is supposed to be
    if not layerNameTypeOK(layerName, layerType): return False

    # Make sure fieldName is already there or create one
    fieldIndex=addFieldToAttrTable(layerName, fieldName, QVariant.Double )
    if fieldIndex==None: return False
    
    # Get features
    features= getLayerFeatures(layerName)
    if not features: return False

    # Add area/length to attribute table
    inFeat= QgsFeature()
    measures= []
    while features.nextFeature(inFeat):
        if layerType==QGis.Polygon: 
            measures.append(inFeat.geometry().area() )
        if layerType==QGis.Line:
            measures.append(inFeat.geometry().length() )
    res=setFieldAttrValues(layerName, fieldName, measures)

    return res 



def linkPointLayerPolygonLayer(pointLayerName, polyLayerName): 
    """Find the polygons of the polyLayername to which each point of 
    pointLayername corresponds to. Return the list with the polygon ids
    to which each point corresponds to"""

    if not layerNameTypeOK(polyLayerName, QGis.Polygon): return None
    if not layerNameTypeOK(pointLayerName, QGis.Point): return None

    polygons=getLayerFeatures(polyLayerName)
    points=getLayerFeatures(pointLayerName)

    polygonIds=[]
    inFeat1 = QgsFeature()
    inFeat2 = QgsFeature()
    while points.nextFeature(inFeat1):
        polygonId=None
        while polygons.nextFeature(inFeat2):
            if inFeat2.geometry().contains(inFeat1):
                polygonId=inFeat2.id()
                break
        polygonIds.append(polygonId)

        return polygonIds 

