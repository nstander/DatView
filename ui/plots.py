# datview/ui/plots.py 
# This file contains the code interfacing with matplotlib for drawing all plots in the GUI
# Author Natasha Stander

try:
    from PyQt5 import QtCore
    from PyQt5.QtWidgets import QSizePolicy, QMenu, QApplication, QFileDialog
    from PyQt5.QtGui import QCursor
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
except ImportError as e:
    print(e)
    from PyQt4 import QtCore
    from PyQt4.QtGui import QSizePolicy, QMenu, QApplication, QCursor, QFileDialog
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
        self.plt=self.fig.add_subplot(111)
        self.fig.set_facecolor('white')
        
        FigureCanvas.setMinimumSize(self, 200, 200)
        FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding,QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.fig.canvas.mpl_connect('scroll_event',self.onScroll)
        self.fig.canvas.mpl_connect('button_press_event',self.onPress)
        self.fig.canvas.mpl_connect('button_release_event',self.onRelease)
        self.fig.canvas.mpl_connect('motion_notify_event',self.onMotion)

        self.pan=None
        self.sel=None # Derived classes should initialize to Rectangle
        self.fieldfilterX=None # Derived classes should intialize if manageX
        self.fieldfilterY=None # Derived classes should intialize if manageY
        self.selp=None

        self.manageX=False
        self.manageY=False

        self.menu=QMenu()
        saveAct=self.menu.addAction("Save PNG")
        saveAct.triggered.connect(self.onSave)
        saveAct=self.menu.addAction("Save SVG")
        saveAct.triggered.connect(self.onSaveSVG)
        resetAct=self.menu.addAction("Reset")
        resetAct.triggered.connect(self.onReset)

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
        self.draw()

    def onScroll(self,event):
        if event.xdata is None or event.ydata is None:
            return
        scale=1
        factor=1.5
        if event.button == 'up':
            scale = factor
        else:
             scale = 1.0/factor
        if scale != 1:
            if self.manageX:
                cur_xlim = self.plt.get_xlim()
                self.plt.set_xlim([event.xdata - (event.xdata - cur_xlim[0]) / scale, event.xdata + (cur_xlim[1]-event.xdata)/scale ])
            if self.manageY:
                cur_ylim = self.plt.get_ylim()
                self.plt.set_ylim([event.ydata - (event.ydata - cur_ylim[0]) / scale, event.ydata + (cur_ylim[1]-event.ydata)/scale ])
            if self.manageX or self.manageY:
                self.draw()

    def onPress(self,event):
        if event.button == 1 and event.xdata is not None and event.ydata is not None:
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
                    self.draw()
            else:
                self.pan=(event.xdata,event.ydata)
        elif event.button == 3:
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
        if event.xdata and event.ydata:
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
                    self.draw()
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
                    self.draw()
        if not handled:
            self.onToolTip(event)

    def onToolTip(self,event):
        pass

    def onSave(self):
        name=QFileDialog.getSaveFileName(self,'Save Plot',filter='*.png')
        if name is not None:
            self.fig.savefig(name,ext="png")

    def onSaveSVG(self):
        name=QFileDialog.getSaveFileName(self,'Save Plot',filter='*.svg')
        if name is not None:
            self.fig.savefig(name,ext="svg")

    def onReset(self):
        self.mydraw(False)

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
        self.draw()

    def xlabels(self,model,field):
        if model.hasLabels(field):
            lbls=model.labels(field)
            self.plt.set_xticks(model.labelints(field))
            self.plt.set_xticklabels(lbls)

    def ylabels(self,model,field):
        if model.hasLabels(field):
            lbls=model.labels(field)
            self.plt.set_yticks(model.labelints(field))
            self.plt.set_yticklabels(lbls)


