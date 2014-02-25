# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Hydrogeios
                                 A QGIS plugin
 Manipulate geo-data for Hydrogeios model
                             -------------------
        begin                : 2014-02-25
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

def classFactory(iface):
    # load Hydrogeios class from file Hydrogeios
    from hydrogeios import Hydrogeios
    return Hydrogeios(iface)
