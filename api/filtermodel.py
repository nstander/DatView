from PyQt4.QtCore import QAbstractItemModel, QModelIndex, Qt
from .filters import *

class FilterModel(QAbstractItemModel):
    def __init__(self,root,dmodel):
        QAbstractItemModel.__init__(self)
        self.root=root
        root.modelchange.connect(self.onFilterChange)
        root.beforeAddChild.connect(self.onChildAdd)
        root.afterAddChild.connect(self.endInsertRows)
        self.dmodel=dmodel

    def index(self,row,col,par=QModelIndex()):
        r=QModelIndex()
        if col < 3: # Only label and values columns
            if par.isValid() and row < par.internalPointer().childcnt():
                r= self.createIndex(row,col,par.internalPointer().children[row])
            elif not par.isValid() and row == 0:
                r= self.createIndex(row,col,self.root)
        return r

    def parent(self,index):
        if index.isValid() and index.internalPointer() != self.root:
            return self.createIndex(index.internalPointer().parent().row,0,index.internalPointer().parent())
        return QModelIndex()

    def rowCount(self,parent):
        if parent.isValid():
            return parent.internalPointer().childcnt()
        return 1 # top item

    def columnCount(self,parent):
        return 3 # filtername min max

    def data(self,index,role):
        if role == Qt.DisplayRole and index.isValid():
            if index.column() == 0:
                if isinstance(index.internalPointer(),FieldFilter):
                    return "%s [%.3f,%.3f] %s"%(\
                        self.dmodel.prettyname(index.internalPointer().field),\
                        self.dmodel.fieldmin(index.internalPointer().field),\
                        self.dmodel.fieldmax(index.internalPointer().field),\
                        index.internalPointer().kind())
                return index.internalPointer().kind()
            elif index.column() == 1 and index.internalPointer().hasMin():
                return "[%.3f"%index.internalPointer().minimum
            elif index.column() == 2 and index.internalPointer().hasMax():
                return "%.3f)"%index.internalPointer().maximum
            elif index.column() == 2 and isinstance(index.internalPointer(),InSetFilter):
                return index.internalPointer().valuesString()
            elif index.column() == 2 and isinstance(index.internalPointer(),GroupFilter):
                return "+"
        elif role == Qt.CheckStateRole and index.isValid() and index.column()==0:
            return index.internalPointer().active
        return None

    def flags(self,index):
        r=Qt.NoItemFlags
        if index.isValid():
            r=Qt.ItemIsSelectable | Qt.ItemIsEnabled
            if index.column() == 0:
                r|= Qt.ItemIsUserCheckable 
            elif (index.column() == 1 and index.internalPointer().hasMin()) or \
                 (index.column() == 2 and index.internalPointer().hasMax()) or \
                 (index.column() == 2 and isinstance(index.internalPointer(),InSetFilter)) or \
                 (index.column() == 2 and isinstance(index.internalPointer(),GroupFilter)):
                r|= Qt.ItemIsEditable
        return r

    def onFilterChange(self,f):
        self.dataChanged.emit(self.createIndex(f.row,0,f),self.createIndex(f.row,1,f))

    def onChildAdd(self,parent,child):
        child.modelchange.connect(self.onFilterChange)
        if isinstance(child,GroupFilter):
            child.beforeAddChild.connect(self.onChildAdd)
            child.afterAddChild.connect(self.endInsertRows)
        self.beginInsertRows(self.createIndex(parent.row,0,parent),parent.childcnt(),parent.childcnt())

    def setData(self,index,value,role):
        if role == Qt.CheckStateRole and index.isValid() and index.column()==0:
            index.internalPointer().setActive(not index.internalPointer().active)
            return True
        return False
        
        
        

# index, parent, rowcount, columncount, data
