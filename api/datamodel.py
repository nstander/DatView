# datview/api/datamodel.py
# Main api of program. DataModel contains the data and filters, and manages all load and save options. 
# Author Natasha Stander

try:
    from PyQt5.QtCore import QObject,pyqtSignal
except ImportError:
    from PyQt4.QtCore import QObject,pyqtSignal

import numpy as np
from .filters import *
from .groupmgr import GroupMgr
import lxml.etree as ElementTree
from .modelcfg import ModelConfig
import sys


class DataModel(QObject):
    filterchange=pyqtSignal()
    sortchange=pyqtSignal()
    filterModelChange=pyqtSignal(GroupFilter)
    stackChange=pyqtSignal()
    sortColumnName="datview_sort_order"
    compareGroupName="datview_compare_group"
    compareIndexName="datview_compare_row"
    genColSeparator="*"
    cmpColTemplate="%s*cmp*%i*%i" # arguments field, compare group 1, compare group 2

    def __init__(self,filename,groupfile=None,cfg=None):
        QObject.__init__(self)
        if cfg is None:
            self.cfg = ModelConfig()
        else:
            self.cfg = cfg
        self.cols=[]
        self.hdrline=None
        self.digitized={}
        self.rdata = None
        self.data = None
        self.npfile = None
        self.cmparray=None
        
        if filename.endswith(".npz"):
            self.loadNumpy(filename)
        else:
            self.loadtxt(filename)

        self.filtered=self.data
        self.rootfilter=AndFilter(self.data.shape) # Includes filters, partitions, flags
        self.topfilter=AndFilter(self.data.shape) # Top of filters Tree
        self.rootfilter.addChild(self.topfilter)
        self.partitionfilter=DataFilter(np.ones(self.data.shape,dtype=bool))
        self.rootfilter.addChild(self.partitionfilter)
        self.flagFilter=DataFilter(np.zeros(self.data.shape,dtype=bool))
        self.flagFilter.setActive(False)
        self.rootfilter.addChild(self.flagFilter)
        self.rootfilter.filterchange.connect(self.applyFilters)
        self.internalFilterChanges=False

        self.mincache={}
        self.maxcache={}
        self.tmincache={}
        self.labelcache={}
        self.groupmgr=None
        if groupfile:
            self.groupmgr=GroupMgr(groupfile)
        self.selfilters={}
        self.sortlst=[]
        self.reverseSort=False
        self.limit=None
        self.limitModeRandom = True
        self.stacks=None


    def loadtxt(self,filename):
        """Called from __init__, not intended to be called by users"""
        with open(filename) as dfile:
            self.hdrline=dfile.readline().strip()
            if self.hdrline.startswith("CrystFEL stream format"):
                print("Usage: This input file (%s) looks like a CrystFEL stream file. It should be a dat file. Please run \n\tdatgen.py -o output.dat %s\nand run this program on the output."%(filename,filename),file=sys.stderr)
                sys.exit()
            self.cols=self.hdrline.split(self.cfg.sep)
            if self.cfg.commentchar is not None:
                self.cols[0] = self.cols[0].replace(cfg.commentchar, "")
        dtypes=[]
        convert={}
        todigitize=[]
        for c in self.cols:
            dtypes.append(self.cfg.dtype(c))
            if 'U' in dtypes[-1]:
                convert[self.cols.index(c)]=np.lib.npyio.asstr
                todigitize.append(c)
        self.rdata=np.loadtxt(filename,skiprows=1,converters=convert,delimiter=self.cfg.sep,
                             dtype={'names':tuple(self.cols),'formats':tuple(dtypes)})
        # We may have string inputs, even with grouping, and it will simplify all the other code
        # if at this point we digitize any string inputs so other code will only ever see numbers
        # and the labels are obtained through the common interface used for grouping anyway. Also,
        # apply conversions in the configuration file.
        dtypes2=[]
        for dtype in dtypes:
            if 'U' in dtype:
                dtypes2.append('i4')
            else:
                dtypes2.append(dtype)
        self.cols.append(DataModel.sortColumnName)
        dtypes2.append('u4')
        self.data=np.empty(self.rdata.shape,dtype={'names':tuple(self.cols),'formats':tuple(dtypes2)})
        for c in self.cols:
            if c in todigitize:
                lbls,inverse=np.unique(self.rdata[c],return_inverse=True)
                self.digitized[c]=np.array(lbls.tolist())
                self.data[c]=inverse
            elif c == DataModel.sortColumnName:
                self.data[c]=np.arange(len(self.rdata))
            else:
                self.data[c]=self.rdata[c]
                if c in self.cfg.invert:
                    self.data[c] = 1/self.data[c]
                if self.cfg.multvalue(c) != 1:
                    self.data[c][self.data[c]!=-1]*=self.cfg.multvalue(c)

    def loadNumpy(self,filename):
        self.npfile = np.load(filename)
        self.data=self.npfile["data"]
        self.cols=list(self.data.dtype.names)
        for dkey in self.npfile["digitizedkeys"].tolist():
            self.digitized[dkey]=None
        if "cmparray" in self.npfile.keys():
            self.cmparray=self.npfile["cmparray"]
        

    def prettyname(self,field):
        origfield=field
        field=self.datafield(field)
        if DataModel.genColSeparator in origfield:
            parts=origfield.split(DataModel.genColSeparator)
            assert parts[1] == "cmp" # Only one that should appear right now
            group1=int(parts[2])
            return "%s of %s" %(self.cfg.prettyname(field), self.stringValue(DataModel.compareGroupName,group1))
        return self.cfg.prettyname(field)

