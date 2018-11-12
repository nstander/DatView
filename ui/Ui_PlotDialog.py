# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PlotDialog.ui'
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

class Ui_PlotDialog(object):
    def setupUi(self, PlotDialog):
        PlotDialog.setObjectName(_fromUtf8("PlotDialog"))
        PlotDialog.resize(358, 255)
        self.verticalLayout_2 = QtGui.QVBoxLayout(PlotDialog)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.description = QtGui.QLabel(PlotDialog)
        self.description.setWordWrap(True)
        self.description.setObjectName(_fromUtf8("description"))
        self.verticalLayout_2.addWidget(self.description)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(PlotDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.xCombo = QtGui.QComboBox(PlotDialog)
        self.xCombo.setObjectName(_fromUtf8("xCombo"))
        self.horizontalLayout.addWidget(self.xCombo)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(PlotDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.yCombo = QtGui.QComboBox(PlotDialog)
        self.yCombo.setObjectName(_fromUtf8("yCombo"))
        self.horizontalLayout_2.addWidget(self.yCombo)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_3 = QtGui.QLabel(PlotDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_3.addWidget(self.label_3)
        self.zCombo = QtGui.QComboBox(PlotDialog)
        self.zCombo.setObjectName(_fromUtf8("zCombo"))
        self.horizontalLayout_3.addWidget(self.zCombo)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_4 = QtGui.QLabel(PlotDialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_4.addWidget(self.label_4)
        self.cCombo = QtGui.QComboBox(PlotDialog)
        self.cCombo.setObjectName(_fromUtf8("cCombo"))
        self.horizontalLayout_4.addWidget(self.cCombo)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.logCheckBox = QtGui.QCheckBox(PlotDialog)
        self.logCheckBox.setObjectName(_fromUtf8("logCheckBox"))
        self.verticalLayout_2.addWidget(self.logCheckBox)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(PlotDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(PlotDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PlotDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PlotDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PlotDialog)

    def retranslateUi(self, PlotDialog):
        PlotDialog.setWindowTitle(_translate("PlotDialog", "Scatter Plot", None))
        self.description.setText(_translate("PlotDialog", "TextLabel", None))
        self.label.setText(_translate("PlotDialog", "X Axis:", None))
        self.label_2.setText(_translate("PlotDialog", "Y Axis:", None))
        self.label_3.setText(_translate("PlotDialog", "Z Axis:", None))
        self.label_4.setText(_translate("PlotDialog", "Color By:", None))
        self.logCheckBox.setText(_translate("PlotDialog", "Log Scale (Colors)", None))

