from qgis.core import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QVariant, QFileInfo
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
from osgeo import gdal, ogr
import os.path
import processing
import h_const
import h_initLayers



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



def unloadShapefile(layerName):
    """Unloads a shapefile from canvas. Returns true if it was loaded."""
    if isLayerLoaded(layerName):
        layers=QgsProject.instance().mapLayersByName(layerName)
        if len(layers)>0:
            QgsProject.instance().removeMapLayer(layers[0])
        return True
    else:
        return False



def unloadRaster(layerName):
    """Unloads a raster from canvas. Returns true if it was loaded."""
    layer=getRasterLayerByName(layerName)
    if layer:
        QgsProject.instance().removeMapLayer(layer)
        return True
    else:
        return False



def loadShapefileToCanvas(prjpath, layerName):
    """Wraps the ftools function. It displayes an error message if something
    goes wrong."""

    if isLayerLoaded(layerName):
        return True
    pathFilename=os.path.join(prjpath, layerName+".shp")
    if not addShapeToCanvas(pathFilename):
        message="Error loading shapefile "+pathFilename
        QMessageBox.critical(None, 'Error', message, QMessageBox.Ok)
        return False
    return True



def loadRasterfileToCanvas(prjpath, layerName):
    """Loads a raste to canvas."""
    if isLayerLoaded(layerName):
        return True
    pathFilename=os.path.join(prjpath, layerName+".tif")
    file_info = QFileInfo(pathFilename)
    if file_info.exists():
        layer_name = file_info.completeBaseName()
    else:
        message="Error loading raster"+pathFilename
        QMessageBox.critical(None, 'Error', message, QMessageBox.Ok)
        return False
    layeropts=QgsRasterLayer.LayerOptions(True)    
    rlayer_new = QgsRasterLayer( pathFilename, layer_name, 'gdal', layeropts )
    if rlayer_new.isValid():
        QgsProject.instance().addMapLayer(rlayer_new)
        return True
    else:
        return False



def isLayerLoaded(layerName):
    """Check if a shapefile is loaded into canvas."""
    layers=QgsProject.instance().mapLayersByName(layerName)
    if len(layers)>0: return True
    else: return False



def isRasterLoaded(layerName):
    """Check if a raster is loaded into canvas."""
    layers=QgsProject.instance().mapLayersByName(layerName)
    if len(layers)>0: return True
    else: return False



def shapefileExists(prjpath, layerName):
    """Checks if a shapefile exists."""
    pathFilename=os.path.join(prjpath, layerName)
    fileExists= os.path.isfile(pathFilename+".shp")
    return fileExists



def layerNameTypeOK(layerName, expectedgeomType):
    """This function checks the geometry of a layer is what is supposed to be"""
    layers=QgsProject.instance().mapLayersByName(layerName)
    if len(layers)==0:
        message=layerName + "  not loaded!"
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return False
    layer=layers[0]
    if layer.geometryType() != expectedgeomType:
        message= layerName + " is a type " + str(layer.geometryType()) + \
                  " layer! A type " + str(expectedgeomType) + " was expected."
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return False
    return True



def layerFeaturesNumberOK(layerName, featuresNum):
    """This function checks if the number of features in a shapefile equals to
    the expected number of features."""
    nfeats=getLayerFeaturesCount(layerName)
    if nfeats==None: return False
    if nfeats!=featuresNum:
        message=layerName+" has not "+ str(featuresNum) + " features!"
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return False
    return True



