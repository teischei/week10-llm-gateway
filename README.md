# LLM Gateway and Routing

This project routes easy sentiment tasks and harder bug explanation tasks through one LiteLLM gateway function.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.2:3b
ollama pull llama3.1:8b
ollama pull llama3.2:1b
python gateway_app.py
```

This version uses local Ollama models, so no API key is required and the model cost is $0.
The `.env` file is ignored by Git if you later choose to use a hosted provider.

## Routing configuration

- `EASY_MODEL` defaults to `ollama/llama3.2:3b` for sentiment classification.
- `HARD_MODEL` defaults to `ollama/llama3.1:8b` for bug explanations.
- `FALLBACK_MODEL` defaults to `ollama/llama3.2:1b` when a primary request fails or times out.
- `MODEL_TIMEOUT_SECONDS` defaults to 60.

You can override any model without editing the source.

```bash
export EASY_MODEL=ollama/llama3.2:3b
export HARD_MODEL=ollama/llama3.1:8b
export FALLBACK_MODEL=ollama/llama3.2:1b
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

## Tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```

## Files
- `gateway_app.py` contains the routing and guarded fallback logic
- `benchmark.py` records the 20 local measurements
- `fallback_demo.py` records a live fallback result
- `results/` stores the measured data and routing policy
- `tests/test_gateway.py` tests routing and fallback behavior
