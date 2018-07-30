#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# datview/scripts/datupdate.py
# Update dat file
# Author Natasha Stander

import sys
import argparse
import numpy as np

parser=argparse.ArgumentParser(description='Given two dat files, add fields to the first file that are found in the second file for matching columns. The second datfile will be converted to a numpy array, so npformats can be used for arrays where floats are not used.')
parser.add_argument('--npformats',default=None,nargs='+',help="The data formats for np.loadtxt")
parser.add_argument('--datfile1',required=True,help='The main dat file')
parser.add_argument('--datfile2',type=open,default=sys.stdin,help='The dat file to sync to the main datfile. Converted to numpy array internally so dtypes may be needed. Can be read from standard in.')
parser.add_argument('--outfile',type=argparse.FileType('w'),default=sys.stdout,help='the output file. If not provided, will be standard out.')
args=parser.parse_args()

cols1=[]
cols2=args.datfile2.readline().split()

out=args.outfile
with open(args.datfile1) as dfile:
    cols1=dfile.readline().split()
    common=set(cols1) & set(cols2)
    outcols=[]
    outcols += cols1
    synccols=[]

    for i,c in enumerate(cols2):
        if c in common:
            synccols.append((i,c))
        else:
            outcols.append(c)

    if args.npformats is not None:
        npdata=np.loadtxt(args.datfile2,dtype={'names' : tuple(cols2), 'formats' : tuple(args.npformats)})
    else:
        npdata=np.loadtxt(args.datfile2)

    print(*outcols,sep='\t',file=out)
    while True:
        line=dfile.readline()
        if not line:
            break

        values=line.split()
        cur = {}
        cur.update(zip(cols1,values))
        
        r=npdata
        for i in range(len(synccols)):
            v=cur[synccols[i][1]]
            try:
                v=float(v)
            except ValueError:
                pass
            r = r[r[synccols[i][1]]==v]
        if r.shape[0] == 1:
            for i in range(len(cols2)):
                if cols2[i] not in common:
                    cur[cols2[i]]=r[0][i]

        for col in outcols:
            if col in cur and cur[col] is not None:
                print(cur[col],end='\t',file=out)
            else:
                print(-1,end='\t',file=out)
        print('\n',end='',file=out)






