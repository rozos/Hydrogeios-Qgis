from qgis.core import *
from PyQt4.QtCore import QVariant

# Precision of floats' comparisons
precise=3

# Irrigation layer constants
irrigLayerName="Irrigation"
irrigLayerType=QGis.Polygon
irrigFieldNames=("IRRIG_AREA", "JUNCT_ID", "RET_PIPE", "RET_RATIO")
irrigFieldTypes=(QVariant.Double, QVariant.Int, QVariant.Int, QVariant.Double)
irrigFieldNameJncId=irrigFieldNames[1]
irrigFieldNameArea=irrigFieldNames[0]

# River layer constants
riverLayerName="River"
riverLayerType=QGis.Line

# Field names given to start/end nodes of a segment
fromNodeFieldName= "FROM_NODE"
toNodeFieldName =   "TO_NODE"

# Borehole layer constants
borehLayerName="Borehole"
borehLayerType=QGis.Point
borehFieldNameGrp="GROUP_ID"

# Hydrojunction layer constants
hydroJncLayerName="HydroJunction"
hydroJncFieldNames=("JUNCT_TYPE", "DESCR", "NAME", "TS_ID", "X", "Y", "Z")
hydroJncFieldTypes=(QVariant.Int, QVariant.String, QVariant.String,
                    QVariant.Int, QVariant.Double, QVariant.Double,
		    QVariant.Double)
hydroJncIdNodeRiv=0
hydroJncIdNodeAqu=1
hydroJncIdNodeIrg=2
hydroJncIdNodeBor=3

# Subbasing layer constants
subbasLayerName="Subbasin"
subbasLayerType=QGis.Polygon
subbasFieldNames=("AREA", "X_CENTROID", "Y_CENTROID", "NAME", "DESCR", 
                  "RIVER_NODE", "RIVER_ID", "MEAN_SLOPE", "MEAN_ELEV", 
                  "PR_LENGTH", "LAG")
subbasFieldTypes=(QVariant.Double, QVariant.Double, QVariant.Double, 
                  QVariant.String, QVariant.String, QVariant.Int, QVariant.Int,
                  QVariant.Double, QVariant.Double, QVariant.Double, 
                  QVariant.Double)
subbasFieldNameArea=subbasFieldNames[0]
subbasFieldNameRivNode=subbasFieldNames[5]
subbasFieldNameRivId=subbasFieldNames[6]
subbasFieldNamePrimLen=subbasFieldNames[9]

# River Aqueduct constants
aquedLayerName= "Aqueduct"
aquedLayerType= QGis.Line

# Groundwater cells
groundLayerName= "GroundWater"
groundLayerType= QGis.Polygon

# Outlet layer constants
outletLayerName="Outlet"
outletLayerType=QGis.Point
outletFieldNames=( "X", "Y")
outletFieldTypes=(QVariant.Double, QVariant.Double)

# DTB
dtmLayerName= "hdr"