#########################################
###           Categorical             ###
#########################################

    def hasLabels(self,field):
        field=self.datafield(field)
        return self.groupmgr is not None and field.startswith(GroupMgr.prefix) or field in self.digitized

    def canAccessDigitized(self,field):
        """ Lazy load digitized values from numpy file """
        if field in self.digitized:
            if self.digitized[field] is None:
                assert self.npfile is not None
                self.digitized[field]=self.npfile[field]
            return True
        return False

    def labels(self,field):
        field=self.datafield(field)
        if self.hasLabels(field):
            if field not in self.labelcache:
                self.labelcache[field]={}
                if self.canAccessDigitized(field):
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
        if self.isCategorical(field):
            if field not in self.labelcache:
                self.labels(field)
            return self.labelcache[field]["ints"]
        return []
        

    def isCategorical(self,field):
        """Return true if values in field are categorical or discrete. Basically flags what should be
           a bar chart versus histogram. Groups are always categorical, columns stored as strings are
           always categorical and some columns with known limited values are specified categorical such
           as multi """
        return field.startswith(GroupMgr.prefix) or field in self.digitized or field in self.cfg.categorical

    def intValues(self,field):
        """Meant for categorical values, return list of all possible"""
        field=self.datafield(field)
        if self.canAccessDigitized(field):
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

        if self.canAccessDigitized(field):
            if v >= 0 and v < len(self.digitized[field]):
                v = self.digitized[field][int(v)]
            else:
                v=""
        elif field.startswith(GroupMgr.prefix) and self.groupmgr is not None:
            v = self.groupmgr.value(field[len(GroupMgr.prefix):],v)
        return str(v)

    def intValue(self,field,i):
        field=self.datafield(field)

        r=None
        if self.canAccessDigitized(field):
            r=np.where(self.digitized[field] == i)[0][0]
        elif field.startswith(GroupMgr.prefix) and self.groupmgr is not None:
            r = self.groupmgr.gid(field[len(GroupMgr.prefix):],i)
        if r is None:
            try:
                r=int(i)
            except ValueError:
                r=None
                pass
        return r

    def datafield(self,field):
        """Return the field name as it appears in the structured array"""
        if field is not None and field not in self.cols: 
            if DataModel.genColSeparator in field:
                field=field.split(DataModel.genColSeparator)[0]
            if (GroupMgr.prefix+field) in self.cols:
                field=GroupMgr.prefix+field
            elif field[len(GroupMgr.prefix):] in self.cols:
                field = field[len(GroupMgr.prefix):]
        return field

