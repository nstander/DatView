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

sys.path.append(os.path.dirname(sys.path[0]))
from api.datamodel import DataModel
from api.modelcfg import ModelConfig

def savePowder(args,partname=None):
    nm = args.outfile
    if partname is not None:
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
        for field in args.h5fields:
            if 'event' in args.model.cols and args.model.filtered['event'][i] != args.model.cfg.nullvalue:
                v=curFile[field][args.model.filtered['event'][i]]
            else:
                v=curFile[field]

            if field not in curPowders:
                curPowders[field]=np.array(v,dtype=np.dtype('f4'))
                curPowders[field+"_sqr"]=np.array(v,dtype=np.dtype('f4'))**2
            else:
                curPowders[field]+=np.array(v,dtype=np.dtype('f4'))
                curPowders[field+"_sqr"]+=np.array(v,dtype=np.dtype('f4'))**2
        count +=1
    out=h5py.File(nm,'w')
    for k in args.h5fields:
        v=curPowders[k]
        v2=curPowders[k+"_sqr"]   
        out[k+"_sum"]=v
        out[k+"_avg"]=v/count
        out[k+"_sig"]=np.sqrt(v2/count-(v/count)**2)
    out["/num_patterns"]=count
    out.close()
    if curFile is not None:
        curFile.close()


parser=argparse.ArgumentParser(description='Create virtual powders for given fields in h5 files.')
parser.add_argument('--h5fields',nargs='+',default=['/entry_1/data_1/data'],help='The field(s) to create a powder for.')
parser.add_argument('--group',default=None,help='The group file output by groupgen.py (groupcfg.txt), keeps files smaller and numeric by enuemrating strings')
parser.add_argument('--filter',default=None,help='A filter file to load. Filter files are XML format. The first Between filter in the file for a field will be updated with selection.')
parser.add_argument('--cfg',default=None,help='Use the provided configuration file (xml) instead of the default one. Default one is found in api/modelcfg.xml')

parser.add_argument('--partnum',default=[],nargs='+',type=int,help='The number of partitions to create. Note that empty partitions are not output so the total output may be less than this number. This defaults to ten for continuous fields or all possible for categorical fields. Accepts multiple arguments, one for each field. Unspecified arguments default to None')
parser.add_argument('--partmin',default=[],nargs='+',type=float,help='Set the minimum of the range to be partitioned. Accepts multiple arguments, one for each field. Unspecified arguments default to None')
parser.add_argument('--partmax',default=[],nargs='+',type=float,help='Set the maximum of the range to be partitioned. Accepts multiple arguments, one for each field. Unspecified arguments default to None')
parser.add_argument('--partition',default=None,nargs='+',help='Field name(s) to partition on. Partitioning only occurs if this is provided, otherwise partnum, partmin, and partmax are not used. Partition names appended to outfile as outfile_nm')

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
    if '%s' not in args.outfile:
        args.outfile +="_%s"

model.saveByPartitions(args,savePowder,partitions,appendName=False)



