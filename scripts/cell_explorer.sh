#!/bin/bash

echo "cell_explorer.sh datfile. See datplot.py for more options"
datviewpath=~/software/datview
$datviewpath/scripts/datplot.py --plot 'histogram -x a' --plot 'histogram -x b' --plot 'histogram -x c' \
                        --plot 'histogram -x alpha' --plot 'histogram -x beta' --plot 'histogram -x gamma'\
                        -r 2 -c 3 --left 0.05 --top 0.93 --bottom 0.07 --wspace 0.25 --figwidth 700 --figheight 400 "$@"
