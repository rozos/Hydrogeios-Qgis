from __future__ import division
import ftools_utils
import h_const
import h_utils
from qgis.core import *
from PyQt4.QtCore import QVariant


def layerConsistenciesOK():
    """This functions checks that the area of all shapes of a polygon layer
    is positive and the the length of all shapes of a line layer is positive"""
    
    if not h_utils.getMinFeatureMeasure(h_const.subbasLayerName, 
                                h_const.subbasLayerType):
        return False

    if not h_utils.getMinFeatureMeasure(h_const.groundLayerName, 
                                h_const.groundLayerType):
        return False

    if not h_utils.getMinFeatureMeasure(h_const.riverLayerName, 
                                h_const.riverLayerType):
        return False

    # Consistency OK
    return True



def layerNamesTypesOK():
    """This function checks the type of layers employed in topology operations.
    The function returns True if the name and the type of layers is what is 
    supposed to be"""
    
    # Check if River is a line layer
    if not h_utils.layerNameTypeOK(h_const.riverLayerName, 
                                   h_const.riverLayerType):
        return False

    # Check if Irrigation is a poly layer
    if not h_utils.layerNameTypeOK(h_const.irrigLayerName, 
                                   h_const.irrigLayerType):
        return False

    # Check if Borehole is a point layer
    if not h_utils.layerNameTypeOK(h_const.borehLayerName, 
                                   h_const.borehLayerType):
        return False

    # All names and types are what expected to be
    return True



def createHydrojunctionLayer(path): 
    """This function creates a new point shapefile (or updates the existing),
    named Hydrojunction, with the nodes of River (segments endpoints),
    Irrigation (polygon centroids) and Borehole (centroid of a group of
    points). It requires River, Borehole and Irrigation be loaded in the
    project"""

    if not layerNamesTypesOK():
        return False
    
    # Get segments of River layer
    riverSegments=h_utils.getLayerFeatures(h_const.riverLayerName)
    if riverSegments==False: return False

    # Loop through segments of River layer to get ending nodes
    inFeat = QgsFeature()
    rivXList= []
    rivYList= []
    i = 0
    while riverSegments.nextFeature(inFeat):
        nodes=inFeat.geometry().asPolyline()
        if i==0:  # If this is first segment (river exit), get first point 
            coordsNum=0
        else:     # Get the last point of segment
            coordsNum=len(nodes)-1
        x,y = 0,1
        rivXList.append( nodes[coordsNum][x] )
        rivYList.append( nodes[coordsNum][y] )
        i += 1
    
    # Get the polygons of Irrigation layer 
    irrigPolygons=h_utils.getLayerFeatures(h_const.irrigLayerName)
    if not irrigPolygons: return False

    # Loop through polygons of Irrigation layer to get their centroids
    inFeat = QgsFeature()
    irgXList= []
    irgYList= []
    while irrigPolygons.nextFeature(inFeat):
        centrpoint = inFeat.geometry().centroid()
        irgXList.append(centrpoint.asPoint().x() )
        irgYList.append(centrpoint.asPoint().y() )
    
    # Get the points of Borhole layer
    borehPoints=h_utils.getLayerFeatures(h_const.borehLayerName)
    if not borehPoints: return False 

    # Get the coords and group_id of points of Borhole layer
    ( pointsXList, 
      pointsYList  ) = h_utils.getPointLayerCoords(h_const.borehLayerName)
    pointsId= h_utils.getFieldAttrValues(h_const.borehLayerName, 
                                         h_const.borehFieldNameGrp)
 
    # Make a List of coords of the gravity centres of the Borhole groups points
    borXList= []
    borYList= []
    borGrpId=set(pointsId)
    for grpid in borGrpId:
        indexes=h_utils.getElementIndexByVal(pointsId, grpid)
        groupXvals= [pointsXList[i] for i in indexes]
        borXList.append( sum(groupXvals)/len(groupXvals) )
        groupYvals= [pointsYList[i] for i in indexes]
        borYList.append( sum(groupYvals)/len(groupYvals) ) 

    # Create a new layer or update the existing
    xCoords= rivXList+irgXList+borXList
    yCoords= rivYList+irgYList+borYList 
    # Create a list with id of the junction type of each junciton
    junctType= ( [h_const.hydroJncIdNodeRiv]*len(rivXList) + 
                 [h_const.hydroJncIdNodeIrg]*len(irgXList) + 
                 [h_const.hydroJncIdNodeBor]*len(borXList)  )
    # Get the z values of the [xCoords yCoords] points
    height = []
    for x,y in zip(xCoords, yCoords):
        height.append(h_utils.getCellValue(h_const.dtmLayerName, (x, y), 1) )
    # Create the Hydrojunction layer
    createOK=h_utils.createPointLayer(path, h_const.hydroJncLayerName,
                           xCoords, yCoords, h_const.hydroJncFieldNames,
                           h_const.hydroJncFieldTypes, 
                           [junctType, [], [], [], xCoords, xCoords, height ] )

    return createOK



