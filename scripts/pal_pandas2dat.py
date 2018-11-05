#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# datview/datgen.py
# Data reduction pandas h5 -> dat for PAL-XFEL
# Author Natasha Stander

import os
import sys
import argparse
import pandas as pd
import numpy as np
import re

parser=argparse.ArgumentParser(description='Create a .dat file from pandas, customized to Pal-XFEL XSS beamline.')
parser.add_argument('--out','-o',type=argparse.FileType('w'),default=sys.stdout,help='Output file')
parser.add_argument('--cols',default=None,nargs='+',help='The columns from the file(s) to keep, defaults to None (=all). If specified, be sure to include ifile, run, event as they will be added to the dataframe before export and won\'t be output unless specified.')
parser.add_argument('--ifilepath',default='/xfel/ffhs/dat/ue_181104_FXL/raw_data/h5/type=raw/run=%03d/scan=001/',nargs='+',help='Use following path to ifile. basename(givenFileName) will be joined to this path. Must include %%i to mark a run number')
parser.add_argument('--run',default=None,type=int,help='specify the run number, guessed from input file run= statements.')
parser.add_argument('files',nargs='+',help='List of files to process')

args=parser.parse_args()

exp=re.compile(r'.*run=(\d+).*')
for f in args.files:
    df=pd.read_hdf(f)
    df=df*1 # Change booleans to integers
    r=args.run
    if r is None:
        r=int(exp.search(f).group(1))
    ifile=f
    if args.ifilepath is not None:
        ifile=os.path.join(args.ifilepath % r, os.path.basename(f))
    n=len(df)
    df=df.assign(ifile=np.array([ifile]*n),run=np.array([r]*n),event=np.arange(n))
    df.to_csv(args.out,sep='\t',na_rep='-1',columns=args.cols,index=False)
    

        
