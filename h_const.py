from qgis.core import *
from PyQt5.QtCore import QVariant

# Define CRS
projectcrs="EPSG:2100"

# Precision of floats' comparisons
precise=3

# Value marking no data cells
nodataCode=-2147483647

# River layer specifications
riverLayerName="River"
riverWkbType=QgsWkbTypes.LineString
riverGeomType=QgsWkbTypes.LineGeometry
riverFieldNames=("RIVER_ID", "NAME", "DESCR", "FROM_NODE", "TO_NODE", "LENGTH",
                 "WIDTH", "BANK_SLOPE", "ROUGH", "INFILT_CF", "Q_MAX", "Q_MIN",
                 "T_PERC", "ROUTING", "TRAV_TIME", "WGHT_X", )
riverFieldTypes=(QVariant.Int, QVariant.String, QVariant.String, QVariant.Int,
                 QVariant.Int, QVariant.Double, QVariant.Double,QVariant.Double,
                 QVariant.Double, QVariant.Double, QVariant.Double,
                 QVariant.Double, QVariant.Double, QVariant.Double,
                 QVariant.Double, QVariant.Double, )
riverFieldId= riverFieldNames[0]
riverFieldLength= riverFieldNames[5]


# Field names given to start/end nodes of a segment
fromNodeFieldName= "FROM_NODE"
toNodeFieldName =   "TO_NODE"


# Groundwater cells layer specifications
grdwatLayerName= "GroundWater"
grdwatWkbType= QgsWkbTypes.Polygon
grdwatGeomType= QgsWkbTypes.PolygonGeometry
grdwatFieldNames=("GROUND_ID", "NAME", "DESCR", "TYPE", "X_CENTROID",
                  "Y_CENTROID", "AREA", "INI_LEV", "TOP_LEVEL", "BOT_LEVEL", 
                  "POR", "COND", "COND_GRP", "POR_GRP", )
grdwatFieldTypes=(QVariant.Int, QVariant.String, QVariant.String, QVariant.Int,
                  QVariant.Double, QVariant.Double ,QVariant.Double,
                  QVariant.Double, QVariant.Double, QVariant.Double, 
                  QVariant.Double, QVariant.Double, QVariant.Int, 
                  QVariant.Int, )
grdwatFieldId=   grdwatFieldNames[0]
grdwatFieldName= grdwatFieldNames[1]
grdwatFieldArea= grdwatFieldNames[6]


# Hydrojunction layer specifications
hydrojncLayerName="HydroJunction"
hydrojncFieldNames=("JUNCT_ID", "NAME", "DESCR", "JUNCT_TYPE", "TS_ID",
                    "X", "Y", "Z")
hydrojncWkbType= QgsWkbTypes.Point
hydrojncGeomType=QgsWkbTypes.PointGeometry
hydrojncFieldTypes=(QVariant.Int, QVariant.String, QVariant.String,
                    QVariant.Int, QVariant.Int, QVariant.Double,
                    QVariant.Double, QVariant.Double)
hydrojncFieldId=hydrojncFieldNames[0]
hydrojncFieldJuncttype=hydrojncFieldNames[3]
hydrojncTypeRiv=0
hydrojncTypeAqu=1
hydrojncTypeIrg=2
hydrojncTypeBor=3
hydrojncTypeSpr=4


# Irrigation layer specifications
irrigLayerName="Irrigation"
irrigWkbType=QgsWkbTypes.Polygon
irrigGeomType=QgsWkbTypes.PolygonGeometry
irrigFieldNames=("IRRIG_AREA", hydrojncFieldId, "RET_PIPE", "RET_RATIO")
irrigFieldTypes=(QVariant.Double, QVariant.Int, QVariant.Double,
                 QVariant.Double)
irrigFieldArea=  irrigFieldNames[0]


# River nodes
riverexitnodeLayerName= "RiverExitNode"
riverexitnodeWkbType= QgsWkbTypes.Point
riverexitnodeGeomType= QgsWkbTypes.PointGeometry
riverexitnodeFieldNames= ("NODE_ID", grdwatFieldId, hydrojncFieldId)
riverexitnodeFieldTypes= (QVariant.Int, QVariant.Int, QVariant.Int)
riverexitnodeFieldId= riverexitnodeFieldNames[0]


