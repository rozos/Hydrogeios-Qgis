# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file Ui_Hydrogeios.ui
# Created with: PyQt4 UI code generator 4.4.4
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Hydrogeios(object):
    def setupUi(self, Hydrogeios):
        Hydrogeios.setObjectName("Hydrogeios")
        Hydrogeios.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(Hydrogeios)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.retranslateUi(Hydrogeios)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Hydrogeios.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Hydrogeios.reject)
        QtCore.QMetaObject.connectSlotsByName(Hydrogeios)

    def retranslateUi(self, Hydrogeios):
        Hydrogeios.setWindowTitle(QtGui.QApplication.translate("Hydrogeios", "Hydrogeios", None, QtGui.QApplication.UnicodeUTF8))
