# datview/ui/plots.py 
# This file contains the code interfacing with matplotlib for drawing all plots in the GUI
# Author Natasha Stander

try:
    from PyQt5 import QtCore
    from PyQt5.QtCore import QObject
    from PyQt5.QtWidgets import QSizePolicy, QMenu, QApplication, QFileDialog, QActionGroup
    from PyQt5.QtGui import QCursor
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
except ImportError as e:
    print(e)
    from PyQt4 import QtCore
    from PyQt4.QtCore import QObject
    from PyQt4.QtGui import QSizePolicy, QMenu, QApplication, QCursor, QFileDialog, QActionGroup
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.mlab
from matplotlib.patches import Rectangle
from matplotlib.colors import LogNorm
from api.filters import BetweenFilter
from scipy.stats import norm


class MyFigure(FigureCanvas):
    def __init__(self,parent=None,flags=0):
        self.fig=Figure()
        FigureCanvas.__init__(self,self.fig)
        self.setParent(parent)
        self.setWindowFlags(QtCore.Qt.WindowFlags(flags))
        self.fig.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.fig.canvas.setFocus()
        self.fig.set_facecolor('white')
        self.plts=[]
        
        FigureCanvas.setMinimumSize(self, 200, 200)
        FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding,QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.fig.canvas.mpl_connect('motion_notify_event',self.onMotion)

    def histogram(self,model,field,axis=None):
        if axis is None:
            axis=self.fig.add_subplot(111)
        p=MyHistogram(model,field,self.fig,axis,self)
        self.plts.append(p)
        return p

    def histogram2D(self,model,xfield,yfield,log=False,axis=None):
        if axis is None:
            axis=self.fig.add_subplot(111)
        p=MyHist2d(model,xfield,yfield,log,self.fig,axis,self)
        self.plts.append(p)
        return p

    def scatter(self,model,xfield,yfield,cfield,axis=None):
        if axis is None:
            axis=self.fig.add_subplot(111)
        p=MyScatter(model,xfield,yfield,cfield,self.fig,axis,self)
        self.plts.append(p)
        return p

    def onMotion(self,event):
        handled=False
        for p in self.plts:
            handled = handled or p.onMotion(event)
        if not handled:
            txt=""
            for p in self.plts:
                t2=p.toolTip(event)
                if t2:
                    txt=t2
            self.setToolTip(txt)

    def onSave(self):
        name=QFileDialog.getSaveFileName(self,'Save Plot',filter='*.png')
        if name is not None:
            self.fig.savefig(name,ext="png")

    def onSaveSVG(self):
        name=QFileDialog.getSaveFileName(self,'Save Plot',filter='*.svg')
        if name is not None:
            self.fig.savefig(name,ext="svg")


