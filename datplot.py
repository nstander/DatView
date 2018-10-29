#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# datview/datplot.py
# Command line interface to generate plots
# Author Natasha Stander

import sys
import argparse
import io

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
except ImportError:
    from PyQt4.QtGui import QApplication
    from PyQt4.QtCore import Qt

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec

from api.datamodel import DataModel
from api.modelcfg import ModelConfig

from ui.plots import MyFigure

def generateAxis(figArgs,plotnum,args):
    r=args.prow
    c=args.pcol
    if r is None:
        r=int(plotnum/figArgs.cols)
    if c is None:
        c=plotnum%figArgs.cols
    return figArgs.fig.add_subplot(figArgs.gs[r:(r+args.prowspan),c:(c+args.pcolspan)])

histParser=argparse.ArgumentParser(prog="histogram")
histParser.add_argument('-x','--xfield',required=True)
histParser.add_argument('--xmin',type=float,default=None,help="x minimum, field minimum (without -1) by default")
histParser.add_argument('--xmax',type=float,default=None,help="x maximum, field maximum by default")
histParser.add_argument('-t','--title',default=None,help="Plot title, defaults to pretty version of field name")
histParser.add_argument('--datashown',choices=['raw','filtered','both'],default='both',help="Plot just the filtered, the complete dataset, or both with complete semi-transparent")
histParser.add_argument('--xbins',default=None,type=int,help="Number of bins. Default from config file. Does not apply to categorical variables.")
histParser.add_argument('-f','--fit',action='store_true',help="Plot the fit line - note this overrides the title to specify the mean and standard deviation.")
histParser.add_argument('--prow',default=None,type=int,help="Plot row inside figure (used in subplot2grid, first row is 0).")
histParser.add_argument('--pcol',default=None,type=int,help="Plot column inside figure (used in subplot2grid, first row is 0).")
histParser.add_argument('--prowspan',default=1,type=int,help="Plot row span inside figure (used in subplot2grid).")
histParser.add_argument('--pcolspan',default=1,type=int,help="Plot column span inside figure (used in subplot2grid).")

def histogram(model,myFigure,figArgs,plotNum,plotArgString):
    plotArgs=histParser.parse_args(plotArgString.split()[1:])
    ax=generateAxis(figArgs,plotNum,plotArgs)
    h=myFigure.histogram(model,plotArgs.xfield,ax)

    r=h.plt.get_xlim()
    if plotArgs.xmin is not None:
        r[0]=plotArgs.xmin
    if plotArgs.xmax is not None:
        r[1]=plotArgs.xmin
    h.range=tuple(r)

    if plotArgs.xbins is not None:
        h.bins=plotArgs.xbins

    if plotArgs.fit:
        h.calcFit()
        model.filterchange.connect(h.calcFit)

    if plotArgs.datashown == 'raw':
        h.drawAll.setChecked(True)
    elif plotArgs.datashown == 'filtered':
        h.drawSelection.setChecked(True)

    h.mydraw(False)
    
    if plotArgs.title is not None:
        h.plt.set_title(plotArgs.title)

hist2dParser=argparse.ArgumentParser(prog="histogram2D")
hist2dParser.add_argument('-x','--xfield',required=True)
hist2dParser.add_argument('--xmin',type=float,default=None,help="x minimum, field minimum (without -1) by default")
hist2dParser.add_argument('--xmax',type=float,default=None,help="x maximum, field maximum by default")
hist2dParser.add_argument('--xbins',default=None,type=int,help="Number of x bins. Default from config file. Does not apply to categorical variables")
hist2dParser.add_argument('-y','--yfield',required=True)
hist2dParser.add_argument('--ymin',type=float,default=None,help="x minimum, field minimum (without -1) by default")
hist2dParser.add_argument('--ymax',type=float,default=None,help="x maximum, field maximum by default")
hist2dParser.add_argument('--ybins',default=None,type=int,help="Number of x bins. Default from config file. Does not apply to categorical variables")
hist2dParser.add_argument('-t','--title',default=None,help="Plot title, defaults to pretty version of field name")
hist2dParser.add_argument('--datashown',choices=['raw','filtered'],default='filtered',help="Plot just the filtered, or the complete dataset")
hist2dParser.add_argument('-l','--log',action='store_true',help="Use log color scale.")
hist2dParser.add_argument('--prow',default=None,type=int,help="Plot row inside figure (used in subplot2grid, first row is 0).")
hist2dParser.add_argument('--pcol',default=None,type=int,help="Plot column inside figure (used in subplot2grid, first row is 0).")
hist2dParser.add_argument('--prowspan',default=1,type=int,help="Plot row span inside figure (used in subplot2grid).")
hist2dParser.add_argument('--pcolspan',default=1,type=int,help="Plot column span inside figure (used in subplot2grid).")