class MyHistogram(MyFigure):
    def __init__(self,model,field,parent=None,flags=0):
        MyFigure.__init__(self,parent,flags)
        self.bins=int(model.cfg.hist1Dbins)
        self.model=model
        self.field=field

        self.fig.canvas.mpl_connect('key_press_event',self.onKey)

        self.manageX=True
        self.fieldfilterX=self.model.selectionFilter(self.field)
        self.fieldfilterX.modelchange.connect(self.onFilterChange)
        self.model.filterchange.connect(self.mydraw)

        self.sel=Rectangle((self.fieldfilterX.minimum,0),self.fieldfilterX.maximum-self.fieldfilterX.minimum,0,alpha=0.3,color='r')
        self.sel.set_visible(self.fieldfilterX.isActive())

        rangeAct=self.menu.addAction("Set Range to Current Limits")
        rangeAct.triggered.connect(self.onSetRange)

        self.mu=None
        self.sigma=None
        self.range=(self.model.fieldmin(self.field),self.model.fieldmax(self.field))

        self.plt.get_yaxis().set_visible(False)
        self.dcache=None
        self.mydraw(False)

    def datadraw(self):
        title=self.model.prettyname(self.field)
        fmt=" %0.2f "+u"\u00B1"+ " %0.2f"
        if self.model.isCategorical(self.field):
            if self.dcache is None:
                self.dcache=np.unique(self.model.data[self.field],return_counts=True)
            if self.model.isFiltered():
                self.plt.bar(self.dcache[0],self.dcache[1],color='black',alpha=0.5,edgecolor="none",align='center')
                fcnts=np.unique(self.model.filtered[self.field],return_counts=True)
                self.plt.bar(fcnts[0],fcnts[1],color='black',align='center')
            else:
                self.plt.bar(self.dcache[0],self.dcache[1],color='black',align='center')
            self.xlabels(self.model,self.field)
        else:
            if self.model.isFiltered():
                b=self.plt.hist(self.model.data[self.field],bins=self.bins,color='black',alpha=0.5,edgecolor="none",
                    range=self.range)[1]
                self.plt.hist(self.model.filtered[self.field],bins=b,color='black',
                    range=self.range)
            else:
                b=self.plt.hist(self.model.data[self.field],bins=self.bins,color='black',
                    range=self.range)[1]
            if self.mu is not None:
                y=matplotlib.mlab.normpdf(np.array(b),self.mu,self.sigma)
                self.plt.plot(b,y/np.max(y)*self.plt.get_ylim()[1]*0.95,'r',linewidth=2)
                title += fmt % (self.mu,self.sigma)
        self.plt.set_title(title)
        self.sel.set_height(self.plt.get_ylim()[1])
        if not self.model.hasLabels(self.field):
            self.plt.locator_params(axis='x', nbins=6)

    def onKey(self,event):
        if event.key == '+' or event.key == '=':
            self.bins *=2
            self.mydraw()
        if event.key == '-':
            self.bins =int(self.bins/2)
            self.mydraw()
        if event.key == 'ctrl+f':
            if self.mu is None:
                # Always fit filtered (if not filtering, will be full model
                dt=self.model.filtered[self.field]
                dt = dt[dt != -1] # But don't use empty
                (self.mu,self.sigma)=norm.fit(dt)
            else:
                self.mu = None
                self.sigma = None
            self.mydraw()

    def onToolTip(self,event):
        txt=""
        if event.xdata is not None and event.ydata is not None:
            txt=str(event.xdata)
            if self.model.isCategorical(self.field):
                bar = int(np.round(event.xdata))
                txt=self.model.stringValue(self.field,bar)
        self.setToolTip(txt)

    def onSetRange(self):
        self.range=tuple(self.plt.get_xlim())
        self.mydraw()

    def onReset(self):
        self.range=(self.model.fieldmin(self.field),self.model.fieldmax(self.field))
        self.mydraw(False)
            