class MyPlot(QObject):
    def __init__(self,fig,plt,parent):
        QtCore.QObject.__init__(self,parent)
        self.fig = fig
        self.plt=plt
        self.fig.canvas.mpl_connect('scroll_event',self.onScroll)
        self.fig.canvas.mpl_connect('button_press_event',self.onPress)
        self.fig.canvas.mpl_connect('button_release_event',self.onRelease)

        self.pan=None
        self.sel=None # Derived classes should initialize to Rectangle
        self.fieldfilterX=None # Derived classes should intialize if manageX
        self.fieldfilterY=None # Derived classes should intialize if manageY
        self.selp=None
        self.cb=None # Colorbar

        self.manageX=False
        self.manageY=False

        self.menu=QMenu()
        saveAct=self.menu.addAction("Save PNG")
        saveAct.triggered.connect(parent.onSave)
        saveAct=self.menu.addAction("Save SVG")
        saveAct.triggered.connect(parent.onSaveSVG)
        resetAct=self.menu.addAction("Reset")
        resetAct.triggered.connect(self.onReset)

        drawActionGroup = QActionGroup(self)
        self.drawAll = drawActionGroup.addAction("Draw All (Ignore Selection)")
        self.drawAll.triggered.connect(self.mydraw)
        self.drawAll.setCheckable(True)
        self.drawBoth = drawActionGroup.addAction("Draw All Semi-transparent; Selection Full Color")
        self.drawBoth.triggered.connect(self.mydraw)
        self.drawBoth.setCheckable(True)
        self.drawBoth.setChecked(True)
        self.drawSelection = drawActionGroup.addAction("Draw Selection Only")
        self.drawSelection.triggered.connect(self.mydraw)
        self.drawSelection.setCheckable(True)
        self.datamenu=self.menu.addMenu("Data")
        self.datamenu.addAction(self.drawAll)
        self.datamenu.addAction(self.drawBoth)
        self.datamenu.addAction(self.drawSelection)

        self.range=None
        self.origRange=None

    def initRange(self, xrange,yrange):
        if self.manageX and self.manageY:
            self.origRange=(tuple(xrange),tuple(yrange))
            rangeAct=self.menu.addAction("Set Range to Current Limits")
            rangeAct.triggered.connect(self.onSetRange)

            xrangeAct=self.menu.addAction("Set X Range to Current Limits")
            xrangeAct.triggered.connect(self.onSetXRange)

            yrangeAct=self.menu.addAction("Set Y Range to Current Limits")
            yrangeAct.triggered.connect(self.onSetYRange)
        elif self.manageX:
            self.origRange=tuple(xrange)
            rangeAct=self.menu.addAction("Set Range to Current Limits")
            rangeAct.triggered.connect(self.onSetXRange)
        elif self.manageY:
            self.origRange=tuple(yrange)
            rangeAct=self.menu.addAction("Set Range to Current Limits")
            rangeAct.triggered.connect(self.onSetYRange)
        self.range=self.origRange


    def onSetRange(self):
        self.range=(tuple(self.plt.get_xlim()),tuple(self.plt.get_ylim()))
        self.mydraw()

    def onSetXRange(self):
        if self.manageY:
            self.range=(tuple(self.plt.get_xlim()),self.range[1])
        else:
            self.range=tuple(self.plt.get_xlim())
        self.mydraw(False)

    def onSetYRange(self):
        if self.manageX:
            self.range=(self.range[0],tuple(self.plt.get_ylim()))
        else:
            self.range=tuple(self.plt.get_ylim())
        self.mydraw(False)

    def onReset(self):
        self.range=self.origRange
        self.mydraw(False)
        

    def datadraw(self):
        pass

    def mydraw(self,keeplimits=True):
        if keeplimits:
            xlim = self.plt.get_xlim()
            ylim = self.plt.get_ylim()
        self.plt.cla()
        self.datadraw()
        self.plt.add_patch(self.sel)
        if keeplimits and self.manageX:
            self.plt.set_xlim(xlim)
        if keeplimits and self.manageY:
            self.plt.set_ylim(ylim)
        self.parent().draw()

    def onScroll(self,event):
        xcenter=event.xdata
        ycenter=event.ydata
        x,y,axis = event.x,event.y,event.inaxes

        # Axis scroll
        xAxes,yAxes=self.plt.transAxes.inverted().transform([x,y])
        if xAxes < 0 and xAxes >=-0.2 and yAxes >= 0 and yAxes <=1: # Hover over y axis
            ycenter=self.plt.transData.inverted().transform([0,y])[1]
            axis=self.plt
        if yAxes < 0 and yAxes >=-0.2 and xAxes >= 0 and xAxes <=1: # Hover over x axis
            xcenter=self.plt.transData.inverted().transform([x,0])[0]
            axis=self.plt

        if xcenter is None and ycenter is None or axis != self.plt:
            return
        scale=1
        factor=1.5
        if event.button == 'up':
            scale = factor
        else:
             scale = 1.0/factor
        if scale != 1:
            if self.manageX and xcenter is not None:
                cur_xlim = self.plt.get_xlim()
                self.plt.set_xlim([xcenter - (xcenter - cur_xlim[0]) / scale, xcenter + (cur_xlim[1]-xcenter)/scale ])
            if self.manageY and ycenter is not None:
                cur_ylim = self.plt.get_ylim()
                self.plt.set_ylim([ycenter - (ycenter - cur_ylim[0]) / scale, ycenter + (cur_ylim[1]-ycenter)/scale ])
            if (self.manageX and xcenter is not None) or (self.manageY and ycenter is not None):
                self.parent().draw()

    def onPress(self,event):
        if event.button == 1 and event.xdata is not None and event.ydata is not None and event.inaxes == self.plt:
            if event.key == 'shift' or QtCore.Qt.ShiftModifier & QApplication.keyboardModifiers() :
                self.selp=(event.xdata,event.ydata)
                if self.manageX:
                    self.sel.set_x(event.xdata)
                    self.sel.set_width(0)
                if self.manageY:
                    self.sel.set_y(event.ydata)
                    self.sel.set_height(0)
                if self.manageX or self.manageY:
                    self.sel.set_visible(True)
                    self.parent().draw()
            else:
                self.pan=(event.xdata,event.ydata)
        elif event.button == 3 and event.inaxes == self.plt:
            self.menu.popup(QCursor.pos())

    def onRelease(self,event):
        if self.pan is not None:
            self.pan=None 
        elif self.selp is not None:
            if not self.manageX or not self.manageY:
                self.selp=None # Only managing 0 or  1 axis, clear right away
            if self.manageX:
                if self.sel.get_width() == 0:
                    self.sel.set_visible(False)
                    self.fieldfilterX.setActive(False)
                else:
                    self.fieldfilterX.setRange(self.sel.get_x(),self.sel.get_width() + self.sel.get_x())
                    self.fieldfilterX.setActive(True)
                self.selp=None # In case we were managing two axis, clear here
            if self.manageY:
                if self.sel.get_height() == 0:
                    self.sel.set_visible(False)
                    self.fieldfilterY.setActive(False)
                else:
                    self.fieldfilterY.setRange(self.sel.get_y(),self.sel.get_height() + self.sel.get_y())
                    self.fieldfilterY.setActive(True)
            self.selp=None # Probably unneccessary but make sure this does get cleared
            if self.manageX or self.manageY:
                self.mydraw()

    def onMotion(self,event):
        handled=False
        if event.xdata and event.ydata and event.inaxes == self.plt:
            if self.pan is not None:
                handled=True
                if self.manageX:
                    xlim=self.plt.get_xlim()
                    xlim -= (event.xdata - self.pan[0])
                    self.plt.set_xlim(xlim)
                if self.manageY:
                    ylim=self.plt.get_ylim()
                    ylim -= (event.ydata - self.pan[1])
                    self.plt.set_ylim(ylim)
                if self.manageX or self.manageY:
                    self.parent().draw()
            elif self.selp is not None:
                handled=True
                if self.manageX:
                    if self.selp[0] <= event.xdata:
                        self.sel.set_width(event.xdata - self.selp[0])
                    else:
                        self.sel.set_x(event.xdata)
                        self.sel.set_width(self.selp[0] - event.xdata)
                if self.manageY:
                    if self.selp[1] <= event.ydata:
                        self.sel.set_height(event.ydata - self.selp[1])
                    else:
                        self.sel.set_y(event.ydata)
                        self.sel.set_height(self.selp[1] - event.ydata)
                if self.manageX or self.manageY:
                    self.parent().draw()

    def onFilterChange(self):
        if self.selp is not None:
            return # Selecting is from this plot, wait for both filters to update so we don't clear variables
        ylim = self.plt.get_ylim()
        xlim = self.plt.get_xlim()
        self.sel.set_x(xlim[0])
        self.sel.set_y(ylim[0])
        self.sel.set_width(xlim[1]-xlim[0])
        self.sel.set_height(ylim[1]-ylim[0])

        if self.manageX:
            self.sel.set_x(self.fieldfilterX.minimum)
            self.sel.set_width(self.fieldfilterX.maximum-self.fieldfilterX.minimum)
            self.sel.set_visible(self.fieldfilterX.isActive())
        if self.manageY:
            self.sel.set_y(self.fieldfilterY.minimum)
            self.sel.set_height(self.fieldfilterY.maximum-self.fieldfilterY.minimum)
            self.sel.set_visible(self.fieldfilterY.isActive() or (self.fieldfilterX is not None and self.fieldfilterX.isActive()))
        self.parent().draw()

    def xlabels(self,model,field,distribute=False):
        if model.hasLabels(field):
            lbls=model.labels(field)
            ticks=model.labelints(field)
            if distribute:
                ticks= ticks.astype(float) + 0.5
            self.plt.set_xticks(ticks)
            self.plt.set_xticklabels(lbls)
        else:
            self.plt.locator_params(axis='x', nbins=model.cfg.numXticks)

    def ylabels(self,model,field,distribute=False):
        if model.hasLabels(field):
            lbls=model.labels(field)
            ticks=model.labelints(field)
            if distribute:
                ticks= ticks.astype(float) + 0.5
            self.plt.set_yticks(ticks)
            self.plt.set_yticklabels(lbls)


