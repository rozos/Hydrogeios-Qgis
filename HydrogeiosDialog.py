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
"""
from PyQt4 import QtCore, QtGui 
from Ui_Hydrogeios import Ui_Hydrogeios
# create the dialog for Hydrogeios
class HydrogeiosDialog(QtGui.QDialog):
  def __init__(self): 
    QtGui.QDialog.__init__(self) 
    # Set up the user interface from Designer. 
    self.ui = Ui_Hydrogeios ()
    self.ui.setupUi(self)