# datview/api/itemmodel.py
# QAbstractTableModel for interfacing the a single item of datamodel.py in ui.itemViewer.py
# Author Natasha Stander

try:
    from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
except ImportError:
    from PyQt4.QtCore import QAbstractTableModel, QModelIndex, Qt

from api.datamodel import DataModel
import numpy as np

class ItemModel(QAbstractTableModel):
    def __init__(self,model,orderMode):
        QAbstractTableModel.__init__(self)
        self.model=model
        self.currow=0
        self.internalrow=0
        self.initiallist=np.arange(len(self.model.data))
        self.validlist=None
        self.sortedlist=None
        self.orderMode=orderMode # Original=0, Sorted=1, Random=2
        self.onListChange()
        self.model.filterchange.connect(self.onListChange)
        self.model.sortchange.connect(self.onListChange)

    def rowCount(self,parent):
        if parent.isValid():
            return 0
        return len(self.model.cols)

    def columnCount(self,parent):
        return 1

    def data(self,index,role):
        if index.isValid() and index.column() == 0:
            field=self.model.cols[index.row()]
            if role == Qt.DisplayRole:
                return "<b>%s:</b> %s" %(self.model.prettyname(field),self.model.value(field,self.currow,False))
            elif role == Qt.ToolTipRole:
                return self.model.value(field,self.currow,False)
        return None

    def flags(self,index):
        r=Qt.NoItemFlags
        if index.isValid():
            r=Qt.ItemIsSelectable | Qt.ItemIsEnabled
        return r

    def next(self):
        self.internalrow +=1
        if self.internalrow >= len(self.validlist):
            self.internalrow -= len(self.validlist)
        self.currow=self.validlist[self.internalrow]
        self.dataChanged.emit(self.createIndex(0,0,QModelIndex()),self.createIndex(len(self.model.cols),0,QModelIndex()))

    def previous(self):
        self.internalrow -=1
        if self.internalrow < 0:
            self.internalrow += len(self.validlist)
        self.currow=self.validlist[self.internalrow]
        self.dataChanged.emit(self.createIndex(0,0,QModelIndex()),self.createIndex(len(self.model.cols),0,QModelIndex()))

    def setRow(self,row):
        if row == self.currow:
            return
        self.currow=row
        self.updateInternalRow()


    def updateInternalRow(self):
        closest=np.searchsorted(self.sortedlist,self.currow)
        if closest >= len(self.sortedlist):
            closest = len(self.sortedlist)-1
        val=self.sortedlist[closest]
        self.internalrow = np.where(self.validlist == val)[0][0]
        self.dataChanged.emit(self.createIndex(0,0,QModelIndex()),self.createIndex(len(self.model.cols),0,QModelIndex()))

    def onListChange(self):
        self.sortedlist=self.initiallist[self.model.rootfilter.keep]
        if self.orderMode == 1: # Sorted
            self.validlist=self.sortedlist[self.model.outArrIndices(False)]
        elif self.orderMode == 2 : # Random
            self.validlist=self.sortedlist
            np.random.shuffle(self.validlist)
        else: # Order mode == 0, Original
            self.validlist=self.sortedlist

    def setOrderMode(self,mode):
        self.orderMode = mode
        self.onListChange()
        


