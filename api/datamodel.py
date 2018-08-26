# datview/api/datamodel.py
# Main api of program. DataModel contains the data and filters, and manages all load and save options. 
# Author Natasha Stander

try:
    from PyQt5.QtCore import QObject,pyqtSignal
except ImportError:
    from PyQt4.QtCore import QObject,pyqtSignal

import numpy as np
from .filters import *
from .filtermodel import FilterModel
from .groupmgr import GroupMgr
import lxml.etree as ElementTree
from .modelcfg import ModelConfig


class DataModel(QObject):
    filterchange=pyqtSignal()
    def __init__(self,filename,groupfile=None,cfg=None):
        QObject.__init__(self)
        if cfg is None:
            self.cfg = ModelConfig()
        else:
            self.cfg = cfg
        self.cols=[]
        with open(filename) as dfile:
            self.hdrline=dfile.readline().strip()
            self.cols=self.hdrline.split(self.cfg.sep)
            if cfg.commentchar is not None:
                self.cols[0] = self.cols[0].replace(cfg.commentchar, "")
        dtypes=[]
        convert={}
        todigitize=[]
        self.digitized={}
        for c in self.cols:
            dtypes.append(self.cfg.dtype(c))
            if 'U' in dtypes[-1]:
                convert[self.cols.index(c)]=np.lib.npyio.asstr
                todigitize.append(c)
        self.rdata=np.loadtxt(filename,skiprows=1,converters=convert,delimiter=self.cfg.sep,
                             dtype={'names':tuple(self.cols),'formats':tuple(dtypes)})
        # We may have string inputs, even with grouping, and it will simplify all the other code
        # if at this point we digitize any string inputs so other code will only ever see numbers
        # and the labels are obtained through the common interface used for grouping anyway.
        if len(todigitize):
            dtypes2=[]
            for dtype in dtypes:
                if 'U' in dtype:
                    dtypes2.append('i4')
                else:
                    dtypes2.append(dtype)
            self.data=np.empty(self.rdata.shape,dtype={'names':tuple(self.cols),'formats':tuple(dtypes2)})
            for c in self.cols:
                if c in todigitize:
                    lbls,inverse=np.unique(self.rdata[c],return_inverse=True)
                    self.digitized[c]=lbls
                    self.data[c]=inverse
                else:
                    self.data[c]=self.rdata[c]
                    if c in self.cfg.invert:
                        self.data[c] = 1/self.data[c]
                    if self.cfg.multvalue(c) != 1:
                        self.data[c][self.data[c]!=-1]*=self.cfg.multvalue(c)
        else:
            self.data=self.rdata
        self.filtered=self.data
        self.topfilter=AndFilter(self.data.shape)
        self.topfilter.filterchange.connect(self.applyFilters)
        self.filtermodel=FilterModel(self.topfilter,self)
        self.mincache={}
        self.maxcache={}
        self.labelcache={}
        self.groupmgr=None
        if groupfile:
            self.groupmgr=GroupMgr(groupfile)
        self.selfilters={}
        self.sortlst=[]
        self.reverseSort=False
        self.limit=None
        self.limitModeRandom = True
        

    def prettyname(self,field):
        return self.cfg.prettyname(field)

