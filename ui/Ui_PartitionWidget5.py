# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PartitionWidget.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PartitionWidget(object):
    def setupUi(self, PartitionWidget):
        PartitionWidget.setObjectName("PartitionWidget")
        PartitionWidget.resize(370, 333)
        self.verticalLayout = QtWidgets.QVBoxLayout(PartitionWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(PartitionWidget)
        self.groupBox.setCheckable(True)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.description = QtWidgets.QLabel(self.groupBox)
        self.description.setWordWrap(True)
        self.description.setObjectName("description")
        self.verticalLayout_2.addWidget(self.description)
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.setObjectName("comboBox")
        self.verticalLayout_2.addWidget(self.comboBox)
        self.minLayout = QtWidgets.QHBoxLayout()
        self.minLayout.setObjectName("minLayout")
        self.minCheckBox = QtWidgets.QCheckBox(self.groupBox)
        self.minCheckBox.setObjectName("minCheckBox")
        self.minLayout.addWidget(self.minCheckBox)
        self.minSpinBox = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.minSpinBox.setEnabled(False)
        self.minSpinBox.setObjectName("minSpinBox")
        self.minLayout.addWidget(self.minSpinBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.minLayout.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.minLayout)
        self.maxLayout = QtWidgets.QHBoxLayout()
        self.maxLayout.setObjectName("maxLayout")
        self.maxCheckBox = QtWidgets.QCheckBox(self.groupBox)
        self.maxCheckBox.setObjectName("maxCheckBox")
        self.maxLayout.addWidget(self.maxCheckBox)
        self.maxSpinBox = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.maxSpinBox.setEnabled(False)
        self.maxSpinBox.setObjectName("maxSpinBox")
        self.maxLayout.addWidget(self.maxSpinBox)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.maxLayout.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.maxLayout)
        self.binLayout = QtWidgets.QHBoxLayout()
        self.binLayout.setObjectName("binLayout")
        self.binCheckBox = QtWidgets.QCheckBox(self.groupBox)
        self.binCheckBox.setObjectName("binCheckBox")
        self.binLayout.addWidget(self.binCheckBox)
        self.binSpinBox = QtWidgets.QSpinBox(self.groupBox)
        self.binSpinBox.setEnabled(False)
        self.binSpinBox.setMinimum(1)
        self.binSpinBox.setProperty("value", 10)
        self.binSpinBox.setObjectName("binSpinBox")
        self.binLayout.addWidget(self.binSpinBox)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.binLayout.addItem(spacerItem2)
        self.verticalLayout_2.addLayout(self.binLayout)
        self.listView = QtWidgets.QListView(self.groupBox)
        self.listView.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed|QtWidgets.QAbstractItemView.SelectedClicked)
        self.listView.setObjectName("listView")
        self.verticalLayout_2.addWidget(self.listView)
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(PartitionWidget)
        self.binCheckBox.toggled['bool'].connect(self.binSpinBox.setEnabled)
        self.minCheckBox.toggled['bool'].connect(self.minSpinBox.setEnabled)
        self.maxCheckBox.toggled['bool'].connect(self.maxSpinBox.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(PartitionWidget)

    def retranslateUi(self, PartitionWidget):
        _translate = QtCore.QCoreApplication.translate
        PartitionWidget.setWindowTitle(_translate("PartitionWidget", "Form"))
        self.groupBox.setTitle(_translate("PartitionWidget", "Legend"))
        self.description.setText(_translate("PartitionWidget", "Change field and colors for stacked histograms. Double click to edit color. Single click on selected to edit label."))
        self.minCheckBox.setText(_translate("PartitionWidget", "Min:"))
        self.maxCheckBox.setText(_translate("PartitionWidget", "Max:"))
        self.binCheckBox.setText(_translate("PartitionWidget", "Bins:"))

