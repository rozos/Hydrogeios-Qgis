import subprocess
import os.path

path=""
dem=""

def argument(arg, suffix=None, ext="tif"):
    if suffix==None: 
        suffix=arg
    pathdem =os.path.join(path, dem ) 
    return " -" + arg + " " + pathdem + suffix + "."+ext


def outletsarg(outlets):
    if outlets!=None:
        pathout =os.path.join(path, outlets) 
        return  " -o " + pathout
    else:
        return ""


def pitremove():
    return "pitremove" + argument("z", "") + argument("fel")


def d8flowdir():
    return  "d8flowdir" + argument("fel") + argument("p")  + argument("sd8")


def dinfflowdir():
    return "dinfflowdir" + argument("fel") + argument("ang") + argument("slp")


def aread8():
    return  "aread8" + argument("p") + argument("ad8")


def aread8_outlets(outlets):
    return "aread8" + outletsarg(outlets) + argument("p")  \
                    + argument("wg","ss") + argument("ad8", "ssa")

def areadinf():
    return "areadinf" + argument("ang") + argument("sca")


def gridnet():
    return  "gridnet" + argument("p") + argument("plen") \
                      + argument("tlen") + + argument("gord")


def peukerdouglas():
    return  "peukerdoublas" + argument("fel") + argument("ss")


def dropanalysis( outlets):
    return  "dropanalysis" + outletsarg(outlets) + argument("p") \
                           + argument("fel") + argument("ssa") \
                           + argument("drp","drp","txt")


def threshold(thresh):
    return + "thresh" + argument("ssa") + argument("src") \
                      + " -thresh " + str(thresh)


def streamnet(thresh):
    return + "streamnet" + argument("fel") + argument("p") + argument("ad8") \
                         + argument("src") + argument("ord") \
                         + argument("tree", "tree", "dat") \
                         + argument("coord", "coord", "dat") \
                         + argument("net", "net", "shp") + argument("w")


def tauDemDelineation(tauDem, path, dem, thresh, outlets):
    """taudem: the path to TauDEM tools, path: the path to project,
    thresh: the threshold to create waterbasin, outlets: the shapefile 
    (path+filename+shp) with outlets"""
    #subprocess.call(
    pass
