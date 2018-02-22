#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import numpy as np
from PyQt4.QtGui import QApplication, QMainWindow,QLabel,QFileDialog, QAction


from api.datamodel import DataModel
from ui.Ui_MainWindow import Ui_MainWindow
import ui.plots



class MyMainWindow(QMainWindow):
    def __init__(self,datfile,groupfile):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.model=DataModel(datfile,groupfile)

        self.ui.actionSave_Dat.triggered.connect(self.onSaveDat)
        self.ui.actionSave_List.setEnabled(self.model.canSaveLst())
        self.ui.actionSave_List.triggered.connect(self.onSaveLst)
        self.ui.actionSave_Stream.setEnabled(self.model.canSaveStream())
        self.ui.actionSave_Stream.triggered.connect(self.onSaveStream)
        

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
        if name is not None:
            self.model.saveSelDat(name)

    def onSaveLst(self):
        name=QFileDialog.getSaveFileName(self,'Save Selected As List File',filter='*.lst')
        if name is not None:
            self.model.saveSelLst(name)

    def onSaveStream(self):
        name=QFileDialog.getSaveFileName(self,'Save Selected As Stream File',filter='*.stream')
        if name is not None:
            self.model.saveSelStream(name)
        

def main():
    parser=argparse.ArgumentParser(description='Display statistics from a dat file and allow filtering and output to new files')
    parser.add_argument('--group',default=None,help='The group file output by groupgen.py (groupcfg.txt), keeps files smaller and numeric by enuemrating strings')
    parser.add_argument('file',help='the dat file')
    args=parser.parse_args()

    app = QApplication(sys.argv)
    w = MyMainWindow(args.file,args.group)
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
