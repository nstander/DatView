# datview/ui/plotDialogs.py 
# This file contains code for Histogram 2D Dialog
# Author Natasha Stander

try:
    from PyQt5.QtWidgets import QDialog
    from PyQt5.QtCore import Qt
    from ui.Ui_PlotDialog5 import Ui_PlotDialog
except ImportError:
    from PyQt4.QtGui import QDialog
    from PyQt4.QtCore import Qt
    from ui.Ui_PlotDialog import Ui_PlotDialog
from api.datamodel import DataModel
from ui.plots import MyFigure

class MyHist2dDialog(QDialog):
    def __init__(self,model,parent):
        QDialog.__init__(self,parent)
        self.ui=Ui_PlotDialog()
        self.ui.setupUi(self)
        self.setWindowTitle("2D Histogram")
        self.ui.description.setText("Select X and Y axis, colors are determined by number of patterns in each bin.")
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

class MyScatterDialog(QDialog):
    def __init__(self,model,parent):
        QDialog.__init__(self,parent)
        self.ui=Ui_PlotDialog()
        self.ui.setupUi(self)
        self.ui.description.setText("Select X and Y axis, and optional color by field")
        self.model = model

        self.ui.zCombo.addItem("None",None)
        self.ui.zCombo.hide()
        self.ui.label_3.hide()
        self.ui.logCheckBox.hide()
        self.ui.cCombo.addItem("None",None)
        for col in sorted(set(self.model.cols) - self.model.cfg.internalCols,key=self.model.prettyname):
            self.ui.xCombo.addItem(self.model.prettyname(col),col)
            self.ui.yCombo.addItem(self.model.prettyname(col),col)
            self.ui.cCombo.addItem(self.model.prettyname(col),col)
        self.accepted.connect(self.onAccept)

    def onAccept(self):
        p=MyFigure(parent=self.parent(),flags=Qt.Window)
        xfield=self.ui.xCombo.itemData(self.ui.xCombo.currentIndex())
        yfield=self.ui.yCombo.itemData(self.ui.yCombo.currentIndex())
        p.scatter(self.model,xfield,yfield,self.ui.cCombo.itemData(self.ui.cCombo.currentIndex()))
        p.setWindowTitle("%s - %s - Scatter" % (self.model.prettyname(xfield),self.model.prettyname(yfield)))
        p.show()

class MyPixelPlotDialog(QDialog):
    def __init__(self,model,parent):
        QDialog.__init__(self,parent)
        self.ui=Ui_PlotDialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Pixel Plot")
        self.ui.description.setText("Color pixels at each coordinate with the value of the color by field. Use to plot data according to real-space coordinates.")
        self.model = model

        self.ui.zCombo.addItem("None",None)
        self.ui.zCombo.hide()
        self.ui.label_3.hide()
        self.ui.logCheckBox.hide()
        cols=set(self.model.cols) - self.model.cfg.internalCols
        for col in sorted(cols,key=self.model.prettyname):
            if model.cfg.dtype(col).startswith("i") or model.cfg.dtype(col).startswith("u"):
                self.ui.xCombo.addItem(self.model.prettyname(col),col)
                self.ui.yCombo.addItem(self.model.prettyname(col),col)
            self.ui.cCombo.addItem(self.model.prettyname(col),col)
        if "chiprow" in cols:
            self.ui.yCombo.setCurrentIndex(self.ui.yCombo.findText(self.model.prettyname("chiprow")))
        elif "row" in cols:
            self.ui.yCombo.setCurrentIndex(self.ui.yCombo.findText(self.model.prettyname("row")))
        if "col" in cols:
            self.ui.xCombo.setCurrentIndex(self.ui.xCombo.findText(self.model.prettyname("col")))

        self.accepted.connect(self.onAccept)

    def onAccept(self):
        p=MyFigure(parent=self.parent(),flags=Qt.Window)
        xfield=self.ui.xCombo.itemData(self.ui.xCombo.currentIndex())
        yfield=self.ui.yCombo.itemData(self.ui.yCombo.currentIndex())
        cfield=self.ui.cCombo.itemData(self.ui.cCombo.currentIndex())
        p.pixelPlot(self.model,xfield,yfield,cfield)
        p.setWindowTitle("%s - Pixel Plot" % (self.model.prettyname(cfield)))
        p.show()

        
