# datview/ui/partitionWidget.py 
# All controls
# Author Natasha Stander

try:
    from PyQt5.QtWidgets import QWidget, QColorDialog
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QColor, QStandardItemModel, QStandardItem
    from ui.Ui_PartitionWidget5 import Ui_PartitionWidget
    qt5=True
except ImportError:
    from PyQt4.QtGui import QWidget, QColor, QStandardItemModel, QStandardItem, QColorDialog
    from PyQt4.QtCore import Qt
    from ui.Ui_PartitionWidget import Ui_PartitionWidget
    qt5=False

from api.datamodel import DataModel
import numpy as np

class MyPartitionWidget(QWidget):
    unassignedStr="NaN / Outside Range"
    def __init__(self,model,setFunc,comboInit=None,checkable=True,colors=False,parent=None):
        QWidget.__init__(self,parent)
        self.ui=Ui_PartitionWidget()
        self.ui.setupUi(self)
        self.model = model
        self.checkable = checkable
        self.colors = colors
        self.setFunction = setFunc

        initial=None
        search=model.datafield(comboInit)
        i=0
        for col in sorted(set(self.model.cols) - self.model.cfg.internalCols,key=self.model.prettyname):
            if (self.model.fieldmax(col) - self.model.trueFieldMin(col)) > 0:
                self.ui.comboBox.addItem(self.model.prettyname(col),col)
                if col == search:
                    initial=i
                i += 1


        self.parts=None
        self.ui.groupBox.setChecked(initial is not None)
        self.listModel=QStandardItemModel()
        self.ui.listView.setModel(self.listModel)
        if self.colors:
            self.ui.listView.doubleClicked.connect(self.selectColor)

        if initial is not None:
            self.ui.comboBox.setCurrentIndex(initial)
        self.ui.comboBox.currentIndexChanged.connect(self.onComboChange)
        self.onComboChange()

        self.ui.groupBox.toggled.connect(self.rebuild)
        self.ui.binSpinBox.editingFinished.connect(self.rebuild)
        self.ui.maxSpinBox.editingFinished.connect(self.rebuild)
        self.ui.minSpinBox.editingFinished.connect(self.rebuild)
        self.listModel.dataChanged.connect(self.update)

    def onComboChange(self):
        field=self.ui.comboBox.itemData(self.ui.comboBox.currentIndex())

        self.ui.minSpinBox.setMinimum(self.model.fieldmin(field))
        self.ui.maxSpinBox.setMinimum(self.model.fieldmin(field))
        self.ui.minSpinBox.setMaximum(self.model.fieldmax(field))
        self.ui.maxSpinBox.setMaximum(self.model.fieldmax(field))

        self.ui.minSpinBox.setValue(self.model.fieldmin(field))
        self.ui.maxSpinBox.setValue(self.model.fieldmax(field))
        self.rebuild()

    def rebuild(self):
        self.listModel.clear()
        if not self.ui.groupBox.isChecked() and self.ui.groupBox.isCheckable():
            self.parts=None
            self.listModel.clear()
            self.update()
            return
        field=self.ui.comboBox.itemData(self.ui.comboBox.currentIndex())

        minimum=None
        if self.ui.minCheckBox.isChecked():
            minimum=self.ui.minSpinBox.value()
        maximum=None
        if self.ui.maxCheckBox.isChecked():
            maximum=self.ui.maxSpinBox.value()
        bins=None
        if self.ui.binCheckBox.isChecked():
            bins=self.ui.binSpinBox.value()

        self.parts=self.model.partition(field,minimum,maximum,bins)

        lst=list(sorted(self.parts.keys()))
        keep=np.zeros(self.model.data.shape,dtype=bool)
        for i,s in enumerate(lst):
            c=self.model.cfg.color(field,s,i)
            item=QStandardItem(s)
            if self.colors:
                item.setData(QColor(c),Qt.DecorationRole)
            if self.checkable:
                item.setCheckable(True)
                item.setCheckState(Qt.Checked)
            item.setData(s)
            self.listModel.appendRow(item)
            keep |= self.parts[s]
        keep = np.logical_not(keep)
        if np.count_nonzero(keep):
            self.parts[MyPartitionWidget.unassignedStr] = keep
            item=QStandardItem(MyPartitionWidget.unassignedStr)
            if self.colors:
                item.setData(QColor("white"),Qt.DecorationRole)
            if self.checkable:
                item.setCheckable(True)
                item.setCheckState(Qt.Unchecked)
            item.setData("NaN / Outside Range")
            self.listModel.appendRow(item)
        self.update()


    def selectColor(self,index):
        c=QColorDialog.getColor(self.listModel.data(index,Qt.DecorationRole),self)
        if c.isValid():
            self.listModel.setData(index,c,Qt.DecorationRole)

    def update(self):
        if self.setFunction is not None:
            if self.colors:
                self.setFunction(self.currentStacks())
            else:
                self.setFunction(self.currentKeep())

    def current(self):
        parts=None
        if self.parts is not None:
            parts={}
            for i in range(self.listModel.rowCount()):
                it=self.listModel.item(i)
                if not self.checkable or it.checkState() == Qt.Checked:
                    parts[it.text()]=self.parts[it.data()]
        return parts

    def currentStacks(self):
        stack=None
        if self.parts is not None:
            stack=[[],[],[]]
            for i in range(self.listModel.rowCount()):
                it=self.listModel.item(i)
                if not self.checkable or it.checkState() == Qt.Checked:
                    if self.colors:
                        stack[0].append(self.parts[it.data()])
                        stack[1].append(it.data(Qt.DecorationRole).name())
                        stack[2].append(it.text())
        return stack

    def currentKeep(self):
        keep=np.ones(self.model.data.shape,dtype=bool)
        if self.parts is not None:
            keep=np.zeros(self.model.data.shape,dtype=bool)
            for i in range(self.listModel.rowCount()):
                it=self.listModel.item(i)
                if not self.checkable or it.checkState() == Qt.Checked:
                    keep |= self.parts[it.data()]
        return keep






