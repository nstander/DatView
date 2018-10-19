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
import numpy as np
from pyqtgraph import ImageView, ColorMap, mkPen, ScatterPlotItem
import h5py
from cfelpyutils import cfel_geom
from cxiview.cfel_imgtools import histogram_clip_levels

class CrystfelImage(QObject):
    def __init__(self,imodel,iview,geom,parent=None):
        QObject.__init__(self,parent)
        self.imodel=imodel
        self.dmodel=imodel.model
        self.iview=iview
        self.iview.ui.menuBtn.hide()
        self.iview.ui.roiBtn.hide()
        
        # Thanks CXIVIEW, Anton & Valerio
        pos = np.array([0.0,0.5,1.0])
        color = np.array([[255,255,255,255], [128,128,128,255], [0,0,0,255]], dtype=np.ubyte)
        new_color_map = ColorMap(pos,color)
        self.iview.ui.histogram.gradient.setColorMap(new_color_map)

        self.lastrow=-1
        self.curFileName=None
        self.curFile=None
        self.canDraw=self.dmodel.canSaveLst()
        self.checkEvent="event" in self.dmodel.cols
        self.yxmap=None
        self.slab_shape=None
        self.image_shape=None
        self.im_out=None
        if geom is not None:
            self.loadGeom(geom)
        self.imodel.dataChanged.connect(self.draw)

        self.iview.view.menu.addSeparator()
        openGeomAct=self.iview.view.menu.addAction("Load CrystFEL Geometry")
        openGeomAct.triggered.connect(self.openGeom)

        peakmenu=self.iview.view.menu.addMenu("Peaks")
        self.peakActionGroup=QActionGroup(self)
        self.peakActionGroup.setExclusive(True)
        self.peakActionGroup.triggered.connect(self.drawPeaks)

        peakNone=peakmenu.addAction("None")
        peakNone.setCheckable(True)
        peakNone.setChecked(True)
        peakNone.setData(0)
        self.peakActionGroup.addAction(peakNone)

        peakCXI=peakmenu.addAction("CXI")
        peakCXI.setCheckable(True)
        peakCXI.setEnabled(self.dmodel.canSaveLst())
        peakCXI.setData(1)
        self.peakActionGroup.addAction(peakCXI)

        peakStream=peakmenu.addAction("Stream")
        peakStream.setCheckable(True)
        peakStream.setEnabled(self.dmodel.hasStreamPeaks())
        peakStream.setData(2)
        self.peakActionGroup.addAction(peakStream)
        self.peakCanvas=ScatterPlotItem()
        self.iview.getView().addItem(self.peakCanvas)

        self.draw()



    def draw(self):
        if not self.canDraw or self.imodel.currow == self.lastrow:
            return

        # Load the image
        image=self.image()
        if image is None:
            return # Problem with file, don't try to load anything else

        # Image was loaded, so update what we've currently got drawn
        self.lastrow=self.imodel.currow

        # Apply geometry
        if self.yxmap is None:
            image=np.transpose(image)
        else:
            image=cfel_geom.apply_geometry_from_pixel_maps(image,self.yxmap,self.im_out)
        self.iview.setImage(image,autoLevels=False,autoRange=False)

        # CXI View Scaling
        bottom,top=histogram_clip_levels(image.ravel(),self.dmodel.cfg.cxiviewHistClipLevelValue)
        self.iview.setLevels(bottom,top)
        self.iview.getHistogramWidget().setHistogramRange(min(bottom,self.dmodel.cfg.cxiviewHistMin),max(top,self.dmodel.cfg.cxiviewHistMax),padding=self.dmodel.cfg.cxiviewHistPadding)

        # Draw Peaks
        self.drawPeaks()
        

    def loadGeom(self,filename):
        self.yxmap,self.slab_shape,img_shape=cfel_geom.pixel_maps_for_image_view(filename)
        self.im_out=np.zeros(img_shape,dtype=np.dtype(float))
        self.lastrow=-1
        self.draw()

    def openGeom(self):
        name=QFileDialog.getOpenFileName(self.iview,'Select CrystFEL Geomery File (.geom)',filter='*.geom')
        if qt5:
            if name:
                self.loadGeom(name[0])
        elif name is not None and len(name):
            self.loadGeom(name)

    # Sub functions called by draw, not meant to be called externally
    def fromMaybeEvent(self,path):
        r=[]
        if self.checkEvent:
            e=self.dmodel.data["event"][self.imodel.currow]
            if e == -1: # No event
                r=self.curFile[path][:]
            else:
                r=self.curFile[path][e][:]
        else: # No events
            r=self.curFile[path][:]
        return r

    def image(self):
        image = None
        ifile = self.dmodel.value("ifile",self.imodel.currow,False)
        if ifile != self.curFileName:
            if self.curFile is not None:
                self.curFile.close()
            self.curFileName = ifile
            self.curFile = h5py.File(ifile,'r')
        for path in self.dmodel.cfg.imageH5paths:
            if path in self.curFile:
                image=self.fromMaybeEvent(path)
                break
        return image

    def cxipeaks(self):
        # Since this function should ideally only be called internally from draw, 
        # after image has been successfully generated, assume we have correct and valid ifile.
        px=[]
        py=[]
        for path in self.dmodel.cfg.peakXH5paths:
            if path in self.curFile:
                px=self.fromMaybeEvent(path)

                if len(px.shape) > 1:
                    # Data is two dimension, assume x is first column and y second
                    py=px[:,1]
                    px=px[:,0]
                else:
                    for path2 in self.dmodel.cfg.peakYH5paths:
                        if path2 in self.curFile:
                            py=self.fromMaybeEvent(path2)
                            break
                break
        return px,py

    def drawPeaks(self):
        px=[]
        py=[]
        if self.peakActionGroup.checkedAction().data() == 1: # H5 Peaks
            px,py=self.cxipeaks()
        elif self.peakActionGroup.checkedAction().data() == 2: # Stream peaks
            px,py=self.dmodel.streamPeaks(self.imodel.currow)

        if self.yxmap is not None and len(px):
            px=np.array(px,dtype=np.dtype(int))
            py=np.array(py,dtype=np.dtype(int))
            slab=py*self.slab_shape[1]+px
            px=self.yxmap[0][slab]
            py=self.yxmap[1][slab]
        self.peakCanvas.setData(px,py,symbol=self.dmodel.cfg.viewerPeakSymbol,size=self.dmodel.cfg.viewerPeakSize,pen=mkPen(self.dmodel.cfg.viewerPeakColor,width=2),brush=(0,0,0,0),pxMode=False)
            



        
                            



