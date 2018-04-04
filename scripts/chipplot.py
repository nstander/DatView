#!/usr/bin/env python

# Author: Natasha Stander

import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt

parser=argparse.ArgumentParser(description='Plot the given column from the stat file using col and chiprow for x and y');
parser.add_argument('--offset',type=float,default=0,help='Add this value to the given column')
parser.add_argument('--xmax',type=int,help='X Maximum')
parser.add_argument('--ymax',type=int,help='Y Maximum')
parser.add_argument('--cmin',type=float,help='Color Map Min')
parser.add_argument('--cmax',type=float,help='Color Map Max')
parser.add_argument('--inverty',action='store_true',help='Invert y axis')
parser.add_argument('--xcol',default='col',help='Name of column for x axis')
parser.add_argument('--ycol',default='chiprow',help='Name of column for y axis')
parser.add_argument('--title','-t',default='Chip Plot',help='Plot Title')
parser.add_argument('--xlabel','-x',default='Column',help='X Axis Label')
parser.add_argument('--ylabel','-y',default='Row',help='Y Axis Label')
parser.add_argument('--save','-s',help='Save the figure to the given filename instead of displaying it')
parser.add_argument('datfile',help='The dat file to use, expects first line to be column names')
parser.add_argument('col',help='The name of the column to plot')
args = parser.parse_args()

cols=[]
with open(args.datfile) as dfile:
  cols=dfile.readline().split()

data = np.loadtxt(args.datfile, skiprows=1,usecols=(cols.index(args.xcol),cols.index(args.ycol),cols.index(args.col)))

x = data[:,0]
y = data[:,1]

xmax = int(np.max(x))
ymax = int(np.max(y))

if args.xmax is not None:
  xmax = args.xmax
if args.ymax is not None:
  ymax = args.ymax

cdat=np.zeros((ymax+1,xmax+1))

for i in range(0,len(x)):
  if x[i] !=-1 and y[i] !=-1 and data[i,2] != -1:
    cdat[int(y[i]),int(x[i])]=data[i,2]+args.offset

valid=data[:,2]
valid=valid[valid!=-1]

cmin = np.min(valid) + args.offset
cmax = np.max(valid) + args.offset

if args.cmin is not None:
  cmin = args.cmin
if args.cmax is not None:
  cmax = args.cmax

fig = plt.figure(figsize=(20,8))
ax1 = plt.subplot(111)
plot = ax1.pcolormesh(cdat,cmap=plt.get_cmap('jet'))
plot.set_clim(cmin,cmax)
if args.inverty:
  plt.gca().invert_yaxis()
plt.axis('image')
plt.subplots_adjust(left=0.03,bottom=0.02,right=0.97,top=0.98,wspace=0,hspace=0)
cbar = plt.colorbar(plot,fraction=0.017,pad=0.02)
if args.col == 'multi':
  cbar.set_ticks((0,1,2,3,4,5))
  cbar.set_ticklabels(('None','Hit','Ind 1', 'Ind 2', 'Ind 3', 'Ind 4'))
plt.xlabel(args.xlabel)
plt.ylabel(args.ylabel)
plt.title(args.title,fontsize=24)
if args.save is None:
  plt.show()
else:
  plt.savefig(args.save, ext="png")

