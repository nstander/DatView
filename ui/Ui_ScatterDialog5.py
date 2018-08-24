# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ScatterDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ScatterDialog(object):
    def setupUi(self, ScatterDialog):
        ScatterDialog.setObjectName("ScatterDialog")
        ScatterDialog.resize(193, 203)
        self.gridLayout = QtWidgets.QGridLayout(ScatterDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(ScatterDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.xCombo = QtWidgets.QComboBox(ScatterDialog)
        self.xCombo.setObjectName("xCombo")
        self.gridLayout.addWidget(self.xCombo, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(ScatterDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.yCombo = QtWidgets.QComboBox(ScatterDialog)
        self.yCombo.setObjectName("yCombo")
        self.gridLayout.addWidget(self.yCombo, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(ScatterDialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.zCombo = QtWidgets.QComboBox(ScatterDialog)
        self.zCombo.setObjectName("zCombo")
        self.gridLayout.addWidget(self.zCombo, 2, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(ScatterDialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.cCombo = QtWidgets.QComboBox(ScatterDialog)
        self.cCombo.setObjectName("cCombo")
        self.gridLayout.addWidget(self.cCombo, 3, 1, 1, 1)
        self.logCheckBox = QtWidgets.QCheckBox(ScatterDialog)
        self.logCheckBox.setObjectName("logCheckBox")
        self.gridLayout.addWidget(self.logCheckBox, 4, 0, 1, 2)
        self.buttonBox = QtWidgets.QDialogButtonBox(ScatterDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 2)

        self.retranslateUi(ScatterDialog)
        self.buttonBox.accepted.connect(ScatterDialog.accept)
        self.buttonBox.rejected.connect(ScatterDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ScatterDialog)

    def retranslateUi(self, ScatterDialog):
        _translate = QtCore.QCoreApplication.translate
        ScatterDialog.setWindowTitle(_translate("ScatterDialog", "Scatter Plot"))
        self.label.setText(_translate("ScatterDialog", "X Axis:"))
        self.label_2.setText(_translate("ScatterDialog", "Y Axis:"))
        self.label_3.setText(_translate("ScatterDialog", "Z Axis:"))
        self.label_4.setText(_translate("ScatterDialog", "Color By:"))
        self.logCheckBox.setText(_translate("ScatterDialog", "Log Scale (Colors)"))