#########################################
###            Filtering              ###
#########################################                

    def isFiltered(self):
        return np.count_nonzero(self.rootfilter.getKeep()) < len(self.data)

    def addFilter(self,toAdd):
        self.topfilter.addChild(toAdd)

    def selectionFilter(self,field):
        origfield=field
        field=self.datafield(field)
        if field not in self.selfilters and origfield not in self.selfilters:
            if DataModel.genColSeparator in origfield:
                parts=origfield.split(DataModel.genColSeparator)
                assert parts[1] == "cmp" # Only one that should appear right now
                group1=int(parts[2])
                group2=int(parts[3])

                f1=BetweenFilter(self.fieldmin(field)-1,self.fieldmax(field)+1,self.cmpvalues(field)[:,group1],field)
                f2=BetweenFilter(self.fieldmin(field)-1,self.fieldmax(field)+1,self.cmpvalues(field)[:,group2],field)
                f1.setActive(False)
                f2.setActive(False)
                nm="%s,%s"%(self.stringValue(DataModel.compareGroupName,group1),self.stringValue(DataModel.compareGroupName,group2))
                f=PairBetweenFilter(self.data.shape,self.cmparray,f1,f2,group1,group2,nm)
                self.addFilter(f)
                self.selfilters[origfield]=f1
                self.selfilters[DataModel.cmpColTemplate%(parts[0],group2,group1)]=f2
            else:
                f=BetweenFilter(self.fieldmin(field)-1,self.fieldmax(field)+1,self.data[field],field)
                f.setActive(False)
                self.addFilter(f)
                self.selfilters[field]=f
        if origfield in self.selfilters:
            return self.selfilters[origfield]
        return self.selfilters[field]

    def applyFilters(self):
        self.filtered=self.data[self.rootfilter.getKeep()]
        if not self.internalFilterChanges:
            self.filterchange.emit()

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

    def trueFieldMin(self,field):
        field=self.datafield(field)
        if field not in self.tmincache:
            self.tmincache[field]=np.min(self.data[field])
        return self.tmincache[field]

    def fieldmax(self,field):
        field=self.datafield(field)
        if field not in self.maxcache:
            self.maxcache[field]=np.max(self.data[field])
        return self.maxcache[field]

