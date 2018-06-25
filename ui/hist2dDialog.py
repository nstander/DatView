# datview/ui/hist2dDialog.py 
# This file contains code for Histogram 2D Dialog
# Author Natasha Stander

from PyQt4.QtGui import QDialog
from PyQt4.QtCore import Qt
from api.datamodel import DataModel
from ui.Ui_ScatterDialog import Ui_ScatterDialog
from ui.plots import MyHist2d

class MyHist2dDialog(QDialog):
    def __init__(self,model,parent):
        QDialog.__init__(self,parent)
        self.ui=Ui_ScatterDialog()
        self.ui.setupUi(self)
        self.setWindowTitle("2D Histogram")
        self.model = model

        # Hide irrelevant combos so we can keep using the same UI file.
        self.ui.zCombo.hide()
        self.ui.cCombo.hide()
        self.ui.label_3.hide()
        self.ui.label_4.hide()
        for col in sorted(set(self.model.cols) - self.model.cfg.internalCols,key=self.model.prettyname):
            self.ui.xCombo.addItem(self.model.prettyname(col),col)
            self.ui.yCombo.addItem(self.model.prettyname(col),col)
        self.accepted.connect(self.onAccept)

    def onAccept(self):
        p=MyHist2d(self.model,self.ui.xCombo.itemData(self.ui.xCombo.currentIndex()),self.ui.yCombo.itemData(self.ui.yCombo.currentIndex()),parent=self.parent(),flags=Qt.Window,log=self.ui.logCheckBox.isChecked())
        p.show()

        
