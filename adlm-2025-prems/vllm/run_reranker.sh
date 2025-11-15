#!/bin/bash

export CUDA_VISIBLE_DEVICES=3
export CURL_CA_BUNDLE="" 

# https://github.com/vllm-project/vllm/pull/19260
uv run vllm serve --config qwen3_reranker.yaml \
    --hf_overrides '{"architectures": ["Qwen3ForSequenceClassification"],"classifier_from_token": ["no", "yes"],"is_original_qwen3_reranker": true}'