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
        DatasetPanel.resize(258, 445)
        self.verticalLayout_3 = QtGui.QVBoxLayout(DatasetPanel)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(DatasetPanel)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.colorByCombo = QtGui.QComboBox(DatasetPanel)
        self.colorByCombo.setObjectName(_fromUtf8("colorByCombo"))
        self.horizontalLayout.addWidget(self.colorByCombo)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.legendListWidget = QtGui.QListWidget(DatasetPanel)
        self.legendListWidget.setObjectName(_fromUtf8("legendListWidget"))
        self.verticalLayout_3.addWidget(self.legendListWidget)
        self.groupBox = QtGui.QGroupBox(DatasetPanel)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
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
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.sortByListWidget = QtGui.QListWidget(self.groupBox)
        self.sortByListWidget.setObjectName(_fromUtf8("sortByListWidget"))
        self.verticalLayout_2.addWidget(self.sortByListWidget)
        self.sortAscendingCheckBox = QtGui.QCheckBox(self.groupBox)
        self.sortAscendingCheckBox.setChecked(True)
        self.sortAscendingCheckBox.setObjectName(_fromUtf8("sortAscendingCheckBox"))
        self.verticalLayout_2.addWidget(self.sortAscendingCheckBox)
        self.limitCheckBox = QtGui.QGroupBox(self.groupBox)
        self.limitCheckBox.setCheckable(True)
        self.limitCheckBox.setChecked(False)
        self.limitCheckBox.setObjectName(_fromUtf8("limitCheckBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.limitCheckBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.limitSpinBox = QtGui.QSpinBox(self.limitCheckBox)
        self.limitSpinBox.setProperty("showGroupSeparator", True)
        self.limitSpinBox.setMaximum(999999)
        self.limitSpinBox.setSingleStep(100)
        self.limitSpinBox.setProperty("value", 20000)
        self.limitSpinBox.setObjectName(_fromUtf8("limitSpinBox"))
        self.verticalLayout.addWidget(self.limitSpinBox)
        self.limRandomButton = QtGui.QRadioButton(self.limitCheckBox)
        self.limRandomButton.setChecked(True)
        self.limRandomButton.setObjectName(_fromUtf8("limRandomButton"))
        self.verticalLayout.addWidget(self.limRandomButton)
        self.limTopButton = QtGui.QRadioButton(self.limitCheckBox)
        self.limTopButton.setObjectName(_fromUtf8("limTopButton"))
        self.verticalLayout.addWidget(self.limTopButton)
        self.verticalLayout_2.addWidget(self.limitCheckBox)
        self.verticalLayout_3.addWidget(self.groupBox)

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
        self.sortAscendingCheckBox.setText(_translate("DatasetPanel", "Ascending", None))
        self.limitCheckBox.setTitle(_translate("DatasetPanel", "Limit Output", None))
        self.limRandomButton.setText(_translate("DatasetPanel", "Random Subset", None))
        self.limTopButton.setText(_translate("DatasetPanel", "Top", None))

