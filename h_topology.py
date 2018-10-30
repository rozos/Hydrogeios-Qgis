from __future__ import division 
import sys
from qgis.core import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QVariant
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
        reply=QMessageBox.question(None, 'Delete', message,
                                   QMessageBox.Yes|QMessageBox.No )
        if reply==QMessageBox.No: return False
    if not linkRiverHydrojunction():
        message="linkRiverHydrojunction failed. Continue?"
        reply=QMessageBox.question(None, 'Delete', message,
                                   QMessageBox.Yes|QMessageBox.No )
        if reply==QMessageBox.No: return False
    if not linkAqueductHydrojunction():
        message="linkAqueductHydrojunction failed. Continue?"
        reply=QMessageBox.question(None, 'Delete', message,
                                   QMessageBox.Yes|QMessageBox.No )
        if reply==QMessageBox.No: return False
    if not linkIrrigHydrojunction(): 
        message="linkIrrigHydrojunction failed. Continue?"
        reply=QMessageBox.question(None, 'Delete', message,
                                   QMessageBox.Yes|QMessageBox.No )
        if reply==QMessageBox.No: return False
    if not linkSpringHydrojunction():
        message="linkSpringHydrojunction failed. Continue?"
        reply=QMessageBox.question(None, 'Delete', message,
                                   QMessageBox.Yes|QMessageBox.No )
        if reply==QMessageBox.No: return False
    if not linkRiverexitnodeHydrojunction():
        message="linkRiverexitnodeHydrojunction failed. Continue?"
        reply=QMessageBox.question(None, 'Delete', message,
                                   QMessageBox.Yes|QMessageBox.No )
        if reply==QMessageBox.No: return False
    return True



def layerConsistenciesOK():
    """This functions checks that the area of all shapes of polygon layers
    employed in topology operations is positive and the length of all line 
    shapes is positive"""
    
    if h_utils.getMinFeatureMeasure(h_const.subbasLayerName)<=0:
        return False

    if h_utils.getMinFeatureMeasure(h_const.grdwatLayerName)<=0:
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
                                   h_const.riverGeomType):
        return False

    # Check if Irrigation is a poly layer
    if not h_utils.layerNameTypeOK(h_const.irrigLayerName, 
                                   h_const.irrigGeomType):
        return False

    # Check if Borehole is a point layer
    if not h_utils.layerNameTypeOK(h_const.borehLayerName, 
                                   h_const.borehGeomType):
        return False

    # Check if DEM is OK
    raster=h_utils.getRasterLayerByName(h_const.DEMlayerName)
    if not raster:
        message=h_const.DEMlayerName + "  not loaded!"
        QMessageBox.critical(None,'Error',message, QMessageBox.Ok)
        return False

    # All names and types are what expected to be
    return True


def getRiverExit(path):
    """This function returns the exit of the river."""
    # If Outlet layer exists, use first point as exit node
    if h_utils.shapefileExists(path, h_const.outletLayerName):
        h_utils.loadShapefileToCanvas(path, h_const.outletLayerName)
        xUserOuts,yUserOuts=h_utils.getPointLayerCoords(h_const.outletLayerName)
        if xUserOuts==[]: return False
        return QgsPointXY(xUserOuts[0], yUserOuts[0] )
    # Find which river exit node is unique
    x,y=0,1
    rivsegmExits= h_utils.getSegmentPoints(h_const.riverLayerName, "first")
    for node in rivsegmExits:
        indexes=h_utils.getElementIndexByVal(rivsegmExits, node)
        if len(indexes)==1:
            return node
    return False