class MyScatter(MyFigure):
    def __init__(self,model,xfield,yfield,cfield,parent=None,flags=0):
        MyFigure.__init__(self,parent,flags)
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

        self.model.filterchange.connect(self.mydraw)
        self.plt.set_xlim((self.model.fieldmin(self.xfield),self.model.fieldmax(self.xfield)))
        self.plt.set_ylim((self.model.fieldmin(self.yfield),self.model.fieldmax(self.yfield)))

        self.sel=Rectangle((0,0),0,0,color='r',fill=False)
        self.onFilterChange() # Let this function worry about actual bounds, we just cared about color and fill
        self.cb=None

        self.setWindowTitle("%s - %s - Scatter" % (self.model.prettyname(self.xfield),self.model.prettyname(self.yfield)))
        self.mydraw()

    def datadraw(self):
        xAll=self.model.data[self.xfield]
        xFiltered=self.model.filtered[self.xfield]

        cAll="black"
        cFiltered="black"
        cm=None
        marker=self.model.cfg.scattermarker
        vmin=None
        vmax=None
        if self.cfield is not None:
            cAll=self.model.data[self.cfield]
            cFiltered=self.model.filtered[self.cfield]
            cm=plt.cm.get_cmap(self.model.cfg.scattercmap)
            vmin=self.model.fieldmin(self.cfield)
            vmax=self.model.fieldmax(self.cfield)

        if self.model.isFiltered():
            self.plt.scatter(xAll,self.model.data[self.yfield],c=cAll,alpha=0.5,cmap=cm,vmin=vmin,vmax=vmax,marker=marker,linewidths=self.model.cfg.scatterlinewidth,s=self.model.cfg.scattersize)
            sc=self.plt.scatter(xFiltered,self.model.filtered[self.yfield],c=cFiltered,cmap=cm,vmin=vmin,vmax=vmax,marker=marker,linewidths=self.model.cfg.scatterlinewidth,s=self.model.cfg.scattersize)
        else:
            sc=self.plt.scatter(xAll,self.model.data[self.yfield],c=cAll,cmap=cm,vmin=vmin,vmax=vmax,marker=marker,linewidths=self.model.cfg.scatterlinewidth,s=self.model.cfg.scattersize)

        self.plt.set_xlabel(self.model.prettyname(self.xfield))
        self.plt.set_ylabel(self.model.prettyname(self.yfield))
        if self.cfield is not None:
            self.plt.set_title(self.model.prettyname(self.cfield))
        if self.cfield is not None and self.cb is None:
            self.cb=self.fig.colorbar(sc)

        self.xlabels(self.model,self.xfield)
        self.ylabels(self.model,self.yfield)

    def onReset(self,event):
        self.plt.set_xlim((self.model.fieldmin(self.xfield),self.model.fieldmax(self.xfield)))
        self.plt.set_ylim((self.model.fieldmin(self.yfield),self.model.fieldmax(self.yfield)))
        self.mydraw()

    def onToolTip(self,event):
        txt=""
        if event.xdata is not None and event.ydata is not None:
            if self.model.isCategorical(self.xfield):
                xtxt=self.model.stringValue(self.xfield,int(np.round(event.xdata)))
            else:
                xtxt="%.4f"%(event.xdata)
            if self.model.isCategorical(self.yfield):
                ytxt=self.model.stringValue(self.yfield,int(np.round(event.ydata)))
            else:
                ytxt="%.4f"%(event.ydata)
            txt="%s,%s"%(xtxt,ytxt)
        self.setToolTip(txt)

