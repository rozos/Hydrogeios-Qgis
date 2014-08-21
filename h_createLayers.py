def createOutletsLayer(path):
    """ Create a new point layer with the end nodes of the rivers segments."""

    # Get River segments
    riverSegments= h_utils.getLayerFeatures(h_const.riverLayerName)
    if not riverSegments: return False

    # Get exit of river segments
    inFeat1 = QgsFeature()
    frstnode=0
    x,y = 0,1
    endPntXs= []
    endPntYs= []
    while riverSegments.nextFeature(inFeat1):
        nodes=inFeat1.geometry().asPolyline()
        endPntXs.append( nodes[frstnode][x] )
        endPntYs.append( nodes[frstnode][y] )
    
    res= createPointLayer(path, h_const.outletLayerName, (endPntXs, endPntYs),
		         h_const.outletFieldNames, h_const.outletFieldTypes,
                         attrValues)
    return res
