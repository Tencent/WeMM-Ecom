#!/usr/bin/env python3
"""Minimal WeMM-Ecom inference with Hugging Face Transformers."""

import argparse

import torch
from transformers import AutoModelForImageTextToText, AutoProcessor

DEFAULT_MODEL = "tencent/WeMM-Ecom-2B"
DEFAULT_PROMPT = "Please briefly describe this product."

SAMPLING = {
    "thinking": {"temperature": 1.0, "top_p": 0.95, "top_k": 20},
    "non_thinking": {"temperature": 0.7, "top_p": 0.8, "top_k": 20},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run multimodal generation with WeMM-Ecom in Transformers."
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Hugging Face model ID or local BF16 checkpoint directory.",
    )
    parser.add_argument(
        "--revision",
        default="main",
        help="Model and processor Hub revision.",
    )
    parser.add_argument(
        "--image",
        action="append",
        default=[],
        help="Local image path or URL (repeatable for multi-image inputs).",
    )
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument(
        "--no-thinking",
        action="store_true",
        help="Disable thinking mode and answer directly (Instruct mode).",
    )
    parser.add_argument("--max-new-tokens", type=int, default=8192)
    return parser.parse_args()


def build_messages(image_paths: list[str], prompt: str) -> list[dict]:
    content = [{"type": "image", "image": path} for path in image_paths]
    content.append({"type": "text", "text": prompt})
    return [{"role": "user", "content": content}]


def split_thinking(text: str) -> tuple[str, str]:
    if "</think>" not in text:
        return "", text.strip()
    reasoning, answer = text.split("</think>", 1)
    return reasoning.replace("<think>", "").strip(), answer.strip()


def main() -> None:
    args = parse_args()
    thinking = not args.no_thinking

    processor = AutoProcessor.from_pretrained(args.model, revision=args.revision)
    model = AutoModelForImageTextToText.from_pretrained(
        args.model,
        revision=args.revision,
        dtype=torch.bfloat16,
        device_map="auto",
    )
    model.eval()

    inputs = processor.apply_chat_template(
        build_messages(args.image, args.prompt),
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt",
        enable_thinking=thinking,
    ).to(model.device)

    with torch.inference_mode():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=True,
            repetition_penalty=1.0,
            **SAMPLING["thinking" if thinking else "non_thinking"],
        )

    generated = output_ids[0, inputs["input_ids"].shape[1]:]
    text = processor.decode(generated, skip_special_tokens=True)
    reasoning, answer = split_thinking(text)

    if reasoning:
        print("[reasoning]")
        print(reasoning)
        print()
    print("[answer]")
    print(answer)


if __name__ == "__main__":
    main()
