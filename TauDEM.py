import subprocess
import os.path


def argument(path, dem, arg, suffix=arg, ext="tif")
    pathdem =os.path.join(path, dem ) 
    return " -" + suffix + pathdem + arg + "."+ext


def outletsarg(outlets):
    if outlets!=None:
        pathout =os.path.join(path, outlets) 
        return  " -o " + pathout
    else:
        return ""


def pitremove(tauDem, path, dem):
    return tauDem+"pitremove -z "+ pathdem +".tif" + argument(path, dem, "fel")


def d8flowdir(tauDem, path, dem):
    return tauDem + "d8flowdir" + argument(path, dem,"fel") \
                  + argument(path, dem,"p")  \
                  + argument(path, dem, "sd8")


def dinfflowdir(tauDem, path, dem):
    return tauDem + "dinfflowdir" + argument(path, dem,"fel") \
                  + argument(path, dem,"ang") + \
                  + argument(path, dem, "slp")


def aread8(tauDem, path, dem):
    return tauDem + "aread8" + argument(path, dem,"p") \
                  + argument(path, dem,"ad8")


def aread8_outlets(tauDem, path, dem, outlets):
    return tauDem + "aread8" + outletsarg(outlets) + argument(path, dem,"p") \
                  + argument(path, dem,"wg","ss") \
                  + argument(path, dem,"ad8", "ssa")

def areadinf(tauDem, path, dem):
    return tauDem + "areadinf" + argument(path, dem,"ang") \
                  + argument(path, dem,"sca")


def gridnet(tauDem, path, dem):
    return tauDem + "gridnet" + argument(path, dem,"p") \
                  + argument(path, dem,"plen") + \
                  + argument(path, dem,"tlen") + \
                  + argument(path, dem,"gord")


def peukerdouglas(tauDem, path, dem):
    return tauDem + "peukerdoublas" + argument(path, dem,"fel") \
                  + argument(path, dem,"ss")


def dropanalysis(tauDem, path, dem, outlets):
    return tauDem + "dropanalysis" + outletsarg(outlets) \
                  + argument(path, dem,"p") \
                  + argument(path, dem,"fel") \
                  + argument(path, dem,"ssa")
                  + argument(path, dem,"drp","drp","txt")


def threshold(tauDem, path, dem, thresh):
    return tauDem + "thresh" + argument(path, dem,"ssa") \
                  + argument(path, dem,"src") \
                  + " -thresh " + str(thresh)


def streamnet(tauDem, path, dem, thresh):
    return tauDem + "streamnet" + argument(path, dem,"fel") \
                  + argument(path, dem,"p") \
                  + argument(path, dem,"ad8") \
                  + argument(path, dem,"src") \
                  + argument(path, dem,"ord") \
                  + argument(path, dem,"tree", "tree", "dat") \
                  + argument(path, dem,"coord", "coord", "dat") \
                  + argument(path, dem,"net", "net", "shp") \
                  + argument(path, dem,"w")


def tauDemDelineation(tauDem, path, dem, thresh, outlets):
    """taudem: the path to TauDEM tools, path: the path to project,
    thresh: the threshold to create waterbasin, outlets: the shapefile 
    (path+filename+shp) with outlets"""
    #subprocess.call(
    pass
