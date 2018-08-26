#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Natasha Stander

import sys
import argparse
import numpy as np

parser=argparse.ArgumentParser(description='Summary statistics for LQ48 beamtime');
parser.add_argument('datfiles',nargs='+',help='The dat file to use, expects first line to be column names')
args = parser.parse_args()

cols=[]
for datfile in args.datfiles:
    with open(datfile) as dfile:
        cols=dfile.readline().split()

    data = np.loadtxt(datfile, skiprows=1,usecols=(cols.index('reslim')))

    m=np.max(data)
    if m == -1:
        m=0
    mA=0
    if m != 0:
        mA=10/m
    print("%s \t%.2f nm^-1 \t%.2f A"%(datfile,m,mA))








