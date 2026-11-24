#!/usr/bin/env bash
set -euo pipefail

MODEL_DIR=${1:?Usage: serve_llamacpp.sh GGUF_MODEL_DIR [EXTRA_LLAMA_SERVER_ARGS...]}
shift

LLAMA_SERVER=${LLAMA_SERVER:-llama-server}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
SERVED_MODEL_NAME=${SERVED_MODEL_NAME:-WeMM-Ecom}
NGL=${NGL:-999}
CTX_SIZE=${CTX_SIZE:-16384}
REASONING=${REASONING:-}

MMPROJ_PATH="$MODEL_DIR/mmproj-F16.gguf"
if [[ ! -f "$MMPROJ_PATH" ]]; then
  echo "Error: multimodal projector not found at $MMPROJ_PATH" >&2
  exit 1
fi

MODEL_GGUF=""
for candidate in "$MODEL_DIR"/*.gguf; do
  [[ -f "$candidate" ]] || continue
  [[ "$(basename "$candidate")" == mmproj* ]] && continue
  MODEL_GGUF="$candidate"
  break
done

if [[ -z "$MODEL_GGUF" ]]; then
  echo "Error: no language model .gguf file found in $MODEL_DIR" >&2
  exit 1
fi

EXTRA_ARGS=()
if [[ -n "$REASONING" ]] && [[ " $* " != *" --reasoning "* ]]; then
  EXTRA_ARGS+=(--reasoning "$REASONING")
fi

exec "$LLAMA_SERVER" \
  -m "$MODEL_GGUF" \
  --mmproj "$MMPROJ_PATH" \
  --alias "$SERVED_MODEL_NAME" \
  --host "$HOST" \
  --port "$PORT" \
  -ngl "$NGL" \
  --ctx-size "$CTX_SIZE" \
  --image-min-tokens 64 \
  --image-max-tokens 16384 \
  --reasoning-format deepseek \
  "${EXTRA_ARGS[@]}" \
  "$@"
