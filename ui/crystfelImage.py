# datview/ui/crystfelImage.py
# Code for interfacing with cxiview code and libraries to display cxi/h5 images
# Author Natasha Stander

try:
    from PyQt5.QtCore import QObject,pyqtSignal
    from PyQt5.QtWidgets import QAction, QFileDialog
    qt5=True
except ImportError:
    from PyQt4.QtCore import QObject,pyqtSignal 
    from PyQt4.QtGui import QAction, QFileDialog
    qt5=False

from api.itemmodel import ItemModel
from api.datamodel import DataModel
import numpy as np
from pyqtgraph import ImageView, ColorMap
import h5py
from cfelpyutils import cfel_geom
from cxiview.cfel_imgtools import histogram_clip_levels

class CrystfelImage(QObject):
    def __init__(self,imodel,iview,geom,parent=None):
        QObject.__init__(self,parent)
        self.imodel=imodel
        self.iview=iview
        self.iview.ui.menuBtn.hide()
        self.iview.ui.roiBtn.hide()
        
        # Thanks CXIVIEW, Anton & Valerio
        pos = np.array([0.0,0.5,1.0])
        color = np.array([[255,255,255,255], [128,128,128,255], [0,0,0,255]], dtype=np.ubyte)
        new_color_map = ColorMap(pos,color)
        self.iview.ui.histogram.gradient.setColorMap(new_color_map)

        self.datapaths=self.imodel.model.cfg.imageH5paths
        self.lastrow=-1
        self.curFileName=None
        self.curFile=None
        self.canDraw=self.imodel.model.canSaveLst()
        self.checkEvent="event" in self.imodel.model.cols
        self.yxmap=None
        self.im_out=None
        if geom is not None:
            self.loadGeom(geom)
        self.imodel.dataChanged.connect(self.draw)
        self.draw()

        self.iview.view.menu.addSeparator()
        openGeomAct=self.iview.view.menu.addAction("Load CrystFEL Geometry")
        openGeomAct.triggered.connect(self.openGeom)


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
        bottom,top=histogram_clip_levels(image.ravel(),self.imodel.model.cfg.cxiviewHistClipLevelValue)
        self.iview.setLevels(bottom,top)
        self.iview.getHistogramWidget().setHistogramRange(min(bottom,self.imodel.model.cfg.cxiviewHistMin),max(top,self.imodel.model.cfg.cxiviewHistMax),padding=self.imodel.model.cfg.cxiviewHistPadding)
        

    def loadGeom(self,filename):
        self.yxmap,slab_shape,img_shape=cfel_geom.pixel_maps_for_image_view(filename)
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
    def image(self):
        image = None
        ifile = self.imodel.model.value("ifile",self.imodel.currow,False)
        if ifile != self.curFileName:
            if self.curFile is not None:
                self.curFile.close()
            self.curFileName = ifile
            self.curFile = h5py.File(ifile,'r')
        for path in self.datapaths:
            if path in self.curFile:
                if self.checkEvent:
                    e=self.imodel.model.data["event"][self.imodel.currow]
                    if e == -1: # No event
                        image=self.curFile[path][:]
                    else:
                        image=self.curFile[path][e][:]
                else: # No events
                    image=self.curFile[path][:]
                break
        return image

        
                            



