"""
/***************************************************************************
Name			 	 : Hydrogeios plugin
Description          : Performs geographic operations required to build a Hydrogeios project.
Date                 : 25/Feb/14 
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
 This script initializes the plugin, making it known to QGIS.
"""
def name(): 
  return "Hydrogeios plugin" 
def description():
  return "Performs geographic operations required to build a Hydrogeios project."
def version(): 
  return "Version 0.1" 
def qgisMinimumVersion():
  return "1.0"
def classFactory(iface): 
  # load Hydrogeios class from file Hydrogeios
  from Hydrogeios import Hydrogeios 
  return Hydrogeios(iface)
