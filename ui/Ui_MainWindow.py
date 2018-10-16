# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 516)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.plotScrollArea = QtGui.QScrollArea(self.centralwidget)
        self.plotScrollArea.setWidgetResizable(True)
        self.plotScrollArea.setObjectName(_fromUtf8("plotScrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 774, 447))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.plotScrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.plotScrollArea)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuSave_Selections_As_2 = QtGui.QMenu(self.menuFile)
        self.menuSave_Selections_As_2.setObjectName(_fromUtf8("menuSave_Selections_As_2"))
        self.menuPlot = QtGui.QMenu(self.menubar)
        self.menuPlot.setObjectName(_fromUtf8("menuPlot"))
        self.menuHistogram_Bar = QtGui.QMenu(self.menuPlot)
        self.menuHistogram_Bar.setObjectName(_fromUtf8("menuHistogram_Bar"))
        self.menuView = QtGui.QMenu(self.menubar)
        self.menuView.setObjectName(_fromUtf8("menuView"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionSave_List = QtGui.QAction(MainWindow)
        self.actionSave_List.setObjectName(_fromUtf8("actionSave_List"))
        self.actionSave_Stream = QtGui.QAction(MainWindow)
        self.actionSave_Stream.setObjectName(_fromUtf8("actionSave_Stream"))
        self.actionSave_Dat = QtGui.QAction(MainWindow)
        self.actionSave_Dat.setObjectName(_fromUtf8("actionSave_Dat"))
        self.actionSave_Plot = QtGui.QAction(MainWindow)
        self.actionSave_Plot.setObjectName(_fromUtf8("actionSave_Plot"))
        self.actionScatter = QtGui.QAction(MainWindow)
        self.actionScatter.setObjectName(_fromUtf8("actionScatter"))
        self.action2D_Histogram = QtGui.QAction(MainWindow)
        self.action2D_Histogram.setObjectName(_fromUtf8("action2D_Histogram"))
        self.actionReset = QtGui.QAction(MainWindow)
        self.actionReset.setObjectName(_fromUtf8("actionReset"))
        self.actionShowFilters = QtGui.QAction(MainWindow)
        self.actionShowFilters.setObjectName(_fromUtf8("actionShowFilters"))
        self.actionSave_Filters = QtGui.QAction(MainWindow)
        self.actionSave_Filters.setObjectName(_fromUtf8("actionSave_Filters"))
        self.actionShowDatasetPanel = QtGui.QAction(MainWindow)
        self.actionShowDatasetPanel.setObjectName(_fromUtf8("actionShowDatasetPanel"))
        self.actionSave_Numpy = QtGui.QAction(MainWindow)
        self.actionSave_Numpy.setObjectName(_fromUtf8("actionSave_Numpy"))
        self.actionItem_Viewer = QtGui.QAction(MainWindow)
        self.actionItem_Viewer.setObjectName(_fromUtf8("actionItem_Viewer"))
        self.menuSave_Selections_As_2.addAction(self.actionSave_List)
        self.menuSave_Selections_As_2.addAction(self.actionSave_Stream)
        self.menuSave_Selections_As_2.addAction(self.actionSave_Dat)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.menuSave_Selections_As_2.menuAction())
        self.menuFile.addAction(self.actionSave_Numpy)
        self.menuFile.addAction(self.actionSave_Plot)
        self.menuFile.addAction(self.actionSave_Filters)
        self.menuHistogram_Bar.addAction(self.actionReset)
        self.menuPlot.addAction(self.menuHistogram_Bar.menuAction())
        self.menuPlot.addAction(self.actionScatter)
        self.menuPlot.addAction(self.action2D_Histogram)
        self.menuView.addAction(self.actionShowFilters)
        self.menuView.addAction(self.actionShowDatasetPanel)
        self.menuView.addAction(self.actionItem_Viewer)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuPlot.menuAction())
        self.menubar.addAction(self.menuView.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Data Viewer", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuSave_Selections_As_2.setTitle(_translate("MainWindow", "Save Selections As", None))
        self.menuPlot.setTitle(_translate("MainWindow", "Plot", None))
        self.menuHistogram_Bar.setTitle(_translate("MainWindow", "Histogram / Bar", None))
        self.menuView.setTitle(_translate("MainWindow", "View", None))
        self.actionOpen.setText(_translate("MainWindow", "Open", None))
        self.actionSave_List.setText(_translate("MainWindow", "CrystFEL List", None))
        self.actionSave_Stream.setText(_translate("MainWindow", "Stream File", None))
        self.actionSave_Dat.setText(_translate("MainWindow", "Dat File", None))
        self.actionSave_Plot.setText(_translate("MainWindow", "Save Plot", None))
        self.actionScatter.setText(_translate("MainWindow", "Scatter", None))
        self.action2D_Histogram.setText(_translate("MainWindow", "2D Histogram", None))
        self.actionReset.setText(_translate("MainWindow", "Reset", None))
        self.actionShowFilters.setText(_translate("MainWindow", "Filters", None))
        self.actionSave_Filters.setText(_translate("MainWindow", "Save Filters", None))
        self.actionShowDatasetPanel.setText(_translate("MainWindow", "Dataset Panel", None))
        self.actionSave_Numpy.setText(_translate("MainWindow", "Save Numpy", None))
        self.actionSave_Numpy.setToolTip(_translate("MainWindow", "Save all data into compressed npz file", None))
        self.actionItem_Viewer.setText(_translate("MainWindow", "Item Viewer", None))

