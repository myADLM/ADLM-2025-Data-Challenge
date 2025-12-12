#!/bin/bash

export CUDA_VISIBLE_DEVICES=0,1,2,3
export CURL_CA_BUNDLE="" 
export VLLM_USE_FLASHINFER_MOE_FP16=1 

uv run vllm serve --config qwen3_vision.yaml