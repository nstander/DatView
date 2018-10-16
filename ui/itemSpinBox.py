# datview/ui/itemSpinBox.py
# Spin box that jumps to next valid index.
# Author Natasha Stander

try:
    from PyQt5.QtWidgets import QSpinBox
except ImportError:
    from PyQt4.QtGui import QSpinBox
from api.itemmodel import ItemModel
import numpy as np


class ItemSpinBox(QSpinBox):
    def __init__(self,parent=None):
        QSpinBox.__init__(self,parent)
        self.imodel=None
        self.editingFinished.connect(self.onEditingFinished)

    def setIModel(self,model):
        self.imodel=model
        self.imodel.dataChanged.connect(self.onIModelChange)
        self.setMaximum(len(self.imodel.model.data)-1)

    def stepBy(self,steps):
        cur=np.searchsorted(self.imodel.sortedlist,self.imodel.currow)
        cur += steps
        if cur >= len(self.imodel.sortedlist):
            cur -= len(self.imodel.sortedlist)
        if cur < 0:
            cur += len(self.imodel.sortedlist)
        self.imodel.setRow(self.imodel.sortedlist[cur])
        
    def onIModelChange(self):
        self.setValue(self.imodel.currow)   

    def onEditingFinished(self):
        self.imodel.setRow(self.value())     
        

