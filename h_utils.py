from qgis.core import *
from PyQt4 import QtGui
from PyQt4.QtCore import QVariant
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
from osgeo import gdal, ogr
import ftools_utils
import os.path
import h_const



def floatsEqual(afloat, bfloat, exponent):
    """Returns true if float numbers are close enough. Closeness is defined by
    the exponent."""
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



def unloadLayer(layerName):
    """Unloads a layer from canvas."""
    layer=ftools_utils.getVectorLayerByName(layerName)
    if layer:
        QgsMapLayerRegistry.instance().removeMapLayer(layer.id())



def loadShapefileToCanvas(pathFilename):
    """Wraps the ftools function. It displayes an error message if something
    goes wrong."""

    if not ftools_utils.addShapeToCanvas(pathFilename):
        message="Error loading output shapefile "+pathFilename
        QtGui.QMessageBox.critical(None, 'Error', message,QtGui.QMessageBox.Ok)
        return False
    return True



def shapefileExists(path, filename):
    """Checks if a shapefile exists."""
    pathFilename=os.path.join(path, filename)
    fileExists= os.path.isfile(pathFilename+".shp")
    return fileExists



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
    if nfeats==None: return False
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
    """Finds the indexes of the elements of the list with numbers 'alist' that
    are equal to the value 'value'."""
    return [ i for i in range(len(alist))
            if floatsEqual(alist[i],value,h_const.precise) ]



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



def getMinFeatureMeasure(layerName):
    """This function returns the area/length of the smallest polygon/line of
    a shapefile."""
    # Get the type
    layer=ftools_utils.getVectorLayerByName(layerName)
    if not layer: return None
    layerType=layer.geometryType()

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
        rlayer=ftools_utils.getRasterLayerByName(layerName)
        if rlayer==None:
            message=layerName + "  not loaded or not a raster!"
        elif band<1:
            message="Band number should greater than 1!"
        elif band>rlayer.bandCount():
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



def getQueryShapeIds(layerName, filterExpr):
    """Prepare a list of feature ids that meet filterExpr."""

    # Get layer
    layer=ftools_utils.getVectorLayerByName(layerName)
    if not layer:
        message=layerName + "  not loaded!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    # Prepare the list
    featreRequest=QgsFeatureRequest().setFilterExpression(filterExpr)
    shapes=layer.getFeatures(featreRequest)
    ids = [f.id() for f in shapes]

    return ids



def setFieldAttrValues(layerName, fieldName, values):
    """Sets all values of a field of the attribute table."""

    # Get features of layer
    features= getLayerFeatures(layerName)
    if not features:
        message= layerName + " is an empty layer!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    # Get the index of fieldName
    fieldIndex=getFieldIndexByName(layerName, fieldName)
    if fieldIndex==None:
        message= layerName + " attribute table does not contain this field!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    # Start editing layer
    layer=ftools_utils.getVectorLayerByName(layerName)
    layer.startEditing()

    # Set the values of the fieldName
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



def delExistingShapefile(path, filename):
    """ Delete an existing layer."""
    if shapefileExists(path, filename):
        message="Delete shapefile "+filename+"?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No )
        if reply==QtGui.QMessageBox.No: return False
        pathFilename=os.path.join(path, filename)
        if not QgsVectorFileWriter.deleteShapeFile(pathFilename):
            message="Can't delete shapefile "+pathFilename
            QtGui.QMessageBox.critical(None,'Err',message,QtGui.QMessageBox.Ok)
            return False
    else:
        message="Shapefile "+filename+" not there!"
        QtGui.QMessageBox.critical(None,'Err',message,QtGui.QMessageBox.Ok)
        return False
    return True



def delSpecificShapes(layerName, ids):
    """Deletes the features of which the id is inside the list of ids."""

    # Get layer
    layer=ftools_utils.getVectorLayerByName(layerName)
    if not layer:
        message=layerName + "  not loaded!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    layer.startEditing()

    # Delete features that meet criteria
    for featId in ids:
        ok = layer.deleteFeature(featId)
        if not ok: return False

    layer.commitChanges()

    return ok



