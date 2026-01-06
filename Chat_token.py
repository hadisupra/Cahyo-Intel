import os
from typing import Dict

try:
    import tiktoken
except Exception:
    tiktoken = None

DEFAULT_USD_TO_IDR = float(os.getenv("USD_TO_IDR", "16000"))
INPUT_PRICE_PER_1K_USD = float(os.getenv("INPUT_PRICE_PER_1K_USD", "0.0005"))
OUTPUT_PRICE_PER_1K_USD = float(os.getenv("OUTPUT_PRICE_PER_1K_USD", "0.0015"))


def _count_tokens(text: str, model_hint: str = "gpt-4o-mini") -> int:
    if not text:
        return 0
    if tiktoken is None:
        # Fallback: rough estimate ~4 chars per token
        return max(1, len(text) // 4)
    try:
        enc = tiktoken.encoding_for_model(model_hint)
    except Exception:
        # Default encoding compatible with most GPT-3.5/4 models
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def run_chat_token(prompt: str, model: str = None) -> Dict[str, float]:
    """
    Lightweight token and cost estimator used by the Streamlit UI.
    - Counts input tokens using tiktoken (or a simple heuristic if unavailable).
    - Output tokens and latency are placeholders (the UI can still display them).
    - Cost computed from env pricing if provided; otherwise returns 0.

    Environment variables (optional):
    - INPUT_PRICE_PER_1K_USD: cost per 1K input tokens in USD
    - OUTPUT_PRICE_PER_1K_USD: cost per 1K output tokens in USD
    - USD_TO_IDR: conversion rate
    - LLM_MODEL: model hint for tokenization
    """
    model_hint = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
    input_tokens = _count_tokens(prompt or "", model_hint)

    # No actual generation happens here, so set output tokens to 0
    output_tokens = 0

    # Compute cost if pricing is provided; otherwise 0
    input_cost_usd = (input_tokens / 1000.0) * INPUT_PRICE_PER_1K_USD
    output_cost_usd = (output_tokens / 1000.0) * OUTPUT_PRICE_PER_1K_USD
    total_cost_idr = (input_cost_usd + output_cost_usd) * DEFAULT_USD_TO_IDR

    # Latency placeholder (actual latency comes from API roundtrip)
    latency_seconds = 0.0

    return {
        "input_tokens": int(input_tokens),
        "output_tokens": int(output_tokens),
        "cost_idr": round(total_cost_idr, 2),
        "latency": round(latency_seconds, 2),
    }
