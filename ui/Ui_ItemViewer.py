# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Viewer.ui'
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

class Ui_ItemViewer(object):
    def setupUi(self, ItemViewer):
        ItemViewer.setObjectName(_fromUtf8("ItemViewer"))
        ItemViewer.resize(716, 471)
        self.verticalLayout = QtGui.QVBoxLayout(ItemViewer)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.backButton = QtGui.QToolButton(ItemViewer)
        self.backButton.setText(_fromUtf8(""))
        self.backButton.setObjectName(_fromUtf8("backButton"))
        self.horizontalLayout_3.addWidget(self.backButton)
        self.playButton = QtGui.QToolButton(ItemViewer)
        self.playButton.setText(_fromUtf8(""))
        self.playButton.setObjectName(_fromUtf8("playButton"))
        self.horizontalLayout_3.addWidget(self.playButton)
        self.forwardButton = QtGui.QToolButton(ItemViewer)
        self.forwardButton.setText(_fromUtf8(""))
        self.forwardButton.setObjectName(_fromUtf8("forwardButton"))
        self.horizontalLayout_3.addWidget(self.forwardButton)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.orderGroupBox = QtGui.QGroupBox(ItemViewer)
        self.orderGroupBox.setTitle(_fromUtf8(""))
        self.orderGroupBox.setFlat(True)
        self.orderGroupBox.setObjectName(_fromUtf8("orderGroupBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.orderGroupBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.originalRadioButton = QtGui.QRadioButton(self.orderGroupBox)
        self.originalRadioButton.setObjectName(_fromUtf8("originalRadioButton"))
        self.horizontalLayout.addWidget(self.originalRadioButton)
        self.sortedRadioButton = QtGui.QRadioButton(self.orderGroupBox)
        self.sortedRadioButton.setChecked(True)
        self.sortedRadioButton.setObjectName(_fromUtf8("sortedRadioButton"))
        self.horizontalLayout.addWidget(self.sortedRadioButton)
        self.randomRadioButton = QtGui.QRadioButton(self.orderGroupBox)
        self.randomRadioButton.setObjectName(_fromUtf8("randomRadioButton"))
        self.horizontalLayout.addWidget(self.randomRadioButton)
        self.horizontalLayout_2.addWidget(self.orderGroupBox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.label = QtGui.QLabel(ItemViewer)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.rowSpinBox = ItemSpinBox(ItemViewer)
        self.rowSpinBox.setMaximum(9999999)
        self.rowSpinBox.setObjectName(_fromUtf8("rowSpinBox"))
        self.horizontalLayout_2.addWidget(self.rowSpinBox)
        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.splitter = QtGui.QSplitter(ItemViewer)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tableView = QtGui.QTableView(self.splitter)
        self.tableView.setShowGrid(False)
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.tableView.horizontalHeader().setVisible(False)
        self.tableView.verticalHeader().setVisible(False)
        self.imageView = ImageView(self.splitter)
        self.imageView.setObjectName(_fromUtf8("imageView"))
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(ItemViewer)
        QtCore.QMetaObject.connectSlotsByName(ItemViewer)

    def retranslateUi(self, ItemViewer):
        ItemViewer.setWindowTitle(_translate("ItemViewer", "Item Viewer", None))
        self.backButton.setToolTip(_translate("ItemViewer", "Previous", None))
        self.playButton.setToolTip(_translate("ItemViewer", "Play", None))
        self.forwardButton.setToolTip(_translate("ItemViewer", "Next", None))
        self.originalRadioButton.setToolTip(_translate("ItemViewer", "As found in file", None))
        self.originalRadioButton.setText(_translate("ItemViewer", "Original", None))
        self.sortedRadioButton.setToolTip(_translate("ItemViewer", "Match current sort order", None))
        self.sortedRadioButton.setText(_translate("ItemViewer", "Sorted", None))
        self.randomRadioButton.setToolTip(_translate("ItemViewer", "Random order", None))
        self.randomRadioButton.setText(_translate("ItemViewer", "Random", None))
        self.label.setText(_translate("ItemViewer", "File Row:", None))
        self.rowSpinBox.setToolTip(_translate("ItemViewer", "Row Number (Original)", None))

from .itemSpinBox import ItemSpinBox
from pyqtgraph import ImageView