def getSegmentPoints(layerName, firstORlast):
    """Get coordinates of the ending nodes of the segments of a line layer."""

    if not layerNameTypeOK(layerName, QgsWkbTypes.LineGeometry): 
        print("getSegmentPoints: Wrong layer geometry type!") 
        return False

    segments=getLayerFeatures(layerName)
    if segments==None: 
        print("getSegmentPoints: Could not get layer segments!") 
        return False 

    inFeat = QgsFeature()
    Points= []
    x,y = 0,1
    while segments.nextFeature(inFeat):
        nodes=inFeat.geometry().asMultiPolyline()
        if len(nodes)==0:
            print("getSegmentPoints: Could not get nodes of polyline!") 
            return []
        if firstORlast=="first":
            frstnode=0
            Points.append(nodes[0][frstnode])
        elif firstORlast=="last":
            lastnode=len(nodes[0])-1
            Points.append(nodes[0][lastnode])
        elif firstORlast=="mid":
            midnode=int(len(nodes[0])/2)
            Points.append(nodes[0][midnode])
        else: 
            print("getSegmentPoints: Uknown second argument!") 
            return []

    return Points 



def getFieldIndexByName(layerName, fieldName, warn=True):
    """Returns the index of the field named fieldName of the attribute table
    of the layer 'vlayer'. If no field with name fieldName, returns None and
    displays an error dialog."""
    provider=getLayerProvider(layerName)
    if provider!=None:
        i = 0
        fieldsList=provider.fields()
        for field in fieldsList:
            if field.name()==fieldName:
                return i
            i = i + 1
    else:
        print("Layer " + layerName + " not found!")
        return None

    # No field with this name found
    if warn:
        message="Field with name "+str(fieldName)+" not found in layer " +\
                 str(layerName)
        QMessageBox.warning(None,'Error',message, QMessageBox.Ok)
    return None



def getElementIndexByVal(alist, value):
    """Finds the indexes of the elements of the list with numbers 'alist' that
    are equal to the value 'value'."""
    if type(value==float):
        return [ i for i in range(len(alist))
                if floatsEqual(alist[i],value,h_const.precise) ]
    if type(value==qgis._core.QgsPointXY):
        return [ i for i in range(len(alist)) if alist[i]==value ]



def getPointLayerCoords(layerName):
    """This function returns the coordinates of a point layer.
    returns (xList, yList). """
    # Check if it is a point layer
    if not layerNameTypeOK(layerName, QgsWkbTypes.PointGeometry): return None

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
    if not layerNameTypeOK(layerName, QgsWkbTypes.PolygonGeometry):
        return None

    # Get polygons of layerName
    polygons= getLayerFeatures(layerName)
    if polygons==None: return None

    coords= []
    inFeat=QgsFeature()
    while polygons.nextFeature(inFeat):
        centrpoint = inFeat.geometry().centroid().asPoint()
        coords.append( (centrpoint.x(), centrpoint.y()) )

    return coords



def getLayerProvider(layerName):
    """This function returns the dataprovider of a loaded layer"""
    layers=QgsProject.instance().mapLayersByName(layerName)
    if len(layers)==0:
        message=layerName + "  not loaded!"
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return None
    layer=layers[0]
    provider= layer.dataProvider()

    return provider



def getLayerFeatures(layerName):
    """This function returns the features of a shapefile."""
    provider= getLayerProvider(layerName)
    if provider==None: return None
    features= provider.getFeatures()
    return features



def getLayerFeaturesCount(layerName):
    """This function returns the number of features of a shapefile."""
    provider= getLayerProvider(layerName)
    if provider==None: return None
    return provider.featureCount()



def getMinFeatureMeasure(layerName):
    """This function returns the area/length of the smallest polygon/line of
    a shapefile."""
    # Get the type
    layers=QgsProject.instance().mapLayersByName(layerName)
    if len(layer)==0: return None 
    layer=layers[0]
    layerType=layer.geometryType()

    # Return 0 if it is point layer
    if layerType==QgsLayerItem.Point: return 0

    # Get features
    features= getLayerFeatures(layerName)
    if features==None: return None

    # Loop to find smalest polygon
    inFeat= QgsFeature()
    minfeature=1e12 # An arbitrary large number
    while features.nextFeature(inFeat):
        if layerType==QgsLayerItem.Polygon:
            minfeature=min(minfeature, inFeat.geometry().area() )
        if layerType==QgsLayerItem.Line:
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
        if rlayer==None:
            message=layerName + "  not loaded or not a raster!"
        elif band<1:
            message="Band number should greater than 1!"
        elif band>rlayer.bandCount():
            message=layerName + "  has not that many bands!"
    if len(message)>0:
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return None

    identity=rlayer.dataProvider().identify( QgsPointXY(coords[0], coords[1]),
                                           QgsRaster.IdentifyFormatValue )
    return identity.results()[band]