def createPointLayer(path, filename, coords, fieldNames, fieldTypes,
                     attrValues):
    """Creates a shapefile with points and populates its attribute table"""

    # Check arguments
    message=""
    if len(fieldNames) != len(fieldTypes):
        message="createPointLayer" + filename + "FieldNames.no <> FieldTypes.no"
    if len(fieldNames) > 1 and len(fieldNames)<>len(attrValues):
        message="createPointLayer" + filename + "FieldNames.no <> attrValues.no"
    if len(message)!=0:
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    # Delete existing layer
    if shapefileExists(path, filename):
        if not delExistingShapefile(path, filename):
            return False

    # Create empty point layer and add attribute fields
    fieldList = QgsFields()
    for fieldname,fieldtype in zip(fieldNames, fieldTypes):
        fieldList.append( QgsField(fieldname, fieldtype) )
    pathFilename=os.path.join(path, filename)
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



def createVectorFromRaster(path, rasterFileName, bandnum, outShapeFileName ):
    """Create a vector layer from a raster layer using values of provided
       band."""
    # Load existing raster
    pathFilename=os.path.join( path, rasterFileName)
    sourceRaster = gdal.Open(pathFilename)
    if not sourceRaster:
        message=pathFilename + "  not found!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    # Delete existing (if any) output shapefile
    if shapefileExists(path, outShapeFileName):
        if not delExistingShapefile(path, outShapeFileName):
            return False

    # Turn raster into vector
    band = sourceRaster.GetRasterBand(bandnum)
    if band==None:
        message="Raster " rasterFileName + " does not have band "+str(bandnum)
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False
    bandArray = band.ReadAsArray()
    driver = ogr.GetDriverByName("ESRI Shapefile")
    pathFilename=os.path.join( path, outShapeFileName)
    outDatasource = driver.CreateDataSource(pathFilename+ ".shp")
    if outDatasource==None:
        message="Could not create " + outShapeFileName
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False
    outLayer = outDatasource.CreateLayer("polygonized", srs=None)
    newField = ogr.FieldDefn('HRU_ID', ogr.OFTInteger)
    outLayer.CreateField(newField)
    gdal.Polygonize( band, None, outLayer, 0, [], callback=None )

    # Free memory and close output stream
    outDatasource.Destroy()
    sourceRaster = None

    return True



def reclassifyRaster(path, inRasterName, bandnum, minValue, rangeUpValues,
                     outRasterName):
    """ Reclassify a raster to groups defined by rangeUpValues."""

    # Get raster
    inRaster=ftools_utils.getRasterLayerByName(inRasterName)
    if not inRaster:
        message=inRasterName+ "  not loaded or not a raster!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    # Check path exists
    if not os.path.isdir(path):
        message= path + " does not exist!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False


    # Define band
    boh = QgsRasterCalculatorEntry()
    bandName=inRasterName+'@'+str(bandnum)
    boh.ref = bandName
    boh.raster = inRaster
    boh.bandNumber =bandnum

    # Prepare entries
    entries = []
    entries.append( boh )

    # Prepare calculation command
    bandNameAddStr= '<='+ bandName + ' AND ' + bandName + '<'
    i = 1
    lowerVal=0
    calcCommand=""
    for upValue in rangeUpValues:
        calcCommand = calcCommand + '( ' + str(minValue) + bandNameAddStr
        calcCommand = calcCommand + str(upValue) + ')' + '*' + str(i)
        if i!=len(rangeUpValues):
            calcCommand = calcCommand + ' + '
            minValue = upValue
            i = i + 1

    # Process calculation with input extent and resolution
    pathFilename=os.path.join( path, outRasterName) + '.tif'
    calc = QgsRasterCalculator(calcCommand, pathFilename, 'GTiff',
                               inRaster.extent(), inRaster.width(),
                               inRaster.height(), entries )
    if not calc: return False
    ok= (calc.processCalculation() == 0)

    return ok



