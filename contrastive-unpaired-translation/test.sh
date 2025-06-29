#!/bin/bash

python test.py \
  --dataroot ./datasets/synth2real \
  --name synth2real \
  --model cut \
  --dataset_mode unaligned \
  --epoch latest \
  --num_test 25 \
  --no_dropout \
  --load_size 720 \
  --crop_size 720 \
  --phase test