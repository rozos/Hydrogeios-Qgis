from __future__ import division 
from qgis.core import *
from PyQt4 import QtGui
from PyQt4.QtCore import QVariant
import ftools_utils
import h_const
import h_utils


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



def getRiverJunctions(riverSegments):
    """Get ending nodes of river segments."""

    inFeat = QgsFeature()
    rivXList= []
    rivYList= []
    x,y = 0,1
    while riverSegments.nextFeature(inFeat):
        nodes=inFeat.geometry().asPolyline()
        if inFeat.id()==0:  # This is last segment. Get first point
            frstnode=0
            rivXList.append( nodes[frstnode][x] )
            rivYList.append( nodes[frstnode][y] )
        lastnode=len(nodes)-1
        rivXList.append( nodes[lastnode][x] )
        rivYList.append( nodes[lastnode][y] )

    return rivXList, rivYList



def createHydrojunctionLayer(path): 
    """This function creates a new point shapefile (or updates the existing),
    named Hydrojunction, with the nodes of River (segments endpoints),
    Irrigation (polygon centroids) and Borehole (centroid of a group of
    points). It requires River, Borehole and Irrigation be loaded in the
    project"""

    if not layerNamesTypesOK():
        return False
    
    # Get ending nodes of river segments
    riverSegments=h_utils.getLayerFeatures(h_const.riverLayerName)
    if riverSegments==False: return False 
    (rivXList, rivYList)= getRiverJunctions(riverSegments)
    
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
                                         h_const.borehFieldGrp)
 
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
    coordinates=zip(xCoords, yCoords)
    for xy in coordinates:
        height.append(h_utils.getCellValue(h_const.dtmLayerName, xy, 1) )
    # Create the Hydrojunction layer
    createOK=h_utils.createPointLayer(path, h_const.hydroJncLayerName,
                           coordinates, h_const.hydroJncFieldNames,
                           h_const.hydroJncFieldTypes, 
                           [junctType, [], [], [], xCoords, xCoords, height ] )

    return createOK



def linkRiverductHydrojunction(layerName, reversDirect): 
    """ This function builds the topology of River or Aqueduct layers
    (RiverDuct) assigning the appropriate Hydrojunction ids to FROM_NODE,
    TO_NODE fields. The arguments are the shapefile name (River or Aqueduct) 
    and the direction the topology is built (River is built with revers 
    direction i.e. from exit to upstream nodes).""" 

    # Get Hydrojunction layer coordinates
    [xList, yList]= h_utils.getPointLayerCoords(h_const.hydroJncLayerName)
    if not xList: return False 

    # Get segments of riverDuct shapefile
    riverDuctSegments= h_utils.getLayerFeatures(layerName);
    if not riverDuctSegments: return False

    # Loop through segments of riverDuct
    inFeat = QgsFeature()
    frstnode=0
    x,y = 0,1
    toNodes= []
    fromNodes= []
    while riverDuctSegments.nextFeature(inFeat):
        nodes=inFeat.geometry().asPolyline()
        lastnode=len(nodes)-1
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
            if h_utils.floatsEqual(strtPntX,hydroJunctPntX,h_const.precise) and\
               h_utils.floatsEqual(strtPntY,hydroJunctPntY,h_const.precise):
                fromNodes.append(j)
            if h_utils.floatsEqual(endPntX,hydroJunctPntX,h_const.precise) and\
               h_utils.floatsEqual(endPntY,hydroJunctPntY,h_const.precise):
                toNodes.append(j)

    # Write values to attribute table
    res=h_utils.setFieldAttrValues(layerName, 
                                   h_const.fromNodeFieldName, fromNodes)
    if not res: return False
    res=h_utils.setFieldAttrValues(layerName,
                                   h_const.toNodeFieldName, toNodes)

    return res



def linkIrrigHydrojunction(): 
    """This function finds for each Irrigation polygon the corresponding 
    hydrojunciton node"""

    # Get Hydrojunction layer coordinates (x,y pairs)
    [xList, yList]= h_utils.getPointLayerCoords(h_const.hydroJncLayerName)
    if not xList: return False 

    # Find to which x,y pair the centroid of each polygon corresponds
    centroids=getPolyLayerCentroids(h_const.irrigLayerName)
    values= []
    for xy in centroids:
        junctid= h_utils.getElementIndexByVal( zip(xList, yList), xy )[0]
        values.append(junctid)

    # Write centroids to attribute table
    res=h_utils.setFieldAttrValues(h_const.irrigLayerName, 
                                   h_const.irrigFieldJncId, values);
    return res



def linkSubbasinRiver():
    """This function finds for each subbasin the corresponding river_id,
    node_id of the primary river segment """

    # Get River segments
    riverSegments= h_utils.getLayerFeatures(h_const.riverLayerName)
    if not riverSegments: return False

    # Get coords of hydrojunction layer points
    [xList, yList]= h_utils.getPointLayerCoords(h_const.hydroJncLayerName)

    # Check that number of river segments euqals the number of subbasins
    riversNum= h_utils.getLayerFeaturesCount(h_const.riverLayerName)
    if not h_utils.layerFeaturesNumberOK(h_const.subbasLayerName, riversNum): 
        return False 

    # Loop through segments of River
    inFeat1 = QgsFeature()
    inFeat2 = QgsFeature()
    subasscount= h_utils.getLayerFeaturesCount(h_const.subbasLayerName)
    rivIds = [None] * subasscount
    nodeIds = [None] * subasscount
    frstnode=0
    x,y = 0,1
    while riverSegments.nextFeature(inFeat1):
        # Get first and last point of river segment
        nodes=inFeat1.geometry().asPolyline()
        lastnode=len(nodes)-1
        strtPntX= nodes[lastnode][x]
        strtPntY= nodes[lastnode][y]
        endPntX=  nodes[frstnode][x]
        endPntY=  nodes[frstnode][y]
        # Reset found-flag
        foundStart= False
        # Find in which subbasin this point belongs to
        subbPolygons= h_utils.getLayerFeatures(h_const.subbasLayerName)
        if not subbPolygons: return False
        i=0
        while subbPolygons.nextFeature(inFeat2):
            if inFeat2.geometry().contains(QgsPoint(strtPntX,strtPntY)):
                if not foundStart: foundStart= True
                else:
                    message="Polygons of Subbasin overlap!"
                    QtGui.QMessageBox.critical(None,'Error',message, 
                                                QtGui.QMessageBox.Yes)
                    return False 
                # Prepare the list with node_id and river_id of this polygon
                rivIds[i]= inFeat1.id()
                k=h_utils.getElementIndexByVal(zip(xList, yList), 
                                                   (endPntX, endPntY) )
                nodeIds[i]= k[0]
            i= i+1
        if not foundStart:
            message="The start of a segment is outside of the subbasin!"
            QtGui.QMessageBox.critical(None,'Error',message, 
                                        QtGui.QMessageBox.Yes)
            return False 

    # Save edits
    res=h_utils.setFieldAttrValues(h_const.subbasLayerName,
                                   h_const.subbasFieldRivId, rivIds)
    if not res: return False
    res=h_utils.setFieldAttrValues(h_const.subbasLayerName,
                                   h_const.subbasFieldRivNode, nodeIds)
    return res
