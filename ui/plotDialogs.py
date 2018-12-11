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
from . import partitionWidget
import numpy as np

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
        x0=0
        y0=0
        xInit=model.datafield(model.cfg.hist2dInitialX)
        yInit=model.datafield(model.cfg.hist2dInitialY)
        for i,col in enumerate(sorted(set(self.model.cols) - self.model.cfg.internalCols,key=self.model.prettyname)):
            self.ui.xCombo.addItem(self.model.prettyname(col),col)
            self.ui.yCombo.addItem(self.model.prettyname(col),col)
            if xInit == col:
                x0=i
            if yInit == col:
                y0=i

        self.ui.yCombo.setCurrentIndex(y0)
        self.ui.xCombo.setCurrentIndex(x0)
        self.accepted.connect(self.onAccept)

    def onAccept(self):
        p=MyFigure(parent=self.parent(),flags=Qt.Window)
        xfield=self.ui.xCombo.itemData(self.ui.xCombo.currentIndex())
        yfield=self.ui.yCombo.itemData(self.ui.yCombo.currentIndex())
        p.histogram2D(self.model,xfield,yfield,log=self.ui.logCheckBox.isChecked())
        p.setWindowTitle("%s - %s - 2D Histogram" % (self.model.prettyname(xfield),self.model.prettyname(yfield)))
        p.show()

class MyScatterDialog(QDialog):
    def __init__(self,model,parent):
        QDialog.__init__(self,parent)
        self.ui=Ui_PlotDialog()
        self.ui.setupUi(self)
        self.ui.description.setText("Select X and Y axis, and optional color by field")
        self.model = model

        self.ui.zCombo.hide()
        self.ui.label_3.hide()
        self.ui.logCheckBox.hide()
        self.ui.cCombo.addItem("None",None)
        x0=0
        y0=0
        c0=0
        xInit=model.datafield(model.cfg.scatterInitialX)
        yInit=model.datafield(model.cfg.scatterInitialY)
        cInit=model.datafield(model.cfg.scatterInitialColor)
        for i,col in enumerate(sorted(set(self.model.cols) - self.model.cfg.internalCols,key=self.model.prettyname)):
            self.ui.xCombo.addItem(self.model.prettyname(col),col)
            self.ui.yCombo.addItem(self.model.prettyname(col),col)
            self.ui.cCombo.addItem(self.model.prettyname(col),col)
            if cInit == col:
                c0=i+1
            if xInit == col:
                x0=i
            if yInit == col:
                y0=i

        self.ui.yCombo.setCurrentIndex(y0)
        self.ui.cCombo.setCurrentIndex(c0)
        self.ui.xCombo.setCurrentIndex(x0)

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

        self.ui.zCombo.hide()
        self.ui.label_3.hide()
        self.ui.logCheckBox.hide()
        cols=set(self.model.cols) - self.model.cfg.internalCols
        i2=0
        x0=0
        y0=0
        c0=0
        xInit=model.datafield(model.cfg.pixelplotInitialX)
        yInit=model.datafield(model.cfg.pixelplotInitialY)
        cInit=model.datafield(model.cfg.pixelplotInitialColor)
        for i,col in enumerate(sorted(cols,key=self.model.prettyname)):
            if model.cfg.dtype(col).startswith("i") or model.cfg.dtype(col).startswith("u") or col in model.digitized:
                self.ui.xCombo.addItem(self.model.prettyname(col),col)
                self.ui.yCombo.addItem(self.model.prettyname(col),col)
                if col == xInit:
                    x0=i2
                if col == yInit:
                    y0=i2
                i2+=1
            self.ui.cCombo.addItem(self.model.prettyname(col),col)
            if cInit == col:
                c0=i

        self.ui.yCombo.setCurrentIndex(y0)
        self.ui.cCombo.setCurrentIndex(c0)
        self.ui.xCombo.setCurrentIndex(x0)

        self.accepted.connect(self.onAccept)

    def onAccept(self):
        p=MyFigure(parent=self.parent(),flags=Qt.Window)
        xfield=self.ui.xCombo.itemData(self.ui.xCombo.currentIndex())
        yfield=self.ui.yCombo.itemData(self.ui.yCombo.currentIndex())
        cfield=self.ui.cCombo.itemData(self.ui.cCombo.currentIndex())
        p.pixelPlot(self.model,xfield,yfield,cfield)
        p.setWindowTitle("%s - Pixel Plot" % (self.model.prettyname(cfield)))
        p.show()

