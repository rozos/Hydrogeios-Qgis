import subprocess
import os.path

_path=""
_dem=""
_taudem=""

def argument(arg, suffix=None, ext="tif"):
    if suffix==None: 
        suffix=arg
    pathdem =os.path.join(_path, _dem ) 
    return " -" + arg + " " + pathdem + suffix + "."+ext


def outletsarg(outlets):
    if outlets!=None:
        pathout =os.path.join(_path, outlets) 
        return  " -o " + pathout
    else:
        return ""


def pitremove():
    return _taudem + "/pitremove" + argument("z", "") + argument("fel")


def d8flowdir():
    return  _taudem + "/d8flowdir" + argument("fel") + argument("p")  + argument("sd8")


def dinfflowdir():
    return _taudem + "/dinfflowdir" + argument("fel") + argument("ang") + argument("slp")


def aread8():
    return  _taudem + "/aread8" + argument("p") + argument("ad8")


def aread8_outlets(outlets):
    return _taudem + "/aread8" + outletsarg(outlets) + argument("p")  \
                    + argument("wg","ss") + argument("ad8", "ssa")

def areadinf():
    return _taudem + "/areadinf" + argument("ang") + argument("sca")


def gridnet():
    return _taudem + "/gridnet" + argument("p") + argument("plen") \
                      + argument("tlen") + + argument("gord")


def peukerdouglas():
    return _taudem + "/peukerdoublas" + argument("fel") + argument("ss")


def dropanalysis( outlets):
    return _taudem + "/dropanalysis" + outletsarg(outlets) + argument("p") \
                           + argument("fel") + argument("ssa") \
                           + argument("drp","drp","txt")


def threshold(thresh):
    return _taudem + "/thresh" + argument("ssa") + argument("src") \
                      + " -thresh " + str(thresh)


def streamnet():
    return _taudem + "/streamnet" + argument("fel") + argument("p") + argument("ad8") \
                         + argument("src") + argument("ord") \
                         + argument("tree", "tree", "dat") \
                         + argument("coord", "coord", "dat") \
                         + argument("net", "net", "shp") + argument("w")


def iniTauDEM(taudem, path, dem):
    """Initialize the global variables of TauDEM module."""
    global _path, _dem, _taudem
    _path=path
    _dem=dem
    _taudem=taudem