def getFieldAttrValues(layerName, fieldName):
    """Gets all values of a field of the attribute table."""
    features=getLayerFeatures(layerName)
    if features==None:return None
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
    layers=QgsProject.instance().mapLayersByName(layerName)
    if len(layers)==0:
        message=layerName + "  not loaded!"
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return False
    layer=layers[0]

    # Prepare the list
    featreRequest=QgsFeatureRequest().setFilterExpression(filterExpr)
    shapes=layer.getFeatures(featreRequest)
    ids = [f.id() for f in shapes]

    return ids



def setFieldAttrValues(layerName, fieldName, values):
    """Sets all values of a field of the attribute table."""

    # Get features of layer
    features= getLayerFeatures(layerName)
    if features==None:
        message= layerName + " is an empty layer!"
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return False

    # Get the index of fieldName
    fieldIndex=getFieldIndexByName(layerName, fieldName)
    if fieldIndex==None:
        message= layerName + " attribute table does not contain this field!"
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return False

    # Start editing layer
    layers=QgsProject.instance().mapLayersByName(layerName)
    layer=layers[0]
    layer.startEditing()

    # Set the values of the fieldName
    i=0
    inFeat=QgsFeature()
    while features.nextFeature(inFeat):
        if i>=len(values): break
        inFeat.setAttribute(fieldIndex, values[i])
        layer.updateFeature(inFeat)
        i=i+1

    # Save edits
    layer.commitChanges()
    return True



def delExistingShapefile(prjpath, filename):
    """ Delete an existing layer."""
    if shapefileExists(prjpath, filename):
        message="Delete shapefile "+filename+"?"
        reply=QMessageBox.question(None, 'Delete', message,
                                   QMessageBox.Yes|QMessageBox.No )
        if reply==QMessageBox.No: return False
        pathFilename=os.path.join(prjpath, filename)
        if not QgsVectorFileWriter.deleteShapeFile(pathFilename):
            message="Can't delete shapefile "+pathFilename
            QMessageBox.critical(None,'Err',message,QMessageBox.Ok)
            return False
    else:
        message="Shapefile "+filename+" not there!"
        QMessageBox.critical(None,'Err',message,QMessageBox.Ok)
        return False
    return True



def delSpecificShapes(layerName, ids):
    """Deletes the features of which the id is inside the list of ids."""

    # Get layer
    layers=QgsProject.instance().mapLayersByName(layerName)
    if len(layers)==0:
        message=layerName + "  not loaded!"
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return False
    layer=layers[0]

    layer.startEditing()

    # Delete features that meet criteria
    for featId in ids:
        ok = layer.deleteFeature(featId)
        if not ok: return False

    layer.commitChanges()

    return True



def delField(layerName, fieldName):
    """Deletes the the fieldName from attribute table of layerName."""
    
    fieldindex=getFieldIndexByName(layerName, fieldName)
    if fieldindex==None: return False

    provider=getLayerProvider(layerName)
    if provider==None: return False
    layers=QgsProject.instance().mapLayersByName(layerName)
    layer=layers[0]

    layer.startEditing()
    ok = provider.deleteAttributes([fieldindex])
    if not ok: return False
    layer.commitChanges()

    return True



