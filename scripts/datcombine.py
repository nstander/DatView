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

parser=argparse.ArgumentParser(description='Combine data files. To sync (adding where values match) use datupdate.py')
parser.add_argument('--cols',default=None,nargs='+',help='The columns to keep. If not specified, columns will be determined by column mode')
parser.add_argument('--colmode',default='union',choices=['intersect','union'],help='If the columns argument is not used, this determines the columns output as either the columns in common between all files or all columns found across files where missing values are filled in with -1')
parser.add_argument('--static',action='append',default=[],nargs='+',help='Name of static column, then value(s), either one value for all or one value per dat file')
parser.add_argument('-o','--out',type=argparse.FileType('w'),default=sys.stdout,help='the output dat file. If not provided, will be standard out.')
parser.add_argument('infiles',nargs='+',help='the dat file (or a .npz file output from datview/datexport)')

args=parser.parse_args()

if args.cols is None:
    allcols=set()
    allcommoncols=set()
    initialcols=None

    for ifile in args.infiles:
        with open(ifile) as dfile:
            if initialcols is None:
                initialcols=dfile.readline().split()
                allcols = set(initialcols)
                allcommoncols = set (initialcols)
            else:
                cols=set(dfile.readline().split())
                allcols |= cols
                allcommoncols &=cols

    args.cols = []
    if args.colmode == "intersect":
        use=allcommoncols
    else:
        use=allcols

    for col in initialcols:
        if col in use:
            args.cols.append(col)
    for col in sorted((use - set(initialcols))):
        args.cols.append(col)
    for coldef in args.static:
        args.cols.append(coldef[0])

print(*args.cols,sep='\t',file=args.out)

for coldef in args.static:
    missing = len(args.infiles)- (len(coldef) - 1) 
    coldef+=[coldef[-1]]*(missing)    

for i,ifile in enumerate(args.infiles):
    with open(ifile) as dfile:
        cols=dfile.readline().split()
        while True:
            line=dfile.readline()
            if not line:
                break
            cur={}
            cur.update(zip(cols,line.split()))
            for coldef in args.static:
                cur[coldef[0]]=coldef[i+1]
            for col in args.cols:
                if col in cur and cur[col] is not None:
                    print(cur[col],end='\t',file=args.out)
                else:
                    print(-1,end='\t',file=args.out) 
            print('\n',end='',file=args.out)           






