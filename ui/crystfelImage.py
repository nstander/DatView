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
from pyqtgraph import ImageView, ColorMap, mkPen, ScatterPlotItem, TextItem
import scipy.constants
import scipy.spatial
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
        self.img_shape=None
        self.geom_coffset=0
        self.geom_pixsize=None
        self.im_out=None
        self.resolutionLambda=None
        self.pixRadiusToRes=None
        self.hkl=None
        self.hklLookup=None
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

        reflectionmenu=self.iview.view.menu.addMenu("Reflections")
        self.reflectionActionGroup=QActionGroup(self)
        self.reflectionActionGroup.setExclusive(True)
        self.reflectionActionGroup.triggered.connect(self.drawReflections)

        refNone=reflectionmenu.addAction("None")
        refNone.setCheckable(True)
        refNone.setChecked(True)
        refNone.setData(0)
        self.reflectionActionGroup.addAction(refNone)

        refStream=reflectionmenu.addAction("Stream")
        refStream.setCheckable(True)
        refStream.setEnabled(self.dmodel.hasStreamReflections())
        refStream.setData(1)
        self.reflectionActionGroup.addAction(refStream)
        self.reflectionCanvas=ScatterPlotItem()
        self.iview.getView().addItem(self.reflectionCanvas)

        self.drawResRingsAct=self.iview.view.menu.addAction("Resolution Rings")
        self.drawResRingsAct.setCheckable(True)
        self.drawResRingsAct.setChecked(False)
        self.drawResRingsAct.triggered.connect(self.drawResRings)
        self.drawResRingsAct.setEnabled(self.yxmap is not None)
        self.resolutionRingsCanvas=ScatterPlotItem()
        self.iview.getView().addItem(self.resolutionRingsCanvas)
        self.resRingsTextItems=[]
        for x in self.dmodel.cfg.viewerResolutionRingsAngstroms:
            self.resRingsTextItems.append(TextItem('',anchor=(0.5,0.8)))
            self.iview.getView().addItem(self.resRingsTextItems[-1])

        self.drawResolutionLimitAct=self.iview.view.menu.addAction("Resolution Limit Ring")
        self.drawResolutionLimitAct.setCheckable(True)
        self.drawResolutionLimitAct.setChecked(False)
        self.drawResolutionLimitAct.triggered.connect(self.drawResLimitRing)
        self.drawResolutionLimitAct.setEnabled(self.yxmap is not None and 'reslim' in self.dmodel.cols)
        self.resolutionLimitCanvas=ScatterPlotItem()
        self.iview.getView().addItem(self.resolutionLimitCanvas)

        if geom is not None:
            self.loadGeom(geom)

        self.toolTipsAct=self.iview.view.menu.addAction("Show Position in Tool Tip")
        self.toolTipsAct.setCheckable(True)
        self.toolTipsAct.setChecked(True)
        self.iview.scene.sigMouseMoved.connect(self.mouseMove)

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

        self.calcResLambda()
        self.drawPeaks()
        self.drawReflections()
        self.drawResRings()
        self.drawResLimitRing()
        

    def loadGeom(self,filename):
        self.yxmap,self.slab_shape,self.img_shape=cfel_geom.pixel_maps_for_image_view(filename)
        self.im_out=np.zeros(self.img_shape,dtype=np.dtype(float))
        self.geom_coffset=cfel_geom.coffset_from_geometry_file(filename)
        self.geom_pixsize=1/cfel_geom.res_from_geometry_file(filename)
        self.drawResRingsAct.setEnabled(True)
        self.drawResolutionLimitAct.setEnabled('reslim' in self.dmodel.cols)
        self.lastrow=-1
        self.draw()

    def openGeom(self):
        name=QFileDialog.getOpenFileName(self.iview,'Select CrystFEL Geomery File (.geom)',filter='*.geom')
        if qt5:
            if name:
                self.loadGeom(name[0])
        elif name is not None and len(name):
            self.loadGeom(name)

    def mouseMove(self,pos):
        mapped=self.iview.getView().mapSceneToView(pos)
        txt=""
        if self.toolTipsAct.isChecked() and mapped.x() >= 0 and mapped.x() < self.iview.image.shape[0] \
                                        and mapped.y() >= 0 and mapped.y() <self.iview.image.shape[1]:
            if self.img_shape is not None:
                x=mapped.x()-self.img_shape[0]/2
                y=self.img_shape[1]/2-mapped.y()
            else:
                x=mapped.x()
                y=mapped.y()
            txt="x: %i, y: %i" % (x,y)
            if self.iview.image is not None:
                txt += " value: %.2f" % self.iview.image[int(mapped.x()),int(mapped.y())]
            if self.pixRadiusToRes is not None:
                txt += " resolution: %.2f"% self.pixRadiusToRes(np.sqrt(x**2+y**2))
            if self.hklLookup is not None:
                res=self.hklLookup.query([mapped.x(),mapped.y()],k=1)
                if len(res) > 0 and res[0] < self.dmodel.cfg.viewerReflectionSize:
                    txt += " hkl: %s" % self.hkl[res[1]]
        self.iview.setToolTip(txt)

    # Sub functions called by draw, not meant to be called externally
    def fromMaybeEvent(self,paths):
        r=None
        for path in paths:
            if path in self.curFile:
                if self.checkEvent:
                    e=self.dmodel.data["event"][self.imodel.currow]
                    if e == -1: # No event
                        r=self.curFile[path]
                    else:
                        r=self.curFile[path][e]
                else: # No events
                    r=self.curFile[path]
                break
        return r

    def image(self):
        image = None
        ifile = self.dmodel.value("ifile",self.imodel.currow,False)
        if ifile != self.curFileName:
            if self.curFile is not None:
                self.curFile.close()
            self.curFileName = ifile
            self.curFile = h5py.File(ifile,'r')
        image=self.fromMaybeEvent(self.dmodel.cfg.imageH5paths)
        return image

    def cxipeaks(self):
        # Since this function should ideally only be called internally from draw, 
        # after image has been successfully generated, assume we have correct and valid ifile.
        px=self.fromMaybeEvent(self.dmodel.cfg.peakXH5paths)
        if px is None:
            px=[]
            py=[]
        else:
            if len(px.shape) > 1:
                # Data is two dimension, assume x is first column and y second
                py=px[:,1]
                px=px[:,0]
            else:
                py=self.fromMaybeEvent(self.dmodel.cfg.peakYH5paths)
                if py is None:
                    px = []
                    py = []
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
        self.peakCanvas.setData(px,py,symbol=self.dmodel.cfg.viewerPeakSymbol,\
            size=self.dmodel.cfg.viewerPeakSize,pen=\
            mkPen(self.dmodel.cfg.viewerPeakColor,width=self.dmodel.cfg.viewerPeakPenWidth),\
            brush=(0,0,0,0),pxMode=False)

    def drawReflections(self):
        px=[]
        py=[]
        self.hkl=None
        self.hklLookup=None
        if self.reflectionActionGroup.checkedAction().data() == 1: # Stream
            px,py,self.hkl=self.dmodel.streamReflections(self.imodel.currow)

        if self.yxmap is not None and len(px):
            px=np.array(px,dtype=np.dtype(int))
            py=np.array(py,dtype=np.dtype(int))
            slab=py*self.slab_shape[1]+px
            px=self.yxmap[0][slab]
            py=self.yxmap[1][slab]
        self.reflectionCanvas.setData(px,py,symbol=self.dmodel.cfg.viewerReflectionSymbol,\
            size=self.dmodel.cfg.viewerReflectionSize,pen=\
            mkPen(self.dmodel.cfg.viewerReflectionColor,width=self.dmodel.cfg.viewerReflectionPenWidth),\
            brush=(0,0,0,0),pxMode=False)
        if self.hkl is not None:
            self.hklLookup=scipy.spatial.cKDTree(np.dstack((px,py))[0])

    def calcResLambda(self):
        self.resolutionLambda=None

        photon_ev=None
        if "phoen" in self.dmodel.cols:
            photon_ev= self.dmodel.data["phoen"][self.imodel.currow]
        if photon_ev is None or photon_ev <= 0:
            photon_ev=self.fromMaybeEvent(self.dmodel.cfg.viewerPhotonEvH5Paths)

        clen=None
        if "aclen" in self.dmodel.cols:
            clen=self.dmodel.data["aclen"][self.imodel.currow] # Value is corrected with coffset
        if clen is None:
            clen=self.fromMaybeEvent(self.dmodel.cfg.viewerCameraLengthH5Paths)
            if clen is not None: # Uncorrected, correct here
                clen +=self.geom_coffset

        # Need valid photon energy, camera length, and geometry (yxmap)
        if photon_ev is None or photon_ev <= 0 or clen is None or self.yxmap is None:
            return # Not enough info 

        lmbd=scipy.constants.h * scipy.constants.c /(scipy.constants.e * photon_ev)
        self.resolutionLambda=lambda r : (2.0/self.geom_pixsize)*(clen)*np.tan(2.0*np.arcsin(lmbd / \
                    (2.0 * r *1e-10)))
        self.pixRadiusToRes=lambda r : 1e10*lmbd/(2.0*np.sin(0.5*np.arctan(r*self.geom_pixsize/clen)))

    def drawResRings(self):
        if not self.drawResRingsAct.isChecked() or self.resolutionLambda is None:
            self.resolutionRingsCanvas.setData([], [])
            for ti in self.resRingsTextItems:
                ti.setText('')
        else:
            ring_sizes=self.resolutionLambda(np.array(self.dmodel.cfg.viewerResolutionRingsAngstroms))
            self.resolutionRingsCanvas.setData([self.img_shape[0]/2]*len(ring_sizes), [self.img_shape[1]/2]*len(ring_sizes),symbol='o',\
                size=ring_sizes,pen=mkPen(self.dmodel.cfg.viewerResRingColor, width=self.dmodel.cfg.viewerResRingWidth),\
                brush=(0,0,0,0),pxMode=False)
            for i,ti in enumerate(self.resRingsTextItems):
                ti.setText("%.1f A" % self.dmodel.cfg.viewerResolutionRingsAngstroms[i],color=self.dmodel.cfg.viewerResRingColor)
                ti.setPos(self.img_shape[0]/2,self.img_shape[1]/2+ring_sizes[i]/2)

    def drawResLimitRing(self):
        if not self.drawResolutionLimitAct.isChecked() or self.resolutionLambda is None:
            self.resolutionLimitCanvas.setData([],[])
        else:
            r=self.dmodel.data['reslim'][self.imodel.currow]
            if r <= 0:
                self.resolutionLimitCanvas.setData([],[])
            else:
                r=10/r
                self.resolutionLimitCanvas.setData([self.img_shape[0]/2], [self.img_shape[1]/2],symbol='o',\
                    size=self.resolutionLambda(r),\
                    pen=mkPen(self.dmodel.cfg.viewerResLimitRingColor, width=self.dmodel.cfg.viewerResLimitRingWidth),\
                    brush=(0,0,0,0),pxMode=False)

        

        
        
        



        
                            