def createPointLayer(prjpath, layerName, points, fieldNames, fieldTypes,
                     attrValues):
    """Creates a shapefile with points and populates its attribute table"""

    # Check arguments
    message=""
    if len(fieldNames) != len(fieldTypes):
        message="createPointLayer: "+ layerName+"FieldNames.no <> FieldTypes.no"
    if len(fieldNames) > 1 and len(fieldNames)!=len(attrValues):
        message="createPointLayer: "+ layerName+"FieldNames.no <> attrValues.no"
    if len(message)!=0:
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return False

    # Delete existing layer
    unloadShapefile(layerName)
    if shapefileExists(prjpath, layerName):
        if not delExistingShapefile(prjpath, layerName):
            return False

    # Create empty point layer
    pathFilename=os.path.join(prjpath, layerName)
    QgsFieldsToAdd=QgsFields()
    for iname, itype in zip(fieldNames, fieldTypes):
        QgsFieldsToAdd.append(QgsField(iname, itype))
    writer= QgsVectorFileWriter(pathFilename, "utf8", QgsFieldsToAdd,
                                QgsWkbTypes.Point, 
                                QgsCoordinateReferenceSystem(h_const.projectcrs)
                                , "ESRI Shapefile")
    if writer.hasError() != QgsVectorFileWriter.NoError:
        message="Error creating shapefile "+filename
        QMessageBox.critical(None,'Error',message,QMessageBox.Ok)
        return False

    # Add points to layer
    npoints= sum(1 for _ in points) 
    for i, point in zip( range(0,npoints), points):
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPointXY(point))
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


def createVectorFromRaster(prjpath, rasterFileName, bandnum, outShapeFileName,
                           outShapeId):
    """Create a vector layer from a raster layer using values of provided
       band."""
    # Load existing raster
    pathFilename=os.path.join( prjpath, rasterFileName)
    sourceRaster = gdal.Open(pathFilename)
    if not sourceRaster:
        message=pathFilename + "  not found!"
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return False

    # Delete existing (if any) output shapefile
    if shapefileExists(prjpath, outShapeFileName):
        if not delExistingShapefile(prjpath, outShapeFileName):
            return False

    # Turn raster into vector
    band = sourceRaster.GetRasterBand(bandnum)
    if band==None:
        message="Raster " + rasterFileName + " does not have band "+str(bandnum)
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return False
    bandArray = band.ReadAsArray()
    driver = ogr.GetDriverByName("ESRI Shapefile")
    pathFilename=os.path.join( prjpath, outShapeFileName)
    outDatasource = driver.CreateDataSource(pathFilename+ ".shp")
    if outDatasource==None:
        message="Could not create " + outShapeFileName
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return False
    outLayer = outDatasource.CreateLayer("polygonized", srs=None)
    newField = ogr.FieldDefn(outShapeId, ogr.OFTInteger)
    outLayer.CreateField(newField)
    gdal.Polygonize( band, None, outLayer, 0, [], callback=None )

    # Free memory and close output stream
    outDatasource.Destroy()
    sourceRaster = None

    return True



def reclassifyRaster(prjpath, inRasterName, bandnum, minValue, tupleUpValues,
                     outRasterName):
    """ Reclassify a raster to groups defined by tupleUpValues."""

    # Get raster
    inRaster=getRasterLayerByName(inRasterName)
    if not inRaster:
        message=inRasterName+ "  not loaded or not a raster!"
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return False

    # Check prjpath exists
    if not os.path.isdir(prjpath):
        message= prjpath + " does not exist!"
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
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
    for upValue in tupleUpValues:
        calcCommand = calcCommand + '( ' + str(minValue) + bandNameAddStr
        calcCommand = calcCommand + str(upValue) + ')' + '*' + str(i)
        if i!=len(tupleUpValues):
            calcCommand = calcCommand + ' + '
            minValue = upValue
            i = i + 1

    # Process calculation with input extent and resolution
    pathFilename=os.path.join( prjpath, outRasterName) + '.tif'
    calc = QgsRasterCalculator(calcCommand, pathFilename, 'GTiff',
                               inRaster.extent(), inRaster.width(),
                               inRaster.height(), entries )
    if not calc: return False
    ok= (calc.processCalculation() == 0)

    return ok



