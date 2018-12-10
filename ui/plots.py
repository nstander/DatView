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

    def pixelPlot(self,model,xfield,yfield,cfield,axis=None):
        if axis is None:
            axis=self.fig.add_subplot(111)
        p=MyPixelPlot(model,xfield,yfield,cfield,self.fig,axis,self)
        self.plts.append(p)
        return p

    def image(self,idata,axis=None):
        if axis is None:
            axis=self.fig.add_subplot(111)
        p=MyImage(idata,self.fig,axis,self)
        self.plts.append(p)
        return p

    def staticScatter(self,data,cfg,title,axis=None):
        if axis is None:
            axis=self.fig.add_subplot(111)
        p=MyScatterStatic(data,cfg,title,self.fig,axis,self)
        self.plts.append(p)
        return p

    def aggPlot(self,model,xfield,yfield,aggFunc,errFunc,partitions,tranpose,aggText,legend,axis=None):
        if axis is None:
            axis=self.fig.add_subplot(111)
        p=MyAggPlot(model,xfield,yfield,aggFunc,errFunc,partitions, tranpose,aggText,legend,self.fig,axis,self)
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
        self.legendActionGroup=None

        self.range=None
        self.origRange=None

    def legendMenu(self):
        self.legendActionGroup=QActionGroup(self)
        legMenu=self.menu.addMenu("Legend")
        legInit=None

        legOpt = self.legendActionGroup.addAction("None")
        legOpt.triggered.connect(self.mydraw)
        legOpt.setCheckable(True)
        legOpt.setChecked(legInit is None)
        legOpt.setData(None)
        legMenu.addAction(legOpt)        

        legendOpts=['best','upper right','upper left','lower left','lower right','right','center left','center right','lower center','upper center','center']
        for i,opt in enumerate(legendOpts):
            legOpt = self.legendActionGroup.addAction(opt)
            legOpt.triggered.connect(self.mydraw)
            legOpt.setCheckable(True)
            legOpt.setChecked(i==legInit)
            legOpt.setData(i)
            legMenu.addAction(legOpt)
        

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
        if self.sel is not None:
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
                if self.manageX and self.fieldfilterX is not None:
                    self.sel.set_x(event.xdata)
                    self.sel.set_width(0)
                if self.manageY and self.fieldfilterY is not None:
                    self.sel.set_y(event.ydata)
                    self.sel.set_height(0)
                if (self.manageX and self.fieldfilterX is not None) or \
                   (self.manageY and self.fieldfilterY is not None):
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
            if self.manageX and self.fieldfilterX is not None:
                if self.sel.get_width() == 0:
                    self.sel.set_visible(False)
                    self.fieldfilterX.setActive(False)
                else:
                    self.fieldfilterX.setRange(self.sel.get_x(),self.sel.get_width() + self.sel.get_x())
                    self.fieldfilterX.setActive(True)
                self.selp=None # In case we were managing two axis, clear here
            if self.manageY and self.fieldfilterY is not None:
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

        if self.manageX and self.fieldfilterX is not None:
            self.sel.set_x(self.fieldfilterX.minimum)
            self.sel.set_width(self.fieldfilterX.maximum-self.fieldfilterX.minimum)
            self.sel.set_visible(self.fieldfilterX.isActive())
        if self.manageY and self.fieldfilterY is not None:
            self.sel.set_y(self.fieldfilterY.minimum)
            self.sel.set_height(self.fieldfilterY.maximum-self.fieldfilterY.minimum)
            self.sel.set_visible(self.fieldfilterY.isActive() or (self.fieldfilterX is not None and self.fieldfilterX.isActive()))
        self.parent().draw()

    def xlabels(self,model,field,distribute=False):
        if model.isCategorical(field):
            lbls=model.labels(field)
            ticks=model.labelints(field)
            if distribute:
                ticks= ticks.astype(float) + 0.5
            self.plt.set_xticks(ticks)
            self.plt.set_xticklabels(lbls)
        else:
            self.plt.locator_params(axis='x', nbins=model.cfg.numXticks)

    def ylabels(self,model,field,distribute=False):
        if model.isCategorical(field):
            lbls=model.labels(field)
            ticks=model.labelints(field)
            if distribute:
                ticks= ticks.astype(float) + 0.5
            self.plt.set_yticks(ticks)
            self.plt.set_yticklabels(lbls)


