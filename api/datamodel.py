from PyQt4.QtCore import QObject,pyqtSignal
import numpy as np


class DataModel(QObject):
    filterchange=pyqtSignal()
    nameind=0
    dtypeind=1
    fmtind=2
    hrmap={ 'run'       : ('Run', 'f4','%i'),
            'subcxi'    : ('CXI SubFile', 'f4','%i'),
            'class'     : ('CXI class','f4','%i'),
            'event'     : ('Event','f4','%i'),
            'id'        : ('Internal ID','U12','%s'),
            'multi'     : ('Crystals Per Frame','f4','%i'),
            'a'         : ('Cell A Axis (nm)','f4','%f'),
            'b'         : ('Cell B Axis (nm)','f4','%f'),
            'c'         : ('Cell C Axis (nm)', 'f4','%f'),
            'alpha'     : ('Alpha Angle', 'f4','%f'),
            'beta'      : ('Beta Angle', 'f4','%f'),
            'gamma'     : ('Gamma Angle', 'f4','%f'),
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
    internalcols=set(['istart','iend','cstart','cend','pstart','pend','rstart','rend'])
    defaulthistograms=['a','b','c','alpha','beta','gamma']
    def __init__(self,filename):
        QObject.__init__(self)
        self.cols=[]
        with open(filename) as dfile:
            self.hdrline=dfile.readline()
            self.cols=self.hdrline.split()
        self.prettynames=[]
        self.dtypes=[]
        convert={}
        for c in self.cols:
            self.prettynames.append(DataModel.hrmap[c][DataModel.nameind])
            self.dtypes.append(DataModel.hrmap[c][DataModel.dtypeind])
            if 'U' in self.dtypes[-1]:
                convert[self.cols.index(c)]=np.lib.npyio.asstr
        self.data=np.loadtxt(filename,skiprows=1,converters=convert,
                             dtype={'names':tuple(self.cols),'formats':tuple(self.dtypes)})
        self.filters={}
        self.filtered=self.data

    def prettyname(self,field):
        return DataModel.hrmap[field][DataModel.nameind]

    def isFiltered(self):
        return len(self.filters) > 0

    def addFilter(self,field,fmin,fmax):
        self.filters[field]=(fmin,fmax)
        self.applyFilters()

    def clearFilter(self,field):
        del self.filters[field]
        self.applyFilters()

    def applyFilters(self):
        if len(self.filters) > 0:
            keep=np.ones((self.data.shape[0],),dtype=bool)
            for k,v in self.filters.items():
                keep &= (self.data[k] >= v[0])
                keep &= (self.data[k] < v[1])
            self.filtered=self.data[keep]
        else:
            self.filtered=self.data
        self.filterchange.emit()

    def saveSelDat(self,fname):
        formats=[]
        for c in self.cols:
            formats.append(DataModel.hrmap[c][DataModel.fmtind])
        np.savetxt(fname,self.filtered,fmt=formats,delimiter='\t',header=self.hdrline[:-1],comments='')

    def canSaveLst(self):
        return 'ifile' in self.cols

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
                    
                    
            

        



    
