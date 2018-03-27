#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import numpy as np
from PyQt4.QtGui import QApplication, QMainWindow,QLabel,QFileDialog, QAction, QTreeView, QHeaderView, QAbstractItemView, QWidget, QMenu


from api.datamodel import DataModel
from ui.Ui_MainWindow import Ui_MainWindow
from ui.Ui_DatasetPanel import Ui_DatasetPanel
import ui.plots, ui.filterEditDelegate

class MyDatasetPanel(QWidget):
    def __init__(self,model):
        QWidget.__init__(self)
        self.ui=Ui_DatasetPanel()
        self.ui.setupUi(self)
        self.model = model

        menu=QMenu()
        for col in sorted(set(self.model.cols) - DataModel.internalCols,key=self.model.prettyname):
            a = menu.addAction(self.model.prettyname(col))
            a.setData(col)
            a.triggered.connect(self.onAddSortField)
        self.ui.addSortField.setMenu(menu)
        self.ui.sortByListWidget.itemSelectionChanged.connect(self.onSelectionChange)
        self.onSelectionChange()
        self.ui.removeSortField.clicked.connect(self.onRemoveSortField)
        self.ui.moveSortField.clicked.connect(self.onMoveSortFieldUp)
        self.ui.limitCheckBox.clicked.connect(self.onLimitChange)
        self.ui.limitSpinBox.editingFinished.connect(self.onLimitChange)
        self.onLimitChange()

    def onAddSortField(self):
        field=self.sender().data()
        self.ui.sortByListWidget.addItem(self.model.prettyname(field))
        self.model.sortlst.append(field)

    def onSelectionChange(self):
        hasSelection=bool(len(self.ui.sortByListWidget.selectedItems()))
        self.ui.removeSortField.setEnabled(hasSelection)
        canMove=hasSelection
        for item in self.ui.sortByListWidget.selectedItems():
            canMove &= self.ui.sortByListWidget.row(item) != 0
        self.ui.moveSortField.setEnabled(canMove)

    def onRemoveSortField(self):
        rows=[]
        for item in self.ui.sortByListWidget.selectedItems():
            rows.append(self.ui.sortByListWidget.row(item))
        for r in sorted(rows,reverse=True):
            del self.model.sortlst[r]
            self.ui.sortByListWidget.takeItem(r)
        self.onSelectionChange()

    def onMoveSortFieldUp(self):
        rows=[]
        for item in self.ui.sortByListWidget.selectedItems():
            rows.append(self.ui.sortByListWidget.row(item))
        for r in sorted(rows):
            self.model.sortlst.insert(r-1,self.model.sortlst.pop(r))
            self.ui.sortByListWidget.insertItem(r-1,self.ui.sortByListWidget.takeItem(r))
            self.ui.sortByListWidget.setCurrentItem(self.ui.sortByListWidget.item(r-1))      

    def onLimitChange(self):
        if self.ui.limitCheckBox.isChecked():
            self.model.limit = self.ui.limitSpinBox.value()
        else:
            self.model.limit = None
        self.ui.limitSpinBox.setEnabled(self.ui.limitCheckBox.isChecked())

    def setLimit(self,l):
        self.ui.limitSpinBox.setValue(l)
        self.ui.limitCheckBox.setChecked(True)
        self.onLimitChange()

    def setSort(self,lst):
        for field in lst:
            self.ui.sortByListWidget.addItem(self.model.prettyname(field))
            self.model.sortlst.append(field)
        

