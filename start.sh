#!/bin/bash
eval "$(conda shell.bash hook)"
conda activate DLC39

VIDEOPATH=$(python load_parameters.py)

conda deactivate

bash analyze.sh $VIDEOPATH