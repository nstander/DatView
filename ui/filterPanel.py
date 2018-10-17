# datview/ui/filterPanel.py
# FilterPanel code for FilterPanel.ui
# Author Natasha Stander

try:
    from PyQt5.QtWidgets import QWidget, QHeaderView, QAbstractItemView, QFileDialog
    from ui.Ui_FilterPanel5 import Ui_FilterPanel
    qt5=True
except ImportError:
    from PyQt4.QtGui import QWidget, QHeaderView, QAbstractItemView, QFileDialog
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
        self.ui.partitionBox.hide()
        self.ui.flaggedBox.hide()

        # Flagged

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


