# Routing policy

## Rules

- Send sentiment classification to `ollama/llama3.2:3b`.
- Send bug explanations to `ollama/llama3.1:8b`.
- If either primary model fails or times out, call `ollama/llama3.2:1b` once and then return an error if that fallback fails.

## Evidence

The easy route completed 10 requests with 9 expected sentiment labels. The hard route completed 10 bug explanations using the stronger 8B model. The detailed records are in `measurements.json` and the route averages are in `summary.md`.

## Cost decision

The actual provider cost for this local Ollama setup is $0 for both routes. A 20-request workload costs $0 with the routed policy and also costs $0 when always using the strong local model, so the projected dollar savings in this setup are $0. The practical savings are avoiding the stronger model for the 10 easy requests and keeping the fast route available for simple work. If this service later uses paid models, the same policy should be measured again with the provider prices before using a dollar estimate.
