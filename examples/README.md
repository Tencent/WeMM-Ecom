# Examples

## Transformers

```bash
python examples/transformers_inference.py \
  --model tencent/WeMM-Ecom-2B \
  --image assets/examples/product_0.jpg \
  --image assets/examples/product_1.jpg \
  --prompt "Describe this product, including its packaging, quantity, and visual style."
```

Pass `--no-thinking` for Instruct mode.

## OpenAI-Compatible API (vLLM / SGLang / llama.cpp)

Start a server on port `8000` (see [docs/serving.md](../docs/serving.md)), then run:

```bash
# Multi-image (Thinking mode)
python examples/openai_client.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model WeMM-Ecom \
  --image assets/examples/product_0.jpg \
  --image assets/examples/product_1.jpg \
  --prompt "Compare the two product views and summarize the key selling points."

# Multi-image (Instruct mode)
python examples/openai_client.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model WeMM-Ecom \
  --no-thinking \
  --image assets/examples/product_0.jpg \
  --image assets/examples/product_1.jpg \
  --prompt "Extract the product category, item count, and packaging material."

# Text-only
python examples/openai_client.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model WeMM-Ecom \
  --no-thinking \
  --prompt "Do 'Loose-Leaf Green Tea 0.1 kg tin' and 'Loose-Leaf Green Tea 100 g tin (single pack)' refer to the same SKU?"
```