# Subbasing layer specifications
subbasLayerName="Subbasin"
subbasWkbType=QgsWkbTypes.Polygon
subbasGeomType=QgsWkbTypes.PolygonGeometry
subbasFieldNames=("SUB_ID", "NAME", "DESCR", "AREA", "X_CENTROID", "Y_CENTROID",
                  riverexitnodeFieldId, riverFieldId, "MEAN_SLOPE", "MEAN_ELEV",
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
borehWkbType=QgsWkbTypes.Point
borehGeomType=QgsWkbTypes.PointGeometry
borehFieldNames=("NAME", "DESCR", "TYPE", "X", "Y", "Z", grdwatFieldId,
                  subbasFieldId, "GROUP_ID", hydrojncFieldId, "PUMP_CAP", 
                  "PUMP_RAT", "DEPTH", )
borehFieldTypes=(QVariant.String, QVariant.String, QVariant.Int,
                 QVariant.Double, QVariant.Double,  QVariant.Double,
                 QVariant.Int, QVariant.Int, QVariant.Int, QVariant.Int,
                 QVariant.Double, QVariant.Double,  QVariant.Double, )
borehFieldGroupId = borehFieldNames[8]
borehFieldJunctId = borehFieldNames[9]


# Spring specifications
springLayerName= "Spring"
springWkbType=QgsWkbTypes.Point 
springGeomType=QgsWkbTypes.PointGeometry
springFieldNames=("NAME", "DESCR", hydrojncFieldId, "INI_DISCH", "X", "Y", 
                  "ALT", grdwatFieldId, subbasFieldId, "COND")
springFieldTypes=(QVariant.String, QVariant.String, QVariant.Int, 
                  QVariant.Double, QVariant.Double, QVariant.Double, 
                  QVariant.Double, QVariant.Int, QVariant.Int, 
                  QVariant.Double,  )


# Aqueduct layer specifications
aquedLayerName= "Aqueduct"
aquedWkbType=QgsWkbTypes.LineString 
aquedGeomType=QgsWkbTypes.LineGeometry
aquedFieldNames=("NAME", "DESCR", "LEAK_CF", "FROM_NODE", "TO_NODE", 
                 "LENGTH", "DISCH_CAP", "UNIT_COST", )
aquedFieldTypes=(QVariant.String, QVariant.String, QVariant.Double,
                 QVariant.Int, QVariant.Int, QVariant.Double, QVariant.Double,
                 QVariant.Double)
aquedFieldLength=aquedFieldNames[5]


# Outlet layer specifications
outletLayerName="Outlet"
outletWkbType=QgsWkbTypes.Point
outletFieldNames=( "X", "Y")
outletFieldTypes=(QVariant.Double, QVariant.Double)


# RiverGround layer specifications
riverGrdwatLayerName="RiverGround"
riverGrdwatWkbType=QgsWkbTypes.LineString
riverGrdwatGeomType= QgsWkbTypes.LineGeometry
riverGrdwatFieldNames=(riverFieldId, grdwatFieldId, "LENGTH",)
riverGrdwatFieldTypes=(QVariant.Int, QVariant.Int, QVariant.Double, )
riverGrdwatFieldGroundId=riverGrdwatFieldNames[1]
riverGrdwatFieldLength=riverGrdwatFieldNames[2]


# HRU layer specifications
HRULayerName="HRU"
HRUWkbType= QgsWkbTypes.Polygon
HRUGeomType= QgsWkbTypes.PolygonGeometry
HRUFieldNames=("HRU_ID", "DESCR", "NAME", "AREA", "HRU_CODE", "RNF_CF",
               "CAP", "KAPA", "LAMDA", "MI", "EPSILON", "EVAP_CAP",)
HRUFieldTypes=(QVariant.Int, QVariant.String, QVariant.String, QVariant.Double,
               QVariant.Int, QVariant.Double, QVariant.Double,
               QVariant.Double, QVariant.Double, QVariant.Double,
               QVariant.Double, QVariant.Double, )
HRUFieldId=HRUFieldNames[0]
HRUFieldCode=HRUFieldNames[4]
HRUFieldArea=HRUFieldNames[3]
#HRUundisFieldId="HRUundisID"


# SubbasinHRU layer specifications
subbasHRULayerName="SubbasinHRU"
subbasHRUWkbType= QgsWkbTypes.Polygon
subbasHRUGeomType= QgsWkbTypes.PolygonGeometry
subbasHRUFieldNames=("NAME", "DESCR", HRUFieldId, subbasFieldId, "AREA",
                     "INI_STOR", "INI_EVAP", )
subbasHRUFieldTypes=(QVariant.String, QVariant.String, QVariant.Int,
                  QVariant.Int, QVariant.Double, QVariant.Double,
                  QVariant.Double, )
subbasHRUFieldArea=subbasHRUFieldNames[4]


# SubGroundHRU layer specifications
grdwatSubbasHRULayerName="SubGroundHRU"
grdwatSubbasHRUWkbType= QgsWkbTypes.Polygon
grdwatSubbasHRUGeomType= QgsWkbTypes.PolygonGeometry
grdwatSubbasHRUFieldNames=(HRUFieldId, subbasFieldId, grdwatFieldId, "AREA",)
grdwatSubbasHRUFieldTypes=(QVariant.Int, QVariant.Int, QVariant.Int,
                        QVariant.Double, )
grdwatSubbasHRUFieldArea=grdwatSubbasHRUFieldNames[3]


# DEM raster
DEMlayerName= "hdr"


# HRU reclassified raster
HRUrasterLayerName= "HRUraster"


# Distance between groundwater cells
distLayerName= "Distance"
distFieldNames= ("CELL_1", "CELL_2", "DISTANCE" )
distFieldTypes= (QVariant.Int, QVariant.Int, QVariant.Double )


# Edge between groundwater cells
edgeLayerName= "Edge"
edgeFieldNames= ("CELL_1", "CELL_2", "EDGE", "IMPERM")
edgeFieldTypes= (QVariant.Int, QVariant.Int, QVariant.Double,
                 QVariant.Double )
