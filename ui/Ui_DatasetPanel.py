# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DatasetPanel.ui'
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

class Ui_DatasetPanel(object):
    def setupUi(self, DatasetPanel):
        DatasetPanel.setObjectName(_fromUtf8("DatasetPanel"))
        DatasetPanel.resize(259, 442)
        self.verticalLayout_2 = QtGui.QVBoxLayout(DatasetPanel)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(DatasetPanel)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.colorByCombo = QtGui.QComboBox(DatasetPanel)
        self.colorByCombo.setObjectName(_fromUtf8("colorByCombo"))
        self.horizontalLayout.addWidget(self.colorByCombo)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.legendListWidget = QtGui.QListWidget(DatasetPanel)
        self.legendListWidget.setObjectName(_fromUtf8("legendListWidget"))
        self.verticalLayout_2.addWidget(self.legendListWidget)
        self.groupBox = QtGui.QGroupBox(DatasetPanel)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.addSortField = QtGui.QToolButton(self.groupBox)
        self.addSortField.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.addSortField.setObjectName(_fromUtf8("addSortField"))
        self.horizontalLayout_2.addWidget(self.addSortField)
        self.removeSortField = QtGui.QToolButton(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.removeSortField.sizePolicy().hasHeightForWidth())
        self.removeSortField.setSizePolicy(sizePolicy)
        self.removeSortField.setObjectName(_fromUtf8("removeSortField"))
        self.horizontalLayout_2.addWidget(self.removeSortField)
        self.moveSortField = QtGui.QToolButton(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.moveSortField.sizePolicy().hasHeightForWidth())
        self.moveSortField.setSizePolicy(sizePolicy)
        self.moveSortField.setObjectName(_fromUtf8("moveSortField"))
        self.horizontalLayout_2.addWidget(self.moveSortField)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.sortByListWidget = QtGui.QListWidget(self.groupBox)
        self.sortByListWidget.setObjectName(_fromUtf8("sortByListWidget"))
        self.verticalLayout.addWidget(self.sortByListWidget)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.limitCheckBox = QtGui.QCheckBox(self.groupBox)
        self.limitCheckBox.setObjectName(_fromUtf8("limitCheckBox"))
        self.horizontalLayout_3.addWidget(self.limitCheckBox)
        self.limitSpinBox = QtGui.QSpinBox(self.groupBox)
        self.limitSpinBox.setProperty("showGroupSeparator", True)
        self.limitSpinBox.setMaximum(999999)
        self.limitSpinBox.setSingleStep(100)
        self.limitSpinBox.setProperty("value", 20000)
        self.limitSpinBox.setObjectName(_fromUtf8("limitSpinBox"))
        self.horizontalLayout_3.addWidget(self.limitSpinBox)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.verticalLayout_2.addWidget(self.groupBox)

        self.retranslateUi(DatasetPanel)
        QtCore.QMetaObject.connectSlotsByName(DatasetPanel)

    def retranslateUi(self, DatasetPanel):
        DatasetPanel.setWindowTitle(_translate("DatasetPanel", "Dataset Panel", None))
        self.label.setText(_translate("DatasetPanel", "Histogram Color by:", None))
        self.groupBox.setTitle(_translate("DatasetPanel", "Output", None))
        self.label_2.setText(_translate("DatasetPanel", "Sort Output", None))
        self.addSortField.setToolTip(_translate("DatasetPanel", "Add Field", None))
        self.addSortField.setText(_translate("DatasetPanel", "+", None))
        self.removeSortField.setToolTip(_translate("DatasetPanel", "Remove selected field", None))
        self.removeSortField.setText(_translate("DatasetPanel", "-", None))
        self.moveSortField.setToolTip(_translate("DatasetPanel", "Move selected field up", None))
        self.moveSortField.setText(_translate("DatasetPanel", "^", None))
        self.limitCheckBox.setText(_translate("DatasetPanel", "Limit Output", None))

