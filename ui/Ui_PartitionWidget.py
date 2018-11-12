# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PartitionWidget.ui'
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

class Ui_PartitionWidget(object):
    def setupUi(self, PartitionWidget):
        PartitionWidget.setObjectName(_fromUtf8("PartitionWidget"))
        PartitionWidget.resize(370, 333)
        self.verticalLayout = QtGui.QVBoxLayout(PartitionWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(PartitionWidget)
        self.groupBox.setCheckable(True)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.description = QtGui.QLabel(self.groupBox)
        self.description.setWordWrap(True)
        self.description.setObjectName(_fromUtf8("description"))
        self.verticalLayout_2.addWidget(self.description)
        self.comboBox = QtGui.QComboBox(self.groupBox)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.verticalLayout_2.addWidget(self.comboBox)
        self.minLayout = QtGui.QHBoxLayout()
        self.minLayout.setObjectName(_fromUtf8("minLayout"))
        self.minCheckBox = QtGui.QCheckBox(self.groupBox)
        self.minCheckBox.setObjectName(_fromUtf8("minCheckBox"))
        self.minLayout.addWidget(self.minCheckBox)
        self.minSpinBox = QtGui.QDoubleSpinBox(self.groupBox)
        self.minSpinBox.setEnabled(False)
        self.minSpinBox.setObjectName(_fromUtf8("minSpinBox"))
        self.minLayout.addWidget(self.minSpinBox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.minLayout.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.minLayout)
        self.maxLayout = QtGui.QHBoxLayout()
        self.maxLayout.setObjectName(_fromUtf8("maxLayout"))
        self.maxCheckBox = QtGui.QCheckBox(self.groupBox)
        self.maxCheckBox.setObjectName(_fromUtf8("maxCheckBox"))
        self.maxLayout.addWidget(self.maxCheckBox)
        self.maxSpinBox = QtGui.QDoubleSpinBox(self.groupBox)
        self.maxSpinBox.setEnabled(False)
        self.maxSpinBox.setObjectName(_fromUtf8("maxSpinBox"))
        self.maxLayout.addWidget(self.maxSpinBox)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.maxLayout.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.maxLayout)
        self.binLayout = QtGui.QHBoxLayout()
        self.binLayout.setObjectName(_fromUtf8("binLayout"))
        self.binCheckBox = QtGui.QCheckBox(self.groupBox)
        self.binCheckBox.setObjectName(_fromUtf8("binCheckBox"))
        self.binLayout.addWidget(self.binCheckBox)
        self.binSpinBox = QtGui.QSpinBox(self.groupBox)
        self.binSpinBox.setEnabled(False)
        self.binSpinBox.setMinimum(1)
        self.binSpinBox.setProperty("value", 10)
        self.binSpinBox.setObjectName(_fromUtf8("binSpinBox"))
        self.binLayout.addWidget(self.binSpinBox)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.binLayout.addItem(spacerItem2)
        self.verticalLayout_2.addLayout(self.binLayout)
        self.listView = QtGui.QListView(self.groupBox)
        self.listView.setEditTriggers(QtGui.QAbstractItemView.EditKeyPressed|QtGui.QAbstractItemView.SelectedClicked)
        self.listView.setObjectName(_fromUtf8("listView"))
        self.verticalLayout_2.addWidget(self.listView)
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(PartitionWidget)
        QtCore.QObject.connect(self.binCheckBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.binSpinBox.setEnabled)
        QtCore.QObject.connect(self.minCheckBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.minSpinBox.setEnabled)
        QtCore.QObject.connect(self.maxCheckBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.maxSpinBox.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(PartitionWidget)

    def retranslateUi(self, PartitionWidget):
        PartitionWidget.setWindowTitle(_translate("PartitionWidget", "Form", None))
        self.groupBox.setTitle(_translate("PartitionWidget", "Legend", None))
        self.description.setText(_translate("PartitionWidget", "Change field and colors for stacked histograms. Double click to edit color. Single click on selected to edit label.", None))
        self.minCheckBox.setText(_translate("PartitionWidget", "Min:", None))
        self.maxCheckBox.setText(_translate("PartitionWidget", "Max:", None))
        self.binCheckBox.setText(_translate("PartitionWidget", "Bins:", None))

