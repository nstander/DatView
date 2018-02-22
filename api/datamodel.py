from PyQt4.QtCore import QObject,pyqtSignal
import numpy as np
from .filters import *
from .groupmgr import GroupMgr


class DataModel(QObject):
    filterchange=pyqtSignal()
    nameind=0
    dtypeind=1
    fmtind=2
    hrmap={ 'run'       : ('Run', 'f4','%i'),
            'subcxi'    : ('CXI File #', 'f4','%i'),
            'class'     : ('CXI Class','f4','%i'),
            'event'     : ('Event','f4','%i'),
            'id'        : ('Internal ID','U12','%s'), #Outdated, for support with older files
            'multi'     : ('Crystals Per Frame','f4','%i'),
            'multiid'   : ('Crystal # On Frame','f4','%i'),
            'a'         : (' A Axis (nm)','f4','%f'),
            'b'         : (' B Axis (nm)','f4','%f'),
            'c'         : (' C Axis (nm)', 'f4','%f'),
            'alpha'     : ('Alpha (deg)', 'f4','%f'),
            'beta'      : ('Beta (deg)', 'f4','%f'),
            'gamma'     : ('Gamma (deg)', 'f4','%f'),
            'indby'     : ('Indexed By','U50','%s'),
            'phoen'     : ('Photon Energy', 'f4','%f'),
            'bmdv'      : ('Beam Divergence', 'f4','%f'),
            'bmbw'      : ('Beam Bandwidth', 'f4','%f'),
            'npeak'     : ('Number of Cheetah Peaks', 'f4','%i'),
            'prorad'    : ('Profile Radius (nm^-1)','f4','%f'),
            'detdx'     : ('Detector X Shift (mm)', 'f4','%f'),
            'detdy'     : ('Detector Y Shift (mm)','f4','%f'),
            'reslim'    : ('Diffraction Resolution Limit (nm^-1)','f4','%f'),
            'nref'      : ('Number of Reflections', 'f4','%i'),
            'nsref'     : ('Number of Saturated Reflections','f4','%i'),
            'niref'     : ('Number of implausibly negative reflections','f4','%i'),
            'o1'        : ('astar[0]','f4','%f'),
            'o2'        : ('astar[1]','f4','%f'),
            'o3'        : ('astar[2]','f4','%f'),
            'o4'        : ('bstar[0]','f4','%f'),
            'o5'        : ('bstar[1]','f4','%f'),
            'o6'        : ('bstar[2]','f4','%f'),
            'o7'        : ('cstar[0]','f4','%f'),
            'o8'        : ('cstar[1]','f4','%f'),
            'o9'        : ('cstar[2]','f4','%f'),
            'row'       : ('Chip Row (by Run)','f4','%i'),
            'col'       : ('Chip Column','f4','%i'),
            'chiprow'   : ('Chip Row (by Chip)','f4','%i'),
            'chipframe' : ('Frame # by Chip','f4','%i'),
            '/LCLS/machineTime' : ('Machine Time (s)','f4','%i'),
            '/LCLS/machineTimeNanoSeconds' : ('Machine Time (ns)','f4','%i'),
            '/LCLS/fiducial' : ('Fiducial','f4','%i'),
            '/cheetah/frameNumber' : ('Frame # (by Run)','f4','%i'),
            'ifile'      : ('Image file (cxi/hdf5)','U256','%s'),
            'sfile'     : ('Stream file','U256','%s'),
            'istart'    : ('Beginning of Chunk File Pointer','i4','%i'),
            'iend'      : ('End of Chunk File Pointer','i4','%i'),
            'cstart'    : ('Begin Crystal Pointer','i4','%i'),
            'cend'      : ('End Crystal Pointer','i4','%i'),
            'rstart'    : ('Reflection Start Pointer','i4','%i'),
            'rend'      : ('Reflection End Pointer','i4','%i'),
            'pstart'    : ('Peak Start Pointer','i4','%i'),
            'pend'      : ('Peak End Pointer','i4','%i'),
            'aclen'      : ('Average camera length','f4','%i'),
            'cent'      : ('Centering','U1','%s'),
            'ltype'      : ('Lattice Type','U15','%s'),
          }
    internalCols=set(['istart','iend','cstart','cend','pstart','pend','rstart','rend'])
    defaultHistograms=set(['a','b','c','alpha','beta','gamma'])
    def __init__(self,filename,groupfile=None):
        QObject.__init__(self)
        self.cols=[]
        with open(filename) as dfile:
            self.hdrline=dfile.readline()
            self.cols=self.hdrline.split()
        self.prettynames=[]
        dtypes=[]
        convert={}
        todigitize=[]
        self.digitized={}
        for c in self.cols:
            self.prettynames.append(self.prettyname(c))
            dtypes.append(self.dtype(c))
            if 'U' in dtypes[-1]:
                convert[self.cols.index(c)]=np.lib.npyio.asstr
                todigitize.append(c)
        self.rdata=np.loadtxt(filename,skiprows=1,converters=convert,
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
        else:
            self.data=self.rdata
        self.filtered=self.data
        self.topfilter=AndFilter(self.data.shape)
        self.topfilter.filterchange.connect(self.applyFilters)
        self.mincache={}
        self.maxcache={}
        self.groupmgr=None
        if groupfile:
            self.groupmgr=GroupMgr(groupfile)

    def prettyname(self,field):
        r=field
        if r.startswith(GroupMgr.prefix):
            r=field[len(GroupMgr.prefix):]
        if r in DataModel.hrmap:
            r=DataModel.hrmap[r][0]
        return r

    def dtype(self,field):
        r='f4' # assume float
        if field in DataModel.hrmap:
            r= DataModel.hrmap[field][1]
        return r

    def fmt(self,field):
        r='%f' # assume float
        # but if it is a group, then it should be an int
        if field.startswith(GroupMgr.prefix):
            r='%i'
        if field in DataModel.hrmap: # or if we already know what it should be
            r= DataModel.hrmap[field][2]
        return r

    def hasLabels(self,field):
        return self.groupmgr is not None and field.startswith(GroupMgr.prefix) or field in self.digitized

    def labels(self,field):
        if self.hasLabels(field):
            if field in self.digitized:
                return self.digitized[field]
            return self.groupmgr.values(field[len(GroupMgr.prefix):])
        return []

    def isCategorical(self,field):
        """Return true if values in field are categorical or discrete. Basically flags what should be
           a bar chart versus histogram. Groups are always categorical, columns stored as strings are
           always categorical and some columns with known limited values are specified categorical such
           as multi """
        return field.startswith(GroupMgr.prefix) or 'U' in self.dtype(field) or field in ['subcxi','class','multi','multiid']

    def isFiltered(self):
        return self.topfilter.isActive()

    def addFilter(self,toAdd):
        self.topfilter.addChild(toAdd)

    def applyFilters(self):
        print ("DM applyFilters")
        self.filtered=self.data[self.topfilter.keep]
        self.filterchange.emit()

    def fieldmin(self,field):
        if field not in self.mincache:
            valid = self.data[field]
            valid = valid[valid != -1]
            self.mincache[field]=np.min(valid)
        return self.mincache[field]

    def fieldmax(self,field):
        if field not in self.maxcache:
            self.maxcache[field]=np.max(self.data[field])
        return self.maxcache[field]

    def saveSelDat(self,fname):
        formats=[]
        for c in self.cols:
            formats.append(self.fmt(c))
        np.savetxt(fname,self.rdata[self.topfilter.keep],fmt=formats,delimiter='\t',header=self.hdrline[:-1],comments='')

    def canSaveLst(self):
        return 'ifile' in self.cols# or (GroupMgr.prefix + "ifile") in self.cols

    def saveSelLst(self,fname):
        assert self.canSaveLst()
        with open(fname,'w') as fout:
            if 'event' in self.cols:
                for i in range(len(self.filtered)):
                    fout.write('%s //%i\n'%(self.filtered['ifile'][i],self.filtered['event'][i]))
            else:
                for i in range(len(self.filtered)):
                    fout.write('%s\n'%self.filtered['ifile'][i])                

    def canSaveStream(self):
        return 'sfile' in self.cols and 'istart' in self.cols and \
                (('cstart' in self.cols and 'cend' in self.cols) or \
                ('iend' in self.cols and self.data['iend'][0] != -1)) 

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

        # If the file was by chunk, then 'cend' will be valid. If it's -1, then we're looking
        # at a crystal file
        chunkmode='iend' in self.cols and len(self.filtered) and self.filtered['iend'][0] != -1
        print('iend' in self.cols , len(self.filtered) , self.filtered['iend'][0] != -1)

        with open(fname,'w') as fout:
            print ("opened output")
            for i in range(len(self.filtered)):
                print(i)
                streamfile=self.filtered['sfile'][i]
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
                        print(line)
                        line=curfile.readline()
                    needheader=False
                    print ("header out done")
                curfile.seek(self.filtered['istart'][i])
                if chunkmode:
                    print ("chunk mode start")
                    fout.write(curfile.read(self.filtered['iend'][i] - self.filtered['istart'][i]))
                    print ("chunk mode end")
                else:
                    # This may be a multicrystal chunk and we only want the specific crystal
                    # asked for. So, write out lines until a begin crystal line, then jump to
                    # the correct crystal and output that.
                    print ("cyrstal mode start")
                    line=curfile.readline()
                    while line and line != '--- Begin crystal\n':
                        fout.write(line)
                        line=curfile.readline()
                    print ("End chunk header")
                    curfile.seek(self.filtered['cstart'][i])
                    fout.write(curfile.read(self.filtered['cend'][i] - self.filtered['cstart'][i]))
                    fout.write('----- End chunk -----\n') # Add on the end chunk line
                    print ("End crystal (and chunk)")
        if curfile is not None:
            curfile.close()
                    
                    
            

        



    
