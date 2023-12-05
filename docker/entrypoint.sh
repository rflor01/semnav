#!/bin/bash

. activate habitat
cd ~/code/ && pip install -e .
bash scripts/launch_training_eval.sh