class MyHistogram(MyPlot):
    def __init__(self,model,field,fig,plt,parent):
        MyPlot.__init__(self,fig,plt,parent)
        self.legendMenu()
        self.bins=int(model.cfg.hist1Dbins)
        self.model=model
        self.field=field

        self.fig.canvas.mpl_connect('key_press_event',self.onKey)

        self.manageX=True
        self.fieldfilterX=self.model.selectionFilter(self.field)
        self.fieldfilterX.modelchange.connect(self.onFilterChange)
        self.model.filterchange.connect(self.mydraw)
        self.model.filterModelChange.connect(self.onFilterModelChange)
        self.model.stackChange.connect(self.mydraw)

        self.sel=Rectangle((self.fieldfilterX.minimum,0),self.fieldfilterX.maximum-self.fieldfilterX.minimum,0,alpha=0.3,color='r')
        self.sel.set_visible(self.fieldfilterX.isActive())

        self.mu=None
        self.sigma=None
        self.edges=None
        self.cnts=None
        self.labels=None
        if not self.model.isCategorical(self.field):
            self.initRange((self.model.fieldmin(self.field),self.model.fieldmax(self.field)),None)

        self.plt.get_yaxis().set_visible(False)
        self.dmin=None
        self.dmax=None
        if self.model.isCategorical(self.field):
            self.dmin = np.min(self.model.data[self.field])
            self.dmax = np.max(self.model.data[self.field])
            # Categorical variables must be integers (or mapped to integers like groups and strings are)
            assert np.equal(np.mod(self.dmin,1),0) and np.equal(np.mod(self.dmax,1),0)
            self.dmin = int(self.dmin)
            self.dmax = int(self.dmax)

        act=self.menu.addAction("Fit Histogram (Ctrl+F)")
        act.triggered.connect(self.calcFit)
        act=self.menu.addAction("Clear Fit (Ctrl+F)")
        act.triggered.connect(self.clearFit)
        act=self.menu.addAction("Increase Bins (+)")
        act.triggered.connect(self.increaseBins)
        act=self.menu.addAction("Decrease Bins (-)")
        act.triggered.connect(self.decreaseBins)

        self.mydraw(False)

    def stackedDraw(self,data,alpha):
        self.edges=None
        if len(data[0]): # Have array to plot
            self.labels=data[2]
            if self.model.isCategorical(self.field):
                self.edges=np.arange(self.dmin -0.5, self.dmax + 1.5)
                self.cnts=np.zeros((len(data[0]),self.dmax-self.dmin+1))
                for i in range(len(data[0])):
                    cnts=np.unique(data[0][i],return_counts=True)
                    self.plt.bar(cnts[0],cnts[1],color=data[1][i],alpha=alpha,
                                 edgecolor="none",align="center",bottom=self.cnts[i,cnts[0].astype(int)-self.dmin],linewidth=0,label=data[2][i])
                    self.cnts[i:,cnts[0].astype(int)-self.dmin]+=cnts[1]
            else:
                self.cnts,self.edges,_=self.plt.hist(data[0],bins=self.bins,color=data[1],range=self.range,
                              alpha=alpha,histtype="barstacked",linewidth=0,rwidth=1,label=data[2])
                self.cnts=np.array(self.cnts)
        return self.edges

    def datadraw(self):
        title=self.model.prettyname(self.field)
        fmt=" %0.2f "+u"\u00B1"+ " %0.2f"
        drawBoth=self.model.isFiltered() and self.drawBoth.isChecked()
        data=self.model.stackedDataCol(self.field,self.drawSelection.isChecked(),"black")
        alpha=1
        if drawBoth:
            alpha=0.5
        edges=self.stackedDraw(data,alpha)
        if drawBoth:
            self.stackedDraw(self.model.stackedDataCol(self.field,True,"black"),1)

        if edges is not None and self.mu is not None:
            y=matplotlib.mlab.normpdf(np.array(edges),self.mu,self.sigma)
            self.plt.plot(edges,y/np.max(y)*self.plt.get_ylim()[1]*0.95,'r',linewidth=2)
            title += fmt % (self.mu,self.sigma)

        self.xlabels(self.model,self.field)
        self.plt.set_title(title)
        self.sel.set_height(self.plt.get_ylim()[1])
        legendPos=self.legendActionGroup.checkedAction().data()
        if legendPos is not None:
            self.plt.legend(loc=legendPos) 

    def onKey(self,event):
        if event.key == '+' or event.key == '=':
            self.increaseBins()
        if event.key == '-':
            self.decreaseBins()
        if event.key == 'ctrl+f':
            if self.mu is None:
                self.calcFit()
            else:
                self.clearFit()

    def increaseBins(self):
        self.bins *=2
        self.mydraw()

    def decreaseBins(self):
        self.bins =int(self.bins/2)
        if self.bins == 0:
            self.bins=1
        self.mydraw()

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
            if self.edges is not None:
                bin=np.searchsorted(self.edges,event.xdata)
                if bin > 0 and bin < len(self.edges):
                    if self.model.isCategorical(self.field):
                        txt=self.model.stringValue(self.field,np.round(event.xdata))
                    else:
                        txt="%.4f-%.4f"%(self.edges[bin-1],self.edges[bin])
                    cnttxt=""
                    if len(self.cnts.shape) > 1:
                        for i in range(len(self.labels)-1,0,-1):
                            cnttxt+="\n%s : %i" %(self.labels[i],self.cnts[i,bin-1]-self.cnts[i-1,bin-1])
                        cnttxt+="\n%s : %i" %(self.labels[0],self.cnts[0,bin-1])
                    else:
                        cnttxt="\n%i"%self.cnts[bin-1]
                    txt="%s%s"%(txt,cnttxt)
            if txt=="":
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
        cAll="black"
        cFiltered="black"
        cm=None
        marker=self.model.cfg.scattermarker
        if self.cfield is not None:
            cAll=self.model.datacol(self.cfield)
            cFiltered=self.model.filtered[self.cfield]
            cm=plt.cm.get_cmap(self.model.cfg.scattercmap)
            if self.vmin is None:
                self.vmin=self.model.fieldmin(self.cfield)
            if self.vmax is None:
                self.vmax=self.model.fieldmax(self.cfield)

        if self.model.isFiltered() and self.drawBoth.isChecked():
            self.plt.scatter(self.model.datacol(self.xfield),self.model.datacol(self.yfield),c=cAll,alpha=0.3,cmap=cm, vmin=self.vmin,vmax=self.vmax,marker=marker,linewidths=self.model.cfg.scatterlinewidth,s=self.model.cfg.scattersize)
            sc=self.plt.scatter(self.model.filtered[self.xfield],self.model.filtered[self.yfield],c=cFiltered,cmap=cm,vmin=self.vmin,vmax=self.vmax,marker=marker,linewidths=self.model.cfg.scatterlinewidth,s=self.model.cfg.scattersize)
        elif self.drawSelection.isChecked():
            sc=self.plt.scatter(self.model.filtered[self.xfield],self.model.filtered[self.yfield],c=cFiltered,cmap=cm,vmin=self.vmin,vmax=self.vmax,marker=marker,linewidths=self.model.cfg.scatterlinewidth,s=self.model.cfg.scattersize)
        else:
            sc=self.plt.scatter(self.model.datacol(self.xfield),self.model.datacol(self.yfield),c=cAll,cmap=cm,
vmin=self.vmin,vmax=self.vmax,marker=marker,linewidths=self.model.cfg.scatterlinewidth,s=self.model.cfg.scattersize)


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
        self.log=self.menu.addAction("Log Color Scale")
        self.log.setCheckable(True)
        self.log.setChecked(log)
        self.log.toggled.connect(self.mydraw)
        act=self.menu.addAction("Increase Bins (+)")
        act.triggered.connect(self.increaseBins)
        act=self.menu.addAction("Decrease Bins (-)")
        act.triggered.connect(self.decreaseBins)

        self.mydraw()

    def datadraw(self):
        drawfiltered=self.drawSelection.isChecked()
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
        if drawfiltered:
            self.H,self.xedges,self.yedges = np.histogram2d(self.model.filtered[self.xfield],self.model.filtered[self.yfield],bins=b,
                              range=self.range)
        else:
            self.H,self.xedges,self.yedges = np.histogram2d(self.model.datacol(self.xfield),self.model.datacol(self.yfield),bins=b,
                              range=self.range)

        norm=None
        if self.log.isChecked():
            norm=LogNorm()
        h=self.H
        if self.model.cfg.histAlwaysMask0:
            h=np.ma.masked_values(h,0)
        sc=self.plt.pcolormesh(self.xedges,self.yedges,np.transpose(h),cmap=plt.cm.get_cmap(self.model.cfg.hist2dcmap),norm=norm)
        if self.cb is None:
            self.cb=self.fig.colorbar(sc,ax=self.plt)
        else:
            self.cb.set_norm(norm)
            self.cb.on_mappable_changed(sc)
            self.cb.update_normal(sc)

        self.plt.set_xlabel(self.model.prettyname(self.xfield))
        self.plt.set_ylabel(self.model.prettyname(self.yfield))

        self.xlabels(self.model,self.xfield,True)
        self.ylabels(self.model,self.yfield,True)

    def onKey(self,event):
        if event.key == '+' or event.key == '=':
            self.increaseBins()
        if event.key == '-':
            self.decreaseBins()

    def increaseBins(self):
        self.xbins *=2
        self.ybins *=2
        self.mydraw()

    def decreaseBins(self):
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
                txt="%s,%s\n%i"%(xtxt,ytxt,self.H[xbin-1,ybin-1])
        return txt

    def onFilterModelChange(self):
        self.fieldfilterX.modelchange.disconnect(self.onFilterChange)
        self.fieldfilterX=self.model.selectionFilter(self.xfield)
        self.fieldfilterX.modelchange.connect(self.onFilterChange)

        self.fieldfilterY.modelchange.disconnect(self.onFilterChange)
        self.fieldfilterY=self.model.selectionFilter(self.yfield)
        self.fieldfilterY.modelchange.connect(self.onFilterChange)
        self.onFilterChange()