class MyHistogram(MyPlot):
    def __init__(self,model,field,fig,plt,parent):
        MyPlot.__init__(self,fig,plt,parent)
        self.bins=int(model.cfg.hist1Dbins)
        self.model=model
        self.field=field

        self.fig.canvas.mpl_connect('key_press_event',self.onKey)

        self.manageX=True
        self.fieldfilterX=self.model.selectionFilter(self.field)
        self.fieldfilterX.modelchange.connect(self.onFilterChange)
        self.model.filterchange.connect(self.mydraw)
        self.model.filterModelChange.connect(self.onFilterModelChange)

        self.sel=Rectangle((self.fieldfilterX.minimum,0),self.fieldfilterX.maximum-self.fieldfilterX.minimum,0,alpha=0.3,color='r')
        self.sel.set_visible(self.fieldfilterX.isActive())

        self.mu=None
        self.sigma=None
        if not self.model.isCategorical(self.field):
            self.initRange((self.model.fieldmin(self.field),self.model.fieldmax(self.field)),None)

        self.plt.get_yaxis().set_visible(False)
        self.dcache=None
        self.mydraw(False)

    def datadraw(self):
        title=self.model.prettyname(self.field)
        fmt=" %0.2f "+u"\u00B1"+ " %0.2f"
        drawBoth=self.model.isFiltered() and self.drawBoth.isChecked()
        if self.model.isCategorical(self.field):
            if self.dcache is None:
                self.dcache=np.unique(self.model.data[self.field],return_counts=True)
            if drawBoth:
                self.plt.bar(self.dcache[0],self.dcache[1],color='black',alpha=0.5,edgecolor="none",align='center')
                fcnts=np.unique(self.model.filtered[self.field],return_counts=True)
                self.plt.bar(fcnts[0],fcnts[1],color='black',align='center')
            elif self.drawSelection.isChecked():
                fcnts=np.unique(self.model.filtered[self.field],return_counts=True)
                self.plt.bar(fcnts[0],fcnts[1],color='black',align='center')
            else:
                self.plt.bar(self.dcache[0],self.dcache[1],color='black',align='center')
        else:
            if drawBoth:
                b=self.plt.hist(self.model.data[self.field],bins=self.bins,color='black',alpha=0.5,edgecolor="none",
                    range=self.range)[1]
                self.plt.hist(self.model.filtered[self.field],bins=b,color='black',
                    range=self.range)
            elif self.drawSelection.isChecked():
                b=self.plt.hist(self.model.filtered[self.field],bins=self.bins,color='black',
                    range=self.range)[1]
            else:
                b=self.plt.hist(self.model.data[self.field],bins=self.bins,color='black',
                    range=self.range)[1]
            if self.mu is not None:
                y=matplotlib.mlab.normpdf(np.array(b),self.mu,self.sigma)
                self.plt.plot(b,y/np.max(y)*self.plt.get_ylim()[1]*0.95,'r',linewidth=2)
                title += fmt % (self.mu,self.sigma)
        self.xlabels(self.model,self.field)
        self.plt.set_title(title)
        self.sel.set_height(self.plt.get_ylim()[1])

    def onKey(self,event):
        if event.key == '+' or event.key == '=':
            self.bins *=2
            self.mydraw()
        if event.key == '-':
            self.bins =int(self.bins/2)
            self.mydraw()
        if event.key == 'ctrl+f':
            if self.mu is None:
                self.calcFit()
            else:
                self.clearFit()


    def calcFit(self):
        # Always fit filtered (if not filtering, will be full model)
        dt=self.model.filtered[self.field]
        dt = dt[dt != -1] # But don't use empty
        if len(dt):
            (self.mu,self.sigma)=norm.fit(dt)
            self.mydraw()
        else:
            self.clearFit()

    def clearFit(self):
        self.mu = None
        self.sigma = None
        self.mydraw()

    def toolTip(self,event):
        txt=""
        if event.xdata is not None and event.ydata is not None and event.inaxes == self.plt:
            txt=str(event.xdata)
            if self.model.isCategorical(self.field):
                bar = int(np.round(event.xdata))
                txt=self.model.stringValue(self.field,bar)
        return txt

    def onFilterModelChange(self):
        self.fieldfilterX.modelchange.disconnect(self.onFilterChange)
        self.fieldfilterX=self.model.selectionFilter(self.field)
        self.fieldfilterX.modelchange.connect(self.onFilterChange)
        self.onFilterChange()

    def onReset(self):
        self.bins=int(self.model.cfg.hist1Dbins)
        self.range=self.origRange
        self.mydraw(False)
            

