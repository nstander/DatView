# datview/ui/filterPanel.py
# FilterPanel code for FilterPanel.ui
# Author Natasha Stander

try:
    from PyQt5.QtWidgets import QWidget, QHeaderView, QAbstractItemView, QFileDialog
    from PyQt5.QtCore import QStringListModel, Qt
    from ui.Ui_FilterPanel5 import Ui_FilterPanel
    qt5=True
except ImportError:
    from PyQt4.QtGui import QWidget, QHeaderView, QAbstractItemView, QFileDialog, QStringListModel
    from PyQt4.QtCore import Qt
    from ui.Ui_FilterPanel import Ui_FilterPanel
    qt5=False
from api.datamodel import DataModel
from api.filtermodel import FilterModel
from . import filterEditDelegate

class MyFilterPanel(QWidget):
    def __init__(self,dmodel,parent=None):
        QWidget.__init__(self,parent)
        self.ui=Ui_FilterPanel()
        self.ui.setupUi(self)
        self.model = dmodel

        # Partitions
        for col in sorted(set(self.model.cols) - self.model.cfg.internalCols,key=self.model.prettyname):
            self.ui.partComboBox.addItem(self.model.prettyname(col),col)
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


        # Flagged
        self.ui.flaggedBox.hide()

        # Filter Tree View
        self.filtermodel = FilterModel(dmodel.topfilter,dmodel)
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
        
        
        

        


