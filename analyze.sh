#!/bin/bash
eval "$(conda shell.bash hook)"
conda activate DLC39

VIDEOPATH=$1

python lvm_demodulate.py $VIDEOPATH
python analyze_dlc.py $VIDEOPATH

conda deactivate 


conda activate deepof
python analyze_deepof.py $VIDEOPATH

python guppy_analyze.py $VIDEOPATH
echo "*******************************Done*******************************"
