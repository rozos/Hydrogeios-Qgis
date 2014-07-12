import ftools_utils
import constants
from qgis.core import *


def createHydrojunctionLayer(): 
    """This procedure creates a new point shapefile (or updates the existing),
    named Hydrojunction, with the nodes of River (segments endpoints),
    Irrigation (polygon centroids) and Borehole (centroid of a group of
    points). It requires River, Borehole and Irrigation be loaded in the
    project"""
    
    # Get segments of "River" shapefile
    riverLayer=ftools_utils.getVectorLayerByName(constants.riverLayer)
    riverProvider=riverLayer.dataProvider()
    riverSegments=riverProvider.getFeatures()
    
    # Check if it is a line layer
    if riverLayer.type() != QGis.Point:
        setErrorHappend("River is not a line layer!")
        return

    # Loop through segments of "River" layer
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
    
     # Get the polygons of "Irrigation" layer
    irrigLayer=ftools_utils.getVectorLayerByName(constants.irrigLayer)
    irrigProvider=irrigLayer.dataProvider()
    irrigPolygons=irrigProvider.getFeatures()
    
    # Check if it is a poly layer
    if riverLayer.type() != QGis.Polygon
        setErrorHappend("Irrigation is not a polygon layer!")
        return

    # Loop through polygons of Irrigation layer
    inFeat = QgsFeature()
    irgXList= []
    irgYList= []
    while irrigPolygons.nextFeature(inFeat)
        centrpoint = inFeat.geometry().centroid()
        irgXList.append(centrpoint.x)
        irgXList.append(centrpoint.y)


def buildRiverductTopologyr(riverDuct, reversDirect):
    """ This function builds the topology of River or Aqueduct shapefiles
    (Riverduct). The arguments are the shapefile (River or Aqueduct) and the
    direction the topology is built (River is built with revers direction i.e.
    from exit to upstream nodes""" 

    # Get points of "HydroJunction" shapefile
    hydroJunctLayer=ftools_utils.getVectorLayerByName(constants.hydroJunctLayer)
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

    # Loop through segments of riverDuct
    inFeat = QgsFeature()
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
            if strtpntX==hydroJunctPntX and strpntY==hydroJunctPntY:
                # inFeat.attribute("from_node")=j
            if endtpntX==hydroJunctPntX and endpntY==hydroJunctPntY:
                # inFeat.attribute("to_node")=j



