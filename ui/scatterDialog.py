#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt4.QtGui import QDialog
from PyQt4.QtCore import Qt
from api.datamodel import DataModel
from ui.Ui_ScatterDialog import Ui_ScatterDialog
from ui.plots import MyScatter

class MyScatterDialog(QDialog):
    def __init__(self,model,parent):
        QDialog.__init__(self,parent)
        self.ui=Ui_ScatterDialog()
        self.ui.setupUi(self)
        self.model = model

        self.ui.xCombo.addItem("Current Order",None)
        self.ui.zCombo.addItem("None",None)
        self.ui.cCombo.addItem("None",None)
        for col in sorted(set(self.model.cols) - DataModel.internalCols,key=self.model.prettyname):
            self.ui.xCombo.addItem(self.model.prettyname(col),col)
            self.ui.yCombo.addItem(self.model.prettyname(col),col)
            self.ui.zCombo.addItem(self.model.prettyname(col),col)
            self.ui.cCombo.addItem(self.model.prettyname(col),col)
        self.accepted.connect(self.onAccept)

    def onAccept(self):
        print(self.ui.xCombo.itemData(self.ui.xCombo.currentIndex()),self.ui.yCombo.itemData(self.ui.yCombo.currentIndex()),self.ui.zCombo.itemData(self.ui.zCombo.currentIndex()),self.ui.cCombo.itemData(self.ui.cCombo.currentIndex()))
        p=MyScatter(self.model,self.ui.xCombo.itemData(self.ui.xCombo.currentIndex()),self.ui.yCombo.itemData(self.ui.yCombo.currentIndex()),self.ui.cCombo.itemData(self.ui.cCombo.currentIndex()),parent=self.parent(),flags=Qt.Window)
        p.show()

        