class MyMainWindow(QMainWindow):
    def __init__(self,datfile,groupfile,filterfile):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.model=DataModel(datfile,groupfile)
        if filterfile is not None:
            self.model.loadFilters(filterfile)

        self.ui.actionSave_Dat.triggered.connect(self.onSaveDat)
        self.ui.actionSave_List.setEnabled(self.model.canSaveLst())
        self.ui.actionSave_List.triggered.connect(self.onSaveLst)
        self.ui.actionSave_Stream.setEnabled(self.model.canSaveStream())
        self.ui.actionSave_Stream.triggered.connect(self.onSaveStream)
        self.ui.actionSave_Filters.triggered.connect(self.onSaveFilters)
        

        self.filtmessage=QLabel(self)
        self.ui.statusbar.addWidget(self.filtmessage)
        self.onFilterChange()
        self.model.filterchange.connect(self.onFilterChange)

        # Histogram Menu
        self.checkedhistograms=[]
        self.cachedHistograms={}
        self.ui.menuHistogram_Bar.removeAction(self.ui.actionReset)
        self.addHistogramMenu(DataModel.defaultHistograms & set(self.model.cols), True)
        self.ui.menuHistogram_Bar.addSeparator()
        self.addHistogramMenu(set(self.model.cols) - DataModel.defaultHistograms - DataModel.internalCols, False)
        self.placeHistograms()

        # Filter Panel
        self.filterpanel=QTreeView()
        self.filterpanel.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.filterpanel.setModel(self.model.filterModel())
        self.filterpanel.setWindowTitle("Filters")
        self.filterpanel.expand(self.model.filterModel().index(0,0))
        self.filterpanel.header().setResizeMode(0,QHeaderView.ResizeToContents)
        self.filterpanel.header().setResizeMode(1,QHeaderView.ResizeToContents)
        self.filterpanel.setHeaderHidden(True)
        self.filterpanel.setItemDelegate(ui.filterEditDelegate.FilterItemDelegate())
        self.ui.actionShowFilters.triggered.connect(self.filterpanel.show)

        # Dataset Panel
        self.datasetpanel=MyDatasetPanel(self.model)
        self.ui.actionShowDatasetPanel.triggered.connect(self.datasetpanel.show)

    def closeEvent(self,evnt):
        self.filterpanel.close()
        self.datasetpanel.close()

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
                h=ui.plots.MyHistogram(parent=self.ui.scrollAreaWidgetContents,model=self.model,field=field)
                self.cachedHistograms[field]=h
            if spot < 3:
                self.ui.gridLayout.setColumnStretch(spot,1)
            if spot%3 == 0:
                self.ui.gridLayout.setRowStretch(int(spot/3),1)
            self.ui.gridLayout.addWidget(h,int(spot/3),spot%3)
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

    def onSaveDat(self):
        name=QFileDialog.getSaveFileName(self,'Save Selected As Dat File',filter='*.dat')
        if name is not None and len(name):
            self.model.saveSelDat(name)

    def onSaveLst(self):
        name=QFileDialog.getSaveFileName(self,'Save Selected As List File',filter='*.lst')
        if name is not None and len(name):
            self.model.saveSelLst(name)

    def onSaveStream(self):
        name=QFileDialog.getSaveFileName(self,'Save Selected As Stream File',filter='*.stream')
        if name is not None and len(name):
            self.model.saveSelStream(name)

    def onSaveFilters(self):
        name=QFileDialog.getSaveFileName(self,'Save Filters',filter='*.xml')
        if name is not None and len(name):
            self.model.saveFilters(name)        
        

def main():
    parser=argparse.ArgumentParser(description='Display statistics from a dat file and allow filtering and output to new files')
    parser.add_argument('--group',default=None,help='The group file output by groupgen.py (groupcfg.txt), keeps files smaller and numeric by enuemrating strings')
    parser.add_argument('--filter',default=None,help='A filter file to load. Filter files are XML format. The first Between filter in the file for a field will be updated with selection.')
    parser.add_argument('--sort',default=None,nargs='+',help='One or more fields to sort the output by. Field names must match the header of the dat file.')
    parser.add_argument('--limit',default=None,type=int,help='Limit the output to this number, if provided')
    parser.add_argument('file',help='the dat file')
    args=parser.parse_args()

    app = QApplication(sys.argv)
    w = MyMainWindow(args.file,args.group, args.filter)
    if args.sort is not None:
        w.datasetpanel.setSort(args.sort)
    if args.limit is not None:
        w.datasetpanel.setLimit(args.limit)
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
