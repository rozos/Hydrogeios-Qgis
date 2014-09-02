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
irrigFieldArea=  irrigFieldNames[0]
irrigFieldJncId= irrigFieldNames[1]


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
borehFieldGroundId= borehFieldNames[6]
borehFieldSubbasId= borehFieldNames[7]
borehFieldGroupId = borehFieldNames[8]


# Hydrojunction layer specifications
hydroJncLayerName="HydroJunction"
hydroJncNames=("NAME", "DESCR", "JUNCT_TYPE", "TS_ID", "X", "Y", "Z")
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
subbasFieldArea=    subbasFieldNames[2]
subbasFieldX=       subbasFieldNames[3]
subbasFieldY=       subbasFieldNames[4]
subbasFieldRivNode= subbasFieldNames[5]
subbasFieldRivId=   subbasFieldNames[6]
subbasFieldPrimLen= subbasFieldNames[9]


# Spring specifications
springLayerName= "Spring"
springLayerType= QGis.Point
springGeomType= QGis.WKBPoint
springFieldNames=("NAME", "DESCR", "INI_DISCH", "X", "Y", "ALT", "GROUND_ID",
                  "SUB_ID", "COND")
springFieldTypes=(QVariant.String, QVariant.String, QVariant.Double, 
                  QVariant.Double, QVariant.Double, QVariant.Double, 
                  QVariant.Int, QVariant.Int, QVariant.Double,  )
springFieldGroundId= springFieldNames[6]
springFieldSubbasId= springFieldNames[7]


# Aqueduct layer specifications
aquedLayerName= "Aqueduct"
aquedLayerType= QGis.Line
aquedGeomType= QGis.WKBLineString


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
grdwatFieldName= grdwatFieldNames[0]


# Outlet layer specifications
outletLayerName="Outlet"
outletLayerType=QGis.WKBPoint
outletFieldNames=( "X", "Y")
outletFieldTypes=(QVariant.Double, QVariant.Double)


# RiverGround layer specifications
riverGroundLayerName="RiverGround"
riverGroundLayerType= QGis.Line
riverGroundGeomType= QGis.WKBLineString
riverGroundFieldNames=("RIVERID", "GROUND_ID", "LENGTH",)
riverGroundFieldTypes=(QVariant.Int, QVariant.Int, QVariant.Double, )
riverGroundFieldRiverId=riverGroundFieldNames[0]
riverGroundFieldGroundId=riverGroundFieldNames[1]
riverGroundFieldLength=riverGroundFieldNames[2]


# HRU layer specifications
HRULayerName="HRU"
HRULayerType= QGis.Polygon
HRUGeomType= QGis.WKBPolygon
HRUFieldNames=("DESCR", "NAME", "AREA", "HRU_CODE", "RNF_CF", "CAP", "KAPA",
               "LAMDA", "MI", "EPSILON", "EVAP_CAP",)
HRUFieldTypes=(QVariant.String, QVariant.String, QVariant.Double,
               QVariant.Int, QVariant.Double, QVariant.Double, 
               QVariant.Double, QVariant.Double, QVariant.Double, 
               QVariant.Double, QVariant.Double, )


# subdHRU layer specifications
subHRULayerName="SubbasinHRU"
subHRULayerType= QGis.Polygon
subHRUGeomType= QGis.WKBPolygon
subHRUFieldNames=("NAME", "DESCR", "HRU_ID", "SUB_ID", "AREA", "INI_STOR",
                  "INI_EVAP", )
subHRUFieldTypes=(QVariant.String, QVariant.String, QVariant.Int, 
                  QVariant.Int, QVariant.Double, QVariant.Double, 
                  QVariant.Double, )


# subGroundHRU layer specifications
groundSubHRULayerName="SubGroundHRU"
groundSubHRULayerType= QGis.Polygon
groundSubHRUGeomType= QGis.WKBPolygon
groundSubHRUFieldNames=("HRU_ID", "SUB_ID", "GROUND_ID", "AREA",)
groundSubHRUFieldTypes=(QVariant.Int, QVariant.Int, QVariant.Int, 
                        QVariant.Double, )


# DTB
dtmLayerName= "hdr"
