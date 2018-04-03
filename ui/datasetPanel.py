#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt4.QtGui import QWidget, QMenu
from api.datamodel import DataModel
from ui.Ui_DatasetPanel import Ui_DatasetPanel

class MyDatasetPanel(QWidget):
    def __init__(self,model,parent=None):
        QWidget.__init__(self,parent)
        self.ui=Ui_DatasetPanel()
        self.ui.setupUi(self)
        self.model = model

        menu=QMenu()
        for col in sorted(set(self.model.cols) - self.model.cfg.internalCols,key=self.model.prettyname):
            a = menu.addAction(self.model.prettyname(col))
            a.setData(col)
            a.triggered.connect(self.onAddSortField)
        self.ui.addSortField.setMenu(menu)
        self.ui.sortByListWidget.itemSelectionChanged.connect(self.onSelectionChange)
        self.onSelectionChange()
        self.ui.removeSortField.clicked.connect(self.onRemoveSortField)
        self.ui.moveSortField.clicked.connect(self.onMoveSortFieldUp)
        self.ui.limitCheckBox.clicked.connect(self.onLimitChange)
        self.ui.limTopButton.clicked.connect(self.onLimitChange)
        self.ui.limRandomButton.clicked.connect(self.onLimitChange)
        self.ui.limitSpinBox.editingFinished.connect(self.onLimitChange)
        self.ui.sortAscendingCheckBox.clicked.connect(self.onSortAscendingChange)
        self.ui.colorByCombo.hide()
        self.ui.label.hide()
        self.ui.legendListWidget.hide()
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
        self.model.limitModeRandom=self.ui.limRandomButton.isChecked()

    def setLimit(self,l):
        self.ui.limitSpinBox.setValue(l)
        self.ui.limitCheckBox.setChecked(True)
        self.onLimitChange()

    def setSort(self,lst):
        for field in lst:
            self.ui.sortByListWidget.addItem(self.model.prettyname(field))
            self.model.sortlst.append(field)

    def onSortAscendingChange(self):
        self.model.reverseSort = not self.ui.sortAscendingCheckBox.isChecked()

