import ftools_utils
import constants
from qgis.core import *


def createHydrojunctionLayer()
 
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
        if i=0:  # Get first point of first segment only (river exit)
            firstpoint=inFeat.geometry()
            rivXList.append(firstpoint.xat(0) )
            rivYList.append(firstpoint.yat(0) )
        else: 
            lasttpoint=inFeat.geometry()
            rivXList.append(lasttpoint.xat(-1))
            rivYList.append(lasttpoint.yat(-1))
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
        centroid = inFeat.geometry().centroid()
        irgXList.append(centroid.x)
        irgXList.append(centroid.y)
