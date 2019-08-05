#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# datview/datgen.py
# Data reduction script, stream(s) -> dat
# Author Natasha Stander

import os
import argparse
import re
import h5py
import sys
import numpy as np
from math import sqrt, cos,radians

from api.groupmgr import GroupMgr

nullvalue=-1

class DatGenerator:
    streamcols=[(('class','subcxi'),re.compile('^Image filename: .*r\d{4}(?:-class(\d))?(?:-c(\d{2}))?\.(?:cxi|h5)')),
                (('run',),re.compile('^Image filename: .*r(\d{4})')),
                (('ifile',),re.compile('^Image filename: (.*)')),
                (('event',),re.compile('^Event: //(\d+)')),
                (('indby',),re.compile('^indexed_by = ([A-Za-z-]+)')),
                (('phoen',),re.compile('^photon_energy_eV = (\d+\.\d+)')),
                (('bmdv',),re.compile('^beam_divergence = (\d+\.\d+e[\+-]\d+) rad')),
                (('bmbw',),re.compile('^beam_bandwidth = (\d+\.\d+e[\+-]\d+) \(fraction\)')),
                (('aclen',),re.compile('^average_camera_length = (\d+\.\d+) m')),
                (('npeak',),re.compile('^num_peaks = (\d+)')),
                (('ltype',),re.compile('^lattice_type = ([A-Za-z-]+)')),
                (('cent',),re.compile('^centering = ([A-Z])')),
                (('a','b','c','alpha','beta','gamma'),re.compile('^Cell parameters (\d+\.\d+) (\d+\.\d+) (\d+\.\d+) nm, (\d+\.\d+) (\d+\.\d+) (\d+\.\d+) deg')),
                (('prorad',),re.compile('^profile_radius = (\d+\.\d+)')),
                (('detdx','detdy'),re.compile('^predict_refine/det_shift x = (-?\d+\.\d+) y = (-?\d+\.\d+) mm')),
                (('reslim',),re.compile('^diffraction_resolution_limit = (\d+\.\d+) nm\^-1 or')),
                (('nref',),re.compile('^num_reflections = (\d+)')),
                (('nsref',),re.compile('^num_saturated_reflections = (\d+)')),
                (('niref',),re.compile('^num_implausible_reflections = (\d+)')),
                (('o1','o2','o3'),re.compile('^astar = ([\+-]\d+\.\d+) ([\+-]\d+\.\d+) ([\+-]\d+\.\d+) nm\^-1')),
                (('o4','o5','o6'),re.compile('^bstar = ([\+-]\d+\.\d+) ([\+-]\d+\.\d+) ([\+-]\d+\.\d+) nm\^-1')),
                (('o7','o8','o9'),re.compile('^cstar = ([\+-]\d+\.\d+) ([\+-]\d+\.\d+) ([\+-]\d+\.\d+) nm\^-1'))]
    listcols = [(('class','subcxi'),re.compile('.*r\d{4}(?:-class(\d))?(?:-c(\d{2}))?\.(?:cxi|h5)')),
                (('run',),re.compile('.*r(\d{4})'))]
    allstrcols=['ifile','run','class','subcxi','event','indby','phoen','bmdv','bmbw','aclen','npeak',
                'ltype','cent','a','b','c','alpha','beta','gamma','prorad','detdx','detdy','reslim','nref',
                'nsref','niref','o1','o2','o3','o4','o5','o6','o7','o8','o9']
    internalcols=['sfile','istart','iend','cstart','cend','pstart','pend','rstart','rend','multiid','multi','vol']
    allstreamcols=allstrcols+internalcols
    alllistcols=['ifile','run','class','subcxi','event','basename']
    concatjoiner="--"
                
    def __init__(self,out,streamcols,cxicols,staticlist,integratecols,concatint,groupmgr=None):
        cxicols +=integratecols
        self.cols=streamcols+cxicols
        self.cxicols=cxicols
        self.integratecols=integratecols
        self.curCXIName=None
        self.curCXI=None
        self.curH5=None
        self.out=out
        self.groupmgr=groupmgr
        self.npdata=None
        self.npcols=None
        self.npsynccols=None
        self.groupcols=[]
        self.static={}
        self.static.update(staticlist)
        self.concatint=concatint
        for s in staticlist:
            self.cols.append(s[0])
        for row in concatint:
            self.cols.append(DatGenerator.concatjoiner.join(row))
        if groupmgr is not None:
            for col in sorted(self.groupmgr.groups()):
                if col in self.cols:
                    self.cols[self.cols.index(col)]=GroupMgr.prefix + col
                    self.groupcols.append(col)
                elif self.groupmgr.matchcol(col) in self.cols:
                    self.cols.append(GroupMgr.prefix + col)
                    self.groupcols.append(col)


    def startout(self):
        print(*self.cols,sep='\t',file=self.out)

    def setNpSync(self,data):
        self.npdata=data
        self.npcols=[]
        self.npsynccols=[]
        for col in data.dtype.names:
            if col in self.cols:
                self.npsynccols.append(col)
            else:
                self.npcols.append(col)
                self.cols.append(col)

    def skipCols(self,skip):
        for col in skip:
            if col in self.cols:
                del self.cols[self.cols.index(col)]

    def addNp(self,cur):
        if self.npdata is not None:
            r=self.npdata
            for sync in self.npsynccols:
                r = r[r[sync]==cur[sync]]
            if r.shape[0] == 1:
                for col in self.npcols:
                        cur[col]=r[col][0]

    def addConcatInt(self,cur):
        for row in self.concatint:
            l=[]
            valid=True
            for v in row:
                if v in cur and cur[v] is not None:
                    l.append(str(int(cur[v])))
                else:
                    valid=False
            if valid:
                cur[DatGenerator.concatjoiner.join(row)]=DatGenerator.concatjoiner.join(l)
                

    def writerow(self,cur):
        cur.update(self.static)
        self.addcxi(cur)
        self.addNp(cur)
        self.addConcatInt(cur)
        self.groupify(cur)
        for col in self.cols:
            if col in cur and cur[col] is not None:
                print(cur[col],end='\t',file=self.out)
            else:
                print(nullvalue,end='\t',file=self.out)
        print('\n',end='',file=self.out)

    def addcxi(self,cur):
        if len(self.cxicols) == 0:
            return
        if cur['ifile'] != self.curCXIName:
            if self.curCXI is not None:
                self.curCXI.close()
            if self.curH5 is not None:
                self.curH5.close()
            self.curCXIName=cur['ifile']
            self.curCXI=h5py.File(self.curCXIName,'r')
            if os.path.isfile(self.curCXIName[:-3] + "h5"):
                self.curH5=h5py.File(self.curCXIName[:-3] + "h5",'r')
        event=cur.get('event')
        if event is None:
            event=0
        else:
            event=int(event)
        for col in self.cxicols:
            v=None
            if col in self.curCXI and event < len(self.curCXI[col]):
                v=self.curCXI[col][event]
            elif self.curH5 and col in self.curH5 and int(event) < len(self.curH5[col]):
                v=self.curH5[col][event]
            if col in self.integratecols:
                v=np.trapz(np.array(v))
            cur[col]=v

    def groupify(self,cur):
        if self.groupmgr is not None:
            for g in self.groupcols:
                cur[GroupMgr.prefix + g] = self.groupmgr.match(g,cur.get(self.groupmgr.matchcol(g),nullvalue),nullvalue)
        

    def parsestream(self,filename):
        with open(filename) as f:
            streamname=os.path.abspath(filename)
            checkre=False
            lineStart=0
            lineEnd=0
            while True:
                line=f.readline()
                lineEnd=lineStart+len(line)
                if not line:
                    break
                line = line.strip()
                if line == '----- Begin chunk -----':
                    cur = {}
                    crylst=[]
                    crylst.append(cur)
                    cur['multi']=0
                    cur['multiid']=0
                    cur['sfile']=streamname
                    cur['istart']=lineStart
                    checkre=True

                elif line == 'Peaks from peak search':
                    cur['pstart']=lineEnd
                    checkre=False

                elif line == 'Reflections measured after indexing':
                    cur['rstart']=lineEnd
                    checkre=False

                elif line == 'End of reflections':
                    cur['rend']=lineStart

                elif line == 'End of peak list':
                    cur['pend']=lineStart

                elif line == '--- Begin crystal':
                    checkre=True
                    if cur['multi'] > 0:
                        cur=cur.copy()
                        crylst.append(cur)
                    cur['multi']+=1
                    cur['multiid']+=1
                    cur['cstart']=lineStart

                elif line == '--- End crystal':
                    # Assume if crystal existed than valid cell parameters were found
                    if 'vol' in self.cols: # But only bother calculating if user asked
                        cosalpha=cos(radians(float(cur['alpha'])))
                        cosbeta =cos(radians(float(cur['beta'])))
                        cosgamma=cos(radians(float(cur['gamma'])))
                        cur['vol']=float(cur['a'])*float(cur['b'])*float(cur['c'])*sqrt(1 - cosalpha**2 - cosbeta**2 - cosgamma**2 + 2 * cosalpha * cosbeta * cosgamma) 
                    cur['cend']=lineEnd


                elif line == '----- End chunk -----':
                    for c in crylst:
                        c['iend']=lineEnd
                        c['multi']=cur['multi']
                        self.writerow(c)
                    checkre=False
                    

                elif checkre:
                    for streamre in DatGenerator.streamcols:
                        mtch=streamre[1].search(line)
                        if mtch:
                            cur.update(zip(streamre[0],mtch.groups()))
                lineStart=lineEnd

    def parselist(self,filename):
        with open(filename) as f:
            while True:
                line=f.readline()
                if not line:
                    break
                parts = line.strip().split()
                if len(parts) == 1 or len(parts) == 2:
                    cur={}
                    cur['ifile']=parts[0]
                    if len(parts) == 2:
                        cur['event']=parts[1][2:]
                    for ifileRE in DatGenerator.listcols:
                        mtch=ifileRE[1].search(parts[0])
                        if mtch:
                            cur.update(zip(ifileRE[0],mtch.groups()))
                    cur['basename']=os.path.basename(parts[0])
                    self.writerow(cur)
                    



