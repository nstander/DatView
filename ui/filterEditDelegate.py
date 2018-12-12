# datview/ui/filterEditDelegate.py
# The filter panel in the GUI is a generic QTreeView defined in the main gui. This file provides all the interactivity to add and update filters for the filter panel
# Author Natasha Stander

try:
    from PyQt5.QtWidgets import QStyledItemDelegate, QDoubleSpinBox, QComboBox, QListWidget, QListWidgetItem, QToolButton, QMenu
    from PyQt5.QtCore import  Qt
except ImportError:
    from PyQt4.QtGui import QStyledItemDelegate, QDoubleSpinBox, QComboBox, QListWidget, QListWidgetItem, QToolButton, QMenu
    from PyQt4.QtCore import  Qt
import sys
import numpy as np
sys.path.append("..")
from api import filters, datamodel


class FilterItemDelegate(QStyledItemDelegate):
    def __init__(self):
        QStyledItemDelegate.__init__(self)

    def createEditor(self,parent,option,index):
        if index.isValid() and ((index.column() == 1 and index.internalPointer().hasMin()) \
                             or (index.column() == 2 and index.internalPointer().hasMax())):
            e=QDoubleSpinBox(parent)
            e.setDecimals(3)
            e.setFrame(False)
            e.setMinimum(-1)
            e.setMaximum(index.model().dmodel.fieldmax(index.internalPointer().field)+1)
            e.setSingleStep(0.1)
            return e
        if index.isValid() and index.column() == 2 and isinstance(index.internalPointer(),filters.InSetFilter):
            combo=QComboBox(parent)
            return combo
        if index.isValid() and index.column() == 2 and (isinstance(index.internalPointer(),filters.OrFilter) or isinstance(index.internalPointer(),filters.AndFilter)):
            e=QToolButton(parent)
            e.setText("+")
            e.setPopupMode(QToolButton.InstantPopup)
            top=QMenu()

            addAnd = top.addAction("AND")
            addAnd.setData(index.internalPointer())
            addAnd.triggered.connect(self.onAddAnd)

            addOr  = top.addAction("OR")
            addOr.setData(index.internalPointer())
            addOr.triggered.connect(self.onAddOr)

            between = top.addMenu("Between")
            greater = top.addMenu(">=")
            less = top.addMenu("<")
            inset = top.addMenu("In")

            if index.model().dmodel.hasComparisons():
                maxMenu=top.addMenu("Max")
                minMenu=top.addMenu("Min")
            for col in sorted(set(index.model().dmodel.cols) - index.model().dmodel.cfg.internalCols,key=index.model().dmodel.prettyname):
                a = between.addAction(index.model().dmodel.prettyname(col))
                a.setData((index,col))
                a.triggered.connect(self.onAddBetween)

                a = greater.addAction(index.model().dmodel.prettyname(col))
                a.setData((index,col))
                a.triggered.connect(self.onAddGreater)

                a = less.addAction(index.model().dmodel.prettyname(col))
                a.setData((index,col))
                a.triggered.connect(self.onAddLess)

                if index.model().dmodel.isCategorical(col):
                    a = inset.addAction(index.model().dmodel.prettyname(col))
                    a.setData((index,col))
                    a.triggered.connect(self.onAddIn)
                if index.model().dmodel.hasComparisons():
                    a = maxMenu.addAction(index.model().dmodel.prettyname(col))
                    a.setData((index,col))
                    a.triggered.connect(self.onAddMax)

                    a = minMenu.addAction(index.model().dmodel.prettyname(col))
                    a.setData((index,col))
                    a.triggered.connect(self.onAddMin)
            e.setMenu(top)
            return e
        return super(FilterItemDelegate,self).createEditor(parent,option,index)

    def setEditorData(self,editor,index):
        if index.isValid() and ((index.column() == 1 and index.internalPointer().hasMin()) \
                                or (index.column() == 2 and (index.internalPointer().hasMax() or \
                                isinstance(index.internalPointer(),filters.InSetFilter)))):
            if index.column() == 1 and index.internalPointer().hasMin():
                editor.setValue(index.internalPointer().minimum)
            elif index.column() == 2 and index.internalPointer().hasMax():
                editor.setValue(index.internalPointer().maximum)
            elif index.column() == 2 and isinstance(index.internalPointer(),filters.InSetFilter):
                lwidget=QListWidget(editor)
                lwidget.addItem(index.internalPointer().valuesString())
                if index.model().dmodel.hasLabels(index.internalPointer().field):
                    lwidget.addItems(index.model().dmodel.labels(index.internalPointer().field))
                    for i in range(1,lwidget.count()):
                        lwidget.item(i).setFlags(lwidget.item(i).flags() | Qt.ItemIsUserCheckable)
                        # i-1 because item 0 is the full list so need to offset all by -1
                        lwidget.item(i).setCheckState(index.model().dmodel.intValue(index.internalPointer().field,lwidget.item(i).text()) in index.internalPointer().allowed)
                else:
                    numbers=np.unique(index.internalPointer().values)
                    for n in numbers:
                        i=QListWidgetItem(str(int(n)))
                        i.setFlags(i.flags() | Qt.ItemIsUserCheckable)
                        i.setCheckState(n in index.internalPointer().allowed)
                        lwidget.addItem(i)
                editor.setModel(lwidget.model())
                editor.setView(lwidget)
                editor.currentIndexChanged.connect(self.onComboChange)
            elif index.column() == 2 and isinstance(index.internalPointer(),filters.GroupFilter):
                pass
        else:
            super(FilterItemDelegate,self).setEditorData(editor,index)

    def setModelData(self,editor,model,index):
        if index.isValid() and ((index.column() == 1 and index.internalPointer().hasMin()) \
                             or (index.column() == 2 and index.internalPointer().hasMax())):
            editor.interpretText()
            if index.column() == 1 and index.internalPointer().hasMin():
                index.internalPointer().setMin(editor.value())
            elif index.column() == 2 and index.internalPointer().hasMax():
                index.internalPointer().setMax(editor.value())
        elif index.isValid() and index.column() == 2 and isinstance(index.internalPointer(),filters.InSetFilter):
            allowed=[]
            for i in range(1,editor.view().count()):
                if editor.view().item(i).checkState():
                    allowed.append(model.dmodel.intValue(index.internalPointer().field,editor.view().item(i).text()))       
            index.internalPointer().setAllowed(allowed)
        else:
            super(FilterItemDelegate,self).setModelData(editor,model,index)

    def updateEditorGeometr(self,editor,option,index):
        if index.isValid() and ((index.column() == 1 and index.internalPointer().hasMin()) \
                             or (index.column() == 2 and (index.internalPointer().hasMax() or \
                                isinstance(index.internalPointer(),filters.InSetFilter)))):
            editor.setGeometry(option.rect)
        else:
            super(FilterItemDelegate,self).updateEditorGeometr(editor,option,index)

    def onComboChange(self):
        combo=self.sender()
        i = combo.currentIndex()
        if i != 0:
            curtext=combo.view().item(0).text().split(',')
            check=not combo.view().item(i).checkState()
            if check:
                curtext.append(combo.currentText())
            else:
                curtext.remove(combo.currentText())
            combo.view().item(0).setText(",".join(curtext))
            combo.view().item(i).setCheckState(check)
            combo.setCurrentIndex(0)
            combo.showPopup()

    def onAddAnd(self):
        act=self.sender()
        par=act.data()
        child=filters.AndFilter(par.shape)
        par.addChild(child)

    def onAddOr(self):
        act=self.sender()
        par=act.data()
        child=filters.OrFilter(par.shape)
        par.addChild(child)

    def onAddBetween(self):
        act=self.sender()
        par=act.data()[0].internalPointer()
        dmodel=act.data()[0].model().dmodel
        field=act.data()[1]
        child=filters.BetweenFilter(dmodel.fieldmin(field)-1,dmodel.fieldmax(field)+1,dmodel.data[field],field)
        par.addChild(child)

    def onAddLess(self):
        act=self.sender()
        par=act.data()[0].internalPointer()
        dmodel=act.data()[0].model().dmodel
        field=act.data()[1]
        child=filters.LessThanFilter(dmodel.fieldmax(field)+1,dmodel.data[field],field)
        par.addChild(child)

    def onAddGreater(self):
        act=self.sender()
        par=act.data()[0].internalPointer()
        dmodel=act.data()[0].model().dmodel
        field=act.data()[1]
        child=filters.GreaterEqualFilter(dmodel.fieldmin(field)-1,dmodel.data[field],field)
        par.addChild(child)

    def onAddIn(self):
        act=self.sender()
        par=act.data()[0].internalPointer()
        dmodel=act.data()[0].model().dmodel
        field=act.data()[1]
        child=filters.InSetFilter(dmodel.intValues(field),dmodel.data[field],field,dmodel.stringValue)
        par.addChild(child)

    def onAddMax(self):
        act=self.sender()
        par=act.data()[0].internalPointer()
        dmodel=act.data()[0].model().dmodel
        field=act.data()[1]
        child=filters.MaxFilter(par.shape,dmodel.cmparray,dmodel.cmpvalues(field),field)
        par.addChild(child)

    def onAddMin(self):
        act=self.sender()
        par=act.data()[0].internalPointer()
        dmodel=act.data()[0].model().dmodel
        field=act.data()[1]
        child=filters.MinFilter(par.shape,dmodel.cmparray,dmodel.cmpvalues(field),field)
        par.addChild(child)



