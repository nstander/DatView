# datview/api/modelcfg.py
# Loads and stores GUI configuration file
# Author Natasha Stander

import os 
import lxml.etree as ElementTree
from .groupmgr import GroupMgr



class ModelConfig:
    def __init__(self,filename=None):
        if filename is None:
            filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),"modelcfg.xml")

        self.sep = None
        self.prettyMap = {}
        self.fmtMap = {}
        self.dtypeMap = {}
        self.multMap = {}
        self.fmtDefault="%f"
        self.dtypeDefault="f4"
        self.multDefault=1
        self.defaultHistograms=set()
        self.internalCols=set()
        self.invert=[]
        self.scattercmap="jet"
        self.hist2dcmap="jet"
        self.pixelcmap="jet"
        self.categorical=[]
        self.commentchar=None
        self.histperrow=3
        self.hist1Dbins=32
        self.hist2Dbins=64
        self.scattermarker='o'
        self.scatterlinewidth=0
        self.scattersize=4
        self.histAlwaysMask0=True
        self.playtime=1000
        self.imageH5paths=["/entry_1/data_1/data","/data/data"]
        self.cxiviewHistClipLevelValue=0.0002
        self.cxiviewHistMax=16384
        self.cxiviewHistMin=-100
        self.cxiviewHistPadding=0.05
        self.viewerPeakSymbol='s'
        self.viewerPeakSize=10
        self.viewerPeakColor='r'
        self.viewerPeakPenWidth=2
        self.peakXH5paths=["/entry_1/result_1/peakXPosRaw","/processing/hitfinder/peakinfo-raw"]
        self.peakYH5paths=["/entry_1/result_1/peakYPosRaw"]
        self.viewerReflectionSymbol='s'
        self.viewerReflectionSize=10
        self.viewerReflectionColor='r'
        self.viewerReflectionPenWidth=2
        self.viewerPhotonEvH5Paths=["/instrument/photon_energy_eV","/LCLS/photon_energy_eV"]
        self.viewerCameraLengthH5Paths=["/instrument/detector_1/EncoderValue","/LCLS/detector_1/EncoderValue","/LCLS/detector0-EncoderValue"]
        self.viewerResolutionRingsAngstroms=[3.0, 4.0, 6.0, 8.0, 10.0, 20.0]
        self.viewerResRingColor='b'
        self.viewerResRingWidth=1
        self.viewerResLimitRingColor='g'
        self.viewerResLimitRingWidth=1
        self.numXticks=6
        self.item1dScatterColor='b'
        self.item1dScatterMarker='o'
        self.item1dScatterlinewidth=None
        self.item1dScattersize=8
        self.item1dPlots=[]


        et=ElementTree.parse(filename)
        root = et.getroot()
        assert root.tag == "modelcfg"
        for child in root:
            if child.tag == "datsep" and child.text:
                self.sep=child.text
            if child.tag == "commentchars" and child.text:
                self.commentchar=child.text
            if child.tag == "defaulthistograms":
                self.defaultHistograms=set(child.get("names").split(","))
            if child.tag == "hidden":
                self.internalCols=set(child.get("names").split(","))
            if child.tag == "categorical":
                self.categorical=set(child.get("names").split(","))
            if child.tag == "fields":
                for field in child:
                    if field.get("nm") == "default":
                        self.fmtDefault=field.get("fmt")
                        self.dtypeDefault=field.get("dtype")
                        self.multDefault=float(field.get("mult"))
                    else:
                        if "fmt" in field.attrib:
                            self.fmtMap[field.get("nm")]=field.get("fmt")
                        if "dtype" in field.attrib:
                            self.dtypeMap[field.get("nm")]=field.get("dtype")
                        if "mult" in field.attrib:
                            self.multMap[field.get("nm")]=float(field.get("mult"))
                        if "prettyname" in field.attrib:
                            self.prettyMap[field.get("nm")]=field.get("prettyname")
                        if "invert" in field.attrib and field.get("invert") == "True":
                            self.invert.append(field.get("nm"))
            if child.tag == "scattercmap" and child.text:
                self.scattercmap=child.text
            if child.tag == "hist2dcmap" and child.text:
                self.hist2dcmap=child.text
            if child.tag == "pixelcmap" and child.text:
                self.pixelcmap=child.text
            if child.tag == "scatterlinewidth" and child.text:
                self.scatterlinewidth=int(child.text)
            if child.tag == "scattermarker" and child.text:
                self.scattermarker=child.text
            if child.tag == "scattersize" and child.text:
                self.scattersize=int(child.text)
            if child.tag == "histperrow" and child.text:
                self.histperrow=int(child.text)
            if child.tag == "hist1Dbins" and child.text:
                self.hist1Dbins=int(child.text)
            if child.tag == "hist2Dbins" and child.text:
                self.hist2Dbins=int(child.text)
            if child.tag == "histAlwaysMask0" and child.text:
                self.histAlwaysMask0 = int(child.text) != 0
            if child.tag == "playInterval" and child.text:
                self.playtime=int(child.text)
            if child.tag == "imageH5paths" and child.text:
                self.imageH5paths=child.text.split(',')
            if child.tag == "cxiviewHistClipLevelValue" and child.text:
                self.cxiviewHistClipLevelValue=float(child.text)
            if child.tag == "cxiviewHistMax" and child.text:
                self.cxiviewHistMax=int(child.text)
            if child.tag == "cxiviewHistMin" and child.text:
                self.cxiviewHistMin=int(child.text)
            if child.tag == "cxiviewHistPadding" and child.text:
                self.cxiviewHistPadding=float(child.text)
            if child.tag == "viewerPeakSize" and child.text:
                self.viewerPeakSize=float(child.text)
            if child.tag == "viewerPeakSymbol" and child.text:
                self.viewerPeakSymbol=child.text
            if child.tag == "viewerPeakColor" and child.text:
                self.viewerPeakColor=child.text
            if child.tag == "viewerPeakPenWidth" and child.text:
                self.viewerPeakPenWidth=float(child.text)
            if child.tag == "peakXH5paths" and child.text:
                self.peakXH5path=child.text.split(',')
            if child.tag == "peakYH5paths" and child.text:
                self.peakYH5path=child.text.split(',')
            if child.tag == "viewerReflectionSize" and child.text:
                self.viewerReflectionSize=float(child.text)
            if child.tag == "viewerReflectionSymbol" and child.text:
                self.viewerReflectionSymbol=child.text
            if child.tag == "viewerReflectionColor" and child.text:
                self.viewerReflectionColor=child.text
            if child.tag == "viewerReflectionPenWidth" and child.text:
                self.viewerReflectionPenWidth=float(child.text)
            if child.tag == "viewerPhotonEvH5paths" and child.text:
                self.viewerPhotonEvH5path=child.text.split(',')
            if child.tag == "viewerCameraLengthH5paths" and child.text:
                self.viewerCameraLengthH5path=child.text.split(',')
            if child.tag == "viewerResolutionRingsAngstroms" and child.text:
                self.viewerResolutionRingsAngstroms=[]
                for f in child.text.split(','):
                    self.viewerResolutionRingsAngstroms.append(float(f))
            if child.tag == "viewerResRingColor" and child.text:
                self.viewerResRingColor=child.text
            if child.tag == "viewerResRingWidth" and child.text:
                self.viewerResRingWidth=float(child.text)
            if child.tag == "viewerResLimitRingColor" and child.text:
                self.viewerResLimitRingColor=child.text
            if child.tag == "viewerResLimitRingWidth" and child.text:
                self.viewerResLimitRingWidth=float(child.text)
            if child.tag == "numXticks" and child.text:
                self.numXticks=int(child.text)
            if child.tag == "item1dScatterlinewidth" and child.text:
                self.item1dScatterlinewidth=int(child.text)
            if child.tag == "item1dScatterColor" and child.text:
                self.item1dScatterColor=child.text
            if child.tag == "item1dScatterMarker" and child.text:
                self.item1dScatterMarker=child.text
            if child.tag == "item1dScattersize" and child.text:
                self.item1dScattersize=int(child.text)
            if child.tag == "item1dPlots" and child.text:
                self.item1dPlots=child.text.split(',')


    def prettyname(self,field):
        r=field
        if r.startswith(GroupMgr.prefix):
            r=field[len(GroupMgr.prefix):]
        if r in self.prettyMap:
            r=self.prettyMap[r]
        return r

    def dtype(self,field):
        r=self.dtypeDefault
        # but if it is a group, then it should be an int
        if field.startswith(GroupMgr.prefix):
            r='i4'
        if field in self.dtypeMap:
            r= self.dtypeMap[field]
        return r

    def fmt(self,field):
        r=self.fmtDefault
        # but if it is a group, then it should be an int
        if field.startswith(GroupMgr.prefix):
            r='%i'
        if field in self.fmtMap: # or if we already know what it should be
            r= self.fmtMap[field]
        return r

    def multvalue(self,field):
        r=self.multDefault
        if field in self.multMap:
            r= self.multMap[field]
        return r





