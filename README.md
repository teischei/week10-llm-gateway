# Starter — LLM Gateway & Routing

A skeleton with two LLM tasks (easy: sentiment, hard: bug-explanation) routed through one
`call_model` choke point via **LiteLLM**. You fill in the routing and fallback.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.2:3b
ollama pull llama3.1:8b
python gateway_app.py
```

This version uses local Ollama models, so no API key is required and the model cost is $0.
The `.env` file is ignored by Git if you later choose to use a hosted provider.

## Routing configuration

- `EASY_MODEL` defaults to `ollama/llama3.2:3b` for sentiment classification.
- `HARD_MODEL` defaults to `ollama/llama3.1:8b` for bug explanations.
- `FALLBACK_MODEL` defaults to the hard model when the primary request fails or times out.
- `MODEL_TIMEOUT_SECONDS` defaults to 60.

You can override any model without editing the source.

```bash
export EASY_MODEL=ollama/llama3.2:3b
export HARD_MODEL=ollama/llama3.1:8b
export FALLBACK_MODEL=ollama/llama3.1:8b
```

## Measurement

Run the 20 local requests and save their latency and cost results.

```bash
.venv/bin/python benchmark.py
```

The script writes one record for each request to `results/measurements.json` and a table to `results/summary.md`. Both routes use local Ollama models, so their actual provider cost is $0.

If the hard route takes longer than your terminal command window, run one saved request at a time.

```bash
.venv/bin/python benchmark.py --task hard --index 0
```

## Fallback check

Run this command to demonstrate a missing primary model falling back to the configured model.

```bash
.venv/bin/python fallback_demo.py
```

## Your job (in `gateway_app.py`)
- `route()` — send the easy task to `EASY_MODEL`, the hard task to `HARD_MODEL`.
- `call_model()` — fall back to `FALLBACK_MODEL` on error/timeout (guard against loops).
- Measure latency + cost across 10 inputs per task and recommend a routing policy.

## Files
- `gateway_app.py` — the skeleton (two tasks + routing TODOs)
- `tests/test_gateway.py` — routing and fallback unit tests
