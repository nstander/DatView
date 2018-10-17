# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FilterPanel.ui'
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

class Ui_FilterPanel(object):
    def setupUi(self, FilterPanel):
        FilterPanel.setObjectName(_fromUtf8("FilterPanel"))
        FilterPanel.resize(487, 564)
        self.verticalLayout_5 = QtGui.QVBoxLayout(FilterPanel)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.splitter = QtGui.QSplitter(FilterPanel)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.widget = QtGui.QWidget(self.splitter)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.partitionBox = QtGui.QGroupBox(self.widget)
        self.partitionBox.setCheckable(True)
        self.partitionBox.setChecked(False)
        self.partitionBox.setObjectName(_fromUtf8("partitionBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.partitionBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.partComboBox = QtGui.QComboBox(self.partitionBox)
        self.partComboBox.setObjectName(_fromUtf8("partComboBox"))
        self.horizontalLayout_4.addWidget(self.partComboBox)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.partitionBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.partBinSpinBox = QtGui.QSpinBox(self.partitionBox)
        self.partBinSpinBox.setMinimum(1)
        self.partBinSpinBox.setProperty("value", 10)
        self.partBinSpinBox.setObjectName(_fromUtf8("partBinSpinBox"))
        self.horizontalLayout.addWidget(self.partBinSpinBox)
        self.horizontalLayout_4.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(self.partitionBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.partMinSpinBox = QtGui.QDoubleSpinBox(self.partitionBox)
        self.partMinSpinBox.setObjectName(_fromUtf8("partMinSpinBox"))
        self.horizontalLayout_2.addWidget(self.partMinSpinBox)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_3 = QtGui.QLabel(self.partitionBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_3.addWidget(self.label_3)
        self.partMaxSpinBox = QtGui.QDoubleSpinBox(self.partitionBox)
        self.partMaxSpinBox.setObjectName(_fromUtf8("partMaxSpinBox"))
        self.horizontalLayout_3.addWidget(self.partMaxSpinBox)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.partitionList = QtGui.QListView(self.partitionBox)
        self.partitionList.setObjectName(_fromUtf8("partitionList"))
        self.verticalLayout.addWidget(self.partitionList)
        self.verticalLayout_4.addWidget(self.partitionBox)
        self.flaggedBox = QtGui.QGroupBox(self.widget)
        self.flaggedBox.setObjectName(_fromUtf8("flaggedBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.flaggedBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.radioButton = QtGui.QRadioButton(self.flaggedBox)
        self.radioButton.setChecked(True)
        self.radioButton.setObjectName(_fromUtf8("radioButton"))
        self.horizontalLayout_5.addWidget(self.radioButton)
        self.radioButton_2 = QtGui.QRadioButton(self.flaggedBox)
        self.radioButton_2.setObjectName(_fromUtf8("radioButton_2"))
        self.horizontalLayout_5.addWidget(self.radioButton_2)
        self.radioButton_3 = QtGui.QRadioButton(self.flaggedBox)
        self.radioButton_3.setObjectName(_fromUtf8("radioButton_3"))
        self.horizontalLayout_5.addWidget(self.radioButton_3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.flaggedList = QtGui.QListView(self.flaggedBox)
        self.flaggedList.setObjectName(_fromUtf8("flaggedList"))
        self.verticalLayout_2.addWidget(self.flaggedList)
        self.verticalLayout_4.addWidget(self.flaggedBox)
        self.filtersBox = QtGui.QGroupBox(self.splitter)
        self.filtersBox.setObjectName(_fromUtf8("filtersBox"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.filtersBox)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.saveFiltersButton = QtGui.QPushButton(self.filtersBox)
        self.saveFiltersButton.setObjectName(_fromUtf8("saveFiltersButton"))
        self.horizontalLayout_6.addWidget(self.saveFiltersButton)
        self.loadFiltersButton = QtGui.QPushButton(self.filtersBox)
        self.loadFiltersButton.setObjectName(_fromUtf8("loadFiltersButton"))
        self.horizontalLayout_6.addWidget(self.loadFiltersButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        self.filterTreeView = QtGui.QTreeView(self.filtersBox)
        self.filterTreeView.setObjectName(_fromUtf8("filterTreeView"))
        self.filterTreeView.header().setVisible(False)
        self.verticalLayout_3.addWidget(self.filterTreeView)
        self.verticalLayout_5.addWidget(self.splitter)

        self.retranslateUi(FilterPanel)
        QtCore.QMetaObject.connectSlotsByName(FilterPanel)

    def retranslateUi(self, FilterPanel):
        FilterPanel.setWindowTitle(_translate("FilterPanel", "Filter Panel", None))
        self.partitionBox.setTitle(_translate("FilterPanel", "Partition", None))
        self.label.setText(_translate("FilterPanel", "Bins:", None))
        self.label_2.setText(_translate("FilterPanel", "Min:", None))
        self.label_3.setText(_translate("FilterPanel", "Max:", None))
        self.flaggedBox.setTitle(_translate("FilterPanel", "Flagged Items", None))
        self.radioButton.setText(_translate("FilterPanel", "Ignore", None))
        self.radioButton_2.setText(_translate("FilterPanel", "Exclude From Selection", None))
        self.radioButton_3.setText(_translate("FilterPanel", "Keep Only Flagged Items", None))
        self.filtersBox.setTitle(_translate("FilterPanel", "Filters", None))
        self.saveFiltersButton.setText(_translate("FilterPanel", "Save", None))
        self.loadFiltersButton.setText(_translate("FilterPanel", "Load", None))

