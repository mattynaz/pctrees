#!/bin/bash -x

#SBATCH --gres=gpu:1      
#SBATCH -p seas_gpu_requeue
#SBATCH -t 18:00:00         # Runtime in D-HH:MM:SS, minimum of 10 minutes
#SBATCH --mem=6000          # Memory pool for all cores (see also --mem-per-cpu) MBs

set -x

module load Anaconda3/2020.11
module load gcc/12.1.0-fasrc01

# baseline with height representation 
python3 -m main --name baseline_height --min_points 1000 --learning_rate 1e-4 --epochs 100 --batch_size 32 --data_dir ../data/MpalaForestGEO_LasClippedtoTreePolygons --label_path labels.csv --top_species 5 --normalize
