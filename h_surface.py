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
    
    if h_utils.getMinFeatureMeasure(h_const.subbasLayerName)==0:
        return False

    if not h_utils.getMinFeatureMeasure(h_const.groundLayerName)==0:
        return False

    if not h_utils.getMinFeatureMeasure(h_const.riverLayerName)==0:
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

    # Unload shapefile
    if h_utils.isShapefileLoaded(h_const.hydroJncLayerName):
	h_utils.unloadLayer(h_const.hydroJncLayerName)
    
    # Get ending nodes of river segments
    (rivXList, rivYList)= h_utils.getSegmentEndsCoords(h_const.riverLayerName, 
                                                       "last")

    # Add to the ending nodes list the coords of starting node of the 1st segm.
    (tmpList1, tmpList2)= h_utils.getSegmentEndsCoords(h_const.riverLayerName, 
                                                       "first")
    rivXList= [tmpList1[0]] + rivXList
    rivYList= [tmpList2[0]] + rivYList
    
    # Get centroids of Irrigation layer 
    res=h_utils.getPolyLayerCentroids(h_const.irrigLayerName)
    if res==None: return False
    irgXList= list(zip(*res)[0])
    irgYList= list(zip(*res)[1])
    
    # Get the points of Borhole layer
    borehPoints=h_utils.getLayerFeatures(h_const.borehLayerName)
    if not borehPoints: return False 

    # Get the coords and group_id of points of Borhole layer
    pointsXList,pointsYList= h_utils.getPointLayerCoords(h_const.borehLayerName)
    pointsId= h_utils.getFieldAttrValues(h_const.borehLayerName, 
                                                      h_const.borehFieldGroupId)
 
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
    junctType= ( [h_const.hydroJncTypeRiv]*len(rivXList) + 
                 [h_const.hydroJncTypeIrg]*len(irgXList) + 
                 [h_const.hydroJncTypeBor]*len(borXList)  )
    # Get the z values of the [xCoords yCoords] points
    heights = []
    coordinates=zip(xCoords, yCoords)
    for xy in coordinates:
        heights.append(h_utils.getCellValue(h_const.DTMlayerName, xy, 1) )
    # Create the Hydrojunction layer
    ok = h_utils.createPointLayer(path, h_const.hydroJncLayerName,
                           coordinates, h_const.hydroJncFieldNames,
                           h_const.hydroJncFieldTypes, [range(0, len(xCoords)),
                           [], [], junctType, [], xCoords, yCoords, heights ] )
    if not ok: return False

    # Load hydrojunction layer
    ok=h_utils.loadShapefileToCanvas(path, h_const.hydroJncLayerName + ".shp")

    return ok



def linkRiverductHydrojunction(layerName, reversDirect): 
    """ This function builds the topology of River or Aqueduct layers
    (RiverDuct) assigning the appropriate Hydrojunction ids to FROM_NODE,
    TO_NODE fields. The arguments are the shapefile name (River or Aqueduct) 
    and the direction the topology is built (River is built with revers 
    direction i.e. from exit to upstream nodes).""" 

    # Make sure River/Aqueduct layer is OK
    if not h_utils.layerNameTypeOK(layerName, h_const.riverLayerType):
        return False

    # Make sure Hydrojunction layer is OK
    if not h_utils.layerNameTypeOK(h_const.hydroJncLayerName, 
                                   h_const.hydroJncLayerType):
        return False

    # Get Hydrojunction layer coordinates
    [hydrojuncXlist, hydrojuncYlist]= \
                          h_utils.getPointLayerCoords(h_const.hydroJncLayerName)

    # Get coordinates of river segments' first and last nodes
    if reversDirect:
        rivEndNodeXlist, rivEndNodeYlist = \
                   h_utils.getSegmentEndsCoords(h_const.riverLayerName, "first")
        rivSrtNodeXlist, rivSrtNodeYlist = \
                    h_utils.getSegmentEndsCoords(h_const.riverLayerName, "last")
    else:
        rivEndNodeXlist, rivEndNodeYlist = \
                    h_utils.getSegmentEndsCoords(h_const.riverLayerName, "last")
        rivSrtNodeXlist, rivSrtNodeYlist = \
                   h_utils.getSegmentEndsCoords(h_const.riverLayerName, "first")

    # Write to fromNode, toNode the appropriate hydrojunction ids
    toNodes= []
    fromNodes= []
    for strNodeX, strNodeY, endNodeX, endNodeY in zip(rivSrtNodeXlist, 
                             rivSrtNodeYlist, rivEndNodeXlist, rivEndNodeYlist):
        for j, hydrojunctX, hydrojunctY in zip(range(0, len(hydrojuncXlist)), \
                                                hydrojuncXlist, hydrojuncYlist):
            if h_utils.floatsEqual(strNodeX, hydrojunctX ,h_const.precise) and\
                    h_utils.floatsEqual(strNodeY, hydrojunctY, h_const.precise):
                fromNodes.append(j)
            if h_utils.floatsEqual(endNodeX, hydrojunctX, h_const.precise) and\
                    h_utils.floatsEqual(endNodeY, hydrojunctY, h_const.precise):
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

    # Make sure Hydrojunction layer is OK
    if not h_utils.layerNameTypeOK(h_const.hydroJncLayerName, 
                                   h_const.hydroJncLayerType):
        return False

    # Make sure Irrigation layer is OK
    if not h_utils.layerNameTypeOK(h_const.irrigLayerName, 
                                   h_const.irrigLayerType):
        return False

    # Get Hydrojunction layer coordinates
    [hydrojuncXlist, hydrojuncYlist]= \
                          h_utils.getPointLayerCoords(h_const.hydroJncLayerName)

    # Find to which x,y pair the centroid of each polygon corresponds
    centroids=h_utils.getPolyLayerCentroids(h_const.irrigLayerName)
    values= []
    for xy in centroids:
        res= h_utils.getElementIndexByVal(zip(hydrojuncXlist,hydrojuncYlist),xy)
        junctid=res[0]
        values.append(junctid)

    # Write centroids to attribute table
    res=h_utils.setFieldAttrValues(h_const.irrigLayerName, 
                                                h_const.hydroJncFieldId, values)
    return res



