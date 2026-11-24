# Serving Guide

WeMM-Ecom uses standard upstream `Qwen3_5ForConditionalGeneration` (0.8B, 2B, 4B, 9B) and `Qwen3_5MoeForConditionalGeneration` (35B-A3B) architectures.

## Model Weights

| Model | Architecture | Weights |
| :--- | :--- | :--- |
| **WeMM-Ecom-35B-A3B** | MoE (3B active) | [🤗 **BF16**](https://huggingface.co/tencent/WeMM-Ecom-35B-A3B) &nbsp;·&nbsp; [🤗 **FP8**](https://huggingface.co/tencent/WeMM-Ecom-35B-A3B-FP8) &nbsp;·&nbsp; [🤗 **GPTQ**](https://huggingface.co/tencent/WeMM-Ecom-35B-A3B-GPTQ) &nbsp;·&nbsp; [🤗 **GGUF**](https://huggingface.co/tencent/WeMM-Ecom-35B-A3B-GGUF) |
| **WeMM-Ecom-9B** | Dense | [🤗 **BF16**](https://huggingface.co/tencent/WeMM-Ecom-9B) &nbsp;·&nbsp; [🤗 **FP8**](https://huggingface.co/tencent/WeMM-Ecom-9B-FP8) &nbsp;·&nbsp; [🤗 **GPTQ**](https://huggingface.co/tencent/WeMM-Ecom-9B-GPTQ) &nbsp;·&nbsp; [🤗 **GGUF**](https://huggingface.co/tencent/WeMM-Ecom-9B-GGUF) |
| **WeMM-Ecom-4B** | Dense | [🤗 **BF16**](https://huggingface.co/tencent/WeMM-Ecom-4B) &nbsp;·&nbsp; [🤗 **FP8**](https://huggingface.co/tencent/WeMM-Ecom-4B-FP8) &nbsp;·&nbsp; [🤗 **GPTQ**](https://huggingface.co/tencent/WeMM-Ecom-4B-GPTQ) &nbsp;·&nbsp; [🤗 **GGUF**](https://huggingface.co/tencent/WeMM-Ecom-4B-GGUF) |
| **WeMM-Ecom-2B** | Dense | [🤗 **BF16**](https://huggingface.co/tencent/WeMM-Ecom-2B) &nbsp;·&nbsp; [🤗 **FP8**](https://huggingface.co/tencent/WeMM-Ecom-2B-FP8) &nbsp;·&nbsp; [🤗 **GPTQ**](https://huggingface.co/tencent/WeMM-Ecom-2B-GPTQ) &nbsp;·&nbsp; [🤗 **GGUF**](https://huggingface.co/tencent/WeMM-Ecom-2B-GGUF) |
| **WeMM-Ecom-0.8B** | Dense | [🤗 **BF16**](https://huggingface.co/tencent/WeMM-Ecom-0.8B) &nbsp;·&nbsp; [🤗 **FP8**](https://huggingface.co/tencent/WeMM-Ecom-0.8B-FP8) &nbsp;·&nbsp; [🤗 **GPTQ**](https://huggingface.co/tencent/WeMM-Ecom-0.8B-GPTQ) &nbsp;·&nbsp; [🤗 **GGUF**](https://huggingface.co/tencent/WeMM-Ecom-0.8B-GGUF) |

## Checkpoint Formats

| Format | Details | Runtime |
| --- | --- | --- |
| BF16 | Unquantized bfloat16 safetensors | Transformers (`>=5.3.0`), vLLM (`>=0.18.0`), or SGLang (`>=0.5.9`) |
| FP8 Block128 | E4M3 128×128 block-scaled weights, dynamic activations; BF16 vision tower | vLLM (`>=0.18.0`) or SGLang on FP8-capable GPUs (SM89/SM90+) |
| GPTQ W4A16 | `compressed-tensors` 4-bit weights (group size 128); BF16 vision tower | vLLM (`>=0.18.0`) |
| GGUF Q4_K_M | `Q4_K_M` language model (`*.gguf`) + `mmproj-F16.gguf` | `llama.cpp` (`llama-server`, commit `e574a17`+) on CPU or CUDA |

## vLLM

### BF16 / FP8 / Dense GPTQ

```bash
vllm serve tencent/WeMM-Ecom-9B-FP8 \
  --served-model-name WeMM-Ecom \
  --reasoning-parser qwen3 \
  --host 0.0.0.0 \
  --port 8000 \
  --max-model-len 32768
```

Add `--tensor-parallel-size 2` (or larger) for multi-GPU serving.

### `WeMM-Ecom-35B-A3B-GPTQ`

Pass `--moe-backend marlin` for the MoE GPTQ checkpoint:

```bash
vllm serve tencent/WeMM-Ecom-35B-A3B-GPTQ \
  --served-model-name WeMM-Ecom \
  --reasoning-parser qwen3 \
  --moe-backend marlin \
  --host 0.0.0.0 \
  --port 8000 \
  --max-model-len 32768
```

Or use the wrapper script (automatically adds `--moe-backend marlin` for `35B-A3B-GPTQ`):

```bash
bash scripts/serve_vllm.sh tencent/WeMM-Ecom-35B-A3B-GPTQ 1 --max-model-len 32768
```

> **Troubleshooting:** If FP8 loading fails with `cuLibraryGetKernelCount` on older CUDA drivers, set `VLLM_USE_DEEP_GEMM=0`. If FlashInfer sampler JIT fails, set `VLLM_USE_FLASHINFER_SAMPLER=0`.

## SGLang

```bash
python -m sglang.launch_server \
  --model-path tencent/WeMM-Ecom-9B \
  --served-model-name WeMM-Ecom \
  --reasoning-parser qwen3 \
  --host 0.0.0.0 \
  --port 8000 \
  --context-length 32768
```

Wrapper script for multi-GPU serving:

```bash
bash scripts/serve_sglang.sh tencent/WeMM-Ecom-35B-A3B 2 --context-length 32768
```

## llama.cpp (GGUF)

Each `-GGUF` repository contains `WeMM-Ecom-<SIZE>-GGUF.gguf` and `mmproj-F16.gguf`. Build [llama.cpp](https://github.com/ggml-org/llama.cpp) (`-DGGML_CUDA=ON` for CUDA, or CPU-only) and launch `llama-server`:

```bash
hf download tencent/WeMM-Ecom-2B-GGUF --local-dir ./WeMM-Ecom-2B-GGUF

llama-server \
  -m ./WeMM-Ecom-2B-GGUF/WeMM-Ecom-2B-GGUF.gguf \
  --mmproj ./WeMM-Ecom-2B-GGUF/mmproj-F16.gguf \
  --alias WeMM-Ecom \
  --host 0.0.0.0 \
  --port 8000 \
  -ngl 999 \
  --ctx-size 16384 \
  --image-min-tokens 64 \
  --image-max-tokens 16384 \
  --reasoning off \
  --reasoning-format deepseek
```

- **Thinking mode in `llama.cpp`**: Recent `llama.cpp` builds default to `--reasoning auto` and inject `enable_thinking=true` whenever a template supports it (including `0.8B` and `2B`). Pass `--reasoning on` for Thinking mode or `--reasoning off` for Instruct mode at startup rather than relying on `--reasoning-budget 0`.
- `--image-min-tokens 64 --image-max-tokens 16384` matches the Hugging Face processor image token bounds (`shortest_edge=65536`, `longest_edge=16777216`).
- Use `-ngl 0` for CPU-only inference, or run `bash scripts/serve_llamacpp.sh ./WeMM-Ecom-2B-GGUF --reasoning off`.

## OpenAI API & Thinking Mode

For **vLLM** and **SGLang**, control Thinking mode per request with `chat_template_kwargs: {"enable_thinking": true}` (Thinking) or `{"enable_thinking": false}` (Instruct). Passing `enable_thinking` explicitly is recommended since template defaults differ by scale (`0.8B`/`2B` default to Instruct; `4B`/`9B`/`35B-A3B` default to Thinking). For **`llama-server`**, set `--reasoning on` or `--reasoning off` at server startup (recent `llama.cpp` builds ignore `enable_thinking` in `chat_template_kwargs`).

```bash
curl -sS http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "WeMM-Ecom",
    "messages": [
      {
        "role": "user",
        "content": [
          {"type": "image_url", "image_url": {"url": "https://example.com/product.jpg"}},
          {"type": "text", "text": "Extract the brand, packaging type, and net weight."}
        ]
      }
    ],
    "max_tokens": 8192,
    "temperature": 0.7,
    "top_p": 0.8,
    "presence_penalty": 1.5,
    "top_k": 20,
    "min_p": 0.0,
    "repetition_penalty": 1.0,
    "chat_template_kwargs": {"enable_thinking": false}
  }'
```

With `--reasoning-parser qwen3` (vLLM / SGLang) or `--reasoning-format deepseek` (`llama-server`), reasoning traces are returned in `choices[0].message.reasoning_content` and the final answer in `choices[0].message.content`.

## Recommended Sampling Parameters

| Mode | `enable_thinking` | Parameters |
| --- | --- | --- |
| Thinking | `True` | `temperature=1.0`, `top_p=0.95`, `top_k=20`, `min_p=0.0`, `presence_penalty=1.5`, `repetition_penalty=1.0` |
| Instruct | `False` | `temperature=0.7`, `top_p=0.8`, `top_k=20`, `min_p=0.0`, `presence_penalty=1.5`, `repetition_penalty=1.0` |

Use `max_tokens >= 8192` in Thinking mode.