def createDBF(prjpath, fileName, fieldNames, fieldTypes, values):
    """Creates a new dbf file (or updates an existing) with the values provided
    in the values list (this is a list of lists in case of many fields."""

    # Check validity of arguments' length
    fieldNamesEqualFieldTypes = ( len(fieldNames)==len(fieldTypes) )
    fieldNamesEqualValueLists = ( len(values)==len(fieldTypes) )
    if not fieldNamesEqualFieldTypes or \
       not fieldNamesEqualValueLists or \
       not len(values):
        message="createDBF:" + fileName + " arguments error!"
        QMessageBox.critical(None, 'Error', message,QMessageBox.Ok)
        return False

    # Delete existing
    if shapefileExists(prjpath, fileName):
        if not delExistingShapefile(prjpath, fileName):
            return False

    # Create the list with the coordinates of dummy points
    numvalues=len(values[0])
    coords=zip([0]*numvalues, [0]*numvalues)

    # Create dummy shapefile to create the required dbf file
    ok=createPointLayer(prjpath, fileName, coords, fieldNames,fieldTypes,values)

    return ok



def addFieldToAttrTable(layerName, fieldName, fieldType):
    """Add a fieldName to attribute table of layerName. Returns the index
    off added field"""

    # Get layer and enable editing
    layers=QgsProject.instance().mapLayersByName(layerName)
    if len(layers)==0:
        message="Layer " + layerName + " is not loaded!"
        QMessageBox.critical(None,'Error',message,QMessageBox.Ok)
        return None
    layer=layers[0]

    layer.startEditing()

    # Get dataprovider
    provider=getLayerProvider(layerName)
    if provider==None:
        print("Layer " + layerName + " not found!")
        return None

    # Check if the fieldName already exists and if not add one
    fieldIndex=getFieldIndexByName(layerName, fieldName, warn=False)
    if fieldIndex!=None:
        # Make sure fieldName is the expected field type
        field=provider.fields()[fieldIndex]
        if field.type() != fieldType:
            message="Field " + str(fieldName) + " of " + str(layerName) + \
                    " is type " + str(field.type()) + " whereas expected " + \
                    str(fieldType) + "!"
            QMessageBox.critical(None,'Err',message,QMessageBox.Ok)
            print("Type " + field.typeName() + " field " + field.name() + "!")
            # return None # Comment-out until bug QGIS bug #20156 is resolved
    else:
        ok = provider.addAttributes( [ QgsField(fieldName,fieldType) ] )
        if not ok:
            message="Could not add a field to layer" + str(layerName)
            QMessageBox.critical(None,'Err',message,QMessageBox.Ok)
            return None
        layer.updateFields()
        fieldIndex=getFieldIndexByName(layerName, fieldName)

    # Save changes and return field index
    layer.commitChanges()
    return fieldIndex



def addShapeIdsToAttrTable(layerName, fieldName):
    """Add to the attribute table of a layer a field that keeps the ids of the
       shapes"""
    if addFieldToAttrTable(layerName, fieldName, QVariant.Int)==None:
        return False
    values=range(getLayerFeaturesCount(layerName))
    return setFieldAttrValues(layerName,fieldName, values)



def addMeasureToAttrTable(layerName, fieldName):
    """Add area/length of each feature to the attribute table of a
    polygon/line shapefile"""
    # Get the layer
    layers=QgsProject.instance().mapLayersByName(layerName)
    if len(layers)==0:
        message= "Layer " + layerName + " not loaded!"
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return False
    layer=layers[0]

    # Check layer type
    layerType=layer.geometryType()
    if layerType==QgsLayerItem.Point:
        message= layerName + "is a point layer. Cannot add a measure!"
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return False

    # Make sure fieldName is already there or create one
    fieldIndex=addFieldToAttrTable(layerName, fieldName, QVariant.Double )
    if fieldIndex==None: 
        fieldIndex=addFieldToAttrTable(layerName, fieldName, QVariant.Double)
        if fieldIndex==None: 
            message= "Cannot add measure to layer" + layerName
            QMessageBox.critical(None,'Err',message, QMessageBox.Ok)
            return False

    # Get features
    features= getLayerFeatures(layerName)
    if features==None:
        message= layerName + " empty layer!"
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return False

    # Add area/length to attribute table
    inFeat= QgsFeature()
    measures= []
    while features.nextFeature(inFeat):
        if layerType==QgsLayerItem.Polygon:
            measures.append(inFeat.geometry().area() )
        if layerType==QgsLayerItem.Line:
            measures.append(inFeat.geometry().length() )
    ok=setFieldAttrValues(layerName, fieldName, measures) 
    if not ok:
        message= "error applying setFieldAttrValue on " + layerName
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return False

    return ok



