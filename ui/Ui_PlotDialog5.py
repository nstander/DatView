# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PlotDialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PlotDialog(object):
    def setupUi(self, PlotDialog):
        PlotDialog.setObjectName("PlotDialog")
        PlotDialog.resize(193, 245)
        self.verticalLayout = QtWidgets.QVBoxLayout(PlotDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.description = QtWidgets.QLabel(PlotDialog)
        self.description.setWordWrap(True)
        self.description.setObjectName("description")
        self.verticalLayout.addWidget(self.description)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(PlotDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.xCombo = QtWidgets.QComboBox(PlotDialog)
        self.xCombo.setObjectName("xCombo")
        self.horizontalLayout.addWidget(self.xCombo)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(PlotDialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.yCombo = QtWidgets.QComboBox(PlotDialog)
        self.yCombo.setObjectName("yCombo")
        self.horizontalLayout_2.addWidget(self.yCombo)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(PlotDialog)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.zCombo = QtWidgets.QComboBox(PlotDialog)
        self.zCombo.setObjectName("zCombo")
        self.horizontalLayout_3.addWidget(self.zCombo)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(PlotDialog)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.cCombo = QtWidgets.QComboBox(PlotDialog)
        self.cCombo.setObjectName("cCombo")
        self.horizontalLayout_4.addWidget(self.cCombo)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.logCheckBox = QtWidgets.QCheckBox(PlotDialog)
        self.logCheckBox.setObjectName("logCheckBox")
        self.verticalLayout.addWidget(self.logCheckBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(PlotDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(PlotDialog)
        self.buttonBox.accepted.connect(PlotDialog.accept)
        self.buttonBox.rejected.connect(PlotDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PlotDialog)

    def retranslateUi(self, PlotDialog):
        _translate = QtCore.QCoreApplication.translate
        PlotDialog.setWindowTitle(_translate("PlotDialog", "Scatter Plot"))
        self.description.setText(_translate("PlotDialog", "TextLabel"))
        self.label.setText(_translate("PlotDialog", "X Axis:"))
        self.label_2.setText(_translate("PlotDialog", "Y Axis:"))
        self.label_3.setText(_translate("PlotDialog", "Z Axis:"))
        self.label_4.setText(_translate("PlotDialog", "Color By:"))
        self.logCheckBox.setText(_translate("PlotDialog", "Log Scale (Colors)"))

