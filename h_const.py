from qgis.core import *

# Irrigation layer constants
irrigLayerName="Irrigation"
irrigLayerType=QGis.Polygon
irrigFieldNameJncId="junct_id"
irrigFieldNameArea="irrig_area"

# River layer constants
riverLayerName="River"
riverLayerType=QGis.Line
riverFieldNameFromNode = "FROM_NODE"
riverFieldNameToNode =   "TO_NODE"

# Borehole layer constants
borehLayerName="Borehole"
borehLayerType=QGis.Point
borehFieldNameGrp="GROUP"

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
subbasFieldNameRivId="river_id"
subbasFieldNameRivNode="river_node"
subbasFieldNamePrimLen="pr_length"

# River Aqueduct constants
aquedLayerName= "Aqueduct"

# Groundwater cells
groundLayerName= "Groundwater"
groundLayerType= QGis.Polygon

# DTB
dtmLayerName= "hdr.bgd"
