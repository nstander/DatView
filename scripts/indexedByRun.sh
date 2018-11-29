#!/bin/bash

echo "Run   Frames  Indexed_Frames  Indexed_Crystals  Average_Diffraction_Resolution_Limit_nm-1 Average_Volume  STD_Volume"
~/software/datview/scripts/datstats.py  --count multiid 0 1 --count multiid 1 --countGE multiid 1 --average reslim --average vol  --partition run --cols run count_multiid_0_1 count_multiid_1 countGE_multiid_1 average_reslim average_vol std_vol --std vol $1 | sort -g
