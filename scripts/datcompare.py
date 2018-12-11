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

parser=argparse.ArgumentParser(description='Generate a comparison input file for datview. A comparison input file has a column for the original field and allows plotting values against each other, like the cell volume of indexing method one against the cell volume of indexing method two for the same set of files. Thereis also a comparison view of the item viewer to see how statistics change per file and comparison specific filters for selecting the highest/lowest out of the inputs. ')
parser.add_argument('--alias',default=None,nargs='+',help='Names for dat files. Otherwise, filename is used')
parser.add_argument('-o','--out',required=True,help='Output file name (npz format)')
parser.add_argument('--synccols',default=['ifile','event'],nargs='+',help='Columns to sync on. By deafult ifile, event. Be careful with multiple crystal results. You may want multiid as well.')
parser.add_argument('--cfg',default=None,help='Use the provided configuration file (xml) instead of the default one. Default one is found in api/modelcfg.xml')
parser.add_argument('infiles',nargs='+',help='dat files (npz not accepted). Files must have the same columns relative to each other')
args=parser.parse_args()

cfg=ModelConfig(args.cfg)

if args.alias is None:
    args.alias=[]
    for infile in args.infiles:
        args.alias.append(os.path.basename(infile))

with open(args.infiles[0]) as dfile:
    hdrline=dfile.readline().strip()
    cols=hdrline.split(cfg.sep)
    if cfg.commentchar is not None:
        cols[0] = cols[0].replace(cfg.commentchar, "")

synccols=[]
for c in args.synccols:
    if c in cols:
        synccols.append(c)

dtypes=[]
convert={}
todigitize=[]
digitized={}
for c in cols:
    dtypes.append(cfg.dtype(c))
    if 'U' in dtypes[-1]:
        convert[cols.index(c)]=np.lib.npyio.asstr
        todigitize.append(c)
rdatalst=[]
rows=[0]
for infile in args.infiles:
    rdatalst.append(np.loadtxt(infile,skiprows=1,converters=convert,delimiter=cfg.sep,
                     dtype={'names':tuple(cols),'formats':tuple(dtypes)}))
    rows.append(len(rdatalst[-1])+rows[-1])

dtypes2=[]
for dtype in dtypes:
    if 'U' in dtype:
        dtypes2.append('i4')
    else:
        dtypes2.append(dtype)

cols.append(DataModel.sortColumnName)
cols.append(DataModel.compareGroupName)
cols.append(DataModel.compareIndexName)
dtypes2.append('u4')
dtypes2.append('u4')
dtypes2.append('u4')

rdata=np.concatenate(rdatalst)
data=np.empty(rdata.shape,dtype={'names':tuple(cols),'formats':tuple(dtypes2)})
offset=0
for c in cols:
    if c in todigitize:
        lbls,inverse=np.unique(rdata[c],return_inverse=True)
        digitized[c]=np.array(lbls.tolist())
        data[c]=inverse
    elif c not in cols[-3:]:
        data[c]=rdata[c]
        if c in cfg.invert:
            data[c] = 1/data[c]
        if cfg.multvalue(c) != 1:
            data[c][data[c]!=-1]*=cfg.multvalue(c)

for i in range(1,len(rows)):
    data[DataModel.compareGroupName][rows[i-1]:rows[i]]=i-1
digitized[DataModel.compareGroupName]=args.alias

data.sort(order=synccols+[DataModel.compareGroupName])
data[DataModel.sortColumnName]=np.arange(len(data))

cmptable=[]
currow=np.ones(len(args.infiles),dtype=int)*-1
cmprow=0
cur=None
for i in range(len(data)):
    if cur is None:
        cur=data[synccols][i]
    next=data[synccols][i]
    if cur != next:
        cmptable.append(currow)
        currow=np.ones(len(args.infiles))*-1
        cmprow += 1
        cur=next
    data[DataModel.compareIndexName][i] = cmprow
    currow[data[DataModel.compareGroupName][i]]=i
cmptable.append(currow)

cmparray=np.stack(cmptable)

np.savez_compressed(args.out,data=data,rdata=rdata,cmparray=cmparray,digitizedkeys=np.asarray(sorted(digitized.keys())),**digitized)









