from qgis.core import *
from PyQt4.QtCore import QVariant

# Irrigation layer constants
irrigLayerName="Irrigation"
irrigLayerType=QGis.Polygon
irrigFieldNameJncId="JUNCT_ID"
irrigFieldNameArea="IRRIG_AREA"

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
hydroJncIdNodeRiv=1
hydroJncIdNodeIrg=2
hydroJncIdNodeBor=3

# Subbasing layer constants
subbasLayerName="Subbasin"
subbasLayerType=QGis.Polygon
subbasFieldNameRivId="RIVER_ID"
subbasFieldNameRivNode="RIVER_NODE"
subbasFieldNamePrimLen="PR_LENGTH"

# River Aqueduct constants
aquedLayerName= "Aqueduct"
aquedLayerType= QGis.Line

# Groundwater cells
groundLayerName= "GroundWater"
groundLayerType= QGis.Polygon

# DTB
dtmLayerName= "hdr"