def histogram2d(model,myFigure,figArgs,plotNum,plotArgString):
    plotArgs=hist2dParser.parse_args(plotArgString.split()[1:])
    ax=generateAxis(figArgs,plotNum,plotArgs)
    h=myFigure.histogram2D(model,plotArgs.xfield,plotArgs.yfield,plotArgs.log,ax)

    xr=h.plt.get_xlim()
    if plotArgs.xmin is not None:
        xr[0]=plotArgs.xmin
    if plotArgs.xmax is not None:
        xr[1]=plotArgs.xmin

    yr=h.plt.get_ylim()
    if plotArgs.ymin is not None:
        yr[0]=plotArgs.ymin
    if plotArgs.ymax is not None:
        yr[1]=plotArgs.ymin

    h.range=(tuple(xr),tuple(yr))

    if plotArgs.xbins is not None:
        h.xbins=args.xbins
    if plotArgs.ybins is not None:
        h.xbins=args.ybins


    if plotArgs.datashown == 'raw':
        h.drawAll.setChecked(True)
    elif plotArgs.datashown == 'filtered':
        h.drawSelection.setChecked(True)

    h.mydraw(False)
    
    if plotArgs.title is not None:
        h.plt.set_title(plotArgs.title)

scatterParser=argparse.ArgumentParser(prog="scatter")
scatterParser.add_argument('-x','--xfield',required=True)
scatterParser.add_argument('--xmin',type=float,default=None,help="x minimum, field minimum (without -1) by default")
scatterParser.add_argument('--xmax',type=float,default=None,help="x maximum, field maximum by default")
scatterParser.add_argument('-y','--yfield',required=True)
scatterParser.add_argument('--ymin',type=float,default=None,help="x minimum, field minimum (without -1) by default")
scatterParser.add_argument('--ymax',type=float,default=None,help="x maximum, field maximum by default")
scatterParser.add_argument('-c','--cfield',default=None,help="Color by field")
scatterParser.add_argument('--cmin',type=float,default=None,help="color minimum, field minimum (without -1) by default")
scatterParser.add_argument('--cmax',type=float,default=None,help="color maximum, field maximum by default")
scatterParser.add_argument('-t','--title',default=None,help="Plot title, defaults to pretty version of color by field name")
scatterParser.add_argument('--datashown',choices=['raw','filtered','both'],default='both',help="Plot just the filtered, the complete dataset, or both with complete semi-transparent")
scatterParser.add_argument('--prow',default=None,type=int,help="Plot row inside figure (used in subplot2grid, first row is 0).")
scatterParser.add_argument('--pcol',default=None,type=int,help="Plot column inside figure (used in subplot2grid, first row is 0).")
scatterParser.add_argument('--prowspan',default=1,type=int,help="Plot row span inside figure (used in subplot2grid).")
scatterParser.add_argument('--pcolspan',default=1,type=int,help="Plot column span inside figure (used in subplot2grid).")

def scatter(model,myFigure,figArgs,plotNum,plotArgString):
    plotArgs=scatterParser.parse_args(plotArgString.split()[1:])
    ax=generateAxis(figArgs,plotNum,plotArgs)
    s=myFigure.scatter(model,plotArgs.xfield,plotArgs.yfield,plotArgs.cfield,ax)

    xr=s.plt.get_xlim()
    if plotArgs.xmin is not None:
        xr[0]=plotArgs.xmin
    if plotArgs.xmax is not None:
        xr[1]=plotArgs.xmin

    yr=s.plt.get_ylim()
    if plotArgs.ymin is not None:
        yr[0]=plotArgs.ymin
    if plotArgs.ymax is not None:
        yr[1]=plotArgs.ymin

    s.plt.set_xlim(tuple(xr))
    s.plt.set_ylim(tuple(yr))
    s.vmin=plotArgs.cmin
    s.vmax=plotArgs.cmax

    if plotArgs.datashown == 'raw':
        s.drawAll.setChecked(True)
    elif plotArgs.datashown == 'filtered':
        s.drawSelection.setChecked(True)

    s.mydraw()
    
    if plotArgs.title is not None:
        s.plt.set_title(plotArgs.title)

