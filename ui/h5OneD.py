# datview/ui/crystfelImage.py
# Code for interfacing with cxiview code and libraries to display cxi/h5 images
# Author Natasha Stander

try:
    from PyQt5.QtCore import QObject,pyqtSignal
    from PyQt5.QtWidgets import QAction, QFileDialog, QActionGroup
    qt5=True
except ImportError:
    from PyQt4.QtCore import QObject,pyqtSignal 
    from PyQt4.QtGui import QAction, QFileDialog, QActionGroup
    qt5=False

from api.itemmodel import ItemModel
from api.datamodel import DataModel
from .plots import MyFigure
import numpy as np
import h5py

class H5OneD(QObject):
    def __init__(self,path,imodel,parent=None):
        QObject.__init__(self,parent)
        self.imodel=imodel
        self.dmodel=imodel.model
        self.path=path
        self.canDraw=self.dmodel.canSaveLst()
        self.checkEvent="event" in self.dmodel.cols
        self.lastrow = -1
        self.curFileName=None
        self.curFile=None
        self.fig=MyFigure(parent=parent)
        self.scatter=self.fig.staticScatter([],self.dmodel.cfg,self.path)
        self.imodel.dataChanged.connect(self.draw)
        self.draw()

    def draw(self):
        if not self.canDraw or self.imodel.currow == self.lastrow:
            return

        data = []
        ifile = self.dmodel.value("ifile",self.imodel.currow,False)
        if ifile != self.curFileName:
            if self.curFile is not None:
                self.curFile.close()
            self.curFileName = ifile
            self.curFile = h5py.File(ifile,'r')
        if self.path in self.curFile:
            if self.checkEvent:
                e=self.dmodel.data["event"][self.imodel.currow]
                if e == self.dmodel.cfg.nullvalue: # No event
                    data=self.curFile[self.path]
                else:
                    data=self.curFile[self.path][e]
            else: # No events
                data=self.curFile[self.path]
        self.scatter.data=data
        self.scatter.mydraw(self.lastrow != -1)
        self.lastrow=self.imodel.currow

       
