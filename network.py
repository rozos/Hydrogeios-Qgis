import ftools_utils
import constants
import auxiliary
from qgis.core import *



def layerNameTypeOK(layerFileName, layerType):
    """This function checks if the type of a layer is what is supposed to be"""
    layer=ftools_utils.getVectorLayerByName(layerFileName)
    if riverLayer.type() != layerType:
        message=layerFileName + " is not a "+ str(layerType) + " layer!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Yes)
        return False
    return True



def layersNameTypeOK():
    """This function checks the type of layers employed in topology operations.
    The function returns True if the name and the type of layers is what is 
    supposed to be"""
    
    # Check if River is a line layer
    if not layerNameTypeOK(constants.riverLayer.filename, QGis.Line):
        return False

    # Check if Irrigation is a poly layer
    if not layerNameTypeOK(constants.irrigLayer.filename, QGis.Polygon):
        return False

    # Check if Borehold is a point layer
    if not layerNameTypeOK(constants.borehLayer.filename, QGis.Point):
        return False

    return True



def createHydrojunctionLayer(): 
    """This procedure creates a new point shapefile (or updates the existing),
    named Hydrojunction, with the nodes of River (segments endpoints),
    Irrigation (polygon centroids) and Borehole (centroid of a group of
    points). It requires River, Borehole and Irrigation be loaded in the
    project"""

    if not layersNameTypeOK:
        return False
    
    # Get segments of River layer
    riverLayer=ftools_utils.getVectorLayerByName(constants.riverLayer.filename)
    riverProvider=riverLayer.dataProvider()
    riverSegments=riverProvider.getFeatures()

    # Loop through segments of River layer to get ending nodes
    inFeat = QgsFeature()
    rivXList= []
    rivYList= []
    i = 0
    while riverSegments.nextFeature(inFeat)
        if i=0:  # If this is first segment (river exit), get first point 
            segment=inFeat.geometry()
            rivXList.append(segment.xat(0) )
            rivYList.append(segment.yat(0) )
        else:    # Get the last point of segment
            lasttpoint=inFeat.geometry()
            rivXList.append(segment.xat(-1))
            rivYList.append(segment.yat(-1))
        i += 1
    
     # Get the polygons of Irrigation layer
    irrigLayer=ftools_utils.getVectorLayerByName(constants.irrigLayer.filename)
    irrigProvider=irrigLayer.dataProvider()
    irrigPolygons=irrigProvider.getFeatures()

    # Loop through polygons of Irrigation layer to get their centroids
    inFeat = QgsFeature()
    irgXList= []
    irgYList= []
    while irrigPolygons.nextFeature(inFeat)
        centrpoint = inFeat.geometry().centroid()
        irgXList.append(centrpoint.x)
        irgXList.append(centrpoint.y)

    # Get the points of Borhold layer
    inFeat = QgsFeature()
    pointsXList= []
    pointsYList= []
    borGrpId= []
    groupfield=getFieldIndexByName(riverDuct, "GROUP")
    if fieldId==-1: return False
    while irrigPolygons.nextFeature(inFeat)
        point=inFeat.geometry()
        pointsXList.append(point.x)
        pointsYList.append(point.y)
        attribs=point.attributes()
        borGrpId.append(attribs(groupField))

    # List of coords for the gravity centres of the pnts of Borhole groups

    # Create a new layer or update the existing
    fieldX= rivXList+irgXList+borXList
    fieldY= rivYList+irgYList+borYList
    fieldJuncType= [ [constants.nodeRivId]*len(rivXList) + 
                      [constants.nodeIrgId]*len(irgXList) + 
                      [constants.nodeBorId]*len(borXList) ]
    createPointLayer(constants.hydroJunctLayer.filename, 
                     constants.hydroJunctLayer.fieldnames, 
                     [fieldJuncType, [], [], [], [], fieldX, fieldY, [] ]



def buildRiverductTopologyr(riverDuct, reversDirect):
    """ This function builds the topology of River or Aqueduct shapefiles
    (Riverduct). The arguments are the shapefile (River or Aqueduct) and the
    direction the topology is built (River is built with revers direction i.e.
    from exit to upstream nodes""" 

    # Get points of HydroJunction layer
    hydroJunctLayer=ftools_utils.getVectorLayerByName(constants.hydroJunctLayer.filename)
    hydroJunctProvider= hydroJunctLayer.dataProvider()
    hydroJunctPoints= hydroJunctProvider.getFeatures()

    # Get X,Y of each Hydrojunction point
    xList= []
    yList= []
    inFeat = QgsFeature()
    while hydroJunctPoints.nextFeature(inFeat)
         xList.append(inFeat.geometry().x )
         yList.append(inFeat.geometry().y )

    # Get segments of riverDuct shapefile
    riverDuctProvider= riverDuct.dataProvider() 
    riverDuctSegments= riverDuctProvider.getFeatures()

    # Get the id of the fields FROM_NODE, TO_NODE
    fromNode=getFieldIndexByName(riverDuct, "FROM_NODE")
    if fromNode==-1: return False
    toNode=getFieldIndexByName(riverDuct, "TO_NODE")
    if toNode==-1: return False

    # Loop through segments of riverDuct
    inFeat = QgsFeature()
    i=0
    while riverDuctSegments.nextFeature(inFeat)
        segment= inFeat.geometry() 
        if reversDirect:  # If topology is built reverse direction
            strtpntX= segment.xat(-1)
            strtpntY= segment.yat(-1)
            endtpntX= segment.xat(0)
            endtpntY= segment.yat(0)
        else:
            strtpntX= segment.xat(0)
            strtpntY= segment.yat(0)
            endtpntX= segment.xat(-1)
            endtpntY= segment.yat(-1)
        j=0
        for hydroJunctPntX, hydroJunctPntY in zip(xList,yList):
            if strtpntX==hydroJunctPntX and strtpntY==hydroJunctPntY:
                riverDuctSegments.changeAttributeValues({i:{fromNode, j})
            if endtpntX==hydroJunctPntX and endpntY==hydroJunctPntY:
                riverDuctSegments.changeAttributeValues({i:{toNode, j})
            j=j+1
        i=i+1 
