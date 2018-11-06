# datview/ui/controlPanel.py 
# All controls
# Author Natasha Stander

try:
    from PyQt5.QtWidgets import QWidget, QHeaderView, QAbstractItemView, QFileDialog,QMenu, QColorDialog
    from PyQt5.QtCore import QStringListModel, Qt, pyqtSignal, QVariant
    from PyQt5.QtGui import QColor, QStandardItemModel, QStandardItem
    from ui.Ui_ControlPanel5 import Ui_ControlPanel
    qt5=True
except ImportError:
    from PyQt4.QtGui import QWidget, QHeaderView, QAbstractItemView, QFileDialog, QStringListModel, QMenu, QColor, QStandardItemModel, QStandardItem, QColorDialog
    from PyQt4.QtCore import Qt, pyqtSignal, QVariant
    from ui.Ui_ControlPanel import Ui_ControlPanel
    qt5=False

from api.datamodel import DataModel
from api.filtermodel import FilterModel
from . import filterEditDelegate
import numpy as np


class MyControlPanel(QWidget):
    flagselected =pyqtSignal(int)
    def __init__(self,model,parent=None):
        QWidget.__init__(self,parent)
        self.ui=Ui_ControlPanel()
        self.ui.setupUi(self)
        self.model = model

        sortmenu=QMenu()
        lIinitial=None
        searchLegend=model.datafield(model.cfg.legendInitial)
        for i,col in enumerate(sorted(set(self.model.cols) - self.model.cfg.internalCols,key=self.model.prettyname)):
            # Sort Menu
            a = sortmenu.addAction(self.model.prettyname(col))
            a.setData(col)
            a.triggered.connect(self.onAddSortField)

            # Combo boxes
            self.ui.partComboBox.addItem(self.model.prettyname(col),col)
            self.ui.legendComboBox.addItem(self.model.prettyname(col),col)
            if col == searchLegend:
                lIinitial=i

        # Sort
        self.ui.addSortField.setMenu(sortmenu)
        self.ui.sortByListWidget.itemSelectionChanged.connect(self.onSelectionChange)
        self.onSelectionChange()
        self.ui.removeSortField.clicked.connect(self.onRemoveSortField)
        self.ui.moveSortField.clicked.connect(self.onMoveSortFieldUp)
        self.ui.sortAscendingCheckBox.clicked.connect(self.onSortAscendingChange)

        # Legend
        self.legend=None
        self.ui.legendGroupBox.setChecked(lIinitial is not None)
        self.legendModel=QStandardItemModel()
        self.ui.legendListView.setModel(self.legendModel)
        self.ui.legendListView.doubleClicked.connect(self.selectLegendColor)

        if lIinitial is not None:
            self.ui.legendComboBox.setCurrentIndex(lIinitial)
        self.ui.legendComboBox.currentIndexChanged.connect(self.onLegendComboChange)
        self.onLegendComboChange()

        self.ui.legendGroupBox.toggled.connect(self.calcLegend)
        self.ui.legendBinSpinBox.editingFinished.connect(self.calcLegend)
        self.ui.legendMaxSpinBox.editingFinished.connect(self.calcLegend)
        self.ui.legendMinSpinBox.editingFinished.connect(self.calcLegend)
        self.legendModel.dataChanged.connect(self.updateModelLegend)

        # Partition
        self.partitions=None
        self.partitionModel=QStringListModel()
        self.ui.partitionList.setModel(self.partitionModel)
        self.ui.partitionList.selectionModel().currentChanged.connect(self.onSelectPartition)

        self.ui.partComboBox.currentIndexChanged.connect(self.onPartitionComboChange)
        self.onPartitionComboChange()

        self.ui.partitionBox.toggled.connect(self.calcPartitions)
        self.ui.partBinSpinBox.valueChanged.connect(self.calcPartitions)
        self.ui.partMaxSpinBox.valueChanged.connect(self.calcPartitions)
        self.ui.partMinSpinBox.valueChanged.connect(self.calcPartitions)

        # Flags
        if self.model.flagFilter.isActive():
            self.ui.flagIgnore.setChecked(True)
            if self.model.flagFilter.invert:
                self.ui.flagExclude.setChecked(True)
            else:
                self.ui.flagKeep.setChecked(True)
        else: 
            self.ui.flagIgnore.setChecked(True)
        self.model.flagFilter.filterchange.connect(self.onFlagChange)
        self.flagModel=QStringListModel()
        self.ui.flaggedList.setModel(self.flagModel)
        self.ui.flagIgnore.clicked.connect(self.onIgnoreFlags)
        self.ui.flagExclude.clicked.connect(self.onExcludeFlags)
        self.ui.flagKeep.clicked.connect(self.onOnlyFlags)
        self.ui.flaggedList.selectionModel().currentChanged.connect(self.onSelectFlag)

        # Limits
        self.ui.limitCheckBox.clicked.connect(self.onLimitChange)
        self.ui.limTopButton.clicked.connect(self.onLimitChange)
        self.ui.limRandomButton.clicked.connect(self.onLimitChange)
        self.ui.limitSpinBox.editingFinished.connect(self.onLimitChange)
        self.onLimitChange()

        # Filters
        self.filtermodel = FilterModel(model.topfilter,model)
        self.ui.filterTreeView.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.ui.filterTreeView.setModel(self.filtermodel)
        if qt5:
            self.ui.filterTreeView.header().setSectionResizeMode(0,QHeaderView.ResizeToContents)
            self.ui.filterTreeView.header().setSectionResizeMode(1,QHeaderView.ResizeToContents)
        else:
            self.ui.filterTreeView.header().setResizeMode(0,QHeaderView.ResizeToContents)
            self.ui.filterTreeView.header().setResizeMode(1,QHeaderView.ResizeToContents)
        self.ui.filterTreeView.setItemDelegate(filterEditDelegate.FilterItemDelegate())
        self.filtermodel.rowsInserted.connect(self.ui.filterTreeView.expandAll)
        self.ui.filterTreeView.expandAll()

        # Filters Save/Load
        self.ui.saveFiltersButton.clicked.connect(self.onSaveFilters)
        self.ui.loadFiltersButton.clicked.connect(self.onLoadFilters)

    # Sorting
    def onAddSortField(self):
        field=self.sender().data()
        self.ui.sortByListWidget.addItem(self.model.prettyname(field))
        self.model.sortlst.append(field)
        self.model.onSortChange()

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
        self.model.onSortChange()
        self.onSelectionChange()

    def onMoveSortFieldUp(self):
        rows=[]
        for item in self.ui.sortByListWidget.selectedItems():
            rows.append(self.ui.sortByListWidget.row(item))
        for r in sorted(rows):
            self.model.sortlst.insert(r-1,self.model.sortlst.pop(r))
            self.ui.sortByListWidget.insertItem(r-1,self.ui.sortByListWidget.takeItem(r))
            self.ui.sortByListWidget.setCurrentItem(self.ui.sortByListWidget.item(r-1))   
        self.model.onSortChange()

    def setSort(self,lst):
        for field in lst:
            self.ui.sortByListWidget.addItem(self.model.prettyname(field))
            self.model.sortlst.append(field)
        self.model.onSortChange()

    def onSortAscendingChange(self):
        self.model.reverseSort = not self.ui.sortAscendingCheckBox.isChecked()
        self.model.onSortChange()

    # Legends
    def onLegendComboChange(self):
        field=self.ui.legendComboBox.itemData(self.ui.legendComboBox.currentIndex())
        enable=not self.model.isCategorical(field)

        if self.ui.legendGroupBox.isChecked() or not enable:
            self.ui.legendBinSpinBox.setEnabled(enable)
            self.ui.legendMinSpinBox.setEnabled(enable)
            self.ui.legendMaxSpinBox.setEnabled(enable)

        self.ui.legendMinSpinBox.setMinimum(self.model.fieldmin(field))
        self.ui.legendMaxSpinBox.setMinimum(self.model.fieldmin(field))
        self.ui.legendMinSpinBox.setMaximum(self.model.fieldmax(field))
        self.ui.legendMaxSpinBox.setMaximum(self.model.fieldmax(field))

        self.ui.legendMinSpinBox.setValue(self.model.fieldmin(field))
        self.ui.legendMaxSpinBox.setValue(self.model.fieldmax(field))
        self.calcLegend()

    def calcLegend(self):
        self.legendModel.clear()
        if not self.ui.legendGroupBox.isChecked():
            self.legend=None
            self.legendModel.clear()
            self.updateModelLegend()
            return
        field=self.ui.legendComboBox.itemData(self.ui.legendComboBox.currentIndex())
        num=None
        minimum=None
        maximum=None
        if self.ui.legendBinSpinBox.isEnabled():
            num=self.ui.legendBinSpinBox.value()
            minimum=self.ui.legendMinSpinBox.value()
            maximum=self.ui.legendMaxSpinBox.value()
        self.legend=self.model.partition(field,minimum,maximum,num)
        lst=list(sorted(self.legend.keys()))
        for i,s in enumerate(lst):
            c=self.model.cfg.color(field,s,i)
            item=QStandardItem(s)
            item.setData(QColor(c),Qt.DecorationRole)
            item.setData(s)
            self.legendModel.appendRow(item)
        self.updateModelLegend()


    def selectLegendColor(self,index):
        c=QColorDialog.getColor(self.legendModel.data(index,Qt.DecorationRole),self)
        if c.isValid():
            self.legendModel.setData(index,c,Qt.DecorationRole)

    def updateModelLegend(self):
        stack=None
        if self.legend is not None:
            stack=[[],[],[]]
            for i in range(self.legendModel.rowCount()):
                it=self.legendModel.item(i)
                stack[0].append(self.legend[it.data()])
                stack[1].append(it.data(Qt.DecorationRole).name())
                stack[2].append(it.text())
        self.model.setStacks(stack)
                
        

    # Partitions
    def onPartitionComboChange(self):
        field=self.ui.partComboBox.itemData(self.ui.partComboBox.currentIndex())
        enable=not self.model.isCategorical(field)

        if self.ui.partitionBox.isChecked() or not enable:
            self.ui.partBinSpinBox.setEnabled(enable)
            self.ui.partMinSpinBox.setEnabled(enable)
            self.ui.partMaxSpinBox.setEnabled(enable)

        self.ui.partMinSpinBox.setMinimum(self.model.fieldmin(field))
        self.ui.partMaxSpinBox.setMinimum(self.model.fieldmin(field))
        self.ui.partMinSpinBox.setMaximum(self.model.fieldmax(field))
        self.ui.partMaxSpinBox.setMaximum(self.model.fieldmax(field))

        self.ui.partMinSpinBox.setValue(self.model.fieldmin(field))
        self.ui.partMaxSpinBox.setValue(self.model.fieldmax(field))
        self.calcPartitions()

    def calcPartitions(self):
        self.model.clearPartition()
        if not self.ui.partitionBox.isChecked():
            self.partitions=None
            self.partitionModel.setStringList([])
            return
        field=self.ui.partComboBox.itemData(self.ui.partComboBox.currentIndex())
        num=None
        minimum=None
        maximum=None
        if self.ui.partBinSpinBox.isEnabled():
            num=self.ui.partBinSpinBox.value()
            minimum=self.ui.partMinSpinBox.value()
            maximum=self.ui.partMaxSpinBox.value()
        self.partitions=self.model.partition(field,minimum,maximum,num)
        self.partitionModel.setStringList(sorted(self.partitions.keys()))

    def onSelectPartition(self):
        part=self.partitionModel.data(self.ui.partitionList.selectionModel().currentIndex(),Qt.DisplayRole)
        self.model.setPartition(self.partitions[part])

    # Flags
    def onFlagChange(self):
        slist=[]
        for i in np.where(self.model.flagFilter.keep)[0]:
            slist.append(str(i))
        self.flagModel.setStringList(slist)

    def onIgnoreFlags(self,checked):
        if checked:
            self.model.flagFilter.setActive(False)

    def onExcludeFlags(self,checked):
        if checked:
            self.model.flagFilter.setInvert(True)
            self.model.flagFilter.setActive(True)

    def onOnlyFlags(self,checked):
        if checked:
            self.model.flagFilter.setInvert(False)
            self.model.flagFilter.setActive(True)

    def onSelectFlag(self):
        row=int(self.flagModel.data(self.ui.flaggedList.selectionModel().currentIndex(),Qt.DisplayRole))
        self.flagselected.emit(row)


    # Limits 
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

    # Filters
    def onSaveFilters(self):
        name=QFileDialog.getSaveFileName(self,'Save Filters As',filter='*.xml')
        if qt5:
            if name:
                self.model.saveFilters(name[0])
        elif name is not None and len(name):
            self.model.saveFilters(name)

    def onLoadFilters(self):
        name=QFileDialog.getOpenFileName(self,'Load Filter File',filter='*.xml')
        if qt5:
            if name:
                self.model.loadFilters(name[0])
        elif name is not None and len(name):
            self.model.loadFilters(name)