def createHydrojunctionLayer(path): 
    """This function creates a new point shapefile (or updates the existing),
    named Hydrojunction, with the nodes of River (segments endpoints),
    Irrigation (polygon centroids) and Borehole (centroid of a group of
    points). It requires River, Borehole and Irrigation be loaded in the
    project"""

    if not layerNamesTypesOK():
        return False

    # Unload shapefile
    if h_utils.isLayerLoaded(h_const.hydrojncLayerName):
        h_utils.unloadShapefile(h_const.hydrojncLayerName)
    
    # Get upstream nodes of river segments
    rivLastNodes= h_utils.getSegmentPoints(h_const.riverLayerName, "last")
    if rivLastNodes==[]: return False

    # Add to the previous list the coords of downstream node of the 1st segm.
    rivExit= getRiverExit(path)
    if rivExit==False: return False
    rivLastNodes.insert(0, rivExit)
    
    # Get coordinates of river nodes
    rivXList=[]
    rivYList=[]
    for item in rivLastNodes:
        rivXList.append(item.x())
        rivYList.append(item.y())

    # Get centroids of Irrigation layer 
    irgXList= []
    irgYList= []
    res=h_utils.getPolyLayerCentroids(h_const.irrigLayerName)
    if res==None: return False
    if res!=[]:
        irgXList= [row[0] for row in res]
        irgYList= [row[1] for row in res]
    
    # Get the coords and group_id of points of Borehole layer
    pointsXList,pointsYList= h_utils.getPointLayerCoords(h_const.borehLayerName)
    pointIds= h_utils.getFieldAttrValues(h_const.borehLayerName, 
                                                      h_const.borehFieldGroupId)
 
    # Make a List of coords of the gravity centres of the Borhole groups points
    borXList= []
    borYList= []
    if pointIds!=[]:
        if pointIds[0]==NULL:
            message="Group IDs not defined in " + h_const.borehLayerName
            okBtn=QMessageBox.Ok
            QMessageBox.critical(None,'Error',message, okBtn)
            return False
        borGrpIds=set(pointIds)
        for grpid in borGrpIds:
            indexes=h_utils.getElementIndexByVal(pointIds, grpid)
            groupXvals= [pointsXList[i] for i in indexes]
            borXList.append( sum(groupXvals)/len(groupXvals) )
            groupYvals= [pointsYList[i] for i in indexes]
            borYList.append( sum(groupYvals)/len(groupYvals) ) 
    
    # Get the points of Spring layer
    res= h_utils.getPointLayerCoords(h_const.springLayerName)
    if res == None: return False
    sprXList, sprYList= res[0], res[1]

    # Create a new layer or update the existing
    xCoords= rivXList+irgXList+borXList+sprXList
    yCoords= rivYList+irgYList+borYList+sprYList
    # Create a list with id of the junction type of each junction
    junctTypes= ( [h_const.hydrojncTypeRiv]*len(rivXList) + 
                 [h_const.hydrojncTypeIrg]*len(irgXList) + 
                 [h_const.hydrojncTypeBor]*len(borXList) +
                 [h_const.hydrojncTypeSpr]*len(sprXList) )
    # Get the z values of the [xCoords yCoords] points
    heights = []
    for x,y in zip(xCoords, yCoords):
        heights.append(h_utils.getCellValue(h_const.DEMlayerName, (x,y), 1) )
    # Create the Hydrojunction layer
    Points=[]
    for x,y in zip(xCoords, yCoords):
        Points.append(QgsPointXY(x,y))
    hydrojnctIds= range(0, len(xCoords))
    ok = h_utils.createPointLayer(path, h_const.hydrojncLayerName,
                           Points, h_const.hydrojncFieldNames,
                           h_const.hydrojncFieldTypes, [ hydrojnctIds, [], [], 
                           junctTypes, [], xCoords, yCoords, heights ] )
    if not ok: return False

    # Load hydrojunction layer
    ok=h_utils.loadShapefileToCanvas(path, h_const.hydrojncLayerName)

    return ok



def linkRiverHydrojunction(): 
    "Builds topology of River"
    return _buildTopowithHydrjncIds(h_const.riverLayerName, True)



def linkAqueductHydrojunction(): 
    "Builds topology of Aqueduct"
    return _buildTopowithHydrjncIds(h_const.aquedLayerName, False)



def _buildTopowithHydrjncIds(layerName, reversDirect): 
    """ This function builds the topology of River or Aqueduct layers
    (RiverDuct) assigning the appropriate Hydrojunction ids to FROM_NODE,
    TO_NODE fields. The arguments are the shapefile name (River or Aqueduct) 
    and the direction the topology is built (River is built with revers 
    direction i.e. from exit to upstream nodes).""" 

    # Make sure River/Aqueduct layer is OK
    if not h_utils.layerNameTypeOK(layerName, h_const.riverGeomType):
        return False

    # Make sure Hydrojunction layer is OK
    if not h_utils.layerNameTypeOK(h_const.hydrojncLayerName, 
                                   h_const.hydrojncGeomType):
        return False

    # Get Hydrojunction layer points
    [hydrojuncXlist, hydrojuncYlist]= \
                          h_utils.getPointLayerCoords(h_const.hydrojncLayerName)
    hydrojunctions=[]
    for x,y in zip(hydrojuncXlist, hydrojuncYlist):
        hydrojunctions.append(QgsPointXY(x,y))

    # Get coordinates of river or aqueduct segments' first and last nodes
    if reversDirect:
        rivEndnodes= h_utils.getSegmentPoints(layerName, "first")
        rivStrtnodes= h_utils.getSegmentPoints(layerName, "last")
    else:
        rivEndnodes= h_utils.getSegmentPoints(layerName, "last")
        rivStrtnodes= h_utils.getSegmentPoints(layerName, "first")

    # Write to fromNode, toNode the appropriate hydrojunction ids
    toNodes= []
    fromNodes= []
    for rivstrtNode, rivendNode in zip(rivStrtnodes, rivEndnodes):
        for j,hydrojunction in zip(range(0,len(hydrojunctions)),hydrojunctions):
            if rivstrtNode==hydrojunction: fromNodes.append(j)
            if rivendNode==hydrojunction: toNodes.append(j)

    # Write values to attribute table
    res=h_utils.setFieldAttrValues(layerName, 
                                   h_const.fromNodeFieldName, fromNodes)
    if not res: return False
    res=h_utils.setFieldAttrValues(layerName,
                                   h_const.toNodeFieldName, toNodes)

    return res