class MyPixelPlot(MyPlot):
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

        self.sel=Rectangle((0,0),0,0,color='r',fill=False)
        self.onFilterChange() # Let this function worry about actual bounds, we just cared about color and fill

        self.drawBoth.setVisible(False)
        self.drawSelection.setChecked(True)

        self.mydraw(False)

    def datadraw(self):
        drawfiltered=self.drawSelection.isChecked()

        xmax=int(np.max(self.model.datacol(self.xfield)))
        ymax=int(np.max(self.model.datacol(self.yfield)))

        self.cdat=np.ones((ymax+1,xmax+1))*-1
        if drawfiltered:
            valid=(self.model.filtered[self.xfield] >=0) & (self.model.filtered[self.yfield] >= 0)
            self.cdat[self.model.filtered[self.yfield][valid],self.model.filtered[self.xfield][valid]] = self.model.filtered[self.cfield][valid]
        else:
            valid=(self.model.datacol(self.xfield) >=0) & (self.model.datacol(self.yfield) >= 0)
            self.cdat[self.model.datacol(self.yfield)[valid],self.model.datacol(self.xfield)[valid]] = self.model.datacol(self.cfield)[valid]

        if self.vmin is None:
            self.vmin=self.model.fieldmin(self.cfield)
        if self.vmax is None:
            self.vmax=self.model.fieldmax(self.cfield)

        p=self.plt.pcolormesh(np.ma.masked_values(self.cdat,-1),cmap=plt.cm.get_cmap(self.model.cfg.pixelcmap),vmin=self.vmin,vmax=self.vmax)

        if self.cb is None:
            self.cb=self.fig.colorbar(p,ax=self.plt)
        else:
            self.cb.on_mappable_changed(p)
        self.plt.set_aspect('equal')

        self.plt.set_xlabel(self.model.prettyname(self.xfield))
        self.plt.set_ylabel(self.model.prettyname(self.yfield))
        self.plt.set_title(self.model.prettyname(self.cfield))


    def onReset(self,event):
        self.mydraw(False)

    def toolTip(self,event):
        txt=""
        if event.xdata is not None and event.ydata is not None and self.cdat is not None and event.inaxes == self.plt:
            x=int(event.xdata)
            y=int(event.ydata)
            if x >= 0 and x < self.cdat.shape[1] and y >= 0 and y < self.cdat.shape[0]:
                txt="%0.2f (%i,%i)" % (self.cdat[y,x],x,y)
        return txt

    def onFilterModelChange(self):
        self.fieldfilterX.modelchange.disconnect(self.onFilterChange)
        self.fieldfilterX=self.model.selectionFilter(self.xfield)
        self.fieldfilterX.modelchange.connect(self.onFilterChange)

        self.fieldfilterY.modelchange.disconnect(self.onFilterChange)
        self.fieldfilterY=self.model.selectionFilter(self.yfield)
        self.fieldfilterY.modelchange.connect(self.onFilterChange)
        self.onFilterChange()