class MyHist2d(MyFigure):
    def __init__(self,model,xfield,yfield,log=False,parent=None,flags=0):
        MyFigure.__init__(self,parent,flags)
        self.model=model
        self.xfield=xfield
        self.yfield=yfield
        self.bins=int(model.cfg.hist2Dbins)
        self.log=log

        self.fig.canvas.mpl_connect('key_press_event',self.onKey)

        self.manageX=True
        self.fieldfilterX=self.model.selectionFilter(self.xfield)
        self.fieldfilterX.modelchange.connect(self.onFilterChange)

        self.manageY=True
        self.fieldfilterY=self.model.selectionFilter(self.yfield)
        self.fieldfilterY.modelchange.connect(self.onFilterChange)

        self.model.filterchange.connect(self.mydraw)
        self.plt.set_xlim((self.model.fieldmin(self.xfield),self.model.fieldmax(self.xfield)))
        self.plt.set_ylim((self.model.fieldmin(self.yfield),self.model.fieldmax(self.yfield)))

        self.sel=Rectangle((0,0),0,0,color='r',fill=False)
        self.onFilterChange() # Let this function worry about actual bounds, we just cared about color and fill
        self.cb=None
        self.H=None
        self.xedges=None
        self.yedges=None

        self.range=((self.model.fieldmin(self.xfield),self.model.fieldmax(self.xfield)),
                                 (self.model.fieldmin(self.yfield),self.model.fieldmax(self.yfield)))

        rangeAct=self.menu.addAction("Set Range to Current Limits")
        rangeAct.triggered.connect(self.onSetRange)

        xrangeAct=self.menu.addAction("Set X Range to Current Limits")
        xrangeAct.triggered.connect(self.onSetXRange)

        yrangeAct=self.menu.addAction("Set Y Range to Current Limits")
        yrangeAct.triggered.connect(self.onSetYRange)

        logtxt=""
        if log:
            logtxt="Log "
        self.setWindowTitle("%s - %s - %s2D Histogram" % (self.model.prettyname(self.xfield),self.model.prettyname(self.yfield),logtxt))
        self.mydraw()

    def datadraw(self):
        # Always use filtered
        b=[self.bins,self.bins]
        if self.model.isCategorical(self.xfield):
            b[0]=len(self.model.labels(self.xfield))
        if self.model.isCategorical(self.yfield):
            b[1]=len(self.model.labels(self.yfield))     
        self.H,self.xedges,self.yedges = np.histogram2d(self.model.filtered[self.xfield],self.model.filtered[self.yfield],bins=b,
                          range=self.range)
        norm=None
        if self.log:
            norm=LogNorm()
        h=self.H
        if self.model.cfg.histAlwaysMask0:
            h=np.ma.masked_values(h,0)
        sc=self.plt.pcolormesh(self.xedges,self.yedges,np.transpose(h),cmap=plt.cm.get_cmap(self.model.cfg.hist2dcmap),norm=norm)
        if self.cb is None:
            self.cb=self.fig.colorbar(sc)
        else:
            self.cb.on_mappable_changed(sc)

        self.plt.set_xlabel(self.model.prettyname(self.xfield))
        self.plt.set_ylabel(self.model.prettyname(self.yfield))

        self.xlabels(self.model,self.xfield)
        self.ylabels(self.model,self.yfield)

    def onKey(self,event):
        if event.key == '+' or event.key == '=':
            self.bins *=2
            self.mydraw()
        if event.key == '-':
            self.bins =int(self.bins/2)
            if self.bins < 1:
                self.bins = 1
            self.mydraw()

    def onReset(self,event):
        self.bins=int(64)
        self.plt.set_xlim((self.model.fieldmin(self.xfield),self.model.fieldmax(self.xfield)))
        self.plt.set_ylim((self.model.fieldmin(self.yfield),self.model.fieldmax(self.yfield)))
        self.mydraw()

    def onToolTip(self,event):
        txt=""
        if event.xdata is not None and event.ydata is not None and self.H is not None:
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
        self.setToolTip(txt)

    def onSetRange(self):
        self.range=(tuple(self.plt.get_xlim()),tuple(self.plt.get_ylim()))
        self.mydraw()

    def onSetXRange(self):
        self.range=(tuple(self.plt.get_xlim()),self.range[1])
        self.mydraw(False)

    def onSetYRange(self):
        self.range=(self.range[0],tuple(self.plt.get_ylim()))
        self.mydraw(False)

    def onReset(self):
        self.range=((self.model.fieldmin(self.xfield),self.model.fieldmax(self.xfield)),
                                 (self.model.fieldmin(self.yfield),self.model.fieldmax(self.yfield)))
        self.mydraw(False)






            
