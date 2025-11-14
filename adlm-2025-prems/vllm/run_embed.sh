#!/bin/bash

export CUDA_VISIBLE_DEVICES=0
export CURL_CA_BUNDLE="" 

uv run vllm serve --config qwen3_embedding.yaml