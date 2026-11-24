#!/usr/bin/env python3
"""Query a WeMM-Ecom server (vLLM, SGLang, or llama.cpp) via the OpenAI-compatible API."""

import argparse
import base64
import mimetypes
import os

from openai import OpenAI

DEFAULT_PROMPT = "Please briefly describe this product."

SAMPLING = {
    "thinking": {"temperature": 1.0, "top_p": 0.95},
    "non_thinking": {"temperature": 0.7, "top_p": 0.8},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send a text or multimodal request to a WeMM-Ecom server."
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--model", default="WeMM-Ecom")
    parser.add_argument(
        "--image",
        action="append",
        default=[],
        help="Local image path or HTTP(S) URL (repeatable for multi-image inputs).",
    )
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument(
        "--no-thinking",
        action="store_true",
        help="Disable thinking mode and answer directly (Instruct mode).",
    )
    parser.add_argument("--max-tokens", type=int, default=8192)
    return parser.parse_args()


def to_image_url(path_or_url: str) -> str:
    if path_or_url.startswith(("http://", "https://", "data:")):
        return path_or_url
    mime = mimetypes.guess_type(path_or_url)[0] or "image/jpeg"
    with open(path_or_url, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{data}"


def build_content(image_paths: list[str], prompt: str) -> list[dict] | str:
    if not image_paths:
        return prompt
    content = [
        {"type": "image_url", "image_url": {"url": to_image_url(path)}}
        for path in image_paths
    ]
    content.append({"type": "text", "text": prompt})
    return content


def parse_message(message) -> tuple[str, str]:
    reasoning = getattr(message, "reasoning_content", None) or ""
    content = message.content or ""
    if not reasoning and "</think>" in content:
        reasoning, content = content.split("</think>", 1)
        reasoning = reasoning.replace("<think>", "")
    return reasoning.strip(), content.strip()


def main() -> None:
    args = parse_args()
    thinking = not args.no_thinking

    api_key = os.environ.get("OPENAI_API_KEY", "EMPTY")
    client = OpenAI(base_url=args.base_url, api_key=api_key)
    response = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "user", "content": build_content(args.image, args.prompt)}],
        max_tokens=args.max_tokens,
        presence_penalty=1.5,
        extra_body={
            "top_k": 20,
            "min_p": 0.0,
            "repetition_penalty": 1.0,
            "chat_template_kwargs": {"enable_thinking": thinking},
        },
        **SAMPLING["thinking" if thinking else "non_thinking"],
    )

    reasoning, answer = parse_message(response.choices[0].message)
    if reasoning:
        print("[reasoning]")
        print(reasoning)
        print()
    print("[answer]")
    print(answer)


if __name__ == "__main__":
    main()
