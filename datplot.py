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

import shlex
import numpy as np
import h5py
from cfelpyutils import cfel_geom
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

def xRange(plot,plotArgs):
    xr=list(plot.plt.get_xlim())
    if plotArgs.xmin is not None:
        xr[0]=plotArgs.xmin
    if plotArgs.xmax is not None:
        xr[1]=plotArgs.xmax
    return xr

def yRange(plot,plotArgs):
    yr=list(plot.plt.get_ylim())
    if plotArgs.ymin is not None:
        yr[0]=plotArgs.ymin
    if plotArgs.ymax is not None:
        yr[1]=plotArgs.ymax
    return yr

def limits(plot,plotArgs):
    plot.plt.set_xlim(tuple(xRange(plot,plotArgs)))
    plot.plt.set_ylim(tuple(yRange(plot,plotArgs)))
    plot.vmin=plotArgs.cmin
    plot.vmax=plotArgs.cmax

def dataAndTitle(plot,plotArgs,keepLimits=False):
    if plotArgs.datashown == 'raw':
        plot.drawAll.setChecked(True)
    elif plotArgs.datashown == 'filtered':
        plot.drawSelection.setChecked(True)

    plot.mydraw(keepLimits)
    
    if plotArgs.title is not None:
        plot.plt.set_title(plotArgs.title)

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
    plotArgs=histParser.parse_args(shlex.split(plotArgString[9:]))
    ax=generateAxis(figArgs,plotNum,plotArgs)
    h=myFigure.histogram(model,plotArgs.xfield,ax)

    h.range=tuple(xRange(h,plotArgs))

    if plotArgs.xbins is not None:
        h.bins=plotArgs.xbins

    if plotArgs.fit:
        h.calcFit()
        model.filterchange.connect(h.calcFit)

    dataAndTitle(h,plotArgs)

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
    plotArgs=hist2dParser.parse_args(shlex.split(plotArgString[11:]))
    ax=generateAxis(figArgs,plotNum,plotArgs)
    h=myFigure.histogram2D(model,plotArgs.xfield,plotArgs.yfield,plotArgs.log,ax)

    h.range=(tuple(xRange(h,plotArgs)),tuple(yRange(h,plotArgs)))

    if plotArgs.xbins is not None:
        h.xbins=args.xbins
    if plotArgs.ybins is not None:
        h.xbins=args.ybins

    dataAndTitle(h,plotArgs)

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
    plotArgs=scatterParser.parse_args(shlex.split(plotArgString[7:]))
    ax=generateAxis(figArgs,plotNum,plotArgs)
    s=myFigure.scatter(model,plotArgs.xfield,plotArgs.yfield,plotArgs.cfield,ax)

    limits(s,plotArgs)
    dataAndTitle(s,plotArgs,True)

pixelParser=argparse.ArgumentParser(prog="pixelplot")
pixelParser.add_argument('-x','--xfield',required=True)
pixelParser.add_argument('--xmin',type=float,default=None,help="x minimum, field minimum (without -1) by default")
pixelParser.add_argument('--xmax',type=float,default=None,help="x maximum, field maximum by default")
pixelParser.add_argument('-y','--yfield',required=True)
pixelParser.add_argument('--ymin',type=float,default=None,help="x minimum, field minimum (without -1) by default")
pixelParser.add_argument('--ymax',type=float,default=None,help="x maximum, field maximum by default")
pixelParser.add_argument('-c','--cfield',required=True,help="Color by field")
pixelParser.add_argument('--cmin',type=float,default=None,help="color minimum, field minimum (without -1) by default")
pixelParser.add_argument('--cmax',type=float,default=None,help="color maximum, field maximum by default")
pixelParser.add_argument('-t','--title',default=None,help="Plot title, defaults to pretty version of color by field name")
pixelParser.add_argument('--datashown',choices=['raw','filtered'],default='filtered',help="Plot just the filtered or plot the complete dataset")
pixelParser.add_argument('--prow',default=None,type=int,help="Plot row inside figure (used in subplot2grid, first row is 0).")
pixelParser.add_argument('--pcol',default=None,type=int,help="Plot column inside figure (used in subplot2grid, first row is 0).")
pixelParser.add_argument('--prowspan',default=1,type=int,help="Plot row span inside figure (used in subplot2grid).")
pixelParser.add_argument('--pcolspan',default=1,type=int,help="Plot column span inside figure (used in subplot2grid).")

