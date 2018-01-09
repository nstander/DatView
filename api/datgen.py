#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import re
import h5py

class DatGenerator:
    streamcols=[(('ifile','run','class','subcxi'),re.compile('^Image filename: (.*r(\d{4})(?:-class(\d))?(?:-c(\d{2}))?.cxi)')),
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
    allstrcols=['ifile','run','class','subcxi','event','indby','phoen','bmdv','bmbw','aclen','npeak',
                'ltype','cent','a','b','c','alpha','beta','gamma','prorad','detdx','detdy','reslim','nref',
                'nsref','niref','o1','o2','o3','o4','o5','o6','o7','o8','o9']
    internalcols=['sfile','istart','iend','cstart','cend','pstart','pend','rstart','rend','multi']
    allcols=allstrcols+internalcols
                
    def __init__(self,imageout,crystalout,streamcols,cxicols):
        self.cols=streamcols+cxicols
        self.cxicols=cxicols
        self.curCXIName=None
        self.curCXI=None
        self.curH5=None
        self.chunkout=imageout
        self.crystalout=crystalout
        print(*self.cols,sep='\t',file=imageout)
        print(*self.cols,sep='\t',file=crystalout)
        pass

    def writerow(self,outstream,cur):
        self.addcxi(cur)
        for col in self.cols:
            if col in cur and cur[col] is not None:
                print(cur[col],end='\t',file=outstream)
            else:
                print(-1,end='\t',file=outstream)
        print('\n',end='',file=outstream)

    def addcxi(self,cur):
        if cur['ifile'] != self.curCXIName:
            if self.curCXI is not None:
                self.curCXI.close()
            if self.curH5 is not None:
                self.curH5.close()
            self.curCXIName=cur['ifile']
            self.curCXI=h5py.File(self.curCXIName,'r')
            if os.path.isfile(self.curCXIName[:-3] + "h5"):
                self.curH5=h5py.File(self.curCXIName[:-3] + "h5",'r')
        for col in self.cxicols:
            if col in self.curCXI and int(cur['event']) < len(self.curCXI[col]):
                cur[col]=self.curCXI[col][int(cur['event'])]
            elif self.curH5 and col in self.curH5 and int(cur['event']) < len(self.curH5[col]):
                cur[col]=self.curH5[col][int(cur['event'])]


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
                    mcur = {}
                    #for col in multicol:
                    #    mcur[col]=0
                    cur['multi']=0
                    cur['sfile']=streamname
                    cur['istart']=lineStart
                    checkre=True

                elif line == 'Peaks from peak search':
                    cur['pstart']=lineStart
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
                    cur['multi']+=1
                    cur['cstart']=lineStart

                elif line == '--- End crystal':
                    cur['cend']=lineEnd
                    self.writerow(self.crystalout,cur)


                elif line == '----- End chunk -----':
                    cur['iend']=lineEnd
                    checkre=False
                    self.writerow(self.chunkout,cur)

                elif checkre:
                    for streamre in DatGenerator.streamcols:
                        mtch=streamre[1].search(line)
                        if mtch:
                            cur.update(zip(streamre[0],mtch.groups()))
                lineStart=lineEnd



if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Create a .dat file from any number of stream files. By default, images.dat will contain one line per chunk and crystals.dat will contain one line per crystal. Output files have one header row and can be appended to eachother with tail -n +1 >> fullfile (to skip the header row).')
    parser.add_argument('--imageout',default='images.dat',help='Output for each chunk')
    parser.add_argument('--crystalout',default='crystals.dat',help='Output for each crystal')
#    parser.add_argument('--group','-g',required=True,help='The group file output by groupgen.py (groupcfg.txt)')
    parser.add_argument('--streamcols',default=DatGenerator.allcols,nargs='+',help='Space separated list of builtin columns to include in output. Use all for all.')
    parser.add_argument('--cxi',action='append',help='Include from cxi/h5 file. Use switch multiple times to include from multiple cxi files. Example: --cxi /cheetah/frameNumber --cxi /LCLS/machineTime')
    parser.add_argument('files',nargs='+',help='one or more crystfel stream files')

    args=parser.parse_args()

    datgen=DatGenerator(open(args.imageout,'w'),open(args.crystalout,'w'),args.streamcols,args.cxi)
    for f in args.files:
        datgen.parsestream(f)
