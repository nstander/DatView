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

    data = np.loadtxt(datfile, skiprows=1,usecols=(cols.index('multi')))

    (multi,cnts)=np.unique(data,return_counts=True)

    print(datfile,"frames(crystals)",end="\t")

    crystals = 0
    indexedframes=0
    frames=0
    for i in range(int(np.max(multi))+1):
      if i in multi:
        cnt=cnts[np.where(multi==i)[0]][0]
        if i != 0:
            crystals+=cnt
            cnt /= i
            indexedframes+=cnt
        frames+=cnt
        print ("%i(%i)"%(cnt,i),end="\t")
      else:
        print (0,end="\t")
    print()
    print("%s %i crystals of %i frames (%.2f%%); %i indexed frames of % i frames (%0.2f%%)"%(datfile,crystals,frames,float(crystals)*100/frames,indexedframes,frames,float(indexedframes)*100/frames))








