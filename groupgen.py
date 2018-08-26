#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# datview/groupgen.py
# Program for write-access to group files
# Author Natasha Stander

import os
import fnmatch
import argparse

class GroupGenerator:
    def __init__(self):
        self.added={}
        self.groups={}
        pass

    def addfiles(self,col,directory,glob,verbose=False):
        for root,dirnames,filenames in os.walk(directory):
            if verbose:
                print('\t%s' % root,end='\r',flush=True)
            for filename in fnmatch.filter(sorted(filenames),glob):
                self.add(col,os.path.join(root,filename),col,os.path.join(root,filename))
            for dname in fnmatch.filter(dirnames,'indexamajig.[0-9]*'):
                dirnames.remove(dname)
            dirnames.sort()
        if verbose:
            print('\n')
            

    def add(self,groupname,entryname,entrycol,entryvals):
        """
        Add an entry to a group. Overwrites the entrycol and entryvals
        if group already exists.

        Args:
            groupname: name of group (ifile, sfile, sample, etc)
            entryname: name of entry (file,file,ps2,etc)
            entrycol:  name of column to determine grouping (ifile,sfile,run,etc)
            entryvals: comma seperated list of values for column to map to group
        """
        if groupname not in self.added:
            self.added[groupname]={}
            self.groups[groupname]={}

        if entryname in self.added[groupname]:
            i=self.added[groupname][entryname]
        else:
            i=len(self.added[groupname])

        self.added[groupname][entryname]=i
        self.groups[groupname][i]=[groupname,i,entryname,entrycol,entryvals]
        pass

    def load(self,filename):
        with open(filename) as fin:
            line = fin.readline() # skip header line
            while True:
                line = fin.readline()
                if not line:
                    break
                fields = list(filter(None,line.strip().split('\t')))
                assert len(fields) == 5 # proper group file formats have 5 non-empty fields
                assert fields[0] not in self.added or fields[2] not in self.added[fields[0]] # Shouldn't have same entry multiple times
                if fields[0] not in self.added:
                    self.added[fields[0]]={}
                    self.groups[fields[0]]={}
                self.added[fields[0]][fields[2]]=int(fields[1])
                self.groups[fields[0]][int(fields[1])]=fields

    def save(self,filename):
        with open(filename,'w') as fout:
            fout.write('%s\t%s\t%s\t%s\t%s\n' % ('group','id','value','matchcol','matchvals'))
            for group in self.groups:
                # Looping over range allows asserting that numbering starts at 0 and continues without skipping
                for i in range(len(self.groups[group])):
                    assert i in self.groups[group]
                    fout.write('%s\t%s\t%s\t%s\t%s\n' % tuple(self.groups[group][i]))

    def addVal(self,group,entry,val):
        assert group in self.groups and entry in self.added[group]
        self.groups[group][self.added[group][entry]][4] += "," + str(val)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Create a group file for an experiment. Keeps dat files shorter by removing redundant strings and allows custom groups. Custom groups can be added with --group. A custom group has a groupname that determines the output column name and entries for each set. For instance, a sample group might have --group sample ps2 run 1 2 3 4 --group sample phyco run 5 6. That would result in a sample column in the dat file where any crystals from runs 1 2 3 or 4 would be mapped to ps2 and any crystals from runs 5 or 6 would be mapped to phyco. Values in dat file map to the entry names rather than recording them directly to save space on things like long filepaths and make it easier to read the files in with numpy without worrying about the length of the field. Matchvalues can be a file containing one value per line. To use that feature, begin the filepath with @. For example -g laser on ifile @filepath.');
    parser.add_argument('--sdir',help='directory to search for stream files')
    parser.add_argument('--sglob',default='*.stream*',help='pattern to match stream files. Only used if --sdir given')
    parser.add_argument('--idir',help='directory to search for cxi (image) files')
    parser.add_argument('--iglob',default='*.cxi',help='pattern to match cxi (image) files. Only used if --idir given')
    parser.add_argument('--group','-g',action='append',nargs='+',help='Add entry to a custom group. Expects 4+ arguments: groupname, entryname, matchcolumn, matchvalues where matchvalues is one or more arguments.')
    parser.add_argument('--update','-u',action='append',nargs='+',help='Add value(s) to matchvals of custom group. Expects 3+ arguments: groupname, entryname, matchvalue(s).')
    parser.add_argument('-v',action='store_true',help='Verbose')
    parser.add_argument('--file',default='groupcfg.txt',help='The output file group file. If it already exists, then this command adds to the existing information. Note that adding an entry again will overwrite the previous matchcolumn and matchvalues.')

    args=parser.parse_args()

    g=GroupGenerator()
    if os.path.exists(args.file):
        if args.v:
            print ("Loading existing file")
        g.load(args.file)
    if args.sdir:
        if args.v:
            print ("Looking for stream files")
        g.addfiles('sfile',args.sdir,args.sglob,args.v)
    if args.idir:
        if args.v:
            print ("Looking for image/cxi files")
        g.addfiles('ifile',args.idir,args.iglob,args.v)
    if args.group and len(args.group):
        if args.v:
            print ("Adding custom groups")
        for lst in args.group:
            assert len(lst) >= 4
            g.add(lst[0],lst[1],lst[2],','.join(lst[3:]))
    if args.update and len(args.update):
        if args.v:
            print ("Updating custom groups")
        for lst in args.update:
            assert len(lst) >= 3
            g.addVal(lst[0],lst[1],','.join(lst[2:]))
    if args.v:
        print ("Saving")
    g.save(args.file)
        




