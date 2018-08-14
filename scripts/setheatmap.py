#!/usr/bin/env python3

# Author: Natasha Stander

import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt

parser=argparse.ArgumentParser(description='Calculate overlap between sets and display as heatmap');
parser.add_argument('--columns',default=['g_ifile','event'],nargs='+',help="The columns to compare between files. By default, will be g_ifile and event.")
parser.add_argument('--npformats',default=['i4','i4'],nargs='+',help="The corresponding data types")
parser.add_argument('--names',default=None,nargs='+',help="If provided, should be names to use instead of file names")
parser.add_argument('--title','-t',default='Intersection Heatmap',help='Plot Title')
parser.add_argument('--save','-s',help='Save the figure to the given filename instead of displaying it')
parser.add_argument("--ext",default="png", help="extension to use in call to savefig. Default=png")
parser.add_argument("--dpi",type=float,default=None, help="dpi to use in call to savefig. Default=png")
parser.add_argument('datfiles',nargs='+',help='The datfiles to use')
args = parser.parse_args()

if args.names is None:
    args.names = args.datfiles

sets=[]
for i in range(len(args.datfiles)):
    cols=[]
    with open(args.datfiles[i]) as dfile:
      cols=dfile.readline().split()

    use=[]
    for col in args.columns:
        use.append(cols.index(col))

    sets.append(set(map(tuple,np.loadtxt(args.datfiles[i], dtype={'names' : tuple(args.columns), 'formats' : tuple(args.npformats)},skiprows=1,usecols=tuple(use)))))

cdat=np.zeros((len(sets),len(sets)))
for i in range(len(sets)):
    s=set()
    s.update(sets[i])
    for k in range(len(sets)):
        if k != i:
            s -= sets[k]
    cdat[i,i]=len(s)
    for j in range(i+1,len(sets)):
        cdat[i,j] = len(sets[i] & sets[j])
        cdat[j,i] = len(sets[i] & sets[j])

fig = plt.figure(figsize=(13,8))
ax1 = plt.subplot(111)
plot = ax1.pcolormesh(cdat,cmap=plt.get_cmap('Wistia'))
plt.axis('image')
cbar = plt.colorbar(plot)
plt.xticks(np.arange(len(sets))+0.5,args.names,rotation=10)
ax1.set_yticks(np.arange(len(sets))+0.5)
ax1.set_yticklabels(args.names)
plt.title(args.title,fontsize=24)
plt.gca().invert_yaxis()
for i in range(len(sets)):
    for j in range(len(sets)):
        plt.text(i+0.25,j+0.5,'%.0f' % (cdat[i,j],))
if args.save is None:
  plt.show()
else:
  plt.savefig(args.save, ext=args.ext,dpi=args.dpi)


