#!/bin/bash

DATASET_NAME="synth2real"
CUDA_VISIBLE_DEVICES=0 python train.py \
  --dataroot ./datasets/$DATASET_NAME \
  --name $DATASET_NAME \
  --CUT_mode CUT \
  --batch_size 1 \
  --n_epochs 100 \
  --n_epochs_decay 100 \
  --save_epoch_freq 10 \
  --gpu_ids 0 \
  --display_ncols 4 \
  --display_freq 100 \
  --display_port 8097 \
  --display_server http://localhost \
  --checkpoints_dir ./checkpoints \
  --num_threads 0