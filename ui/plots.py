from PyQt4 import QtGui, QtCore
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

class MyFigure(FigureCanvas):
    def __init__(self,parent=None):
        self.fig=Figure()
        FigureCanvas.__init__(self,self.fig)
        self.setParent(parent)
        self.fig.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.fig.canvas.setFocus()
        self.plt=self.fig.add_subplot(111)
        self.fig.set_facecolor('white')
        
        FigureCanvas.setMinimumSize(self, 200, 200)
        FigureCanvas.setSizePolicy(self,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class MyHistogram(MyFigure):
    def __init__(self,model,field,parent=None):
        MyFigure.__init__(self,parent)
        self.bins=int(64)
        self.model=model
        self.field=field
        self.panx0=None
        self.sel=Rectangle((0,0),0,0,alpha=0.3,color='r')
        self.sel.set_visible(False)
        self.selx0=None

        self.fig.canvas.mpl_connect('key_press_event',self.onKey)
        self.fig.canvas.mpl_connect('scroll_event',self.onScroll)
        self.fig.canvas.mpl_connect('button_press_event',self.onPress)
        self.fig.canvas.mpl_connect('button_release_event',self.onRelease)
        self.fig.canvas.mpl_connect('motion_notify_event',self.onMotion)
        self.model.filterchange.connect(self.mydraw)

        self.plt.get_yaxis().set_visible(False)
        self.plt.hist(self.model.data[self.field],bins=self.bins,color='black')
        self.mydraw()

    def mydraw(self):
        xlim = self.plt.get_xlim()
        self.plt.cla()
        self.plt.set_title(self.model.prettyname(self.field))
        self.plt.add_patch(self.sel)
        if self.model.isFiltered():
            b=self.plt.hist(self.model.data[self.field],bins=self.bins,color='black',alpha=0.5,edgecolor="none")[1]
            self.plt.hist(self.model.filtered[self.field],bins=b,color='black')
        else:
            self.plt.hist(self.model.data[self.field],bins=self.bins,color='black')
        self.plt.set_xlim(xlim)
        self.draw()

    def onKey(self,event):
        if event.key == '+' or event.key == '=':
            self.bins *=2
            self.mydraw()
        if event.key == '-':
            self.bins =int(self.bins/2)
            self.mydraw()

    def onScroll(self,event):
        scale=1
        factor=1.5
        if event.button == 'up':
            scale = 1.0/factor
        else:
            scale = factor
        if scale != 1:
            cur_xlim = self.plt.get_xlim()
            self.plt.set_xlim([event.xdata - (event.xdata - cur_xlim[0]) / scale, event.xdata + (cur_xlim[1]-event.xdata)/scale ])
            self.draw()

    def onPress(self,event):
        if event.button == 1:
            if event.key == 'shift':
                self.selx0=event.xdata
                self.sel.set_x(event.xdata)
                self.sel.set_width(0)
                self.sel.set_height(self.plt.get_ylim()[1])
                self.sel.set_visible(True)
                self.draw()
            else:
                self.panx0=event.xdata

    def onRelease(self,event):
        if self.panx0 is not None:
            self.panx0=None 
        elif self.selx0 is not None:
            self.selx0=None
            if self.sel.get_width() == 0:
                self.sel.set_visible(False)
                self.model.clearFilter(self.field)
            else:
                self.model.addFilter(self.field,self.sel.get_x(),self.sel.get_width() + self.sel.get_x())
            self.mydraw()

    def onMotion(self,event):
        if self.panx0 is not None and event.xdata:
            xlim=self.plt.get_xlim()
            xlim -= (event.xdata - self.panx0)
            self.plt.set_xlim(xlim)
            self.draw()
        elif self.selx0 is not None and event.xdata:
            if self.selx0 <= event.xdata:
                self.sel.set_width(event.xdata - self.selx0)
            else:
                self.sel.set_x(event.xdata)
                self.sel.set_width(self.selx0 - event.xdata)
            self.draw()

            
