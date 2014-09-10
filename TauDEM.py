# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TauDEM    
                                 A QGIS function
 Use this function to automate TauDEM commands run from within QGIS
                              -------------------
        begin                : 2014-09-09
        copyright            : (C) 2014 by ITIA
        email                : rozos@itia.ntua.gr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import subprocess
import os

_path=""
_dem=""
_taudem=""


def initialize(taudemPath, projectPath, DEMname):
    """Initialize the global variables of TauDEM module."""
    global _path, _dem, _taudem
    _path   = projectPath
    _dem    = DEMname
    _taudem = taudemPath



def autoDelineate(thresh, outlet=None):
    """Run all TauDEM commands to delineate a watershed."""
    if _path=="" or _dem=="" or _taudem=="":
        return "Please run initialize() first!"

    res = pitremove()
    if res != 0:
        return "pitremove failed with " + str(res)
    res = d8flowdir()
    if res != 0:
        return "d8flowdir failed with " + str(res)
    res = dinfflowdir()
    if res != 0:
        return "dinfflowdir failed with " + str(res)
    res = aread8()
    if res != 0:
        return "aread8 failed with " + str(res)
    res = areadinf()
    if res != 0:
        return "areadinf failed with " + str(res)
    res = gridnet()
    if res != 0:
        return "gridnet failed with " + str(res)
    res = peukerdouglas()
    if res != 0:
        return "peukerdouglas failed with " + str(res)
    res = aread8_outlet(outlet)
    if res != 0:
        return "aread8_outlet failed with " + str(res)
    if outlet!=None: res = dropanalysis(outlet)
    if res != 0:
        return "dropanalysis failed with " + str(res)
    res = threshold(thresh)
    if res != 0:
        return "threshold failed with " + str(res)
    res = streamnet(outlet)
    if res != 0:
        return "streamnet failed with " + str(res)

    return "OK!"



def _argument(arg, suffix=None, ext="tif", basename=None):
    if suffix==None: 
        suffix=arg
    if basename==None:
        pathdem =os.path.join(_path, _dem ) 
    else:
        pathdem =os.path.join(_path, basename ) 
    return " -" + arg + " " + pathdem + suffix + "."+ext



def _outletarg(outlet):
    if outlet!=None:
        pathout =os.path.join(_path, outlet) 
        return  " -o " + pathout + ".shp"
    else:
        return ""



def _execute(cmd):
    """Executes a taudem command and handle errors accordingly."""
    res = os.system(os.path.join(_taudem,cmd))
    if res!=0:
        errlogFile = os.path.join(_path, "error.log") 
        try:
            res =os.system(os.path.join(_taudem,cmd)+" 1> "+errlogFile+" 2>&1")
            f=open(errlogFile, 'a+')
            f.write('\n\n PREVIOUS OUTPUT WAS PRODUCED BY THE FOLLOWING \n')
            f.write(os.path.join(_taudem,cmd) +'\n')
        except Exception as e:
            res = str(e)
    return res



def pitremove():
    cmd = "pitremove" + _argument("z", "") + _argument("fel")
    return _execute(cmd)



def d8flowdir():
    cmd=  "d8flowdir" + _argument("fel") + _argument("p") + _argument("sd8")
    return _execute(cmd)



def dinfflowdir():
    cmd= "dinfflowdir" + _argument("fel") + _argument("ang") + _argument("slp")
    return _execute(cmd)



def aread8():
    cmd = "aread8" + _argument("p") + _argument("ad8")
    return _execute(cmd)



def aread8_outlet(outlet):
    cmd =  "aread8" + _outletarg(outlet) + _argument("p")  \
                     + _argument("wg","ss") + _argument("ad8", "ssa")
    return _execute(cmd)



def areadinf():
    cmd = "areadinf" + _argument("ang") + _argument("sca")
    return _execute(cmd)



def gridnet():
    cmd = "gridnet" + _argument("p") + _argument("plen") \
                     + _argument("tlen") + _argument("gord")
    return _execute(cmd)



def peukerdouglas():
    cmd = "peukerdouglas" + _argument("fel") + _argument("ss")
    return _execute(cmd)



def dropanalysis(outlet):
    cmd = "dropanalysis" + _outletarg(outlet) + _argument("p") \
                         + _argument("fel")+ _argument("ssa")+ _argument("ad8")\
                         + _argument("drp","drp","txt")
    return _execute(cmd)



def threshold(thresh):
    cmd = "threshold"+_argument("ssa")+_argument("src")+" -thresh " +str(thresh)
    return _execute(cmd)



def gagewatershed(gaugingStations):
    cmd = "gagewatershed" + _argument("p") + _outletarg(gaugingStations) \
                          + _argument("gw")
    return _execute(cmd)



def streamnet(outlet):
    cmd = "streamnet" + _argument("fel") + _argument("p") + _argument("ad8") \
                      + _argument("src") + _argument("ord") \
                      + _argument("tree", "tree", "dat") \
                      + _argument("coord", "coord", "dat")  \
                      + _outletarg(outlet) \
                      + _argument("net", "", "shp","River") + _argument("w")
    return _execute(cmd)