class MyAggPlotDialog(QDialog):
    def __init__(self,model,parent):
        QDialog.__init__(self,parent)
        self.ui=Ui_PlotDialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Aggregated Plot")
        self.ui.description.setText("Aggregate values of x field using method. Show error bars from selected method. Use legend for multiple lines. Max is not included in range when set. Bins are automatically determined when not set.")
        self.model = model

        self.ui.xCombo.hide()
        self.ui.label.hide()

        self.ui.label_3.setText("Aggregate Method:")
        self.ui.zCombo.addItem("Average",np.average)
        self.ui.zCombo.addItem("Median",np.median)
        self.ui.zCombo.addItem("Min",np.min)
        self.ui.zCombo.addItem("Max",np.max)
        self.ui.zCombo.addItem("Count",len)
        self.ui.zCombo.addItem("Count Valid (not -1)",lambda x : np.count_nonzero(x!=-1))

        self.ui.label_4.setText("Error Bars:")
        self.ui.cCombo.addItem("None",None)
        self.ui.cCombo.addItem("Standard Deviation",lambda x : [np.std(x)])
        self.ui.cCombo.addItem("Min,Max",lambda x : [np.min(x),np.max(x)])

        self.ui.logCheckBox.setText("Transpose")
        cols=set(self.model.cols) - self.model.cfg.internalCols
        yInit=model.datafield(model.cfg.aggplotInitialY)
        y0=0
        for i,col in enumerate(sorted(cols,key=self.model.prettyname)):
            self.ui.yCombo.addItem(self.model.prettyname(col),col)
            if col == yInit:
                y0=i
        self.ui.yCombo.setCurrentIndex(y0)
        self.accepted.connect(self.onAccept)

        self.aggFieldWidget=partitionWidget.MyPartitionWidget(model, None, model.cfg.aggplotInitialX, True, False, self)
        self.aggFieldWidget.ui.description.hide()
        self.aggFieldWidget.ui.groupBox.setTitle("X Axis (aggregated)")
        self.aggFieldWidget.ui.groupBox.setChecked(True)
        self.aggFieldWidget.ui.groupBox.setCheckable(False)
        self.aggFieldWidget.ui.listView.hide()
        self.aggFieldWidget.onComboChange()
        self.ui.verticalLayout_2.insertWidget(6,self.aggFieldWidget)

        self.legendWidget=partitionWidget.MyPartitionWidget(model, None, model.cfg.aggplotInitialLegend, True, True, self)
        self.legendWidget.ui.description.setText("Split results into lines.")
        self.legendWidget.ui.groupBox.setTitle("Lines")
        self.ui.verticalLayout_2.insertWidget(7,self.legendWidget)
        self.adjustSize()

        

    def onAccept(self):
#model,xfield,yfield,aggFunc,errFunc,partitions,tranpose
        p=MyFigure(parent=self.parent(),flags=Qt.Window)
        xfield=self.aggFieldWidget.ui.comboBox.itemData(self.aggFieldWidget.ui.comboBox.currentIndex())
        yfield=self.ui.yCombo.itemData(self.ui.yCombo.currentIndex())
        aggFunc=self.ui.zCombo.itemData(self.ui.zCombo.currentIndex())
        eFunc=self.ui.cCombo.itemData(self.ui.cCombo.currentIndex())
        tran=self.ui.logCheckBox.isChecked()
        errTxt=""
        if eFunc is not None:
            errTxt=u" \u00B1 %s"%(self.ui.cCombo.currentText())
        aggtext="%s %s%s"%(self.ui.zCombo.currentText(),"%s",errTxt)
        p.aggPlot(self.model,xfield,yfield,aggFunc,eFunc,self.aggFieldWidget.current(),tran,aggtext,self.legendWidget.currentStacks())
        p.setWindowTitle("%s %s - %s Aggregated Plot" % (self.ui.zCombo.currentText(),self.model.prettyname(xfield),self.model.prettyname(yfield)))
        p.show()
        pass



        
