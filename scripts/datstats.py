#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# datview/datcombine.py
# Combine data files
# Author Natasha Stander

import sys
import argparse
import os
import numpy as np
import h5py

sys.path.append(os.path.dirname(sys.path[0]))
from api.datamodel import DataModel
from api.modelcfg import ModelConfig

def addline(args,partname=None):
    cur={}
    if args.partition:
        cur['_'.join(args.partition)]=partname
    for c in args.average:
        cur['average_'+c]=np.average(args.model.filtered[c][args.model.filtered[c] != args.model.cfg.nullvalue])
    for c in args.averageN:
        cur['averageN_'+c]=np.average(args.model.filtered[c])
    for c in args.min:
        cur['min_'+c]=np.min(args.model.filtered[c][args.model.filtered[c] != args.model.cfg.nullvalue])
    for c in args.minN:
        cur['minN_'+c]=np.min(args.model.filtered[c])
    for c in args.max:
        cur['max_'+c]=np.max(args.model.filtered[c])
    for c in args.std:
        cur['std_'+c]=np.std(args.model.filtered[c])
    for c in args.count:
        if len(c):
            if len(c) == 1:
                cur["count_"+'_'.join(c)]=np.count_nonzero(args.model.filtered[c[0]] != args.model.cfg.nullvalue)
            else:
                cnt=0
                for v in c[1:]:
                    cnt = cnt + np.count_nonzero(args.model.filtered[c[0]] == float(v))
                cur["count_"+'_'.join(c)]=cnt
        else:
            cur["count"]=len(args.model.filtered)
    for c in args.countGE:
        cur["countGE_"+'_'.join(c)]=np.count_nonzero(args.model.filtered[c[0]] >= float(v))

    for col in args.cols:
        if col in cur and cur[col] is not None:
            print(cur[col],end='\t',file=args.out)
        else:
            print(args.model.cfg.nullvalue,end='\t',file=args.out)
    print('\n',end='',file=args.out)


parser=argparse.ArgumentParser(description='Print Statistics')
parser.add_argument('--group',default=None,help='Group file(s). If more than one is specified, than there must be one group file per dat file')
parser.add_argument('--cfg',default=None,help='Use the provided configuration file (xml) instead of the default one. Default one is found in api/modelcfg.xml')
parser.add_argument('--filter',default=None,help='A filter file to load. Filter files are XML format. The first Between filter in the file for a field will be updated with selection.')

parser.add_argument('--cols',default=None,nargs='+',help='Specify the order of the columns. Otherwise, column order is alphabetical. Column names are calcmethod_name, so --average reslim would be average_reslim and --max vol would be max_vol. The partition column is the column(s) for partitioning joined by _')

parser.add_argument('--average',action='append',default=[],help='Take the average of the given column. Include switch multiple times for multiple columns')
parser.add_argument('--averageN',action='append',default=[],help='Take the average of the given column (including masked values). Include switch multiple times for multiple columns')
parser.add_argument('--min',action='append',default=[],help='Take the minimum of the given column ignoring masked values. Include switch multiple times for multiple columns')
parser.add_argument('--minN',action='append',default=[],help='Take the minimum of the given column (including masked values). Include switch multiple times for multiple columns')
parser.add_argument('--max',action='append',default=[],help='Take the maximum of the given column. Include switch multiple times for multiple columns')
parser.add_argument('--median',action='append',default=[],help='Take the median of the given column. Include switch multiple times for multiple columns')
parser.add_argument('--std',action='append',default=[],help='Take the standard deviation of the given column. Include switch multiple times for multiple columns')
parser.add_argument('--count',action='append',nargs='*',default=[],help='Number in partition. Optionally specify values to count equal to (valid value otherwise). For instance "--count multiid 0 1" would count the number of 0 (unindexed) patterns and the number of 1st indexed crystals which would total the number of frames. "--count" without a column will return the number of rows in the file/partition. Currently just working for numeric columns')
parser.add_argument('--countGE',action='append',nargs=2,default=[],help='Count number in column greater than equal to value. Two arguments: col name, value')

parser.add_argument('--partnum',default=[],nargs='+',type=int,help='The number of partitions to create. Note that empty partitions are not output so the total output may be less than this number. This defaults to ten for continuous fields or all possible for categorical fields. Accepts multiple arguments, one for each field. Unspecified arguments default to None')
parser.add_argument('--partmin',default=[],nargs='+',type=float,help='Set the minimum of the range to be partitioned. Accepts multiple arguments, one for each field. Unspecified arguments default to None')
parser.add_argument('--partmax',default=[],nargs='+',type=float,help='Set the maximum of the range to be partitioned. Accepts multiple arguments, one for each field. Unspecified arguments default to None')
parser.add_argument('--partition',default=None,nargs='+',help='Field name(s) to partition on. Partitioning only occurs if this is provided, otherwise partnum, partmin, and partmax are not used. Partition names appended to outfile as outfile_nm')

parser.add_argument('-o','--out',type=argparse.FileType('w'),default=sys.stdout,help='the output file. If not provided, will be standard out.')
parser.add_argument('infile',help='the dat file (or a .npz file output from datview/datexport)')
args=parser.parse_args()

model=DataModel(args.infile,args.group,cfg=ModelConfig(args.cfg))
if args.filter is not None:
    model.loadFilters(args.filter)

args.model=model

if args.cols is None:
    args.cols=[]
    for c in args.average:
        args.cols.append("average_"+c)
    for c in args.averageN:
        args.cols.append("averageN_"+c)
    for c in args.min:
        args.cols.append("min_"+c)
    for c in args.minN:
        args.cols.append("minN_"+c)
    for c in args.max:
        args.cols.append("max_"+c)
    for c in args.std:
        args.cols.append("std_"+c)
    for c in args.count:
        if len(c):
            args.cols.append("count_"+'_'.join(c))
        else:
            args.cols.append("count")
    for c in args.countGE:
        args.cols.append("countGE_"+'_'.join(c))
    args.cols.sort()
    if args.partition is not None:
        args.cols.insert(0,'_'.join(args.partition))

partitions=None
if args.partition is not None:
    partitions=model.partitionMulti(args.partition,args.partmin,args.partmax,args.partnum)

print(*args.cols,sep='\t',file=args.out)
model.saveByPartitions(args,addline,partitions,appendName=False)