class MyImage(MyPlot):
    def __init__(self,idata,fig,plt,parent):
        MyPlot.__init__(self,fig,plt,parent)

        self.idata=idata
        self.vmin=None
        self.vmax=None
        self.cmap=None
        self.manageX=True
        self.manageY=True

        self.sel=Rectangle((0,0),0,0,color='r',fill=False)
        self.datamenu.setEnabled(False)

        self.mydraw(False)

    def datadraw(self):
        self.plt.imshow(self.idata,cmap=self.cmap,vmin=self.vmin,vmax=self.vmax)

    def onReset(self,event):
        self.mydraw(False)

    def toolTip(self,event):
        txt=""
        if event.xdata is not None and event.ydata is not None and self.idata is not None and event.inaxes == self.plt:
            x=int(event.xdata)
            y=int(event.ydata)
            if x >= 0 and x < self.idata.shape[1] and y >= 0 and y < self.idata.shape[0]:
                txt="%0.2f (%i,%i)" % (self.idata[y,x],x,y)
        return txt

class MyScatterStatic(MyPlot):
    def __init__(self,data,cfg,title,fig,plt,parent):
        MyPlot.__init__(self,fig,plt,parent)

        self.manageX=True
        self.manageY=True
        self.data=data
        self.title=title
        self.cfg=cfg
        self.mydraw(False)

    def datadraw(self):
        if len(self.data):
            self.plt.scatter(np.arange(len(self.data)),self.data,c=self.cfg.item1dScatterColor,marker=self.cfg.item1dScatterMarker, linewidths=self.cfg.item1dScatterlinewidth,s=self.cfg.item1dScattersize)
        self.plt.set_title(self.title)

    def onReset(self,event):
        self.mydraw(False)

    def toolTip(self,event):
        txt=""
        if event.xdata is not None and event.ydata is not None and event.inaxes == self.plt:
            txt="%.4f,%.4f"%(event.xdata,event.ydata)
        return txt