#########################################
###           Categorical             ###
#########################################

    def hasLabels(self,field):
        field=self.datafield(field)
        return self.groupmgr is not None and field.startswith(GroupMgr.prefix) or field in self.digitized

    def labels(self,field):
        field=self.datafield(field)
        if self.hasLabels(field):
            if field not in self.labelcache:
                self.labelcache[field]={}
                if field in self.digitized:
                    self.labelcache[field]["labels"] = self.digitized[field]
                    self.labelcache[field]["ints"] = np.arange(len(self.digitized[field]))
                else:
                    self.labelcache[field]["ints"] = np.unique(self.data[field])
                    labels=[]
                    for i in self.labelcache[field]["ints"]:
                        labels.append(self.groupmgr.value(field[len(GroupMgr.prefix):],i))
                    self.labelcache[field]["labels"] = labels
            return self.labelcache[field]["labels"]
        elif self.isCategorical(field):
            # If it is categorical, but doesn't have labels, then it has numerical values and 
            # the unique values present should be returned. This covers cases like Run or # of 
            # crystals on a frame.
            if field not in self.labelcache:
                self.labelcache[field]={}
                self.labelcache[field]["labels"]=np.unique(self.data[field])
                self.labelcache[field]["ints"]=self.labelcache[field]["labels"]
            return self.labelcache[field]["labels"]
        return []

    def labelints(self,field):
        field=self.datafield(field)
        if self.hasLabels(field):
            if field not in self.labelcache:
                self.labels()
            return self.labelcache[field]["ints"]
        return []
        

    def isCategorical(self,field):
        """Return true if values in field are categorical or discrete. Basically flags what should be
           a bar chart versus histogram. Groups are always categorical, columns stored as strings are
           always categorical and some columns with known limited values are specified categorical such
           as multi """
        return field.startswith(GroupMgr.prefix) or 'U' in self.cfg.dtype(field) or field in self.cfg.categorical

    def intValues(self,field):
        """Meant for categorical values, return list of all possible"""
        field=self.datafield(field)
        if field in self.digitized:
            return range(len(self.digitized[field])) # It's digitized 0:N-1
        elif self.groupmgr is not None and field.startswith(GroupMgr.prefix):
            return range(len(self.groupmgr.values(field[len(GroupMgr.prefix):]))) # Valid groupfiles are 0:N-1 
        else:
            vals = np.unique(self.data[field])
            r=[]
            for v in vals:
                r.append(int(v))
            return r

    def value(self,field,i,filtered=True):
        """Return the value of the field at (filtered if filtered=True) row i. Returns true value rather than digitized or group-id value"""
        field=self.datafield(field)

        if filtered:
            v=self.filtered[field][i]
        else:
            v=self.data[field][i]
        return self.stringValue(field,v)

    def stringValue(self,field,v):
        field=self.datafield(field)

        if field in self.digitized:
            if v >= 0 and v < len(self.digitized[field]):
                v = self.digitized[field][v]
            else:
                v=""
        elif field.startswith(GroupMgr.prefix) and self.groupmgr is not None:
            v = self.groupmgr.value(field[len(GroupMgr.prefix):],v)
        return str(v)

    def intValue(self,field,i):
        field=self.datafield(field)

        r=None
        if field in self.digitized:
            r=np.where(self.digitized[field] == i)[0][0]
        elif field.startswith(GroupMgr.prefix) and self.groupmgr is not None:
            r = self.groupmgr.gid(field[len(GroupMgr.prefix):],i)
        if r is None:
            try:
                r=int(i)
            except ValueError:
                print ("value error for",i)
                pass
        return r

    def datafield(self,field):
        """Return the field name as it appears in the structured array"""
        if field not in self.cols: 
            if (GroupMgr.prefix+field) in self.cols:
                field=GroupMgr.prefix+field
            elif field[len(GroupMgr.prefix):] in self.cols:
                field = field[len(GroupMgr.prefix):]
        return field

#########################################
###            Filtering              ###
#########################################                

    def isFiltered(self):
        return self.topfilter.isActive()

    def addFilter(self,toAdd):
        self.topfilter.addChild(toAdd)

    def selectionFilter(self,field):
        field=self.datafield(field)
        if field not in self.selfilters:
            f=BetweenFilter(self.fieldmin(field)-1,self.fieldmax(field)+1,self.data[field],field)
            f.setActive(False)
            self.addFilter(f)
            self.selfilters[field]=f
        return self.selfilters[field]

    def applyFilters(self):
        self.filtered=self.data[self.topfilter.keep]
        self.filterchange.emit()

    def filterModel(self):
        return self.filtermodel

    def fieldmin(self,field):
        field=self.datafield(field)
        if field not in self.mincache:
            valid = self.data[field]
            valid = valid[valid != -1]
            if len(valid):
                self.mincache[field]=np.min(valid)
            else:
                self.mincache[field]=-1
        return self.mincache[field]

    def fieldmax(self,field):
        field=self.datafield(field)
        if field not in self.maxcache:
            self.maxcache[field]=np.max(self.data[field])
        return self.maxcache[field]

