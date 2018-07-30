#!/bin/bash

echo "This message always prints. Usage: datfile process-hkl-output.dat outputname. This script is meant to be updated with filepaths appropriate for your computer."
(echo "ifile event phkl_scale phkl_cc"; sed 's|//||g' $2) | ~/software/datview/scripts/groupify.py --group groupcfg.txt | ~/software/datview/scripts/datupdate.py --datfile1 $1 --outfile $3 --npformats i4 i4 f4 f4

