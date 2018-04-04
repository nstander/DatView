#!/usr/bin/env python

# Based on Peakogram, but for use with dat files, specifically ones output by stream2dat.py
# Author: Natasha Stander

import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt

parser=argparse.ArgumentParser(description='Plot a 2D histogram from a dat file');
parser.add_argument('--bin','-b',type=int,default=50,help='The number of bins')
parser.add_argument('--xmin',type=float,help='X Minimum')
parser.add_argument('--xmax',type=float,help='X Maximum')
parser.add_argument('--ymin',type=float,help='Y Minimum')
parser.add_argument('--ymax',type=float,help='Y Maximum')
parser.add_argument('--title','-t',default='2D Histogram',help='Plot Title')
parser.add_argument('--xlabel','-x',help='X Axis Label, defaults to xcol')
parser.add_argument('--ylabel','-y',help='Y Axis Label, defaults to ycol')
parser.add_argument('--save','-s',help='Save the figure to the given filename instead of displaying it')
parser.add_argument('--config','-c',help='If given, override x/y min, max, and labels with script stored defaults. Currently supported option is psII.')
parser.add_argument('datfile',help='The dat file to use, expects first line to be column names')
parser.add_argument('xcol',help='The name of the column to use on the x axis.')
parser.add_argument('ycol',help='The name of the column to use on the y axis.')
args = parser.parse_args()

if args.config == "psII":
  psIImap={'reslim' : ('Diffraction Resolution Limit (nm^-1)',None,None),
           'a'      : ('Cell A Axis (nm)', 12.5 , 14.5),
           'b'      : ('Cell B Axis (nm)', 22.2 , 24.2),
           'c'      : ('Cell C Axis (nm)', 30.0 , 32.0),
           'alpha'  : ('Alpha Angle', None, None),
           'beta'   : ('Beta Angle', None, None),
           'gamma'  : ('Gamma Angle', None, None),
           'phoen'  : ('Photon Energy', None, None),
           'bmdv'   : ('Beam Divergence', None, None),
           'bmbw'   : ('Beam Bandwidth', None, None),
           'npeak'  : ('Number of Cheetah Peaks', None, None),
           'prorad' : ('Profile Radius (nm^-1)', None, None),
           'detdx'  : ('Detector X Shift (mm)', -1, 1),
           'detdy'  : ('Detector Y Shift (mm)', -1, 1),
           'nref'   : ('Number of Reflections', None, None),
           'niref'  : ('Number of implausibly negative reflections', None, 25),
           'run'    : ('Run', None, None),
           'Scale'  : ('Process_hkl Scale', None, None),
           'CC'     : ('Process_hkl CC', None, None)
          }
  args.xmin=psIImap[args.xcol][1] 
  args.xmax=psIImap[args.xcol][2]
  args.xlabel=psIImap[args.xcol][0]
  args.ymin=psIImap[args.ycol][1]
  args.ymax=psIImap[args.ycol][2]
  args.ylabel=psIImap[args.ycol][0]
  

cols=[]
with open(args.datfile) as dfile:
  cols=dfile.readline().split()

data = np.loadtxt(args.datfile, skiprows=1,usecols=(cols.index(args.xcol),cols.index(args.ycol)))

x = data[:,0]
y = data[:,1]

xmin = np.min(x)
xmax = np.max(x)
ymin = np.min(y)
ymax = np.max(y)
xlabel=args.xcol
ylabel=args.ycol

if args.xmin is not None:
  xmin = args.xmin
if args.xmax is not None:
  xmax = args.xmax
if args.ymin is not None:
  ymin = args.ymin
if args.ymax is not None:
  ymax = args.ymax
if args.xlabel is not None:
  xlabel=args.xlabel
if args.ylabel is not None:
  ylabel=args.ylabel

keepers = np.where((x>=xmin) & (x<=xmax) & (y>=ymin) & (y<=ymax))

x = x[keepers]
y = y[keepers]

H,xedges,yedges = np.histogram2d(y,x,bins=args.bin)

fig = plt.figure()
ax1 = plt.subplot(111)
plot = ax1.pcolormesh(yedges,xedges,H)
cbar = plt.colorbar(plot)
plt.xlabel(xlabel)
plt.ylabel(ylabel)
plt.title(args.title)
if args.save is None:
  plt.show()
else:
  plt.savefig(args.save, ext="png")