def linkRiverductHydrojunction(layerName, reversDirect): 
    """ This function builds the topology of River or Aqueduct layers
    (RiverDuct) assigning the appropriate Hydrojunction ids to from_node,
    to_node fields. The arguments are the shapefile name (River or Aqueduct) 
    and the direction the topology is built (River is built with revers 
    direction i.e. from exit to upstream nodes).""" 

    # Get Hydrojunction layer coordinates
    [xList, yList]= h_utils.getPointLayerCoords(h_const.hydroJncLayerName)
    if not xList: return False 

    # Get segments of riverDuct shapefile
    riverDuctSegments= h_utils.getLayerFeatures(layerName);
    if not riverDuctSegments: return False

    # Start editing layer
    layer=ftools_utils.getVectorLayerByName(layerName)
    layer.startEditing()

    # Get the id of the fields FROM_NODE, TO_NODE
    fromNode=h_utils.getFieldIndexByName(layerName, 
                                         h_const.fromNodeFieldName)
    if not fromNode: return False
    toNode=h_utils.getFieldIndexByName(layerName, 
                                       h_const.toNodeFieldName)
    if not toNode: return False

    # Loop through segments of riverDuct
    inFeat = QgsFeature()
    while riverDuctSegments.nextFeature(inFeat):
        nodes=inFeat.geometry().asPolyline()
        lastnode=len(nodes)-1
        frstnode=0
        x,y = 0,1
        if reversDirect:  # Topology is built following reverse direction
            strtPntX= nodes[lastnode][x]
            strtPntY= nodes[lastnode][y]
            endPntX=  nodes[frstnode][x]
            endPntY=  nodes[frstnode][y]
        else:
            strtPntX= nodes[frstnode][x]
            strtPntY= nodes[frstnode][y]
            endPntX=  nodes[lastnode][x]
            endPntY=  nodes[lastnode][y]
        jxyList=zip(range(0,len(xList)), xList, yList)
        for j, hydroJunctPntX, hydroJunctPntY in jxyList:
            if strtPntX==hydroJunctPntX and strtPntY==hydroJunctPntY:
                inFeat.setAttribute(fromNode, j)
            if endPntX==hydroJunctPntX and endPntY==hydroJunctPntY:
                inFeat.setAttribute(toNode, j)
            layer.updateFeature(inFeat)

    # Save edits
    layer.commitChanges()
    return True



def linkIrrigHydrojunction(): 
    """This function finds for each Irrigation polygon the corresponding 
    hydrojunciton node"""

    # Get Hydrojunction layer coordinates (x,y pairs)
    [xList, yList]= h_utils.getPointLayerCoords(h_const.hydroJncLayerName)
    if not xList: return False 

    # Get polygons of Irrigation shapefile
    irrigPolygons= h_utils.getLayerFeatures(h_const.irrigLayerName);
    if not irrigPolygons: return False

    # Get the index of "junct_id" column
    JncId=getFieldIndexByName(h_const.irrigLayerName, 
                              h_const.irrigFieldNameJncId);
    if not JncId: return False

    # Find to which x,y pair the centroid of each polygon corresponds
    inFeat=QgsFeature()
    while irrigPolygons.nextFeature(inFeat):
        centrpoint = inFeat.geometry().centroid()
        if (centrpoint.x, centrpoint.y) in zip(xList, yList):
            k=getElementIndexByVal(zip(xList, yList), 
                                   (centrpoint.x, centrpoint.y) )
            inFeat.changeAttributeValue(JuncId, k)



def linkSubbasinRiver():
    """This function finds for each subbasin the corresponding river_id,
    node_id and length of the primary river segment """

    # Get River layer
    riverSegments= h_utils.getLayerFeatures(h_const.riverLayerName)
    if not riverSegments: return False

    # Get Subbasin layer
    subbPolygons= h_utils.getLayerFeatures(h_const.subbasLayerName)
    if not subbPolygons: return False

    # Find the columns of attribute table
    rivId=h_utils.getFieldIndexByName(h_const.subbasLayerName,
                                      h_const.subbasFieldNameRivId)
    rivNode=h_utils.getFieldIndexByName(h_const.subbasLayerName,
                                        h_const.subbasFieldNameRivNode)
    primLen=h_utils.getFieldIndexByName(h_const.subbasLayerName,
                                        h_const.subbasFieldNamePrimLen)
    if not (rivId and rivNode and primLen): return False

    # Get coords of hydrojunction layer points
    [xList, yList]= getPointLayerCoords(h_const.hydroJncLayerName)

    # Check that number of river segments euqals the number of subbasins
    riversNum= getLayerFeaturesCount(h_const.riverLayerName)
    if not layerFeaturesNumberOK(h_const.subbasLayerName, riversNum): 
        return False 

    # Loop through segments of River
    inFeat = QgsFeature()
    while riverSegments.nextFeature(inFeat):
        # Get first and last point of river segment
        segment= inFeat.geometry() 
        strtPntX= segment.xat(0)
        strtPntY= segment.yat(0)
        endPntX= segment.xat(-1)
        endPntY= segment.yat(-1)
        strtPnt = QgsGeometry.fromPoint(QgsPoint(strtPntX,strtPntY))
        endPnt = QgsGeometry.fromPoint(QgsPoint(endPntX,endPntY))
        # Reset found-flag
        foundStart= False
        # Find in which subbasin this point belongs to
        inFeat2= QgsFeature()
        while subbPolygons.nextFeature(inFeat2):
            if inFeat2.geometry().contains(strtPntX):
                if not foundStart: foundStart= True
                else:
                    message="Polygons of Subbasin overlap!"
                    QtGui.QMessageBox.critical(None,'Error',message, 
                                                QtGui.QMessageBox.Yes)
                    return False 
                # Set the attributes of this polygon
                inFeat2.changeAttributeValue(rivId, inFeat1.id())
                inFeat2.changeAttributeValue(primLen,
                                             inFeat2.geometry().length())
                if (endPntX, endPntY) in zip(xList, yList):
                    k=h_utils.getElementIndexByVal(zip(xList, yList), 
                                                   (endPntX, endPntY) )
                    inFeat2.changeAttributeValue(rivNode, k)
        if not foundStart:
                message="The start of a segment is outside of the subbasin!"
                QtGui.QMessageBox.critical(None,'Error',message, 
                                            QtGui.QMessageBox.Yes)
                return False 
