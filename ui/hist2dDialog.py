# datview/ui/hist2dDialog.py 
# This file contains code for Histogram 2D Dialog
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
from ui.plots import MyFigure

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
        p=MyFigure(parent=self.parent(),flags=Qt.Window)
        xfield=self.ui.xCombo.itemData(self.ui.xCombo.currentIndex())
        yfield=self.ui.yCombo.itemData(self.ui.yCombo.currentIndex())
        p.histogram2D(self.model,xfield,yfield,log=self.ui.logCheckBox.isChecked())
        logtxt=""
        if self.ui.logCheckBox.isChecked():
            logtxt="Log "
        p.setWindowTitle("%s - %s - %s2D Histogram" % (self.model.prettyname(xfield),self.model.prettyname(yfield),logtxt))
        p.show()

        
