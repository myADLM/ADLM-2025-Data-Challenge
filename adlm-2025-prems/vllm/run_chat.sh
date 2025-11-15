#!/bin/bash

export CUDA_VISIBLE_DEVICES=0
export CURL_CA_BUNDLE="" 
export VLLM_USE_FLASHINFER_MXFP4_MOE=1 

uv run vllm serve --config gpt_oss_20b.yaml