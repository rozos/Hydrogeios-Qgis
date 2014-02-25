# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_hydrogeios.ui'
#
# Created: Tue Feb 25 22:40:23 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Hydrogeios(object):
    def setupUi(self, Hydrogeios):
        Hydrogeios.setObjectName(_fromUtf8("Hydrogeios"))
        Hydrogeios.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(Hydrogeios)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.retranslateUi(Hydrogeios)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Hydrogeios.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Hydrogeios.reject)
        QtCore.QMetaObject.connectSlotsByName(Hydrogeios)

    def retranslateUi(self, Hydrogeios):
        Hydrogeios.setWindowTitle(QtGui.QApplication.translate("Hydrogeios", "Hydrogeios", None, QtGui.QApplication.UnicodeUTF8))