def linkPointLayerToPolygonLayer(pointLayerName, polyLayerName):
    """Finds the polygons of the polyLayername to which each point of
    pointLayername corresponds to. Returns the list with the polygon ids
    to which each point corresponds to."""

    if not layerNameTypeOK(polyLayerName, QgsWkbTypes.PolygonGeometry): 
        print("linkPointLayerToPolygonLayer: " +polyLayerName+ " wrong layer!")
        return None
    if not layerNameTypeOK(pointLayerName, QgsWkbTypes.PointGeometry): 
        print("linkPointLayerToPolygonLayer: " +pointLayerName+ " wrong layer!")
        return None

    points=getLayerFeatures(pointLayerName)
    if points==None:
        print("linkPointLayerToPolygonLayer: " +pointLayerName+ " no points!")
        return None

    polygonIds=[]
    inFeat1 = QgsFeature()
    inFeat2 = QgsFeature()
    while points.nextFeature(inFeat1):
        polygons=getLayerFeatures(polyLayerName)
        polygonId=None
        while polygons.nextFeature(inFeat2):
            if inFeat2.geometry().contains(inFeat1.geometry()):
                polygonId=inFeat2.id()
                break
        polygonIds.append(polygonId)

    return polygonIds



def dissolve(projectpath, dissolve_layer, outlayerName):
    layers=QgsProject.instance().mapLayersByName(dissolve_layer) 
    inlayer=os.path.join(projectpath, dissolve_layer+".shp")
    outlayer=os.path.join(projectpath, outlayerName+".shp")
    try:
        processing.run('qgis:dissolve', {'FIELD': ['DN'], 'INPUT': inlayer, 
                        'OUTPUT':outlayer} )
    except Exception as e:
        print(str(e))
        return False
        
    return True



def copyShapefile(origShapefile, copyShapefile):
    pass



def addFieldsToAttrTable(prjpath, layerName, fieldTypes, fieldNames):

    # Make sure the layer is loaded 
    wasloaded=isLayerLoaded(layerName)
    if not wasloaded:
        if not loadShapefileToCanvas(prjpath, layerName):
            print("Problem loading layer " + layerName + "!")
            return False

    # Make sure all required fields are there
    for fieldname,fieldtype in zip(fieldNames, fieldTypes):
        if addFieldToAttrTable(layerName, fieldname, fieldtype)==None:
            print("Problem in field " + fieldname + "!")
            return False

    # Unload if it was not loaded
    if not wasloaded:
        if not loadShapefileToCanvas(prjpath, layerName):
            return unloadShapefile(layerName)

    return True



# Return QgsRasterLayer from a layer name ( as string )
def getRasterLayerByName( myName ):
    layermap = QgsProject.instance().mapLayers()
    for key, layer in layermap.items():
        if layer.type() == QgsMapLayer.RasterLayer and layer.name() == myName:
            if layer.isValid():
                return layer
            else:
                return None



# Convinience function to add a vector layer to canvas based on input shapefile path ( as string )
def addShapeToCanvas( shapefile_path ):
    file_info = QFileInfo( shapefile_path )
    if file_info.exists():
        layer_name = file_info.completeBaseName()
    else:
        return False
    vlayer_new = QgsVectorLayer( shapefile_path, layer_name, "ogr" )
    if vlayer_new.isValid():
        QgsProject.instance().addMapLayers( [vlayer_new] )
        return True
    else:
        return False
