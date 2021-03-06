#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# datview/datview.py
# Main program and window of GUI.
# Author Natasha Stander

import sys
import argparse
import numpy as np
try:
    from PyQt5.QtWidgets import QApplication, QMainWindow,QLabel,QFileDialog, QAction, QWidget, QMenu, QMessageBox
    from PyQt5.QtCore import Qt, QEvent
    from ui.Ui_MainWindow5 import Ui_MainWindow
    qt5=True
except ImportError:
    from PyQt4.QtGui import QApplication, QMainWindow,QLabel,QFileDialog, QAction, QWidget, QMenu, QMessageBox
    from PyQt4.QtCore import Qt, QEvent
    from ui.Ui_MainWindow import Ui_MainWindow
    qt5=False

from api.datamodel import DataModel
from api.modelcfg import ModelConfig
from ui.controlPanel import MyControlPanel
from ui.plotDialogs import *
from ui.itemViewer import MyItemViewer
from ui.plots import MyFigure

class MyMainWindow(QMainWindow):
    def __init__(self,datfile,groupfile,filterfile,cfg,geom,mask):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Datview: %s"%datfile)

        config=ModelConfig(cfg)
        self.model=DataModel(datfile,groupfile,cfg=config)
        self.histcolumns=config.histperrow
        if filterfile is not None:
            self.model.loadFilters(filterfile)

        self.ui.actionSave_Dat.triggered.connect(self.onSaveDat)
        self.ui.actionSave_List.setEnabled(self.model.canSaveLst())
        self.ui.actionSave_List.triggered.connect(self.onSaveLst)
        self.ui.actionSave_Stream.setEnabled(self.model.canSaveStream())
        self.ui.actionSave_Stream.triggered.connect(self.onSaveStream)
        self.ui.actionSave_Numpy.setEnabled(self.model.canSaveNumpy())
        self.ui.actionSave_Numpy.triggered.connect(self.onSaveNumpy)
        self.ui.actionScatter.triggered.connect(self.onShowScatter)
        self.ui.action2D_Histogram.triggered.connect(self.onShowHist2d)
        self.ui.actionPixel.triggered.connect(self.onShowPixelPlot)
        self.ui.actionAggregated_Plot.triggered.connect(self.onShowAggPlot)
        self.ui.actionOpen.setVisible(False)
        self.ui.actionSave_Plot.setVisible(False)
        self.ui.actionComparison_Scatter.setVisible(self.model.hasComparisons())
        self.ui.actionComparison_Scatter.triggered.connect(self.onShowCmpScatter)
        self.ui.actionComparison_2D_Histogram.setVisible(self.model.hasComparisons())
        self.ui.actionComparison_2D_Histogram.triggered.connect(self.onShowCmpHist2d)
        

        self.filtmessage=QLabel(self)
        self.ui.statusbar.addWidget(self.filtmessage)
        self.onFilterChange()
        self.model.filterchange.connect(self.onFilterChange)

        # Histogram Menu
        self.checkedhistograms=[]
        self.cachedHistograms={}
        self.ui.menuHistogram_Bar.removeAction(self.ui.actionReset)
        self.addHistogramMenu(self.model.cfg.defaultHistograms & set(self.model.cols), True)
        self.ui.menuHistogram_Bar.addSeparator()
        self.addHistogramMenu(set(self.model.cols) - self.model.cfg.defaultHistograms - self.model.cfg.internalCols, False)
        self.placeHistograms()

        # Filter Panel
        self.controlPanel=MyControlPanel(self.model,parent=self)
        self.controlPanel.setWindowFlags(Qt.Window)
        self.ui.actionViewControls.triggered.connect(self.controlPanel.show)
        self.ui.actionSave_Filters.triggered.connect(self.controlPanel.onSaveFilters)

        # Item Viewer
        itemviewer=MyItemViewer(self.model,geom,mask,parent=self)
        itemviewer.setWindowFlags(Qt.Window)
        self.ui.actionItem_Viewer.triggered.connect(itemviewer.show)
        self.controlPanel.flagselected.connect(itemviewer.model.setRow)

        if qt5:
            self.ui.plotScrollArea.viewport().installEventFilter(self)

    def eventFilter(self, source, event):
        if (event.type() == QEvent.Wheel and source is self.ui.plotScrollArea.viewport()):
            return True
        return super(QMainWindow, self).eventFilter(source, event)

    def addHistogramMenu(self, lst, checked=False):
        for col in sorted(lst,key=self.model.prettyname):
            act=QAction(self.model.prettyname(col),self)
            act.setCheckable(True)
            act.setChecked(checked)
            self.ui.menuHistogram_Bar.addAction(act)
            act.triggered.connect(lambda checked, field=col: self.onHistAction(field,checked))
            if checked:
                self.checkedhistograms.append(col)                

    def placeHistograms(self):
        spot=0
        for field in self.checkedhistograms:
            if field in self.cachedHistograms:
                h=self.cachedHistograms[field]
            else:
                h=MyFigure(parent=self.ui.scrollAreaWidgetContents)
                h.histogram(model=self.model,field=field)
                self.cachedHistograms[field]=h
            if spot < self.histcolumns:
                self.ui.gridLayout.setColumnStretch(spot,1)
            if spot%self.histcolumns == 0:
                self.ui.gridLayout.setRowStretch(int(spot/self.histcolumns),1)
            self.ui.gridLayout.addWidget(h,int(spot/self.histcolumns),spot%self.histcolumns)
            h.setVisible(True)
            spot += 1

    def onHistAction(self,field,checked):
        if checked:
            self.checkedhistograms.append(field)
        else:
            self.checkedhistograms.remove(field)
            self.cachedHistograms[field].setVisible(False)
        self.placeHistograms()

    def onFilterChange(self):
        self.filtmessage.setText('%d of %d Selected' %(len(self.model.filtered), len(self.model.data)))

    def getSaveName(self,title,filter):
        name=QFileDialog.getSaveFileName(self,title,filter=filter)
        if qt5:
            if name:
                return name[0]
        elif name is not None and len(name):
            return name
        return None

    def onSaveDat(self):
        name=self.getSaveName('Save Selected As Dat File','*.dat')
        if name:
            self.model.saveByPartitions(name, self.model.saveSelDat, self.controlPanel.partWidget.current())

    def onSaveLst(self):
        name=self.getSaveName('Save Selected As List File','*.lst')
        if name:
            self.model.saveByPartitions(name, self.model.saveSelLst, self.controlPanel.partWidget.current())

    def onSaveStream(self):
        name=self.getSaveName('Save Selected As Stream File','*.stream')
        if name:
            try:
                self.model.saveByPartitions(name, self.model.saveSelStream, self.controlPanel.partWidget.current())
            except FileNotFoundError as err:
                QMessageBox.warning(self,"Unable to Save",str(err))

    def onSaveNumpy(self):
        name=self.getSaveName('Save ALL as compressed numpy file','*.npz')
        if name:
            self.model.saveAllNumpy(name)     

    def onShowScatter(self):
        d=MyScatterDialog(self.model,self)
        d.exec()

    def onShowCmpScatter(self):
        d=MyCompareScatterDialog(self.model,self)
        d.exec()

    def onShowHist2d(self):
        d=MyHist2dDialog(self.model,self)
        d.exec()

    def onShowCmpHist2d(self):
        d=MyCompare2DHistDialog(self.model,self)
        d.exec()

    def onShowPixelPlot(self):
        d=MyPixelPlotDialog(self.model,self)
        d.exec()

    def onShowAggPlot(self):
        d=MyAggPlotDialog(self.model,self)
        d.exec()
        

