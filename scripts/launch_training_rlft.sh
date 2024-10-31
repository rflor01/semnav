#!/bin/bash
# Get number of GPUs
if [ -z "$NVIDIA_VISIBLE_DEVICES" ]
then
    echo "NVIDIA_VISIBLE_DEVICES is not set"
else
    IFS=',' read -ra ADDR <<< "$NVIDIA_VISIBLE_DEVICES"
    num_gpus=${#ADDR[@]}
    echo "Number of GPUs: $num_gpus"
fi
# Get number of CPUs
num_cpus=$(nproc)

export GLOG_minloglevel=2
export MAGNUM_LOG=quiet
export HABITAT_SIM_LOG=quiet
export OMP_NUM_THREADS=$((num_cpus/num_gpus))

config="configs/experiments/rl_ft_objectnav.yaml"
DATA_PATH="data/datasets/objectnav/objectnav_hm3d/objectnav_hm3d_v1"
TENSORBOARD_DIR="tb/RLFT_Working_collectenvironmentresultcorrect"
CHECKPOINT_DIR="data/checkpoints/RLFT_Working_collectenvironmentresultcorrect"
PRETRAINED_WEIGHTS="data/checkpoints/semantic_rgb_lrcycliccor0.00001dgx_PRETRAINEDencoder40categories2_correctedconstant/ckpt.13.pth"
INFLECTION_COEF=3.234951275740812

echo "In ObjectNav IL DDP"
torchrun --nproc_per_node $num_gpus \
    --max-restarts 3\
    run.py \
    --exp-config $config \
    --run-type train \
    TENSORBOARD_DIR $TENSORBOARD_DIR \
    CHECKPOINT_FOLDER $CHECKPOINT_DIR \
    NUM_UPDATES 3200000000 \
    NUM_ENVIRONMENTS 16 \
    RL.DDPPO.force_distributed True \
    RL.DDPPO.pretrained_weights $PRETRAINED_WEIGHTS \
    TASK_CONFIG.DATASET.DATA_PATH "$DATA_PATH/{split}/{split}.json.gz" \
    TASK_CONFIG.TASK.INFLECTION_WEIGHT_SENSOR.INFLECTION_COEF $INFLECTION_COEF \
