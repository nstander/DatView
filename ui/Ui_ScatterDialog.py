# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ScatterDialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ScatterDialog(object):
    def setupUi(self, ScatterDialog):
        ScatterDialog.setObjectName(_fromUtf8("ScatterDialog"))
        ScatterDialog.resize(193, 203)
        self.gridLayout = QtGui.QGridLayout(ScatterDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(ScatterDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.xCombo = QtGui.QComboBox(ScatterDialog)
        self.xCombo.setObjectName(_fromUtf8("xCombo"))
        self.gridLayout.addWidget(self.xCombo, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(ScatterDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.yCombo = QtGui.QComboBox(ScatterDialog)
        self.yCombo.setObjectName(_fromUtf8("yCombo"))
        self.gridLayout.addWidget(self.yCombo, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(ScatterDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.zCombo = QtGui.QComboBox(ScatterDialog)
        self.zCombo.setObjectName(_fromUtf8("zCombo"))
        self.gridLayout.addWidget(self.zCombo, 2, 1, 1, 1)
        self.label_4 = QtGui.QLabel(ScatterDialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.cCombo = QtGui.QComboBox(ScatterDialog)
        self.cCombo.setObjectName(_fromUtf8("cCombo"))
        self.gridLayout.addWidget(self.cCombo, 3, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ScatterDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)

        self.retranslateUi(ScatterDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ScatterDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ScatterDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ScatterDialog)

    def retranslateUi(self, ScatterDialog):
        ScatterDialog.setWindowTitle(_translate("ScatterDialog", "Scatter Plot", None))
        self.label.setText(_translate("ScatterDialog", "X Axis:", None))
        self.label_2.setText(_translate("ScatterDialog", "Y Axis:", None))
        self.label_3.setText(_translate("ScatterDialog", "Z Axis:", None))
        self.label_4.setText(_translate("ScatterDialog", "Color By:", None))

