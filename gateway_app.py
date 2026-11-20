"""AI-Native Teams — gateway + routing skeleton for Week 10.

Two LLM tasks of different difficulty, both routed through ONE gateway function so you
can swap/route models in one place. Fill in the routing TODOs.

Uses LiteLLM (https://docs.litellm.ai) as an OpenAI-compatible gateway across providers.
You may point EASY_MODEL at a local Ollama model and HARD_MODEL at a hosted one.

Setup:
    pip install -r requirements.txt
    export OPENAI_API_KEY=...        # or whatever your chosen providers need
Run:
    python gateway_app.py
"""
import os
import time

import litellm

EASY_MODEL = os.getenv("EASY_MODEL", "ollama/llama3.2:3b")
HARD_MODEL = os.getenv("HARD_MODEL", "ollama/llama3.1:8b")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", HARD_MODEL)
MODEL_TIMEOUT_SECONDS = int(os.getenv("MODEL_TIMEOUT_SECONDS", "60"))


def call_model(model: str, prompt: str, used_fallback: bool = False) -> str:
    """Single choke point for all model calls — route, log, and fall back here."""
    try:
        resp = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            timeout=MODEL_TIMEOUT_SECONDS,
        )
        return resp["choices"][0]["message"]["content"].strip()
    except Exception as exc:  # noqa: BLE001
        if used_fallback or model == FALLBACK_MODEL:
            raise RuntimeError(f"Model call failed for {model}") from exc
        print(f"[{model}] failed, trying fallback {FALLBACK_MODEL}")
        return call_model(FALLBACK_MODEL, prompt, used_fallback=True)


def route(task: str, prompt: str) -> str:
    """Route each task to the model chosen for its difficulty."""
    if task == "easy":
        model = EASY_MODEL
    elif task == "hard":
        model = HARD_MODEL
    else:
        raise ValueError(f"Unknown task type {task}")
    started = time.time()
    out = call_model(model, prompt)
    print(f"[{task}] model={model} latency={time.time() - started:.2f}s")
    return out


# --- The two tasks -----------------------------------------------------------------
def classify_sentiment(review: str) -> str:  # EASY
    return route("easy", f"Reply with one word (positive/negative/neutral): {review}")


def explain_bug(code: str) -> str:  # HARD
    return route("hard", f"Explain the bug in this code and suggest a fix:\n{code}")


if __name__ == "__main__":
    print(classify_sentiment("This product totally changed my morning routine!"))
    print(explain_bug("def avg(xs): return sum(xs) / len(xs)  # crashes on []"))