#########################################
###            Partition              ###
#########################################  

    def partitionMulti(self,fields,minimums=[],maximums=[],nums=[]):
        l=len(fields)
        minimums+=[None]*(l-len(minimums))
        maximums+=[None]*(l-len(maximums))
        nums+=[None]*(l-len(nums))
            
        cur=None
        next=None
        for i,field in enumerate(fields):
            if cur is None:
                cur=self.partition(field,minimums[i],maximums[i],nums[i])
            else:
                next=self.partition(field,minimums[i],maximums[i],nums[i])
                tmpcur=cur
                cur={}
                for n1,v1 in tmpcur.items():
                    for n2,v2 in next.items():
                        v=v1 & v2
                        if np.count_nonzero(v):
                            cur[n1+"_"+n2]=v
        return cur
                

    def partition(self,field,minimum=None,maximum=None,num=None):
        field=self.datafield(field)
        maxWasNone = maximum is None
        if minimum is None:
            minimum = self.fieldmin(field)
        if maximum is None:
            maximum = self.fieldmax(field)
        if num is None:
            if self.isCategorical(field):
                edges=np.array(self.intValues(field))
                edges=edges[(edges>=minimum) & (edges<=maximum)]
                if maxWasNone:
                    edges=np.append(edges,maximum+1)
            else:
                edges=np.linspace(minimum,maximum,11)
        else:
            edges=np.linspace(minimum,maximum,num+1)

        ret={}
        for i in range(len(edges)-1):
            if num is None and self.isCategorical(field):
                nm=self.stringValue(field,edges[i])
            else:
                nm="%.2f-%.2f"%(edges[i],edges[i+1])
            if i == len(edges)-2 and maxWasNone:
                dt=(self.data[field]>=edges[i]) & (self.data[field]<=edges[i+1])
            else:
                dt=(self.data[field]>=edges[i]) & (self.data[field]<edges[i+1])
            if np.count_nonzero(dt):
                ret[nm]=dt
        return ret

    def setPartition(self,keep):
        """Set the current partition filter's keep."""
        self.partitionfilter.setkeep(keep)

    def clearPartition(self):
        """Set the current partition filter's keep."""
        self.partitionfilter.setkeep(np.ones(self.data.shape,dtype=bool))

    def datacol(self,field,filtered=False,respectPartition=True):
        origfield=field
        field=self.datafield(field)
        keep=np.ones(self.data.shape,dtype=bool)

        if respectPartition:
            keep &=self.partitionfilter.getKeep()
        if filtered:
            keep &=self.topfilter.getKeep()

        if DataModel.genColSeparator in origfield:
            parts=origfield.split(DataModel.genColSeparator)
            assert parts[1] == "cmp" # Only one that should appear right now
            group1=int(parts[2])
            group2=int(parts[3])
            validpairs=(self.cmparray[:,group1] != -1) & (self.cmparray[:,group2] != -1)
            keepvalid=(keep[self.cmparray[validpairs,group1].astype(int)]) & (keep[self.cmparray[validpairs,group2].astype(int)])
            finalret=self.cmparray[keepvalid,group1]
            return self.data[field][finalret.astype(int)]
        return self.data[field][keep]

    def stackedDataCol(self,field,filtered=False,defaultcolor='b',respectPartition=True, keep=None,stacks=0):
        """Return [[arrays],[colors],[labels]]"""
        field=self.datafield(field)
        finalkeep=np.ones(self.data.shape,dtype=bool)
        if keep is not None:
            finalkeep &=keep
        if respectPartition:
            finalkeep &=self.partitionfilter.getKeep()
        if filtered:
            finalkeep &=self.topfilter.getKeep()

        if stacks == 0:
            stacks=self.stacks
        if stacks is None:
            return [[ self.data[field][finalkeep] ], [defaultcolor] , ["all"] ]
        else:
            a=[]
            c=[]
            l=[]
            for i in range(len(stacks[0])):
                d= self.data[field][finalkeep&stacks[0][i]]
                if len(d):
                    a.append(d)
                    c.append(stacks[1][i])
                    l.append(stacks[2][i])
        return [a,c,l]
                
            

    def setStacks(self,stack):
        self.stacks=stack
        self.stackChange.emit()

    def hasComparisons(self):
        return self.cmparray is not None and len(self.cmparray.shape) > 1

    def cmpvalues(self,field):
        assert self.hasComparisons()
        field=self.datafield(field)
        values=np.ones(self.cmparray.shape)*-1
        valid=self.cmparray != -1
        values[valid]=self.data[field][self.cmparray[valid].astype(int)]
        return values


        

