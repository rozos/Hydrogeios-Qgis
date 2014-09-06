from qgis.core import *
from PyQt4.QtCore import QVariant


# Precision of floats' comparisons
precise=3


# River layer specifications
riverLayerName="River"
riverLayerType=QGis.Line
riverGeomType=QGis.WKBLineString
riverFieldNames=("RIVER_ID", "NAME", "DESCR", "FROM_NODE", "TO_NODE", "LENGTH",
                 "WIDTH", "BANK_SLOPE", "ROUGH", "INFILT_CF", "Q_MAX", "Q_MIN",
                 "T_PERC", "ROUTING", "TRAV_TIME", "WGHT_X", )
riverFieldTypes=(QVariant.Int, QVariant.String, QVariant.String, QVariant.Int,
                 QVariant.Int, QVariant.Double, QVariant.Double,QVariant.Double,
                 QVariant.Double, QVariant.Double, QVariant.Double,
                 QVariant.Double, QVariant.Double, QVariant.Double,
                 QVariant.Double, QVariant.Double, )
riverFieldId= riverFieldNames[0]


# Field names given to start/end nodes of a segment
fromNodeFieldName= "FROM_NODE"
toNodeFieldName =   "TO_NODE"


# Groundwater cells layer specifications
grdwatLayerName= "GroundWater"
grdwatLayerType= QGis.Polygon
grdwatGeomType= QGis.WKBPolygon
grdwatFieldNames=("GROUND_ID", "NAME", "DESCR", "TYPE", "X_CENTROID",
                  "Y_CENTROID", "INI_LEV", "TOP_LEVEL", "BOT_LEVEL", "POR",
                  "COND", "COND_GRP", "POR_GRP", )
grdwatFieldTypes=(QVariant.Int, QVariant.String, QVariant.String, QVariant.Int,
                  QVariant.Double, QVariant.Double, QVariant.Double,
                  QVariant.Double, QVariant.Double, QVariant.Double,
                  QVariant.Double, QVariant.Int, QVariant.Int, )
grdwatFieldId=   grdwatFieldNames[0]
grdwatFieldName= grdwatFieldNames[1]


# Hydrojunction layer specifications
hydroJncLayerName="HydroJunction"
hydroJncFieldNames=("JUNCT_ID", "NAME", "DESCR", "JUNCT_TYPE", "TS_ID",
                    "X", "Y", "Z")
hydroJncLayerType= QGis.Point
hydroJncFieldTypes=(QVariant.Int, QVariant.String, QVariant.String,
                    QVariant.Int, QVariant.Int, QVariant.Double,
                    QVariant.Double, QVariant.Double)
hydroJncFieldId=hydroJncFieldNames[0]
hydroJncTypeRiv=0
hydroJncTypeAqu=1
hydroJncTypeIrg=2
hydroJncTypeBor=3


# Irrigation layer specifications
irrigLayerName="Irrigation"
irrigLayerType=QGis.Polygon
irrigGeomType=QGis.WKBPolygon
irrigFieldNames=("IRRIG_AREA", hydroJncFieldId, "RET_PIPE", "RET_RATIO")
irrigFieldTypes=(QVariant.Double, QVariant.Int, QVariant.Double,
                 QVariant.Double)
irrigFieldId  =  irrigFieldNames[0]
irrigFieldArea=  irrigFieldNames[1]


# Subbasing layer specifications
subbasLayerName="Subbasin"
subbasLayerType=QGis.Polygon
subbasGeomType=QGis.WKBPolygon
subbasFieldNames=("SUB_ID", "NAME", "DESCR", "AREA", "X_CENTROID", "Y_CENTROID",
                  "RIVER_NODE", riverFieldId, "MEAN_SLOPE", "MEAN_ELEV",
                  "PR_LENGTH", "LAG")
subbasFieldTypes=(QVariant.Int, QVariant.String, QVariant.String,
                  QVariant.Double, QVariant.Double, QVariant.Double,
                  QVariant.Int, QVariant.Int, QVariant.Double,
                  QVariant.Double, QVariant.Double, QVariant.Double)
subbasFieldId=      subbasFieldNames[0]
subbasFieldArea=    subbasFieldNames[3]
subbasFieldX=       subbasFieldNames[4]
subbasFieldY=       subbasFieldNames[5]
subbasFieldRivNode= subbasFieldNames[6]
subbasFieldPrimLen= subbasFieldNames[10]


