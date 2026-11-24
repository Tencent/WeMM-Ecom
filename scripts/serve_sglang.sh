#!/usr/bin/env bash
set -euo pipefail

MODEL_PATH=${1:?Usage: serve_sglang.sh MODEL_PATH [TENSOR_PARALLEL_SIZE] [EXTRA_SGLANG_ARGS...]}
TP_SIZE=${2:-1}
SHIFT_COUNT=$(( $# >= 2 ? 2 : 1 ))
shift "$SHIFT_COUNT"

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
SERVED_MODEL_NAME=${SERVED_MODEL_NAME:-WeMM-Ecom}

exec python -m sglang.launch_server \
  --model-path "$MODEL_PATH" \
  --served-model-name "$SERVED_MODEL_NAME" \
  --tp-size "$TP_SIZE" \
  --reasoning-parser qwen3 \
  --host "$HOST" \
  --port "$PORT" \
  "$@"
