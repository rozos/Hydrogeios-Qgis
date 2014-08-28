from qgis.core import *
from PyQt4.QtCore import QVariant

# Precision of floats' comparisons
precise=3

# Irrigation layer specifications
irrigLayerName="Irrigation"
irrigLayerType=QGis.Polygon
irrigGeomType=QGis.WKBPolygon
irrigFieldNames=("IRRIG_AREA", "JUNCT_ID", "RET_PIPE", "RET_RATIO")
irrigFieldTypes=(QVariant.Double, QVariant.Int, QVariant.Double, 
		 QVariant.Double)
irrigFieldNameJncId=irrigFieldNames[1]
irrigFieldNameArea=irrigFieldNames[0]

# River layer specifications
riverLayerName="River"
riverLayerType=QGis.Line
riverGeomType=QGis.WKBLineString
riverFieldNames=("NAME", "DESCR", "FROM_NODE", "TO_NODE", "LENGTH", "WIDTH", 
                 "BANK_SLOPE", "ROUGH", "INFILT_CF", "Q_MAX", "Q_MIN", 
                 "T_PERC", "ROUTING", "TRAV_TIME", "WGHT_X", )
riverFieldTypes=(QVariant.String, QVariant.String, QVariant.Int, QVariant.Int, 
                 QVariant.Double, QVariant.Double, QVariant.Double, 
                 QVariant.Double, QVariant.Double, QVariant.Double, 
                 QVariant.Double, QVariant.Double, QVariant.Double, 
                 QVariant.Double, QVariant.Double, )

# Field names given to start/end nodes of a segment
fromNodeFieldName= "FROM_NODE"
toNodeFieldName =   "TO_NODE"

# Borehole layer specifications
borehLayerName="Borehole"
borehLayerType=QGis.WKBPoint
borehFieldNames=("NAME", "DESCR", "TYPE", "X", "Y", "Z", "GROUND_ID", "SUB_ID",
                 "GROUP_ID", "PUMP_CAP", "PUMP_RAT", "DEPTH", )
borehFieldTypes=(QVariant.String, QVariant.String, QVariant.Int,
                 QVariant.Double, QVariant.Double,  QVariant.Double,
                 QVariant.Int, QVariant.Int, QVariant.Int, QVariant.Double,
                 QVariant.Double,  QVariant.Double, )
borehFieldNameGrp=borehFieldNames[6]

# Hydrojunction layer specifications
hydroJncLayerName="HydroJunction"
hydroJncFieldNames=("NAME", "DESCR", "JUNCT_TYPE", "TS_ID", "X", "Y", "Z")
hydroJncFieldTypes=(QVariant.String, QVariant.String, QVariant.Int, 
                    QVariant.Int, QVariant.Double, QVariant.Double,
                    QVariant.Double)
hydroJncIdNodeRiv=0
hydroJncIdNodeAqu=1
hydroJncIdNodeIrg=2
hydroJncIdNodeBor=3

# Subbasing layer specifications
subbasLayerName="Subbasin"
subbasLayerType=QGis.Polygon
subbasGeomType=QGis.WKBPolygon
subbasFieldNames=("NAME", "DESCR", "AREA", "X_CENTROID", "Y_CENTROID",
                  "RIVER_NODE", "RIVER_ID", "MEAN_SLOPE", "MEAN_ELEV", 
                  "PR_LENGTH", "LAG")
subbasFieldTypes=(QVariant.String, QVariant.String, QVariant.Double, 
                  QVariant.Double, QVariant.Double, QVariant.Int, QVariant.Int,
                  QVariant.Double, QVariant.Double, QVariant.Double, 
                  QVariant.Double)
subbasFieldNameArea=subbasFieldNames[2]
subbasFieldNameRivNode=subbasFieldNames[5]
subbasFieldNameRivId=subbasFieldNames[6]
subbasFieldNamePrimLen=subbasFieldNames[9]
subbasFieldNameX=subbasFieldNames[3]
subbasFieldNameY=subbasFieldNames[4]

# Spring specifications
springLayerName= "Spring"
springLayerType= QGis.Point
springGeomType= QGis.WKBPoint
springFieldNames=("NAME", "DESCR", "INI_DISCH", "X", "Y", "ALT", "GROUND_ID",
                  "SUB_ID", "COND")
springFieldTypes=(QVariant.String, QVariant.String, QVariant.Double, 
                  QVariant.Double, QVariant.Double, QVariant.Double, 
                  QVariant.Int, QVariant.Int, QVariant.Double,  )


# Aqueduct layer specifications
aquedLayerName= "Aqueduct"
#aquedLayerType= QGis.WKBLine

# Groundwater cells layer specifications
grdwatLayerName= "GroundWater"
grdwatLayerType= QGis.Polygon
grdwatGeomType= QGis.WKBPolygon
grdwatFieldNames=("NAME", "DESCR", "TYPE", "X_CENTROID", "Y_CENTROID", 
                  "INI_LEV", "TOP_LEVEL", "BOT_LEVEL", "POR", "COND", 
                  "COND_GRP", "POR_GRP", )
grdwatFieldTypes=(QVariant.String, QVariant.String, QVariant.Int, 
                  QVariant.Double, QVariant.Double, QVariant.Double, 
                  QVariant.Double, QVariant.Double, QVariant.Double, 
                  QVariant.Double, QVariant.Int, QVariant.Int, )

# Outlet layer specifications
outletLayerName="Outlet"
outletLayerType=QGis.WKBPoint
outletFieldNames=( "X", "Y")
outletFieldTypes=(QVariant.Double, QVariant.Double)

# DTB
dtmLayerName= "hdr"
