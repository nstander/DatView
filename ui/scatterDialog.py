# datview/ui/hist2dDialog.py 
# This file contains code for scatter plot dialog
# Author Natasha Stander

try:
    from PyQt5.QtWidgets import QDialog
    from PyQt5.QtCore import Qt
    from ui.Ui_ScatterDialog5 import Ui_ScatterDialog
except ImportError:
    from PyQt4.QtGui import QDialog
    from PyQt4.QtCore import Qt
    from ui.Ui_ScatterDialog import Ui_ScatterDialog
from api.datamodel import DataModel
from ui.plots import MyScatter

class MyScatterDialog(QDialog):
    def __init__(self,model,parent):
        QDialog.__init__(self,parent)
        self.ui=Ui_ScatterDialog()
        self.ui.setupUi(self)
        self.model = model

        self.ui.zCombo.addItem("None",None)
        self.ui.zCombo.hide()
        self.ui.label_3.hide()
        self.ui.logCheckBox.hide()
        self.ui.cCombo.addItem("None",None)
        for col in sorted(set(self.model.cols) - self.model.cfg.internalCols,key=self.model.prettyname):
            self.ui.xCombo.addItem(self.model.prettyname(col),col)
            self.ui.yCombo.addItem(self.model.prettyname(col),col)
            self.ui.zCombo.addItem(self.model.prettyname(col),col)
            self.ui.cCombo.addItem(self.model.prettyname(col),col)
        self.accepted.connect(self.onAccept)

    def onAccept(self):
        p=MyScatter(self.model,self.ui.xCombo.itemData(self.ui.xCombo.currentIndex()),self.ui.yCombo.itemData(self.ui.yCombo.currentIndex()),self.ui.cCombo.itemData(self.ui.cCombo.currentIndex()),parent=self.parent(),flags=Qt.Window)
        p.show()

        
