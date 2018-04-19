#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys,os
import argparse
import numpy as np

sys.path.append(os.path.dirname(sys.path[0]))
from api.datamodel import DataModel
from api.modelcfg import ModelConfig

parser=argparse.ArgumentParser(description='Show the min (with -1), min(no -1), mean (no -1), max of each column.')
parser.add_argument('--cfg',default=None,help='Use the provided configuration file (xml) instead of the default one. Default one is found in api/modelcfg.xml')
parser.add_argument('infile',help='the dat file')
args=parser.parse_args()


model=DataModel(args.infile,None,cfg=ModelConfig(args.cfg))
print("name\tmin (all)\tmin (no -1)\tmean\tmax")
for col in model.cols:
    print (col,np.min(model.data[col]), model.fieldmin(col), np.mean(model.data[col][model.data[col]!= -1]),np.max(model.data[col]),sep="\t")