#########################################
###            Load/Save              ###
#########################################

    def outArrIndices(self,applyLimit=True):
        outarr=np.arange(len(self.filtered))
        if len(self.sortlst):
            outarr=np.argsort(self.filtered,order=self.sortlst)
            if self.reverseSort:
                outarr = np.flipud(outarr)
        if applyLimit and self.limit is not None and len(outarr) > self.limit:
            if self.limitModeRandom:
                keep=np.random.permutation(np.arange(len(outarr)))[:self.limit] # Select random set of size self.limit
                outarr=outarr[np.sort(keep)] # Maintain previous sorting order by sorting keep
            else:
                outarr=outarr[:self.limit]
        return outarr

    def saveSelDat(self,fname):
        formats=[]
        for c in self.cols:
            formats.append(self.cfg.fmt(c))
        outarr=self.rdata[self.topfilter.keep][self.outArrIndices()]
        d='\t'
        if self.cfg.sep is not None:
            d=self.cfg.sep
        np.savetxt(fname,outarr,fmt=formats,delimiter=d,header=self.hdrline,comments='')
        print ("Wrote",fname)

    def canSaveLst(self):
        return 'ifile' in self.cols or ((GroupMgr.prefix + "ifile") in self.cols and self.groupmgr is not None)

    def saveSelLst(self,fname):
        assert self.canSaveLst()
        outarr=self.outArrIndices()
        with open(fname,'w') as fout:
            if 'event' in self.cols:
                for i in outarr:
                    fout.write('%s //%i\n'%(self.value('ifile',i) ,self.filtered['event'][i]))
            else:
                for i in outarr:
                    fout.write('%s\n'%(self.value('ifile',i)))
        print ("Wrote",fname)

    def canSaveStream(self):
        return ('sfile' in self.cols or ((GroupMgr.prefix+"sfile") in self.cols and self.groupmgr is not None)) \
                and 'istart' in self.cols and 'cstart' in self.cols and 'cend' in self.cols

    def saveSelStream(self,fname):
        assert self.canSaveStream()
        # We could sort the filtered to read files in order, but keeping the order
        # will automatically allow a sorting extension and sorted stream files are
        # useful for programs that just have a start at and end after option to manipulate
        # Also, until the sorting option is implemented, the default order is in order of appearance
        # in stream files.

        # For now, don't bother caching open files because operating systems have limits on the # of 
        # open files, and it's probably faster to open and close files then to guess which files to
        # keep open
        curfile=None
        curfileName=None
        needheader=True

        with open(fname,'w') as fout:
            for i in self.outArrIndices():
                streamfile=self.value('sfile',i)
                if streamfile != curfileName:
                    if curfile is not None:
                        curfile.close()
                    curfileName=streamfile
                    curfile=open(streamfile,'r')
                if needheader:
                    curfile.seek(0)
                    line=curfile.readline()
                    while line and line != '----- Begin chunk -----\n':
                        fout.write(line)
                        line=curfile.readline()
                    needheader=False
                curfile.seek(self.filtered['istart'][i])
                if self.filtered['cstart'][i] < 0:
                    fout.write(curfile.read(self.filtered['iend'][i] - self.filtered['istart'][i]))
                else:
                    # This may be a multicrystal chunk and we only want the specific crystal
                    # asked for. So, write out lines until a begin crystal line, then jump to
                    # the correct crystal and output that.
                    line=curfile.readline()
                    while line and line != '--- Begin crystal\n':
                        fout.write(line)
                        line=curfile.readline()
                    curfile.seek(self.filtered['cstart'][i])
                    fout.write(curfile.read(self.filtered['cend'][i] - self.filtered['cstart'][i]))
                    fout.write('----- End chunk -----\n') # Add on the end chunk line
        if curfile is not None:
            curfile.close()
        print ("Wrote",fname)


    def saveFilters(self,fname):
        root=ElementTree.Element("filters")
        self.topfilter.toXML(root)
        et=ElementTree.ElementTree(root)
        et.write(fname,pretty_print=True)
        print("Wrote",fname)

    def loadFilters(self,fname):
        et=ElementTree.parse(fname)
        root = et.getroot()
        assert root.tag == "filters" and len(list(root)) == 1
        child=root[0]
        if child.tag == "and":
            self.topfilter=AndFilter(self.data.shape)
        elif child.tag == "or":
            self.topfilter=OrFilter(self.data.shape)
        else:
            assert False # Top filter must be group filter
        self.topfilter.setActive(child.get("active") == "True")
        self.loadFilterRecursive(child,self.topfilter)
        self.topfilter.filterchange.connect(self.applyFilters)
        self.applyFilters()
        self.filtermodel=FilterModel(self.topfilter,self)

    def loadFilterRecursive(self,xmlEl,filterpar):
        for child in xmlEl:
            if child.tag == "between":
                f=BetweenFilter(float(child.get("min")),float(child.get("max")),self.data[self.datafield(child.get("field"))],child.get("field"))
                if child.get("field") not in self.selfilters:
                    self.selfilters[child.get("field")] = f
            elif child.tag == "greaterequal":
                f=GreaterEqualFilter(float(child.get("min")),self.data[self.datafield(child.get("field"))],child.get("field"))
            elif child.tag == "lessthan":
                f=LessThanFilter(float(child.get("max")),self.data[self.datafield(child.get("field"))],child.get("field"))
            elif child.tag == "inset":
                allowedlst=child.get("set").split(",")
                allowedset=set()
                for v in allowedlst:
                    allowedset.add(self.intValue(child.get("field"),v))
                f=InSetFilter(allowedset,self.data[self.datafield(child.get("field"))],child.get("field"),self.stringValue)
            elif child.tag == "or":
                f=OrFilter(self.data.shape)
                loadFilterRecursive(child,f)
            elif child.tag == "and":
                f=AndFilter(self.data.shape)
                self.loadFilterRecursive(child,f)
            else:
                assert False #Unsupported
            f.setActive(child.get("active") == "True")
            filterpar.addChild(f)

        



    