if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Create a .dat file from any number of stream files. Output files have one header row and can be appended to eachother with tail -n +1 >> fullfile (to skip the header row) assuming columns are the same.')
    parser.add_argument('--out','-o',type=argparse.FileType('w'),default=sys.stdout,help='Output file')
    parser.add_argument('--group',default=None,help='The group file output by groupgen.py (groupcfg.txt), for custom groups and/or enumerating strings')
    parser.add_argument('--builtincols',default=None,nargs='+',help='Space separated list of builtin columns to include in output. Defaults to all possible.')
    parser.add_argument('--cxi',action='append',default=[],help='Include from cxi/h5 file. Use switch multiple times to include from multiple cxi files. Example: --cxi /cheetah/frameNumber --cxi /LCLS/machineTime')
    parser.add_argument('--cxiintegrate',action='append',default=[],help='Include from cxi/h5 file. Use switch multiple times to include from multiple cxi files. Assumes 1D data that should be integrated with np.trapz for a single value')
    parser.add_argument('--static',action='append',default=[],nargs=2,help='Include a column whose value is the same for all output. Arguments are column_name column_value. Example --static dataset jan2012. You can include the switch multiple times for multiple static columns.')
    parser.add_argument('--npfile',default=None,help='Filepath to numpy file containing a record array. Columns in numpy file will be synced with stats after cxi columns but before grouping. Column names from rec array will be used and column names that match will be used for syncing. So, a rec array with the columns (a,b,c,d,e) with a stream file input would use values of a, b, and c from the stream file that match and add the values for d and e to the output in columns named d and e. A more natural example might be a recarray with columns (ifile,event,dataToAdd1,dataToAdd2).')
    parser.add_argument('--skipcols',default=[],nargs='+',help='Remove the given columns from the output. Fast alternative to specifying all but a few columns to other options.')
    parser.add_argument('--concatint',action='append',default=[],nargs='+',help='Concatenate integer columns with --. Useful for grouping on multiple values. Values are converted to integers before concatenation so there is no 0 padding.')
    parser.add_argument('files',nargs='+',help='Files to process. They can be CrystFEL stream files or CrystFEL list files, but the two shouldn\'t be mixed in the same command. The extension on the first file determines how all remaining files will be processed, with .lst or .txt indicating a list file and anything else is assumed to be a stream file. Events must be specified in the list file (listing CXI files will not read each event seperately. Use CrystFEL\'s list_events to convert a list of CXI files to a list of events).')


    args=parser.parse_args()

    # First, check if we're dealing with list files or stream files
    extension = os.path.splitext(args.files[0])[1]
    listmode = extension == ".lst" or extension == ".txt"

    if args.builtincols is None:
        if listmode:
            args.builtincols = DatGenerator.alllistcols
        else:
            args.builtincols = DatGenerator.allstreamcols

    gmgr=None
    if args.group:
        gmgr=GroupMgr(args.group,True)

    datgen=DatGenerator(args.out,args.builtincols,args.cxi,args.static,args.cxiintegrate,args.concatint,gmgr)

    if args.npfile is not None:
        npdata=np.load(args.npfile)
        datgen.setNpSync(npdata)

    datgen.skipCols(args.skipcols)
            
    datgen.startout()    
    for f in args.files:
        if listmode:
            datgen.parselist(f)
        else:
            datgen.parsestream(f)

