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
from . import filterEditDelegate, partitionWidget
import numpy as np


class MyControlPanel(QWidget):
    flagselected =pyqtSignal(int)
    def __init__(self,model,parent=None):
        QWidget.__init__(self,parent)
        self.ui=Ui_ControlPanel()
        self.ui.setupUi(self)
        self.model = model

        sortmenu=QMenu()
        for i,col in enumerate(sorted(set(self.model.cols) - self.model.cfg.internalCols,key=self.model.prettyname)):
            # Sort Menu
            a = sortmenu.addAction(self.model.prettyname(col))
            a.setData(col)
            a.triggered.connect(self.onAddSortField)

        # Sort
        self.ui.addSortField.setMenu(sortmenu)
        self.ui.sortByListWidget.itemSelectionChanged.connect(self.onSelectionChange)
        self.onSelectionChange()
        self.ui.removeSortField.clicked.connect(self.onRemoveSortField)
        self.ui.moveSortField.clicked.connect(self.onMoveSortFieldUp)
        self.ui.sortAscendingCheckBox.clicked.connect(self.onSortAscendingChange)

        # Legend
        self.legendWidget=partitionWidget.MyPartitionWidget(model, self.model.setStacks, model.cfg.legendInitial, True, True, self)
        self.legendWidget.ui.description.setText("Change field and colors for stacked histograms. Double click to edit color. Single click on selected to edit label. Checkboxes only affect visibility, not the selected items.")
        self.legendWidget.ui.groupBox.setTitle("Histogram Legends")
        self.ui.verticalLayout_7.insertWidget(1,self.legendWidget)

        # Partition
        self.partWidget=partitionWidget.MyPartitionWidget(model, self.model.setPartition, model.cfg.partitionInitial, True, False, self)
        self.partWidget.ui.description.setText("Partition the data. Selecting a partition changes the full dataset shown in plots to just match the partition. When partitions are active, output is split with one output for each partition.")
        self.partWidget.ui.groupBox.setTitle("Partitions")
        self.ui.verticalLayout_7.insertWidget(2,self.partWidget)

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



