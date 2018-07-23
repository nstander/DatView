#!/bin/bash

echo "This usage message always prints. This script does not check that the dat files are compatible."
echo "Usage: datconcat.sh output input[s]"
cp $2 $1
tail -q -n +2 ${@:3} >> $1

