#!/bin/bash
# Get number of GPUs
if [ -z "$CUDA_VISIBLE_DEVICES" ]
then
    echo "CUDA_VISIBLE_DEVICES is not set"
else
    IFS=',' read -ra ADDR <<< "$CUDA_VISIBLE_DEVICES"
    num_gpus=${#ADDR[@]}
    echo "Number of GPUs: $num_gpus"
fi
# Get number of CPUs
num_cpus=$(nproc)

export GLOG_minloglevel=2
export MAGNUM_LOG=quiet
export HABITAT_SIM_LOG=quiet
export OMP_NUM_THREADS=$((num_cpus/num_gpus))

config="configs/experiments/il_objectnav.yaml"
DATA_PATH="data/datasets/objectnav/objectnav_hm3d/objectnav_hm3d_hd"
TENSORBOARD_DIR="tb/debug5"
CHECKPOINT_DIR="data/checkpoints/debug5"
INFLECTION_COEF=3.234951275740812


echo "In ObjectNav IL DDP"
torchrun --nproc_per_node $num_gpus run.py \
    --exp-config $config \
    --run-type train \
    TENSORBOARD_DIR $TENSORBOARD_DIR \
    CHECKPOINT_FOLDER $CHECKPOINT_DIR \
    NUM_UPDATES 3200000000 \
    NUM_ENVIRONMENTS 2 \
    IL.BehaviorCloning.num_mini_batch 2\
    EVAL.USE_CKPT_CONFIG False\
    RL.DDPPO.force_distributed True \
    TASK_CONFIG.DATASET.DATA_PATH "$DATA_PATH/{split}/{split}.json.gz" \
    TASK_CONFIG.TASK.INFLECTION_WEIGHT_SENSOR.INFLECTION_COEF $INFLECTION_COEF \
