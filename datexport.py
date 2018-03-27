#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse

from api.datamodel import DataModel

parser=argparse.ArgumentParser(description='Export to a new file. If new file name contains .stream, output will be a CrystFEL stream. If new file name contains .lst, output will be a CrystFEL lst. Otherwise, output will be a .dat file. Note that the group file is necessary IF exporting to stream or lst and stream or image files have been grouped, or IF "in" filtering is performed on grouped fields because "in" filters always use complete names rather than numbers.')
parser.add_argument('--group',default=None,help='The group file output by groupgen.py (groupcfg.txt), keeps files smaller and numeric by enuemrating strings')
parser.add_argument('--filter',default=None,help='A filter file to load. Filter files are XML format. The first Between filter in the file for a field will be updated with selection.')
parser.add_argument('--sort',default=None,nargs='+',help='One or more fields to sort the output by. Field names must match the header of the dat file. Multiple arguments accepted so don\'t use as last switch before inputs.')
parser.add_argument('--limit',default=None,type=int,help='Limit the output to this number, if provided')
parser.add_argument('infile',help='the dat file')
parser.add_argument('outfile',help='the output file, format automatically determined by line ending')
args=parser.parse_args()

model=DataModel(args.infile,args.group)
if args.filter is not None:
    model.loadFilters(args.filter)
if args.sort is not None:
    model.sortlst = args.sort
if args.limit is not None:
    model.limit = args.limit

if '.stream' in args.outfile:
    model.saveSelStream(args.outfile)
elif '.lst' in args.outfile:
    model.saveSelLst(args.outfile)
else:
    model.saveSelDat(args.outfile)