class MyAggPlot(MyPlot):
    def __init__(self,model,xfield,yfield,aggFunc,errFunc,partitions,tranpose,aggText,legendstacks,fig,plt,parent):
        MyPlot.__init__(self,fig,plt,parent)
        self.model=model
        self.tranpose=tranpose
        if self.tranpose:
            self.xfield=yfield
            self.yfield=xfield
        else:
            self.xfield=xfield
            self.yfield=yfield
        self.aggField=yfield
        self.aggFunc=aggFunc
        self.errFunc=errFunc
        self.aggtext=aggText
        self.legendstacks=legendstacks
        self.legendMenu()

        x=[]
        keep=[]
        for k,v in partitions.items():
            keep.append(v)
            try:
                k2=float(k)
            except ValueError:
                k2 = None
            if k2 is None and model.isCategorical(xfield):
                k2=model.intValue(xfield,k)
            if k2 is None:
                bounds=k.split('-')
                k2=np.average(float(bounds[0]),float(bounds[1]))
            x.append(k2)
        self.x=np.array(x)
        self.keep=np.array(keep)[np.argsort(x)]
        self.x.sort()

        self.manageX=True
        self.fieldfilterX=self.model.selectionFilter(self.xfield)
        self.fieldfilterX.modelchange.connect(self.onFilterChange)

        self.manageY=True
        self.fieldfilterY=self.model.selectionFilter(self.yfield)
        self.fieldfilterY.modelchange.connect(self.onFilterChange)


        self.model.filterchange.connect(self.mydraw)
        self.model.filterModelChange.connect(self.onFilterModelChange)

        self.sel=Rectangle((0,0),0,0,color='r',fill=False)
        self.onFilterChange() # Let this function worry about actual bounds, we just cared about color and fill

        self.mydraw(False)

    def datadraw(self):
        lbls=["all"]
        colors={"all":"b"}
        dtype=[]
        if self.legendstacks is not None:
            lbls=self.legendstacks[2]
            colors=dict(zip(lbls,self.legendstacks[1]))
        for lbl in lbls:
            dtype.append((lbl,'f4'))
        y=np.zeros((len(self.x)),dtype=dtype)
        y.fill(np.nan)
        uplim=np.zeros((len(self.x)),dtype=dtype)
        lowlim=np.zeros((len(self.x)),dtype=dtype)
        for i,k in enumerate(self.keep):
            stackedData=self.model.stackedDataCol(self.aggField, filtered=self.drawSelection.isChecked(),keep=k,stacks=self.legendstacks)
            for j in range(len(stackedData[0])):
                v=self.aggFunc(stackedData[0][j])
                y[stackedData[2][j]][i]=v
                if self.errFunc is not None:
                    e=self.errFunc(stackedData[0][j])
                    if len(e) == 1:
                        lowlim[stackedData[2][j]][i]=e[0]
                        uplim[stackedData[2][j]][i]=e[0]
                    else:
                        assert len(e) == 2
                        lowlim[stackedData[2][j]][i]=v-e[0]
                        uplim[stackedData[2][j]][i]=e[1]-v
        for l in lbls:
            if self.tranpose:
                self.plt.errorbar(y[l],self.x,xerr=[lowlim[l],uplim[l]],label=l,color=colors[l],marker=self.model.cfg.aggmarker)
            else:
                self.plt.errorbar(self.x,y[l],yerr=[lowlim[l],uplim[l]],label=l,color=colors[l],marker=self.model.cfg.aggmarker)
        legendPos=self.legendActionGroup.checkedAction().data()
        if legendPos is not None:
            self.plt.legend(loc=legendPos)  
        self.plt.set_xlabel(self.model.prettyname(self.xfield))
        self.plt.set_ylabel(self.model.prettyname(self.yfield))
        self.plt.set_title(self.aggtext % self.model.prettyname(self.aggField))

        self.xlabels(self.model,self.xfield,True)
        self.ylabels(self.model,self.yfield,True)

    def onReset(self,event):
        self.mydraw(False)

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




            
