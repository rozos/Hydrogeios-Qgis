from qgis.core import *
import os.path
import ftools_utils
import h_utils

def intersect( path, inputLayerAname, inputLayerBname, outputLayerName):

    # make sure layer A is loaded
    layerAloaded=h_utils.isShapefileLoaded(inputLayerAname)
    if not layerAloaded:
        pathFilenameA=os.path.join( path, inputLayerAname)
        if not h_utils.loadShapefileToCanvas(pathFilenameA+".shp" ):
            return False

    # make sure layer B is loaded
    layerBloaded=h_utils.isShapefileLoaded(inputLayerBname)
    if not layerBloaded:
        pathFilenameB=os.path.join( path, inputLayerBname) 
        if not h_utils.loadShapefileToCanvas(path, pathFilenameB+".shp" ):
            return False

    # Del output shapefile
    h_utils.unloadLayer(outputLayerName)
    outpathFilename=os.path.join( path, outputLayerName+".shp") 
    fileExists= os.path.isfile(outpathFilename)
    if fileExists:
        ok=h_utils.delExistingShapefile(path, outputLayerName)
        if not ok: return False

    # Get layers and providers
    vproviderA = h_utils.getLayerProvider(inputLayerAname)
    vproviderB = h_utils.getLayerProvider(inputLayerBname)
    vlayerA = ftools_utils.getVectorLayerByName(inputLayerAname)
    vlayerB = ftools_utils.getVectorLayerByName(inputLayerBname)

    mySelectionA=None
    mySelectionB=None
    GEOS_EXCEPT = True
    FEATURE_EXCEPT = True

    # check for crs compatibility
    crsA = vproviderA.crs()
    crsB = vproviderB.crs()
    if not crsA.isValid() or not crsB.isValid():
        crs_match = None
    else:
        crs_match = crsA == crsB
    fields = ftools_utils.combineVectorFields( vlayerA, vlayerB )
    writer = QgsVectorFileWriter( outpathFilename, "UTF-8", fields,
                                  vproviderA.geometryType(), vproviderA.crs() )
    if writer.hasError():
        message="Unable to create " + outpathFilename
        QtGui.QMessageBox.critical(None, 'Error', message,QtGui.QMessageBox.Ok)
        return False

    inFeatA = QgsFeature()
    inFeatB = QgsFeature()
    outFeat = QgsFeature()
    nElement = 0

    index = ftools_utils.createIndex( vproviderB )

    # there is selection in input layer
    if mySelectionA:
        nFeat = vlayerA.selectedFeatureCount()
        selectionA = vlayerA.selectedFeatures()
        #self.emit( SIGNAL( "runStatus(PyQt_PyObject)" ), 0)
        #self.emit( SIGNAL( "runRange(PyQt_PyObject)" ), ( 0, nFeat ) )
        # we have selection in overlay layer
        if mySelectionB:
            selectionB = vlayerB.selectedFeaturesIds()
            for inFeatA in selectionA:
                nElement += 1
                #self.emit( SIGNAL( "runStatus(PyQt_PyObject)" ), nElement )
                geom = QgsGeometry( inFeatA.geometry() )
                atMapA = inFeatA.attributes()
                intersects = index.intersects( geom.boundingBox() )
                for id in intersects:
                    if id in selectionB:
                        slctFeat=QgsFeatureRequest().setFilterFid( int( id ) )
                        vproviderB.getFeatures( slctFeat).nextFeature( inFeatB )
                        tmpGeom = QgsGeometry( inFeatB.geometry() )
                        try:
                            if geom.intersects( tmpGeom ):
                                atMapB = inFeatB.attributes()
                                intergeom=( geom.intersection( tmpGeom ) )
                                int_geom = QgsGeometry(intergeom)
                                if int_geom.wkbType() == 0:
                                    int_com = geom.combine( tmpGeom )
                                    int_sym = geom.symDifference( tmpGeom )
                                    intcomdif= int_com.difference( int_sym ) 
                                    int_geom = QgsGeometry(intcomdif) 
                                try:
                                    # Geometry list: prevents writing error
                                    # in geometries of different types
                                    # produced by the intersection
                                    # fix #3549
                                    geomType=geom.wkbType() 
                                    gList = ftools_utils.getGeomType(geomType)
                                    if int_geom.wkbType() in gList:
                                        outFeat.setGeometry( int_geom )
                                        outFeat.setAttributes( atMapA + atMapB )
                                        writer.addFeature( outFeat )
                                except:
                                    FEATURE_EXCEPT = False
                                    continue
                        except:
                            GEOS_EXCEPT = False
                            break
        # we don't have selection in overlay layer
        else:
            for inFeatA in selectionA:
                nElement += 1
                #self.emit( SIGNAL( "runStatus(PyQt_PyObject)" ), nElement )
                geom = QgsGeometry( inFeatA.geometry() )
                atMapA = inFeatA.attributes()
                intersects = index.intersects( geom.boundingBox() )
                for id in intersects:
                    slctFeat=QgsFeatureRequest().setFilterFid( int( id ) ) 
                    vproviderB.getFeatures( slctFeat).nextFeature( inFeatB )
                    tmpGeom = QgsGeometry( inFeatB.geometry() )
                    try:
                        if geom.intersects( tmpGeom ):
                            atMapB = inFeatB.attributes()
                            int_geom = QgsGeometry( geom.intersection( tmpGeom))
                            if int_geom.wkbType() == 0:
                                int_com = geom.combine( tmpGeom )
                                int_sym = geom.symDifference( tmpGeom )
                                intcomdif=int_com.difference( int_sym ) 
                                int_geom = QgsGeometry(intcomdif)
                            try:
                                gList = ftools_utils.getGeomType(geom.wkbType())
                                if int_geom.wkbType() in gList:
                                    outFeat.setGeometry( int_geom )
                                    outFeat.setAttributes( atMapA + atMapB )
                                    writer.addFeature( outFeat )
                            except:
                                EATURE_EXCEPT = False
                                continue
                    except:
                        GEOS_EXCEPT = False
                        break
    # there is no selection in input layer
    else:
        nFeat = vproviderA.featureCount()
        #self.emit( SIGNAL( "runStatus(PyQt_PyObject)" ), 0)
        #self.emit( SIGNAL( "runRange(PyQt_PyObject)" ), ( 0, nFeat ) )
        # we have selection in overlay layer
        if mySelectionB:
            selectionB = vlayerB.selectedFeaturesIds()
            fitA = vproviderA.getFeatures()
            while fitA.nextFeature( inFeatA ):
                nElement += 1
                #self.emit( SIGNAL( "runStatus(PyQt_PyObject)" ), nElement )
                geom = QgsGeometry( inFeatA.geometry() )
                atMapA = inFeatA.attributes()
                intersects = index.intersects( geom.boundingBox() )
                for id in intersects:
                    if id in selectionB:
                        slctFeat=QgsFeatureRequest().setFilterFid( int( id ) ) 
                        vproviderB.getFeatures(slctFeat).nextFeature( inFeatB )
                        tmpGeom = QgsGeometry( inFeatB.geometry() )
                        try:
                            if geom.intersects( tmpGeom ):
                                atMapB = inFeatB.attributes()
                                geointer=geom.intersection(tmpGeom)
                                int_geom = QgsGeometry(geointer)
                                if int_geom.wkbType() == 0:
                                    int_com = geom.combine( tmpGeom )
                                    int_sym = geom.symDifference( tmpGeom )
                                    intcondif= int_com.difference( int_sym ) 
                                    int_geom = QgsGeometry( intcomdif)
                                try:
                                    geomType=geom.wkbType()
                                    gList = ftools_utils.getGeomType(geomType)
                                    if int_geom.wkbType() in gList:
                                        outFeat.setGeometry( int_geom )
                                        outFeat.setAttributes( atMapA + atMapB )
                                        writer.addFeature( outFeat )
                                except:
                                    FEATURE_EXCEPT = False
                                    continue
                        except:
                            GEOS_EXCEPT = False
                            break
        # we have no selection in overlay layer
        else:
            fitA = vproviderA.getFeatures()
            while fitA.nextFeature( inFeatA ):
                nElement += 1
                #self.emit( SIGNAL( "runStatus(PyQt_PyObject)" ), nElement )
                geom = QgsGeometry( inFeatA.geometry() )
                atMapA = inFeatA.attributes()
                intersects = index.intersects( geom.boundingBox() )
                for id in intersects:
                    slctFeat=QgsFeatureRequest().setFilterFid( int( id ) ) 
                    vproviderB.getFeatures(slctFeat).nextFeature( inFeatB )
                    tmpGeom = QgsGeometry( inFeatB.geometry() )
                    try:
                        if geom.intersects( tmpGeom ):
                            atMapB = inFeatB.attributes()
                            int_geom = QgsGeometry( geom.intersection(tmpGeom ))
                            if int_geom.wkbType() == 0:
                                int_com = geom.combine( tmpGeom )
                                int_sym = geom.symDifference( tmpGeom )
                                intcomdif=int_com.difference( int_sym ) 
                                int_geom = QgsGeometry( intcomdif)

                            try:
                                gList = ftools_utils.getGeomType(geom.wkbType())
                                if int_geom.wkbType() in gList:
                                    outFeat.setGeometry( int_geom )
                                    outFeat.setAttributes( atMapA + atMapB )
                                    writer.addFeature( outFeat )
                            except:
                                FEATURE_EXCEPT = False
                                continue
                    except:
                        GEOS_EXCEPT = False
                        break
    del writer

    return True
