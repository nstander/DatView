#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import numpy as np
from PyQt4.QtGui import QApplication, QMainWindow,QLabel,QFileDialog


from api.datamodel import DataModel
from ui.Ui_MainWindow import Ui_MainWindow
import ui.plots



class MyMainWindow(QMainWindow):
    def __init__(self,datfile):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.model=DataModel(datfile)

        self.ui.actionSave_Dat.triggered.connect(self.onSaveDat)
        self.ui.actionSave_List.setEnabled(self.model.canSaveLst())
        self.ui.actionSave_List.triggered.connect(self.onSaveLst)
        self.ui.actionSave_Stream.setEnabled(self.model.canSaveStream())
        self.ui.actionSave_Stream.triggered.connect(self.onSaveStream)
        

        self.filtmessage=QLabel(self)
        self.ui.statusbar.addWidget(self.filtmessage)
        self.onFilterChange()
        self.model.filterchange.connect(self.onFilterChange)

        self.ui.gridLayout.addWidget(ui.plots.MyHistogram(parent=self.ui.scrollAreaWidgetContents,model=self.model,field='a'),0,0)
        self.ui.gridLayout.addWidget(ui.plots.MyHistogram(parent=self.ui.scrollAreaWidgetContents,model=self.model,field='b'),0,1)
        self.ui.gridLayout.addWidget(ui.plots.MyHistogram(parent=self.ui.scrollAreaWidgetContents,model=self.model,field='c'),0,2)
        self.ui.gridLayout.addWidget(ui.plots.MyHistogram(parent=self.ui.scrollAreaWidgetContents,model=self.model,field='alpha'),1,0)
        self.ui.gridLayout.addWidget(ui.plots.MyHistogram(parent=self.ui.scrollAreaWidgetContents,model=self.model,field='beta'),1,1)
        self.ui.gridLayout.addWidget(ui.plots.MyHistogram(parent=self.ui.scrollAreaWidgetContents,model=self.model,field='gamma'),1,2)

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
    parser.add_argument('file',help='the dat file')
    args=parser.parse_args()

    app = QApplication(sys.argv)
    w = MyMainWindow(args.file)
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