# Borehole layer specifications
borehLayerName="Borehole"
borehLayerType=QGis.Point
borehGeomType=QGis.WKBPoint
borehFieldNames=("NAME", "DESCR", "TYPE", "X", "Y", "Z", grdwatFieldId,
                  subbasFieldId, "GROUP_ID", "PUMP_CAP", "PUMP_RAT", "DEPTH", )
borehFieldTypes=(QVariant.String, QVariant.String, QVariant.Int,
                 QVariant.Double, QVariant.Double,  QVariant.Double,
                 QVariant.Int, QVariant.Int, QVariant.Int, QVariant.Double,
                 QVariant.Double,  QVariant.Double, )
borehFieldGrdwatId= borehFieldNames[6]
borehFieldSubbasId= borehFieldNames[7]
borehFieldGroupId = borehFieldNames[8]


# Spring specifications
springLayerName= "Spring"
springLayerType= QGis.Point
springGeomType= QGis.WKBPoint
springFieldNames=("NAME", "DESCR", "INI_DISCH", "X", "Y", "ALT", grdwatFieldId,
                  subbasFieldId, "COND")
springFieldTypes=(QVariant.String, QVariant.String, QVariant.Double,
                  QVariant.Double, QVariant.Double, QVariant.Double,
                  QVariant.Int, QVariant.Int, QVariant.Double,  )


# Aqueduct layer specifications
aquedLayerName= "Aqueduct"
aquedLayerType= QGis.Line
aquedGeomType= QGis.WKBLineString


# Outlet layer specifications
outletLayerName="Outlet"
outletLayerType=QGis.WKBPoint
outletFieldNames=( "X", "Y")
outletFieldTypes=(QVariant.Double, QVariant.Double)


# RiverGround layer specifications
riverGrdwatLayerName="RiverGround"
riverGrdwatLayerType= QGis.Line
riverGrdwatGeomType= QGis.WKBLineString
riverGrdwatFieldNames=(riverFieldId, grdwatFieldId, "LENGTH",)
riverGrdwatFieldTypes=(QVariant.Int, QVariant.Int, QVariant.Double, )
riverGrdwatFieldGroundId=riverGrdwatFieldNames[1]
riverGrdwatFieldLength=riverGrdwatFieldNames[2]


# HRU layer specifications
HRULayerName="HRU"
HRULayerType= QGis.Polygon
HRUGeomType= QGis.WKBPolygon
HRUFieldNames=("HRU_ID", "DESCR", "NAME", "AREA", "HRU_CODE", "RNF_CF",
               "CAP", "KAPA", "LAMDA", "MI", "EPSILON", "EVAP_CAP",)
HRUFieldTypes=(QVariant.Int, QVariant.String, QVariant.String, QVariant.Double,
               QVariant.Int, QVariant.Double, QVariant.Double,
               QVariant.Double, QVariant.Double, QVariant.Double,
               QVariant.Double, QVariant.Double, )
HRUFieldId=HRUFieldNames[0]


# SubbasinHRU layer specifications
subbasHRULayerName="SubbasinHRU"
subbasHRULayerType= QGis.Polygon
subbasHRUGeomType= QGis.WKBPolygon
subbasHRUFieldNames=("NAME", "DESCR", HRUFieldId, subbasFieldId, "AREA",
                     "INI_STOR", "INI_EVAP", )
subbasHRUFieldTypes=(QVariant.String, QVariant.String, QVariant.Int,
                  QVariant.Int, QVariant.Double, QVariant.Double,
                  QVariant.Double, )
subbasHRUFieldArea=subbasHRUFieldNames[4]


# subGroundHRU layer specifications
grdwatSubbasHRULayerName="SubGroundHRU"
grdwatSubbasHRULayerType= QGis.Polygon
grdwatSubbasHRUGeomType= QGis.WKBPolygon
grdwatSubbasHRUFieldNames=(HRUFieldId, subbasFieldId, grdwatFieldId, "AREA",)
grdwatSubbasHRUFieldTypes=(QVariant.Int, QVariant.Int, QVariant.Int,
                        QVariant.Double, )
grdwatSubbasHRUFieldArea=grdwatSubbasHRUFieldNames[3]


# DTM raster
DTMlayerName= "hdr"


# HRU reclassified raster
HRUrasterLayerName= "HRUraster"