def pixelPlot(model,myFigure,figArgs,plotNum,plotArgString):
    plotArgs=pixelParser.parse_args(shlex.split(plotArgString[9:]))
    ax=generateAxis(figArgs,plotNum,plotArgs)
    p=myFigure.pixelPlot(model,plotArgs.xfield,plotArgs.yfield,plotArgs.cfield,ax)

    limits(p,plotArgs)
    dataAndTitle(p,plotArgs,True)

imageH5Parser=argparse.ArgumentParser(prog="imageh5")
imageH5Parser.add_argument('-i','--imagefile',required=True,help="The image file path")
imageH5Parser.add_argument('-g','--geom',default=None,help="CrystFEL Geometry file")
imageH5Parser.add_argument('-d','--datapath',default=None,help="Path in H5 file to load data from. Checks image file paths from config if not provided")
imageH5Parser.add_argument('-e','--event',type=int,default=None,help="event number")
imageH5Parser.add_argument('--cmap',default="jet",help="Color map to use")
imageH5Parser.add_argument('--cmin',type=float,default=None,help="color minimum")
imageH5Parser.add_argument('--cmax',type=float,default=None,help="color maximum")
imageH5Parser.add_argument('-t','--title',default=None,help="Plot title, defaults to datapath")
imageH5Parser.add_argument('--prow',default=None,type=int,help="Plot row inside figure (used in subplot2grid, first row is 0).")
imageH5Parser.add_argument('--pcol',default=None,type=int,help="Plot column inside figure (used in subplot2grid, first row is 0).")
imageH5Parser.add_argument('--prowspan',default=1,type=int,help="Plot row span inside figure (used in subplot2grid).")
imageH5Parser.add_argument('--pcolspan',default=1,type=int,help="Plot column span inside figure (used in subplot2grid).")

def imageh5(model,myFigure,figArgs,plotNum,plotArgString):
    plotArgs=imageH5Parser.parse_args(shlex.split(plotArgString[7:]))
    ax=generateAxis(figArgs,plotNum,plotArgs)

    f=h5py.File(plotArgs.imagefile,'r')
    path=plotArgs.datapath
    if path is None:
        for p in model.cfg.imageH5paths:
            if p in f:
                path=p
                break
    if path is None:
        print("Error: need a data path in h5 file. Couldn't find any default paths.")
        return
    if plotArgs.event is None:
        data=f[path]
    else:
        data=f[path][e]

    if plotArgs.geom is not None:
        data=cfel_geom.apply_geometry_from_file(np.array(data),plotArgs.geom)

    img=myFigure.image(data,ax)
    img.cmap = plotArgs.cmap
    img.vmin = plotArgs.cmin
    img.vmax = plotArgs.cmax
    img.mydraw(True)
    if plotArgs.title:
        img.plt.set_title(plotArgs.title)
    f.close()



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
    pixelParser.print_usage(plothelp)
    imageH5Parser.print_usage(plothelp)
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
  -l, --log             Use log color scale
  -i, --imagefile       The image file path
  -g, --geom            CrystFEL geometry file for image file
  -d, --datapath        Path in H5 file to get image from, guessed from
                        config if not provided
  -e, --event           Event number of image file
  --cmap                Color map name, defaults from config""")
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
    parser.add_argument('--partnum',default=[],nargs='+',type=int,help='The number of partitions to create. Note that empty partitions are not output so the total output may be less than this number. This defaults to ten for continuous fields or all possible for categorical fields. Accepts multiple arguments, one for each field. Unspecified arguments default to None')
    parser.add_argument('--partmin',default=[],nargs='+',type=float,help='Set the minimum of the range to be partitioned. Accepts multiple arguments, one for each field. Unspecified arguments default to None')
    parser.add_argument('--partmax',default=[],nargs='+',type=float,help='Set the maximum of the range to be partitioned. Accepts multiple arguments, one for each field. Unspecified arguments default to None')
    parser.add_argument('--partition',default=None,nargs='+',help='Field name(s) to partition on. Partitioning only occurs if this is provided, otherwise partnum, partmin, and partmax are not used. Partition names appended to outfile as outfile_nm')

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
        elif p.startswith("pixelplot"):
            pixelPlot(model,qFig,args,i,p)
        elif p.startswith("imageh5"):
            imageh5(model,qFig,args,i,p)
        else:
            print("Unrecognized plot string: ",p)

    if args.title is not None:
        qFig.fig.suptitle(args.title,fontsize=20)

    if args.save is not None:
        partitions=None
        if args.partition is not None:
            partitions=model.partitionMulti(args.partition,args.partmin,args.partmax,args.partnum)
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


    




        

