#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# datview/datexport.py
# Command line interface to load/export options of GUI 
# Author Natasha Stander

import sys
import argparse

from api.datamodel import DataModel
from api.modelcfg import ModelConfig

parser=argparse.ArgumentParser(description='Export to a new file. If the new file name ends with ".npz" the full dat file will be converted to a compressed numpy file and all other options are ignored. If new file name contains .stream, output will be a CrystFEL stream. If new file name contains .lst, output will be a CrystFEL lst. Otherwise, output will be a .dat file. Note that the group file is necessary IF exporting to stream or lst and stream or image files have been grouped, or IF "in" filtering is performed on grouped fields because "in" filters always use complete names rather than numbers. Order of operations: provided filter is applied, partitions are applied, then sort and limit are applied to each partition individually.')
parser.add_argument('--group',default=None,help='The group file output by groupgen.py (groupcfg.txt), keeps files smaller and numeric by enuemrating strings')
parser.add_argument('--filter',default=None,help='A filter file to load. Filter files are XML format. The first Between filter in the file for a field will be updated with selection.')
parser.add_argument('--sort',default=None,nargs='+',help='One or more fields to sort the output by. Field names must match the header of the dat file. Multiple arguments accepted so don\'t use as last switch before inputs.')
parser.add_argument('--reversesort',action="store_true",help='Sort descending instead of ascending')
parser.add_argument('--limit',default=None,type=int,help='Limit the output to this number, if provided')
parser.add_argument('--limitmode',default="random",choices=['random','top'],help='Whether to take random subset to enforce limit or to take first. Default is random.')
parser.add_argument('--cfg',default=None,help='Use the provided configuration file (xml) instead of the default one. Default one is found in api/modelcfg.xml')

parser.add_argument('--partnum',default=None,type=int,help='The number of partitions to create. Note that empty partitions are not output so the total output may be less than this number. This defaults to ten for continuous fields or all possible for categorical fields.')
parser.add_argument('--partmin',default=None,type=float,help='Set the minimum of the range to be partitioned')
parser.add_argument('--partmax',default=None,type=float,help='Set the maximum of the range to be partitioned')
parser.add_argument('--partition',default=None,help='Field name to partition on. Partitioning only occurs if this is provided, otherwise partnum, partmin, and partmax are not used. Partition names appended to outfile as outfile_nm')

parser.add_argument('infile',help='the dat file (or a .npz file output from datview/datexport)')
parser.add_argument('outfile',help='the output file, format automatically determined by line ending')
args=parser.parse_args()


model=DataModel(args.infile,args.group,cfg=ModelConfig(args.cfg))
if args.outfile.endswith(".npz"):
    model.saveAllNumpy(args.outfile)
    exit()

if args.filter is not None:
    model.loadFilters(args.filter)
if args.sort is not None:
    model.sortlst = args.sort
if args.limit is not None:
    model.limit = args.limit
model.limitModeRandom = args.limitmode == "random"
model.reverseSort = args.reversesort

if args.partition is not None:
    partitions=model.partition(args.partition,args.partmin,args.partmax,args.partnum)
    for k,v in partitions.items():
        model.overrideFilter(v)
        if '.stream' in args.outfile:
            model.saveSelStream(args.outfile+"_"+k)
        elif '.lst' in args.outfile:
            model.saveSelLst(args.outfile+"_"+k)
        else:
            model.saveSelDat(args.outfile+"_"+k)
else:
    if '.stream' in args.outfile:
        model.saveSelStream(args.outfile)
    elif '.lst' in args.outfile:
        model.saveSelLst(args.outfile)
    else:
        model.saveSelDat(args.outfile)

