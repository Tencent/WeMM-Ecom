#!/usr/bin/env bash
set -euo pipefail

MODEL_PATH=${1:?Usage: serve_vllm.sh MODEL_PATH [TENSOR_PARALLEL_SIZE] [EXTRA_VLLM_ARGS...]}
TP_SIZE=${2:-1}
SHIFT_COUNT=$(( $# >= 2 ? 2 : 1 ))
shift "$SHIFT_COUNT"

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
SERVED_MODEL_NAME=${SERVED_MODEL_NAME:-WeMM-Ecom}

EXTRA_ARGS=()
if [[ "$MODEL_PATH" == *35B-A3B-GPTQ* ]] && [[ " $* " != *" --moe-backend "* ]]; then
  EXTRA_ARGS+=(--moe-backend marlin)
fi

exec vllm serve "$MODEL_PATH" \
  --served-model-name "$SERVED_MODEL_NAME" \
  --tensor-parallel-size "$TP_SIZE" \
  --reasoning-parser qwen3 \
  --host "$HOST" \
  --port "$PORT" \
  "${EXTRA_ARGS[@]}" \
  "$@"
