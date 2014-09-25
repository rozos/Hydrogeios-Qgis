from __future__ import division 
from qgis.core import *
from PyQt4 import QtGui
from PyQt4.QtCore import QVariant
import ftools_utils
import h_const
import h_utils


def build():
    """This wrapper function calls all the functions required to build the
    hydrosystem toplogy."""
    if not h_utils.addShapeIdsToAttrTable(h_const.hydrojncLayerName,
                                          h_const.hydrojncFieldId):
        return False
    if not layerConsistenciesOK() or not layerNamesTypesOK():
        message="Layers involved in topology are not OK. Continue?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No )
        if reply==QtGui.QMessageBox.No: return False
    if not linkRiverHydrojunction():
        message="linkRiverHydrojunction failed. Continue?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No )
        if reply==QtGui.QMessageBox.No: return False
    if not linkAqueductHydrojunction():
        message="linkAqueductHydrojunction failed. Continue?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No )
        if reply==QtGui.QMessageBox.No: return False
    if not linkIrrigHydrojunction(): 
        message="linkIrrigHydrojunction failed. Continue?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No )
        if reply==QtGui.QMessageBox.No: return False
    if not linkSpringHydrojunction():
        message="linkSpringHydrojunction failed. Continue?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No )
        if reply==QtGui.QMessageBox.No: return False
    if not linkRiverexitnodeHydrojunction():
        message="linkRiverexitnodeHydrojunction failed. Continue?"
        reply=QtGui.QMessageBox.question(None, 'Delete', message,
                                   QtGui.QMessageBox.Yes|QtGui.QMessageBox.No )
        if reply==QtGui.QMessageBox.No: return False
    return True



def layerConsistenciesOK():
    """This functions checks that the area of all shapes of polygon layers
    employed in topology operations is positive and the length of all line 
    shapes is positive"""
    
    if h_utils.getMinFeatureMeasure(h_const.subbasLayerName)<=0:
        return False

    if h_utils.getMinFeatureMeasure(h_const.groundLayerName)<=0:
        return False

    if h_utils.getMinFeatureMeasure(h_const.riverLayerName)<=0:
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

    # Check if DEM is OK
    raster=ftools_utils.getRasterLayerByName(h_const.DEMlayerName)
    if not raster:
        message=h_const.DEMlayerName + "  not loaded!"
        QtGui.QMessageBox.critical(None,'Error',message, QtGui.QMessageBox.Ok)
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
    if h_utils.isShapefileLoaded(h_const.hydrojncLayerName):
        h_utils.unloadLayer(h_const.hydrojncLayerName)
    
    # Get upstream nodes of river segments
    res= h_utils.getSegmentEndsCoords(h_const.riverLayerName, "last")
    if res==False: return False
    rivXList, rivYList= res[0], res[1]

    # Add to the previouw list the coords of downstream node of the 1st segm.
    (tmpList1, tmpList2)= h_utils.getSegmentEndsCoords(h_const.riverLayerName, 
                                                       "first")
    rivXList= [tmpList1[0]] + rivXList
    rivYList= [tmpList2[0]] + rivYList
    
    # Get centroids of Irrigation layer 
    irgXList= []
    irgYList= []
    res=h_utils.getPolyLayerCentroids(h_const.irrigLayerName)
    if res==None: return False
    if res!=[]:
        irgXList= list(zip(*res)[0])
        irgYList= list(zip(*res)[1])
    
    # Get the coords and group_id of points of Borehole layer
    pointsXList,pointsYList= h_utils.getPointLayerCoords(h_const.borehLayerName)
    pointIds= h_utils.getFieldAttrValues(h_const.borehLayerName, 
                                                      h_const.borehFieldGroupId)
 
    # Make a List of coords of the gravity centres of the Borhole groups points
    borXList= []
    borYList= []
    if pointIds!=[NULL]:
        borGrpIds=set(pointIds)
        for grpid in borGrpIds:
            indexes=h_utils.getElementIndexByVal(pointIds, grpid)
            groupXvals= [pointsXList[i] for i in indexes]
            borXList.append( sum(groupXvals)/len(groupXvals) )
            groupYvals= [pointsYList[i] for i in indexes]
            borYList.append( sum(groupYvals)/len(groupYvals) ) 
    
    # Get the points of Spring layer
    res= getPointLayerCoords(h_const.springLayerName)
    if res == None: return False
    sprXList, sprYList= res[0], res[1]

    # Create a new layer or update the existing
    xCoords= rivXList+irgXList+borXList+sprXList
    yCoords= rivYList+irgYList+borYList+sprYList
    # Create a list with id of the junction type of each junciton
    junctTypes= ( [h_const.hydrojncTypeRiv]*len(rivXList) + 
                 [h_const.hydrojncTypeIrg]*len(irgXList) + 
                 [h_const.hydrojncTypeBor]*len(borXList) +
                 [h_const.hydrojncTypeSpr]*len(sprXList) )
    # Get the z values of the [xCoords yCoords] points
    heights = []
    coordinates=zip(xCoords, yCoords)
    for xy in coordinates:
        heights.append(h_utils.getCellValue(h_const.DEMlayerName, xy, 1) )
    # Create the Hydrojunction layer
    ok = h_utils.createPointLayer(path, h_const.hydrojncLayerName,
                           coordinates, h_const.hydrojncFieldNames,
                           h_const.hydrojncFieldTypes, [range(0, len(xCoords)),
                           [], [], junctTypes, [], xCoords, yCoords, heights ] )
    if not ok: return False

    # Load hydrojunction layer
    ok=h_utils.loadShapefileToCanvas(path, h_const.hydrojncLayerName)

    return ok



