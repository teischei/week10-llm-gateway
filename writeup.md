# Week 10 writeup

## Routing and fallback configuration

I used LiteLLM as the single gateway in `gateway_app.py`. The easy sentiment task goes to `ollama/llama3.2:3b`, while the harder bug explanation task goes to `ollama/llama3.1:8b`. When either primary call fails or times out, `call_model` tries `ollama/llama3.2:1b` once. The retry flag stops the fallback from looping if the fallback model also fails. All model names and timeout settings can be changed with environment variables, and `.env` is ignored by Git so a future hosted provider key would not be committed.

## Results from 20 routed requests

| Route | Model | Runs | Average latency seconds | Median latency seconds | Cost per request |
| --- | --- | --- | --- | --- | --- |
| Easy | `ollama/llama3.2:3b` | 10 | 0.433 | 0.141 | $0.000000 |
| Hard | `ollama/llama3.1:8b` | 10 | 21.515 | 20.955 | $0.000000 |

I ran 10 sentiment inputs and 10 bug explanation inputs through the routing policy. The easy route matched the expected label on 9 of the 10 inputs. I checked the harder responses and confirmed that they identified the main issue and suggested a fix. The individual measurements are saved in `results/measurements.json`, and `results/fallback_demo.txt` records a real missing-model failure that used the fallback model.

## Recommended policy and savings

I would keep the 3B model for short sentiment classification and reserve the 8B model for bug explanations. The smaller model was much faster for the easy task, while the stronger model gave detailed bug explanations. Both models run locally, so the actual provider cost for all 20 requests was $0. Always using the strong local model would also cost $0, so the projected dollar savings in this local setup are $0, but routing avoids using the larger model for the 10 easy requests and keeps it free for harder work. If I move to paid models, I would measure the same routes with the provider prices before claiming a dollar amount saved.

## What I learned

Treating model calls as infrastructure made the routing rule and fallback behavior easier to see as part of the application instead of separate prompt code. The local measurements showed that a smaller model can return a simple answer much faster, while bug explanations justify sending harder work to the stronger model. A gateway also makes provider changes safer because the rest of the app uses one call location. For an AI native team, I would keep the routing data and fallback events visible so the team can adjust the policy when quality, latency, or cost changes.