class MyScatter(MyPlot):
    def __init__(self,model,xfield,yfield,cfield,fig,plt,parent):
        MyPlot.__init__(self,fig,plt,parent)
        self.model=model
        self.xfield=xfield
        self.yfield=yfield
        self.cfield=cfield

        self.manageX=True
        self.fieldfilterX=self.model.selectionFilter(self.xfield)
        self.fieldfilterX.modelchange.connect(self.onFilterChange)

        self.manageY=True
        self.fieldfilterY=self.model.selectionFilter(self.yfield)
        self.fieldfilterY.modelchange.connect(self.onFilterChange)

        self.vmin=None
        self.vmax=None

        self.model.filterchange.connect(self.mydraw)
        self.model.filterModelChange.connect(self.onFilterModelChange)
        self.plt.set_xlim((self.model.fieldmin(self.xfield),self.model.fieldmax(self.xfield)))
        self.plt.set_ylim((self.model.fieldmin(self.yfield),self.model.fieldmax(self.yfield)))

        self.sel=Rectangle((0,0),0,0,color='r',fill=False)
        self.onFilterChange() # Let this function worry about actual bounds, we just cared about color and fill

        self.mydraw()

    def datadraw(self):
        xAll=self.model.data[self.xfield]
        xFiltered=self.model.filtered[self.xfield]

        cAll="black"
        cFiltered="black"
        cm=None
        marker=self.model.cfg.scattermarker
        if self.cfield is not None:
            cAll=self.model.data[self.cfield]
            cFiltered=self.model.filtered[self.cfield]
            cm=plt.cm.get_cmap(self.model.cfg.scattercmap)
            if self.vmin is None:
                self.vmin=self.model.fieldmin(self.cfield)
            if self.vmax is None:
                self.vmax=self.model.fieldmax(self.cfield)

        if self.model.isFiltered() and self.drawBoth.isChecked():
            self.plt.scatter(self.model.data[self.xfield],self.model.data[self.yfield],c=cAll,alpha=0.3,cmap=cm,vmin=self.vmin,vmax=self.vmax,marker=marker,linewidths=self.model.cfg.scatterlinewidth,s=self.model.cfg.scattersize)
            sc=self.plt.scatter(self.model.filtered[self.xfield],self.model.filtered[self.yfield],c=cFiltered,cmap=cm,vmin=self.vmin,vmax=self.vmax,marker=marker,linewidths=self.model.cfg.scatterlinewidth,s=self.model.cfg.scattersize)
        elif self.drawSelection.isChecked():
            sc=self.plt.scatter(self.model.filtered[self.xfield],self.model.filtered[self.yfield],c=cFiltered,cmap=cm,vmin=self.vmin,vmax=self.vmax,marker=marker,linewidths=self.model.cfg.scatterlinewidth,s=self.model.cfg.scattersize)
        else:
            sc=self.plt.scatter(self.model.data[self.xfield],self.model.data[self.yfield],c=cAll,cmap=cm,vmin=self.vmin,vmax=self.vmax,marker=marker,linewidths=self.model.cfg.scatterlinewidth,s=self.model.cfg.scattersize)


        self.plt.set_xlabel(self.model.prettyname(self.xfield))
        self.plt.set_ylabel(self.model.prettyname(self.yfield))
        if self.cfield is not None:
            self.plt.set_title(self.model.prettyname(self.cfield))
        if self.cfield is not None and self.cb is None:
            self.cb=self.fig.colorbar(sc,ax=self.plt)

        self.xlabels(self.model,self.xfield)
        self.ylabels(self.model,self.yfield)

    def onReset(self,event):
        xrange=(self.model.fieldmin(self.xfield),self.model.fieldmax(self.xfield))
        yrange=(self.model.fieldmin(self.yfield),self.model.fieldmax(self.yfield))
        if self.drawSelection.isChecked() and self.model.isFiltered():
            xrange=(np.min(self.model.filtered[self.xfield]),np.max(self.model.filtered[self.xfield]))
            yrange=(np.min(self.model.filtered[self.yfield]),np.max(self.model.filtered[self.yfield]))
        self.plt.set_xlim(xrange)
        self.plt.set_ylim(yrange)
        self.mydraw()

    def toolTip(self,event):
        txt=""
        if event.xdata is not None and event.ydata is not None and event.inaxes == self.plt:
            if self.model.isCategorical(self.xfield):
                xtxt=self.model.stringValue(self.xfield,int(np.round(event.xdata)))
            else:
                xtxt="%.4f"%(event.xdata)
            if self.model.isCategorical(self.yfield):
                ytxt=self.model.stringValue(self.yfield,int(np.round(event.ydata)))
            else:
                ytxt="%.4f"%(event.ydata)
            txt="%s,%s"%(xtxt,ytxt)
        return txt

    def onFilterModelChange(self):
        self.fieldfilterX.modelchange.disconnect(self.onFilterChange)
        self.fieldfilterX=self.model.selectionFilter(self.xfield)
        self.fieldfilterX.modelchange.connect(self.onFilterChange)

        self.fieldfilterY.modelchange.disconnect(self.onFilterChange)
        self.fieldfilterY=self.model.selectionFilter(self.yfield)
        self.fieldfilterY.modelchange.connect(self.onFilterChange)
        self.onFilterChange()