def linkRiverHydrojunction(): 
    "Builds topology of River"
    return _linkRiverductHydrojunction(h_const.riverLayerName, True)



def linkAqueductHydrojunction(): 
    "Builds topology of Aqueduct"
    return _linkRiverductHydrojunction(h_const.aquedLayerName, False)



def _linkRiverductHydrojunction(layerName, reversDirect): 
    """ This function builds the topology of River or Aqueduct layers
    (RiverDuct) assigning the appropriate Hydrojunction ids to FROM_NODE,
    TO_NODE fields. The arguments are the shapefile name (River or Aqueduct) 
    and the direction the topology is built (River is built with revers 
    direction i.e. from exit to upstream nodes).""" 

    # Make sure River/Aqueduct layer is OK
    if not h_utils.layerNameTypeOK(layerName, h_const.riverLayerType):
        return False

    # Make sure Hydrojunction layer is OK
    if not h_utils.layerNameTypeOK(h_const.hydrojncLayerName, 
                                   h_const.hydrojncLayerType):
        return False

    # Get Hydrojunction layer coordinates
    [hydrojuncXlist, hydrojuncYlist]= \
                          h_utils.getPointLayerCoords(h_const.hydrojncLayerName)

    # Get coordinates of river or aqueduct segments' first and last nodes
    if reversDirect:
        rivEndnodeXlist, rivEndnodeYlist = \
                   h_utils.getSegmentEndsCoords(layerName, "first")
        rivStrnodeXlist, rivStrnodeYlist = \
                    h_utils.getSegmentEndsCoords(layerName, "last")
    else:
        rivEndnodeXlist, rivEndnodeYlist = \
                    h_utils.getSegmentEndsCoords(layerName, "last")
        rivStrnodeXlist, rivStrnodeYlist = \
                   h_utils.getSegmentEndsCoords(layerName, "first")

    # Write to fromNode, toNode the appropriate hydrojunction ids
    toNodes= []
    fromNodes= []
    for strNodeX, strNodeY, endNodeX, endNodeY in zip(rivStrnodeXlist, 
                             rivStrnodeYlist, rivEndnodeXlist, rivEndnodeYlist):
        for j, hydrojunctX, hydrojunctY in zip(range(0, len(hydrojuncXlist)), \
                                                hydrojuncXlist, hydrojuncYlist):
            if h_utils.floatsEqual(strNodeX, hydrojunctX, h_const.precise) and\
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

    # Make sure Irrigation layer is OK
    if not h_utils.layerNameTypeOK(h_const.irrigLayerName, 
                                   h_const.irrigLayerType):
        return False

    # Find to which hydrojucntion the centroid of each polygon corresponds to
    centroids=h_utils.getPolyLayerCentroids(h_const.irrigLayerName)
    if centroids==False: return False
    if centroids==None: 
        return True
    idsList=_getHydrojunctIds(centroids)

    # Write hydrojnct ids to attribute table of Irrigation
    res=h_utils.setFieldAttrValues(h_const.irrigLayerName, 
                                               h_const.hydrojncFieldId, idsList)
    return res



def linkSpringHydrojunction():
    """Finds the corresponding hydrojunctions points to spring nodes and writes
    the ids of the former to the attribute table of the latter."""

    # Make sure Spring layer is OK
    if not h_utils.layerNameTypeOK(h_const.springLayerName, 
                                   h_const.springLayerType):
        return False

    # Find to which HydroJnct y pair corresponds each spring
    res = h_utils.getPointLayerCoords(h_const.springLayerName)
    if res==False: return False
    if res==None: 
        return True
    xSpring, ySpring = res[0], res[1]
    idsList=_getHydrojunctIds(zip(xSpring, ySpring) )

    # Write hydrojnct ids to attribute table of Spring
    res=h_utils.setFieldAttrValues(h_const.springLayerName, 
                                               h_const.hydrojncFieldId, idsList)
    return res



def linkRiverexitnodeHydrojunction():
    """Finds to which hydrojunction corresponds each river exit node. Updates
       the junct_id field of RiverExitNode attribute table."""

    # Make sure RiverExitNode layer is OK
    if not h_utils.layerNameTypeOK(h_const.riverexitnodeLayerName, 
                                   h_const.riverexitnodeLayerType):
        return False

    # Find to wich HydroJnct pair corresponds each river exit node
    res = h_utils.getPointLayerCoords(h_const.riverexitnodeLayerName)
    if res==False: return False
    if res==None: 
        return True
    xNode, yNode= res[0], res[1]
    idsList=_getHydrojunctIds(zip(xNode, yNode) )

    # Write hydrojnct ids to attribute table of RiverExitNode
    res=h_utils.setFieldAttrValues(h_const.riverexitnodeLayerName, 
                                              h_const.hydrojncFieldId, idsList)
    return res



def _getHydrojunctIds(coords):
    """Returns a list of ids of the Hydrojuntion nodes that have the 
    provided coordinates."""

    # Make sure Hydrojunction layer is OK
    if not h_utils.layerNameTypeOK(h_const.hydrojncLayerName, 
                                   h_const.hydrojncLayerType):
        return False

    # Get Hydrojunction layer coordinates
    [hydrojuncXlist, hydrojuncYlist]= \
                          h_utils.getPointLayerCoords(h_const.hydrojncLayerName)
    hydrojunctionCoords= zip(hydrojuncXlist,hydrojuncYlist)

    # Find to wich hydrojunct. corresponds each coordinate of the provided list
    idsList= []
    for xy in coords:
        res= h_utils.getElementIndexByVal(hydrojunctionCoords, xy)
        assert(len(res)==1)
        junctid=res[0]
        idsList.append(junctid)
    
    return idsList