def saveFigByPartitions(args,partname=None):
    nm = args.save
    if partname is not None:
        nm = args.save % partname
        if '%' in args.title:
            args.qFig.fig.suptitle(args.title%partname,fontsize=20)
    if args.save.endswith("svg"):
        args.qFig.print_figure(nm,format="svg")
    else:
        args.qFig.print_figure(nm,format="png",dpi=args.dpi)

if __name__ == '__main__':
    plothelp=io.StringIO()
    plothelp.write("Available Plots:\n")
    histParser.print_usage(plothelp)
    hist2dParser.print_usage(plothelp)
    scatterParser.print_usage(plothelp)
    plothelp.write("""
Plot Argument Descriptions:
  -x XFIELD, --xfield XFIELD
  --xmin XMIN           x minimum, field minimum (without -1) by default
  --xmax XMAX           x maximum, field maximum by default
  --xbins XBINS         Number of x bins. Default from config file. Does not
                        apply to categorical variables
  -y YFIELD, --yfield YFIELD
  --ymin YMIN           x minimum, field minimum (without -1) by default
  --ymax YMAX           x maximum, field maximum by default
  --ybins YBINS         Number of x bins. Default from config file. Does not
                        apply to categorical variables
  -c CFIELD, --cfield CFIELD
                        Color by field
  --cmin CMIN           color minimum, field minimum (without -1) by default
  --cmax CMAX           color maximum, field maximum by default
  -t TITLE, --title TITLE
                        Plot title, defaults to pretty version of color by
                        field name
  --datashown {raw,filtered,both}
                        Plot just the filtered, the complete dataset, or both
                        with complete semi-transparent
  --prow PROW           Plot row inside figure (used in subplot2grid, first
                        row is 0).
  --pcol PCOL           Plot column inside figure (used in subplot2grid, first
                        col is 0).
  --prowspan PROWSPAN   Plot row span inside figure (used in subplot2grid).
  --pcolspan PCOLSPAN   Plot column span inside figure (used in subplot2grid).
  -f, --fit             Plot the fit line - note a provided title overrides
                        the the mean and standard deviation display in title.
  -l, --log             Use log color scale""")
    parser=argparse.ArgumentParser(description="""Command line interface for plotting. Group, filter, sort, and partition\noptions are available, and if partitions are given then output is saved for\neach partition separately. This script supports subplots, so each plot must be\nspecified with --plot/-p and the argument to plot must be quoted to be read in\nas a single string. The argument to plot specifies all the options for the\ngiven plot.""",epilog=plothelp.getvalue().replace("usage:",""),formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-p','--plot',action='append',default=[],help='Add a plot to the figure, has a single argument (use quotes) to be parsed on its own, see bottom of help text for options')
    parser.add_argument('-r','--rows',default=None,type=int,help="The number of rows in the figure. Defaults to rows in config if more than one plot provided. You should specify this if you start using prowspan and pcolspan in plots.")
    parser.add_argument('-c','--cols',default=None,type=int,help="The number of cols in the figure. Defaults to rows in config divided by number of plots if more than one plot provided. You should specify this if you start using prowspan and pcolspan in plots.")
    parser.add_argument('--left',default=0.1,type=float,help="left argument to the grid spec")
    parser.add_argument('--right',default=0.95,type=float,help="right argument to the grid spec")
    parser.add_argument('--bottom',default=0.15,type=float,help="bottom argument to the grid spec")
    parser.add_argument('--top',default=0.83,type=float,help="top argument to the grid spec")
    parser.add_argument('--wspace',default=0.4,type=float,help="wspace argument to the grid spec")
    parser.add_argument('--hspace',default=0.3,type=float,help="hspace argument to the grid spec")
    parser.add_argument('--figwidth',default=None,type=float,help="fig width in pixels, defaults to 300*cols")
    parser.add_argument('--figheight',default=None,type=float,help="fig height in pixels, defaults to 300*rows")
    parser.add_argument('--dpi',default=None,type=int,help="DPI for saving")

    parser.add_argument('-t','--title',default=None,help="Overall Figure title, Use %%s to include partition name")
    parser.add_argument('-s','--save',default=None,help="Save to provided file name instead of displaying. The filename can contain %%s to show the spot to include the partition name. Extension png or svg determines save output type")

    parser.add_argument('--group',default=None,help='The group file output by groupgen.py (groupcfg.txt)')
    parser.add_argument('--filter',default=None,help='A filter file to load. Filter files are XML format. The first Between filter in the file for a field will be updated with selection.')
    parser.add_argument('--sort',default=None,nargs='+',help='One or more fields to sort the output by. Field names must match the header of the dat file. Multiple arguments accepted so don\'t use as last switch before inputs.')
    parser.add_argument('--reversesort',action="store_true",help='Sort descending instead of ascending')
    parser.add_argument('--cfg',default=None,help='Use the provided configuration file (xml) instead of the default one. Default one is found in api/modelcfg.xml')
    parser.add_argument('--partnum',default=None,type=int,help='The number of partitions to create. Note that empty partitions are not output so the total output may be less than this number. This defaults to ten for continuous fields or all possible for categorical fields.')
    parser.add_argument('--partmin',default=None,type=float,help='Set the minimum of the range to be partitioned')
    parser.add_argument('--partmax',default=None,type=float,help='Set the maximum of the range to be partitioned')
    parser.add_argument('--partition',default=None,help='Field name to partition on. Partitioning only occurs if this is provided and plots are being saved, otherwise partnum, partmin, and partmax are not used. Partition names appended to outfile if %%s is not present')

    parser.add_argument('datfile',help='the dat file (or a .npz file output from datview/datexport)')
    args=parser.parse_args()


    # Load Dat File
    model=DataModel(args.datfile,args.group,cfg=ModelConfig(args.cfg))
    if args.filter is not None:
        model.loadFilters(args.filter)
    if args.sort is not None:
        model.sortlst = args.sort
    model.reverseSort = args.reversesort

    if args.cols is None:
        if len(args.plot) == 1:
            args.cols = 1
        else:
            args.cols=model.cfg.histperrow
    if args.rows is None:
        if len(args.plot) == 1:
            args.rows = 1
        else:
            args.rows=int(np.ceil(len(args.plot)/args.cols))

    if args.figwidth is None:
        args.figwidth=300*args.cols
    if args.figheight is None:
        args.figheight=300*args.rows
    qFig=MyFigure(flags=Qt.Window)
    qFig.setAttribute(Qt.WA_DeleteOnClose)
    qFig.resize(args.figwidth,args.figheight)
    qFig.fig.set_size_inches(args.figwidth/qFig.fig.dpi,args.figheight/qFig.fig.dpi)
    args.gs=matplotlib.gridspec.GridSpec(args.rows,args.cols,left=args.left,right=args.right,bottom=args.bottom,\
                                        top=args.top,wspace=args.wspace,hspace=args.hspace)
    args.fig=qFig.fig

    for i,p in enumerate(args.plot):
        if p.startswith("histogram2D") or p.startswith("histogram2d"):
            histogram2d(model,qFig,args,i,p)
        elif p.startswith("histogram"):
            histogram(model,qFig,args,i,p)
        elif p.startswith("scatter"):
            scatter(model,qFig,args,i,p)
        else:
            print("Unrecognized plot string: ",p)

    if args.title is not None:
        qFig.fig.suptitle(args.title,fontsize=20)

    if args.save is not None:
        partitions=None
        if args.partition is not None:
            partitions=model.partition(args.partition,args.partmin,args.partmax,args.partnum)
            if '%' not in args.save:
                args.save += '_%s'

        args.qFig=qFig
        model.saveByPartitions(args,saveFigByPartitions,partitions,False,False)

    else:
        app = QApplication(sys.argv)
        qFig.show()
        r= app.exec_()
        app.deleteLater()
        sys.exit(r)


    




        

