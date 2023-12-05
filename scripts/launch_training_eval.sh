#!/bin/bash
export NUM_GPUS=4
export GLOG_minloglevel=2
export MAGNUM_LOG=quiet
export HABITAT_SIM_LOG=quiet

config="configs/experiments/il_objectnav.yaml"
DATA_PATH="data/datasets/objectnav/hm3d/v1"
TENSORBOARD_DIR="tb/final_8env_mini2/"
CHECKPOINT_DIR="data/data/final_8env_mini2"


echo "In ObjectNav IL DDP"
python -u -m run \
    --exp-config $config \
    --run-type eval \
    TENSORBOARD_DIR $TENSORBOARD_DIR \
    CHECKPOINT_FOLDER $CHECKPOINT_DIR \
    EVAL.USE_CKPT_CONFIG False\
    NUM_UPDATES 50000 \
    NUM_ENVIRONMENTS 16 \
    RL.DDPPO.force_distributed True \
    TASK_CONFIG.DATASET.DATA_PATH "$DATA_PATH/{split}/{split}.json.gz" \
