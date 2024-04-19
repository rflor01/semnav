#!/bin/sh
#$ -cwd
#$ -l node_f=20
#$ -j y
#$ -l h_rt=24:00:00
#$ -o slurm_logs/$JOB_NAME_$JOB_ID.out
#$ -N tsubame_cyclic_lr

# ******************* Setup dirs ***********************************
setup="full"
# Define paths
config="configs/experiments/off_objectnav.yaml"
DATA_PATH="data/datasets/objectnav/objectnav_hm3d_hd_${setup}"
TENSORBOARD_DIR="tb/${JOB_NAME}_${setup}"
CHECKPOINT_DIR="data/checkpoints/offnav/${JOB_NAME}_${setup}"

mkdir -p $TENSORBOARD_DIR
mkdir -p $CHECKPOINT_DIR
mkdir -p slurm_logs

export config
export DATA_PATH
export TENSORBOARD_DIR
export CHECKPOINT_DIR
export GLOG_minloglevel=2
export MAGNUM_LOG=quiet
export HABITAT_SIM_LOG=quiet
# ******************* Setup openmpi *******************************
module load openmpi/5.0.2-nvhpc
# Get number of GPUs
if [ -z "$NVIDIA_VISIBLE_DEVICES" ]
then
    echo "NVIDIA_VISIBLE_DEVICES is not set"
else
    IFS=',' read -ra ADDR <<< "$NVIDIA_VISIBLE_DEVICES"
    num_gpus=${#ADDR[@]}
fi
# Get number of CPUs
num_cpus=$(nproc)
export OMP_NUM_THREADS=$((num_cpus/num_gpus))
export NNODES=$NHOSTS
export NPERNODE=$num_gpus
export NP=$(($NPERNODE * $NNODES))
export MASTER_ADDR=`head -n 1 $SGE_JOB_SPOOL_DIR/pe_hostfile | cut -d " " -f 1`
export MASTER_PORT=$((10000+ ($JOB_ID % 50000)))
echo NNODES=$NNODES
echo NPERNODE=$NPERNODE
echo NP=$NP
echo MASTERADDR=$MASTER_ADDR
echo MASTERPORT=$MASTER_PORT
# ******************************************************************

echo "In ObjectNav OFFNAV"
mpirun -np $NP -npernode $NPERNODE \
  apptainer exec --nv \
    --bind /gs/fs/tga-aklab/data \
    --bind /gs/fs/tga-aklab/carlos/repositorios \
    --bind /gs/fs/tga-aklab/carlos/miniconda3 \
    apptainer/offnav.sif \
    bash scripts/train_multi_node.sh