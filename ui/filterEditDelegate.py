from PyQt4.QtGui import QStyledItemDelegate, QDoubleSpinBox, QComboBox, QListWidget, QListWidgetItem
from PyQt4.QtCore import  Qt
import sys
import numpy as np
sys.path.append("..")
from api import filters


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
                        lwidget.item(i).setCheckState((i-1) in index.internalPointer().allowed)
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