def linkIrrigHydrojunction(): 
    """This function finds for each Irrigation polygon the corresponding 
    hydrojunction node"""

    # Make sure Irrigation layer is OK
    if not h_utils.layerNameTypeOK(h_const.irrigLayerName, 
                                   h_const.irrigGeomType):
        return False

    # Find to which hydrojucntion the centroid of each polygon corresponds to
    centroids=h_utils.getPolyLayerCentroids(h_const.irrigLayerName)
    if centroids==False: return False
    if centroids==None: 
        return True
    idsList=_getHydrojunctIds(centroids)
    if idsList==False:
        return False

    # Write hydrojnct ids to attribute table of Irrigation
    res=h_utils.setFieldAttrValues(h_const.irrigLayerName, 
                                               h_const.hydrojncFieldId, idsList)
    return res



def linkSpringHydrojunction():
    """Finds the corresponding hydrojunctions points to spring nodes and writes
    the ids of the former to the attribute table of the latter."""

    # Make sure Spring layer is OK
    if not h_utils.layerNameTypeOK(h_const.springLayerName, 
                                   h_const.springGeomType):
        return False

    # Find to which HydroJnct y pair corresponds each spring
    res = h_utils.getPointLayerCoords(h_const.springLayerName)
    if res==False: return False
    if res==None: 
        return True
    xSpring, ySpring = res[0], res[1]
    idsList=_getHydrojunctIds(zip(xSpring, ySpring) )
    if idsList==False:
        return False

    # Write hydrojnct ids to attribute table of Spring
    res=h_utils.setFieldAttrValues(h_const.springLayerName, 
                                               h_const.hydrojncFieldId, idsList)
    return res



def linkRiverexitnodeHydrojunction():
    """Finds to which hydrojunction corresponds each river exit node. Updates
       the junct_id field of RiverExitNode attribute table."""

    # Make sure RiverExitNode layer is OK
    if not h_utils.layerNameTypeOK(h_const.riverexitnodeLayerName, 
                                   h_const.riverexitnodeGeomType):
        return False

    # Find to wich HydroJnct pair corresponds each river exit node
    res = h_utils.getPointLayerCoords(h_const.riverexitnodeLayerName)
    if res==False: return False
    if res==None: 
        return True
    xNode, yNode= res[0], res[1]
    idsList=_getHydrojunctIds(zip(xNode, yNode) )
    if idsList==False:
        return False

    # Write hydrojnct ids to attribute table of RiverExitNode
    res=h_utils.setFieldAttrValues(h_const.riverexitnodeLayerName, 
                                              h_const.hydrojncFieldId, idsList)
    return res


def _hydroJunctionsSameLocationError(res):
    """Displays error message and pring to stderr some info."""
    message="Hydrojunctions on exactly same location!"
    okBtn=QMessageBox.Ok
    QMessageBox.critical(None,'Error',message, okBtn)
    sys.stderr.write("Hydrojunction IDs on same location:"+str(res))

def _nohydroJunctionsOnThisPointError(xy):
    """Displays error message and pring to stderr some info."""
    message="No hydrojunction with these coordinates!"
    okBtn=QMessageBox.Ok
    QMessageBox.critical(None,'Error',message, okBtn)
    sys.stderr.write("X,Y:"+str(xy))

def _getHydrojunctIds(coords):
    """Returns a list of ids of the Hydrojuntion nodes that have the 
    provided coordinates."""

    # Make sure Hydrojunction layer is OK
    if not h_utils.layerNameTypeOK(h_const.hydrojncLayerName, 
                                   h_const.hydrojncGeomType):
        return False

    # Get Hydrojunction layer coordinates
    [hydrojuncXlist, hydrojuncYlist]= \
                          h_utils.getPointLayerCoords(h_const.hydrojncLayerName)
    hydrojunctionCoords= []
    for x,y in zip(hydrojuncXlist,hydrojuncYlist):
        hydrojunctionCoords.append((x,y))

    # Find to wich hydrojunct. corresponds each coordinate of the provided list
    idsList= []
    Xcoords = [row[0] for row in coords]
    Ycoords = [row[1] for row in coords]
    for x,y in zip(Xcoords,Ycoords):
        res= h_utils.getElementIndexByVal(hydrojunctionCoords, (x,y) )
        if res==[]:
            _nohydroJunctionsOnThisPointError((x,y))
            return False
        if (len(res)>1):
            _hydroJunctionsSameLocationError(res)
            return False
        junctid=res[0]
        idsList.append(junctid)
    
    return idsList