def linkSubbasinRiver():
    """This function finds for each subbasin the corresponding river_id,
    node_id of the primary river segment """

    # Make sure River/Hydrojunction layers are OK
    if not h_utils.layerNameTypeOK(h_const.riverLayerName, 
                                                    h_const.riverLayerType) or \
       not h_utils.layerNameTypeOK(h_const.hydroJncLayerName, 
                                                     h_const.hydroJncLayerType):

        return False

    # Get coords of hydrojunction layer points
    [hydrojuncXlist, hydrojuncYlist]= \
                          h_utils.getPointLayerCoords(h_const.hydroJncLayerName)

    # Check that number of river segments euqals the number of subbasins
    riversNum= h_utils.getLayerFeaturesCount(h_const.riverLayerName)
    if not h_utils.layerFeaturesNumberOK(h_const.subbasLayerName, riversNum): 
        return False 

    # Get coordinates of river segments' first nodes
    rivSrtNodeXlist, rivSrtNodeYlist = \
                    h_utils.getSegmentEndsCoords(h_const.riverLayerName, "last")
    rivEndNodeXlist, rivEndNodeYlist = \
                   h_utils.getSegmentEndsCoords(h_const.riverLayerName, "first")

    # Find to which subbasin each segment start belongs to
    subassCount= h_utils.getLayerFeaturesCount(h_const.subbasLayerName)
    rivIds = [None] * subassCount
    nodeIds = [None] * subassCount

    for rivid, strNodeX, strNodeY, endNodeX, endNodeY, in zip( \
               range(0,len(rivSrtNodeXlist)), rivSrtNodeXlist, rivSrtNodeYlist,\
                                              rivEndNodeXlist, rivEndNodeYlist):
        # Reset found-flag
        foundStart= False
        # Find in which subbasin this point belongs to
        subbPolygons= h_utils.getLayerFeatures(h_const.subbasLayerName)
        if not subbPolygons: return False
        i=0
        inFeat = QgsFeature()
        while subbPolygons.nextFeature(inFeat):
            if inFeat.geometry().contains(QgsPoint(strNodeX,strNodeY)):
                if not foundStart:
                    foundStart= True
                else:
                    message="Polygons of Subbasin overlap!"
                    QtGui.QMessageBox.critical(None,'Error',message, 
                                                QtGui.QMessageBox.Yes)
                    return False 
                # Prepare the list with node_id and river_id of this polygon
                rivIds[i]= rivid
                k=h_utils.getElementIndexByVal( \
                     zip(hydrojuncXlist, hydrojuncYlist), (endNodeX, endNodeY) )
                nodeIds[i]= k[0]
            i= i+1

        if not foundStart:
            message="The start of a river segment is outside of the subbasin!"
            QtGui.QMessageBox.critical(None,'Error',message, 
                                        QtGui.QMessageBox.Yes)
            return False 

    # Save edits
    res=h_utils.setFieldAttrValues(h_const.subbasLayerName,
                                   h_const.riverFieldId, rivIds)
    if not res: return False
    res=h_utils.setFieldAttrValues(h_const.subbasLayerName,
                                   h_const.subbasFieldRivNode, nodeIds)
    return res



def addSubbasinId():
    """Add to the attr. table of Subbasin a field that keeps the polys' ids."""
    ok=h_utils.addShapeIdsToField(h_const.subbasLayerName,
                                  h_const.subbasFieldId)
    return ok
