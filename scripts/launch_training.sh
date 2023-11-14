#!/bin/bash
export NUM_GPUS=4
export GLOG_minloglevel=2
export MAGNUM_LOG=quiet
export HABITAT_SIM_LOG=quiet

config="configs/experiments/il_objectnav.yaml"
DATA_PATH="data/datasets/objectnav/objectnav_hm3d_hd"
TENSORBOARD_DIR="tb/behavior/"
CHECKPOINT_DIR="data/il_ckpts"


echo "In ObjectNav IL DDP"
python -u -m torch.distributed.launch \
    --use_env \
    --nproc_per_node $NUM_GPUS \
    run.py \
    --exp-config $config \
    --run-type train \
    TENSORBOARD_DIR $TENSORBOARD_DIR \
    CHECKPOINT_FOLDER $CHECKPOINT_DIR \
    NUM_UPDATES 100000 \
    NUM_ENVIRONMENTS 30 \
    EVAL USE_CKPT_CONFIG False\
    RL.DDPPO.force_distributed True \
    TASK_CONFIG.DATASET.DATA_PATH "$DATA_PATH/{split}/{split}.json.gz" \
