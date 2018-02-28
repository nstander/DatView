from PyQt4.QtGui import QStyledItemDelegate, QDoubleSpinBox
import sys
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
        return super(FilterItemDelegate,self).createEditor(parent,option,index)

    def setEditorData(self,editor,index):
        if index.isValid() and ((index.column() == 1 and index.internalPointer().hasMin()) \
                             or (index.column() == 2 and index.internalPointer().hasMax())):
            if index.column() == 1 and index.internalPointer().hasMin():
                editor.setValue(index.internalPointer().minimum)
            elif index.column() == 2 and index.internalPointer().hasMax():
                editor.setValue(index.internalPointer().maximum)
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
        else:
            super(FilterItemDelegate,self).setModelData(editor,model,index)

    def updateEditorGeometr(self,editor,option,index):
        if index.isValid() and ((index.column() == 1 and index.internalPointer().hasMin()) \
                             or (index.column() == 2 and index.internalPointer().hasMax())):
            editor.setGeometry(option.rect)
        else:
            super(FilterItemDelegate,self).updateEditorGeometr(editor,option,index)
