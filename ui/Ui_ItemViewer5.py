# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Viewer.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ItemViewer(object):
    def setupUi(self, ItemViewer):
        ItemViewer.setObjectName("ItemViewer")
        ItemViewer.resize(716, 471)
        self.verticalLayout = QtWidgets.QVBoxLayout(ItemViewer)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.backButton = QtWidgets.QToolButton(ItemViewer)
        self.backButton.setText("")
        self.backButton.setObjectName("backButton")
        self.horizontalLayout_3.addWidget(self.backButton)
        self.playButton = QtWidgets.QToolButton(ItemViewer)
        self.playButton.setText("")
        self.playButton.setObjectName("playButton")
        self.horizontalLayout_3.addWidget(self.playButton)
        self.forwardButton = QtWidgets.QToolButton(ItemViewer)
        self.forwardButton.setText("")
        self.forwardButton.setObjectName("forwardButton")
        self.horizontalLayout_3.addWidget(self.forwardButton)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.orderGroupBox = QtWidgets.QGroupBox(ItemViewer)
        self.orderGroupBox.setTitle("")
        self.orderGroupBox.setFlat(True)
        self.orderGroupBox.setObjectName("orderGroupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.orderGroupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.originalRadioButton = QtWidgets.QRadioButton(self.orderGroupBox)
        self.originalRadioButton.setObjectName("originalRadioButton")
        self.horizontalLayout.addWidget(self.originalRadioButton)
        self.sortedRadioButton = QtWidgets.QRadioButton(self.orderGroupBox)
        self.sortedRadioButton.setChecked(True)
        self.sortedRadioButton.setObjectName("sortedRadioButton")
        self.horizontalLayout.addWidget(self.sortedRadioButton)
        self.randomRadioButton = QtWidgets.QRadioButton(self.orderGroupBox)
        self.randomRadioButton.setObjectName("randomRadioButton")
        self.horizontalLayout.addWidget(self.randomRadioButton)
        self.horizontalLayout_2.addWidget(self.orderGroupBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.label = QtWidgets.QLabel(ItemViewer)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.rowSpinBox = ItemSpinBox(ItemViewer)
        self.rowSpinBox.setMaximum(9999999)
        self.rowSpinBox.setObjectName("rowSpinBox")
        self.horizontalLayout_2.addWidget(self.rowSpinBox)
        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.splitter = QtWidgets.QSplitter(ItemViewer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.tableView = QtWidgets.QTableView(self.splitter)
        self.tableView.setShowGrid(False)
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setVisible(False)
        self.tableView.verticalHeader().setVisible(False)
        self.imageView = ImageView(self.splitter)
        self.imageView.setObjectName("imageView")
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(ItemViewer)
        QtCore.QMetaObject.connectSlotsByName(ItemViewer)

    def retranslateUi(self, ItemViewer):
        _translate = QtCore.QCoreApplication.translate
        ItemViewer.setWindowTitle(_translate("ItemViewer", "Item Viewer"))
        self.backButton.setToolTip(_translate("ItemViewer", "Previous"))
        self.playButton.setToolTip(_translate("ItemViewer", "Play"))
        self.forwardButton.setToolTip(_translate("ItemViewer", "Next"))
        self.originalRadioButton.setToolTip(_translate("ItemViewer", "As found in file"))
        self.originalRadioButton.setText(_translate("ItemViewer", "Original"))
        self.sortedRadioButton.setToolTip(_translate("ItemViewer", "Match current sort order"))
        self.sortedRadioButton.setText(_translate("ItemViewer", "Sorted"))
        self.randomRadioButton.setToolTip(_translate("ItemViewer", "Random order"))
        self.randomRadioButton.setText(_translate("ItemViewer", "Random"))
        self.label.setText(_translate("ItemViewer", "File Row:"))
        self.rowSpinBox.setToolTip(_translate("ItemViewer", "Row Number (Original)"))

from .itemSpinBox import ItemSpinBox
from pyqtgraph import ImageView
