#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# datview/datexport.py
# Command line interface to load/export options of GUI 
# Author Natasha Stander

import sys
import argparse
import os
import numpy as np
import h5py
import tables

sys.path.append(os.path.dirname(sys.path[0]))
from api.datamodel import DataModel
from api.modelcfg import ModelConfig

savelst={}

def savePowder(args,partname=None):
    nm = args.outfile
    if partname is not None and not args.savelst:
        nm = args.outfile % partname

    curFile=None
    curFileName=None

    curPowders={}
    count=0
    for i in args.model.outArrIndices():
        if curFileName != args.model.value('ifile',i):
            if curFile is not None:
                curFile.close()
            curFileName = args.model.value('ifile',i)
            curFile=h5py.File(curFileName,'r')
        count +=1
        for field in args.h5fields:
            if 'event' in args.model.cols and args.model.filtered['event'][i] != -1:
                v=curFile[field][args.model.filtered['event'][i]]
            else:
                v=curFile[field]
            c=np.ones(v.shape)

            if args.backgrounds is not None:
                v-=args.backgrounds[field]

            if args.histclipmin is not None:
                c[v<args.histclipmin]=0
                v[v<args.histclipmin]=0
            if args.histclipmax is not None:
                c[v>args.histclipmax]=0
                v[v>args.histclipmax]=0

            if args.flatten:
                v=np.sum(v[:])
                c=count

            if field not in curPowders:
                curPowders[field]=np.array(v,dtype=np.dtype('f4'))
                curPowders[field+"_sqr"]=np.array(v,dtype=np.dtype('f4'))**2
                curPowders[field+"_cnt"]=c
            else:
                curPowders[field]+=np.array(v,dtype=np.dtype('f4'))
                curPowders[field+"_sqr"]+=np.array(v,dtype=np.dtype('f4'))**2
                curPowders[field+"_cnt"]+=c
    if args.savelst:
        if partname is None:
            partname = "all"
        if args.partition is not None and len(args.partition) >1:
            parts=partname.split('_')
            major='_'.join(parts[:-1])
            minor=parts[-1]
            if not major in savelst:
                savelst[major]={}
            savelst[major][minor]={}
            out=savelst[major][minor]
        else:
            savelst[partname]={}
            out=savelst[partname]
    else:
        out=h5py.File(nm,'w')
    for k in args.h5fields:
        v=curPowders[k]
        v2=curPowders[k+"_sqr"] 
        c=curPowders[k+"_cnt"]  
        c[c==0]=1 # avoid divide by 0 errors, should be 0 where this would be 0 anyway
        out[k+"_sum"]=v
        out[k+"_avg"]=v/c
        out[k+"_sig"]=np.sqrt(v2/c-(v/c)**2)
    out["/num_patterns"]=count

    if not args.savelst:
        out.close()
    if curFile is not None:
        curFile.close()

def writelst(outname,savedict,args):
    with open(outname,'w') as fout:
        outlst=None
        for k in sorted(savedict.keys()):
            if outlst is None:
                outlst = sorted(savedict[k].keys())
                nm='part'
                if args.partition is not None:
                    nm=args.partition[-1]
                fout.write(nm+'\t'+'\t'.join(outlst)+'\n')
            vallst=[k]
            for k2 in outlst:
                vallst.append(str(savedict[k][k2]))
            fout.write('\t'.join(vallst)+'\n')


parser=argparse.ArgumentParser(description='Create virtual powders for given fields in h5 files.')
parser.add_argument('--h5fields',nargs='+',default=['/entry_1/data_1/data'],help='The field(s) to create a powder for.')
parser.add_argument('--group',default=None,help='The group file output by groupgen.py (groupcfg.txt), keeps files smaller and numeric by enuemrating strings')
parser.add_argument('--filter',default=None,help='A filter file to load. Filter files are XML format. The first Between filter in the file for a field will be updated with selection.')
parser.add_argument('--cfg',default=None,help='Use the provided configuration file (xml) instead of the default one. Default one is found in api/modelcfg.xml')

parser.add_argument('--partnum',default=[],nargs='+',type=int,help='The number of partitions to create. Note that empty partitions are not output so the total output may be less than this number. This defaults to ten for continuous fields or all possible for categorical fields. Accepts multiple arguments, one for each field. Unspecified arguments default to None')
parser.add_argument('--partmin',default=[],nargs='+',type=float,help='Set the minimum of the range to be partitioned. Accepts multiple arguments, one for each field. Unspecified arguments default to None')
parser.add_argument('--partmax',default=[],nargs='+',type=float,help='Set the maximum of the range to be partitioned. Accepts multiple arguments, one for each field. Unspecified arguments default to None')
parser.add_argument('--partition',default=None,nargs='+',help='Field name(s) to partition on. Partitioning only occurs if this is provided, otherwise partnum, partmin, and partmax are not used. Partition names appended to outfile as outfile_nm')

parser.add_argument('--histclipmax',default=None,type=float,help='Values above are set to 0')
parser.add_argument('--histclipmin',default=None,type=float,help='Values below are set to 0')

parser.add_argument('--flatten',action='store_true',help='Sum the array to a single value after clipping')
parser.add_argument('--savelst',action='store_true',help='Assuming flat data, save output as text file columns')

parser.add_argument('--background',default=None,help='Subtract before histogram clipping, should be h5 file with same fields.')

parser.add_argument('infile',help='the dat file (or a .npz file output from datview/datexport)')
parser.add_argument('outfile',help='the output file, use %%s to show location of partition name. Will be h5 format')
args=parser.parse_args()


model=DataModel(args.infile,args.group,cfg=ModelConfig(args.cfg))
if args.filter is not None:
    model.loadFilters(args.filter)

assert model.canSaveLst()

args.model=model

partitions=None
if args.partition is not None:
    partitions=model.partitionMulti(args.partition,args.partmin,args.partmax,args.partnum)
    if '%s' not in args.outfile and not args.savelst:
        args.outfile +="_%s"

backgrounds=None
if args.background is not None:
    backgrounds={}
    f=h5py.File(args.background,'r')
    for field in args.h5fields:
        backgrounds[field]=np.array(h5py[field],dtype=np.dtype('f4'))
args.backgrounds=backgrounds
        

model.saveByPartitions(args,savePowder,partitions,appendName=False)
if args.savelst:
    if args.partition is not None and len(args.partition) >1:
        if '%s' not in args.outfile:
                args.outfile +="_%s"
        for major in sorted(savelst.keys()):
            writelst(args.outfile % major, savelst[major],args)
    else:
        writelst(args.outfile, savelst,args)
        
    