class MyHist2d(MyPlot):
    def __init__(self,model,xfield,yfield,log,fig,plt,parent):
        MyPlot.__init__(self,fig,plt,parent)
        self.model=model
        self.xfield=xfield
        self.yfield=yfield
        self.xbins=int(model.cfg.hist2Dbins)
        self.ybins=int(model.cfg.hist2Dbins)
        self.log=log

        self.fig.canvas.mpl_connect('key_press_event',self.onKey)

        self.manageX=True
        self.fieldfilterX=self.model.selectionFilter(self.xfield)
        self.fieldfilterX.modelchange.connect(self.onFilterChange)

        self.manageY=True
        self.fieldfilterY=self.model.selectionFilter(self.yfield)
        self.fieldfilterY.modelchange.connect(self.onFilterChange)

        self.model.filterchange.connect(self.mydraw)
        self.model.filterModelChange.connect(self.onFilterModelChange)
        self.plt.set_xlim((self.model.fieldmin(self.xfield),self.model.fieldmax(self.xfield)))
        self.plt.set_ylim((self.model.fieldmin(self.yfield),self.model.fieldmax(self.yfield)))

        self.sel=Rectangle((0,0),0,0,color='r',fill=False)
        self.onFilterChange() # Let this function worry about actual bounds, we just cared about color and fill
        self.H=None
        self.xedges=None
        self.yedges=None

        xshift=0
        if self.model.isCategorical(self.xfield):
            xshift = 1

        yshift=0
        if self.model.isCategorical(self.yfield):
            yshift = 1

        self.initRange((self.model.fieldmin(self.xfield),self.model.fieldmax(self.xfield)+xshift),
                                 (self.model.fieldmin(self.yfield),self.model.fieldmax(self.yfield)+yshift))
        self.plt.set_xlim(self.range[0])
        self.plt.set_ylim(self.range[1])

        self.drawBoth.setVisible(False)
        self.drawSelection.setChecked(True)

        self.mydraw()

    def datadraw(self):
        drawfiltered=self.drawSelection.isChecked()
        model=self.model.filtered
        if not drawfiltered:
            model = self.model.data
        b=[self.xbins,self.ybins]
        if self.model.isCategorical(self.xfield):
            edges = self.model.labelints(self.xfield)
            xemin = np.searchsorted(edges,self.range[0][0])
            xemax = np.searchsorted(edges,self.range[0][1])
            xedges=edges[xemin:xemax]
            xedges=np.append(xedges,np.max(xedges)+1)
            b[0]=xedges
        if self.model.isCategorical(self.yfield):
            edges = self.model.labelints(self.yfield)
            yemin = np.searchsorted(edges,self.range[1][0])
            yemax = np.searchsorted(edges,self.range[1][1])
            yedges=edges[yemin:yemax]
            yedges=np.append(yedges,np.max(yedges)+1)
            b[1]=yedges    
        self.H,self.xedges,self.yedges = np.histogram2d(model[self.xfield],model[self.yfield],bins=b,
                          range=self.range)
        norm=None
        if self.log:
            norm=LogNorm()
        h=self.H
        if self.model.cfg.histAlwaysMask0:
            h=np.ma.masked_values(h,0)
        sc=self.plt.pcolormesh(self.xedges,self.yedges,np.transpose(h),cmap=plt.cm.get_cmap(self.model.cfg.hist2dcmap),norm=norm)
        if self.cb is None:
            self.cb=self.fig.colorbar(sc,ax=self.plt)
        else:
            self.cb.on_mappable_changed(sc)

        self.plt.set_xlabel(self.model.prettyname(self.xfield))
        self.plt.set_ylabel(self.model.prettyname(self.yfield))

        self.xlabels(self.model,self.xfield,True)
        self.ylabels(self.model,self.yfield,True)

    def onKey(self,event):
        if event.key == '+' or event.key == '=':
            self.xbins *=2
            self.ybins *=2
            self.mydraw()
        if event.key == '-':
            self.xbins =int(self.xbins/2)
            if self.xbins < 1:
                self.xbins = 1
            self.ybins =int(self.ybins/2)
            if self.ybins < 1:
                self.ybins = 1
            self.mydraw()

    def onReset(self,event):
        self.xbins=int(self.model.cfg.hist2Dbins)
        self.ybins=int(self.model.cfg.hist2Dbins)
        self.range=self.origRange
        self.plt.set_xlim(self.range[0])
        self.plt.set_ylim(self.range[1])
        self.mydraw()

    def toolTip(self,event):
        txt=""
        if event.xdata is not None and event.ydata is not None and self.H is not None and event.inaxes == self.plt:
            xbin=np.searchsorted(self.xedges,event.xdata)
            ybin=np.searchsorted(self.yedges,event.ydata)
            if xbin > 0 and xbin < len(self.xedges) and ybin > 0 and ybin < len(self.yedges):
                if self.model.isCategorical(self.xfield):
                    xtxt=self.model.stringValue(self.xfield,xbin-1)
                else:
                    xtxt="%.4f-%.4f"%(self.xedges[xbin-1],self.xedges[xbin])
                if self.model.isCategorical(self.yfield):
                    ytxt=self.model.stringValue(self.yfield,ybin-1)
                else:
                    ytxt="%.4f-%.4f"%(self.yedges[ybin-1],self.yedges[ybin])
                txt="%s,%s,%i"%(xtxt,ytxt,self.H[xbin-1,ybin-1])
        return txt

    def onFilterModelChange(self):
        self.fieldfilterX.modelchange.disconnect(self.onFilterChange)
        self.fieldfilterX=self.model.selectionFilter(self.xfield)
        self.fieldfilterX.modelchange.connect(self.onFilterChange)

        self.fieldfilterY.modelchange.disconnect(self.onFilterChange)
        self.fieldfilterY=self.model.selectionFilter(self.yfield)
        self.fieldfilterY.modelchange.connect(self.onFilterChange)
        self.onFilterChange()








            