def createDBF(path, fileName, fieldNames, fieldTypes, values):
    """Creates a new dbf file (or updates an existing) with the values provided
    in the values list (this is a list of lists in case of many fields."""

    # Check validity of arguments' length
    fieldNamesEqualFieldTypes = ( len(fieldNames)==len(fieldTypes) )
    fieldNamesEqualValueLists = ( len(values)==len(fieldTypes) )
    if not fieldNamesEqualFieldTypes or \
       not fieldNamesEqualValueLists or \
       not len(values):
        message="createDBF:" + fileName + " arguments error!"
        QtGui.QMessageBox.critical(None, 'Error', message,QtGui.QMessageBox.Ok)
        return False

    # Delete existing
    if shapefileExists(path, fileName):
        if not delExistingShapefile(path, fileName):
            return False

    # Create the list with the coordinates of dummy points
    numvalues=len(values[0])
    coords=zip([0]*numvalues, [0]*numvalues)

    # Create dummy shapefile to create the required dbf file
    ok=createPointLayer(path, fileName, coords, fieldNames, fieldTypes, values)

    return ok



def addFieldToAttrTable(layerName, fieldName, fieldType):
    """Add a fieldName to attribute table of layerName. Returns the index
    off added field"""

    # Get layer and enable editing
    layer=ftools_utils.getVectorLayerByName(layerName)
    if not layer:
        message="Layer " + layerName + " is not loaded!"
        QtGui.QMessageBox.critical(None,'Error',message,QtGui.QMessageBox.Ok)
        return None
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



def addShapeIdsToField(layerName, fieldName):
    """Add to the attribute table of a layer a field that keeps the ids of the
       shapes"""

    ok=addFieldToAttrTable(layerName, fieldName, QVariant.Int)
    if not ok: return False
    values=range(getLayerFeaturesCount(layerName))
    return setFieldAttrValues(layerName,fieldName, values)



def addMeasureToAttrTable(layerName, fieldName):
    """Add area/length of each feature to the attribute table of a
    polygon/line shapefile"""
    # Get the layer
    layer=ftools_utils.getVectorLayerByName(layerName)
    if not layer:
        message= "Layer " + layerName + " not loaded!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    # Check layer type
    layerType=layer.geometryType()
    if layerType==QGis.Point:
        message= layerName + "is a point layer. Cannot add a measure!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    # Make sure fieldName is already there or create one
    fieldIndex=addFieldToAttrTable(layerName, fieldName, QVariant.Double )
    if fieldIndex==None: 
        fieldIndex=addFieldToAttrTable(layerName, fieldName, QVariant.Double)
        if fieldIndex==None: 
            message= "Cannot add measure to layer" + layerName
            QtGui.QMessageBox.critical(None,'Err',message, QtGui.QMessageBox.Ok)
            return False

    # Get features
    features= getLayerFeatures(layerName)
    if not features:
        message= layerName + " empty layer!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    # Add area/length to attribute table
    inFeat= QgsFeature()
    measures= []
    while features.nextFeature(inFeat):
        if layerType==QGis.Polygon:
            measures.append(inFeat.geometry().area() )
        if layerType==QGis.Line:
            measures.append(inFeat.geometry().length() )
    ok=setFieldAttrValues(layerName, fieldName, measures) 
    if not ok:
        message= "error applying setFieldAttrValue on " + layerName
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
        return False

    return ok



def linkPointLayerToPolygonLayer(pointLayerName, polyLayerName):
    """Finds the polygons of the polyLayername to which each point of
    pointLayername corresponds to. Returns the list with the polygon ids
    to which each point corresponds to."""

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
            if inFeat2.geometry().contains(inFeat1.geometry()):
                polygonId=inFeat2.id()
                break
        polygonIds.append(polygonId)

    return polygonIds
