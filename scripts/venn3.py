#!/usr/bin/env python3

# Based on Peakogram, but for use with dat files, specifically ones output by stream2dat.py
# Author: Natasha Stander

import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib_venn import venn3

parser=argparse.ArgumentParser(description='Plot a Venn Diagram from 3 dat files');
parser.add_argument('--columns',default=['g_ifile','event'],nargs='+',help="The columns to compare between files. By default, will be g_ifile and event.")
parser.add_argument('--npformats',default=['i4','i4'],nargs='+',help="The corresponding data types")
parser.add_argument('--names',default=None,nargs=3,help="If provided, should be 3 names to use instead of file names")
parser.add_argument('datfiles',nargs=3,help='The datfiles to use')
args = parser.parse_args()

if args.names is None:
    args.names = args.datfiles

sets=[]
for i in range(3):
    cols=[]
    with open(args.datfiles[i]) as dfile:
      cols=dfile.readline().split()

    use=[]
    for col in args.columns:
        use.append(cols.index(col))

    sets.append(set(map(tuple,np.loadtxt(args.datfiles[i], dtype={'names' : tuple(args.columns), 'formats' : tuple(args.npformats)},skiprows=1,usecols=tuple(use)))))

venn3(sets,args.names)
plt.show()

