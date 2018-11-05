#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import h5py
import sys
import argparse
import os
import tables

parser=argparse.ArgumentParser(description='List events for h5. Current defaults are for PAL-XFEL')
parser.add_argument('--h5path',default='/eh1/mpccd1/image/block0_items',help='the path in h5 file to multi dimensional data')
parser.add_argument('--h5file','-i',required=True,help='the h5 file')
parser.add_argument('--outname','-o',required=True,help='output file name')
args=parser.parse_args()

f=h5py.File(args.h5file,'r')
n=f[args.h5path].shape[0]

ifile=os.path.abspath(args.h5file)
with open(args.outname,'w') as fout:
    for i in range(n):
        fout.write('%s //%i\n'%(ifile,i))
f.close()