#########################################
###            Load/Save              ###
#########################################

    def onSortChange(self):
        outarr=np.arange(len(self.data))
        if len(self.sortlst):
            outarr=np.argsort(self.data,order=self.sortlst)
            if self.reverseSort:
                outarr = np.flipud(outarr)
        self.data[DataModel.sortColumnName][outarr]=np.arange(len(self.data))
        self.filtered=self.data[self.rootfilter.getKeep()]
        self.sortchange.emit()

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

    def saveByPartitions(self,fname,function,partitions=None,internal=True,appendName=True):
        if partitions is not None:
            previous=self.partitionfilter.getKeep()
            self.internalFilterChanges = internal
            for k,v in sorted(partitions.items()):
                self.setPartition(v)
                if np.count_nonzero(self.rootfilter.getKeep()):
                    if appendName:
                        function(fname+"_"+k)
                    else:
                        function(fname,k)
            self.setPartition(previous)
            self.internalFilterChanges = False
        else:
            function(fname)


    def saveSelDat(self,fname):
        formats=[]
        if self.hasComparisons():
            rdata=self.data
            for c in self.cols:
                formats.append(self.cfg.fmt(c))
        else:
            for c in self.cols:
                if c != DataModel.sortColumnName:
                    formats.append(self.cfg.fmt(c))
            rdata = self.rdata

        if rdata is None:
            assert self.npfile is not None
            rdata = self.npfile["rdata"]
        outarr=rdata[self.rootfilter.getKeep()][self.outArrIndices()]
        d='\t'
        if self.cfg.sep is not None:
            d=self.cfg.sep
        hline = self.hdrline
        if hline is None:
            sep=self.cfg.sep
            if sep is None:
                sep = "\t"
            
            if self.cfg.commentchar is None:
                hline = sep.join(rdata.dtype.names)
            else:
                hline = sep.join((self.cfg.commentchar,*rdata.dtype.names))          
        np.savetxt(fname,outarr,fmt=formats,delimiter=d,header=hline,comments='')
        print ("Wrote",fname)

    def canSaveLst(self):
        return 'ifile' in self.cols or ((GroupMgr.prefix + "ifile") in self.cols and self.groupmgr is not None)

    def saveSelLst(self,fname):
        assert self.canSaveLst()
        outarr=self.outArrIndices()
        with open(fname,'w') as fout:
            for i in outarr:
                if 'event' in self.cols and self.filtered['event'][i] != -1:
                    fout.write('%s //%i\n'%(self.value('ifile',i) ,self.filtered['event'][i]))
                else:
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

    def canSaveNumpy(self):
        return self.npfile is None # Don't resave a numpy file as a numpy file. Too complicated.

    def saveAllNumpy(self,fname):
        assert self.canSaveNumpy()
        np.savez_compressed(fname,data=self.data,rdata=self.rdata,digitizedkeys=np.asarray(sorted(self.digitized.keys())),**self.digitized)

    def saveFilters(self,fname):
        root=ElementTree.Element("filters")
        self.topfilter.toXML(root)
        et=ElementTree.ElementTree(root)
        et.write(fname,pretty_print=True)
        print("Wrote",fname)

    def loadFilters(self,fname):
        self.topfilter.setActive(False) #Invalidate current, easier than deleting
        self.selfilters = {} # clear these
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
        self.rootfilter.addChild(self.topfilter)
        self.filterModelChange.emit(self.topfilter)
        self.applyFilters()

    def loadFilterRecursive(self,xmlEl,filterpar):
        for child in xmlEl:
            if child.tag == "or":
                f=OrFilter(self.data.shape)
                loadFilterRecursive(child,f)
            elif child.tag == "and":
                f=AndFilter(self.data.shape)
                self.loadFilterRecursive(child,f)
            elif child.tag == "pairbetween":
                if not self.hasComparisons():
                    continue # Don't load this filter if no comparison array
                tmp=AndFilter(self.data.shape)
                self.loadFilterRecursive(child,tmp)
                if len(tmp.children) != 2:
                    continue # Something went wrong, maybe field doesn't exist
                
                field=tmp.children[0].field
                group1=int(child.get("col1"))
                c1=BetweenFilter(tmp.children[0].minimum,tmp.children[0].maximum,self.cmpvalues(field)[:,group1],field)
                

                field=tmp.children[1].field
                group2=int(child.get("col2"))
                c2=BetweenFilter(tmp.children[1].minimum,tmp.children[1].maximum,self.cmpvalues(field)[:,group2],field)

                nm1=DataModel.cmpColTemplate%(field,group1,group2)
                nm2=DataModel.cmpColTemplate%(field,group2,group1)

                if field in self.selfilters and self.selfilters[field] == tmp.children[0]:
                    del self.selfilters[field]
                if nm1 not in self.selfilters:
                    self.selfilters[nm1]=c1
                if nm2 not in self.selfilters:
                    self.selfilters[nm2]=c2

                f=PairBetweenFilter(self.data.shape,self.cmparray,c1,c2,group1,group2,child.get("namestr"))
            else: # field filter
                if self.datafield(child.get("field")) not in self.cols:
                    continue # Filter doesn't apply
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
                elif child.tag == "max":
                    if not self.hasComparisons():
                        continue # Don't load this filter if no comparison array
                    f=MaxFilter(self.data.shape,self.cmparray,self.cmpvalues(child.get("field")),child.get("field"))
                elif child.tag == "min":
                    if not self.hasComparisons():
                        continue # Don't load this filter if no comparison array
                    f=MinFilter(self.data.shape,self.cmparray,self.cmpvalues(child.get("field")),child.get("field"))
                elif child.tag == "allbetween":
                    if not self.hasComparisons():
                        continue # Don't load this filter if no comparison array
                    f=AllBetweenFilter(self.data.shape,self.cmparray,self.cmpvalues(child.get("field")),child.get("field"),\
                        float(child.get("min")),float(child.get("max")))
                elif child.tag == "anybetween":
                    if not self.hasComparisons():
                        continue # Don't load this filter if no comparison array
                    f=AnyBetweenFilter(self.data.shape,self.cmparray,self.cmpvalues(child.get("field")),child.get("field"),\
                        float(child.get("min")),float(child.get("max")))
                elif child.tag == "allsame":
                    if not self.hasComparisons():
                        continue # Don't load this filter if no comparison array
                    f=AllSameFilter(self.data.shape,self.cmparray,self.cmpvalues(child.get("field")),child.get("field"))
                elif child.tag == "anydifferent":
                    if not self.hasComparisons():
                        continue # Don't load this filter if no comparison array
                    f=AnyDifferentFilter(self.data.shape,self.cmparray,self.cmpvalues(child.get("field")),child.get("field"))
                else:
                    assert False #Unsupported
            f.setActive(child.get("active") == "True")
            filterpar.addChild(f)

    def hasStreamPeaks(self):
        return ('sfile' in self.cols or \
                  ((GroupMgr.prefix+"sfile") in self.cols and self.groupmgr is not None)) \
                and 'pstart' in self.cols and 'pend' in self.cols

    def streamPeaks(self,datarow):
        peakx=[]
        peaky=[]
        with open(self.value("sfile",datarow,False)) as sfile:
            sfile.seek(self.data["pstart"][datarow])
            end=self.data["pend"][datarow]
            while(sfile.tell() != end):
                l=sfile.readline().strip().split()
                try:
                    x=float(l[0])
                    y=float(l[1])
                    peakx.append(x)
                    peaky.append(y)
                except ValueError:
                    pass # First line won't be convertable
        return peakx, peaky

    def hasStreamReflections(self):
        return ('sfile' in self.cols or \
                  ((GroupMgr.prefix+"sfile") in self.cols and self.groupmgr is not None)) \
                and 'rstart' in self.cols and 'rend' in self.cols

    def streamReflections(self,datarow):
        peakx=[]
        peaky=[]
        hkl=[]
        start = self.data["rstart"][datarow]
        if start != -1: # Have Reflections (might not if not indexed)
            with open(self.value("sfile",datarow,False)) as sfile:
                sfile.seek(start)
                end=self.data["rend"][datarow]
                while(sfile.tell() != end):
                    l=sfile.readline().strip().split()
                    try:
                        x=float(l[7])
                        y=float(l[8])
                        peakx.append(x)
                        peaky.append(y)
                        hkl.append(' '.join(l[0:3]))
                    except ValueError:
                        pass # First line won't be convertable
        return peakx, peaky, hkl

        



    