def main():
    parser=argparse.ArgumentParser(description='Display statistics from a dat file and allow filtering and output to new files')
    parser.add_argument('--group',default=None,help='The group file output by groupgen.py (groupcfg.txt), keeps files smaller and numeric by enuemrating strings')
    parser.add_argument('-g','--geom',default=None,help='A CrystFEL style geometry file (.geom) for displaying images in ItemViewer')
    parser.add_argument('--mask',default=None,help='An H5 mask or gain calibration file. The image is multiplied by this mask before display in the ItemViewer so 1 is keep and 0 is set to 0. Path within the file to the mask data is configured with maskh5path in modelcfg.xml')
    parser.add_argument('--filter',default=None,help='A filter file to load. Filter files are XML format. The first Between filter in the file for a field will be updated with selection.')
    parser.add_argument('--sort',default=None,nargs='+',help='One or more fields to sort the output by. Field names must match the header of the dat file.')
    parser.add_argument('--limit',default=None,type=int,help='Limit the output to this number, if provided')
    parser.add_argument('--cfg',default=None,help='Use the provided configuration file (xml) instead of the default one. Default one is found in api/modelcfg.xml')
    parser.add_argument('file',help='the dat file (or a .npz file output from datview/datexport)')
    args=parser.parse_args()

    app = QApplication(sys.argv)
    w = MyMainWindow(args.file,args.group, args.filter,args.cfg,args.geom,args.mask)
    if args.sort is not None:
        w.controlPanel.setSort(args.sort)
    if args.limit is not None:
        w.controlPanel.setLimit(args.limit)
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
