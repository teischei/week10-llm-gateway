"""Run ten real requests through each Week 10 route and save the measurements."""
import argparse
import json
import statistics
import time
from pathlib import Path

import gateway_app

EASY_INPUTS = [
    ("This product totally changed my morning routine.", "positive"),
    ("Broke after two days and was a waste of money.", "negative"),
    ("It arrived on Tuesday in a brown box.", "neutral"),
    ("I love it and would buy it again.", "positive"),
    ("The app crashes and customer service was terrible.", "negative"),
    ("The manual is available in six languages.", "neutral"),
    ("Best purchase I made this year.", "positive"),
    ("It feels cheap and I regret buying it.", "negative"),
    ("It does what it says without anything extra.", "neutral"),
    ("The quality is fantastic and shipping was fast.", "positive"),
]

HARD_INPUTS = [
    "def avg(xs): return sum(xs) / len(xs)",
    "def add(item, items=[]):\n    items.append(item)\n    return items",
    "for i in range(1, len(xs)):\n    print(xs[i])",
    "if name is 'admin':\n    grant()",
    "for value in values:\n    if value < 0:\n        values.remove(value)",
    "fns = [lambda: i for i in range(3)]\nprint([fn() for fn in fns])",
    "print(0.1 + 0.2 == 0.3)",
    "async def load():\n    data = fetch()\n    return data['id']",
    "def total(prices):\n    sum = 0\n    for price in prices:\n        sum += price\n    return sum(prices)",
    "def last(values): return values[len(values)]",
]


def run_easy(index: int, review: str, expected: str) -> dict:
    started = time.perf_counter()
    output = gateway_app.classify_sentiment(review)
    latency = time.perf_counter() - started
    return {
        "task": "easy",
        "index": index,
        "model": gateway_app.EASY_MODEL,
        "input": review,
        "expected": expected,
        "output": output,
        "correct": expected in output.lower(),
        "latency_seconds": round(latency, 3),
        "cost_usd": 0.0,
    }


def run_hard(index: int, code: str) -> dict:
    started = time.perf_counter()
    output = gateway_app.explain_bug(code)
    latency = time.perf_counter() - started
    return {
        "task": "hard",
        "index": index,
        "model": gateway_app.HARD_MODEL,
        "input": code,
        "output": output,
        "latency_seconds": round(latency, 3),
        "cost_usd": 0.0,
    }


def summary(rows: list[dict]) -> str:
    lines = [
        "# Measurement summary",
        "",
        "| route | model | runs | average latency seconds | median latency seconds | cost per request |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for task in ("easy", "hard"):
        group = [row for row in rows if row["task"] == task]
        if not group:
            continue
        latencies = [row["latency_seconds"] for row in group]
        lines.append(
            "| "
            f"{task} | `{group[0]['model']}` | {len(group)} | "
            f"{statistics.mean(latencies):.3f} | {statistics.median(latencies):.3f} | $0.000000 |"
        )
    easy = [row for row in rows if row["task"] == "easy"]
    lines.append("")
    if easy:
        lines.append(f"Easy route accuracy was {sum(row['correct'] for row in easy)}/{len(easy)} based on the expected label.")
    lines.append("Cost is $0 because both models ran locally through Ollama.")
    return "\n".join(lines) + "\n"


def load_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = json.loads(path.read_text())
    indexes = {"easy": 0, "hard": 0}
    for row in rows:
        if "index" not in row:
            row["index"] = indexes[row["task"]]
        indexes[row["task"]] = max(indexes[row["task"]], row["index"] + 1)
    return rows


def add_row(rows: list[dict], row: dict) -> list[dict]:
    rows = [old for old in rows if not (old["task"] == row["task"] and old["index"] == row["index"])]
    rows.append(row)
    return sorted(rows, key=lambda item: (item["task"], item["index"]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=("easy", "hard"))
    parser.add_argument("--index", type=int)
    parser.add_argument("--summarize", action="store_true")
    args = parser.parse_args()
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    measurements_path = results_dir / "measurements.json"
    rows = load_rows(measurements_path)

    if args.summarize:
        pass
    elif args.task is not None:
        if args.index is None or not 0 <= args.index < 10:
            parser.error("--task needs --index from 0 through 9")
        if args.task == "easy":
            review, expected = EASY_INPUTS[args.index]
            rows = add_row(rows, run_easy(args.index, review, expected))
        else:
            rows = add_row(rows, run_hard(args.index, HARD_INPUTS[args.index]))
    else:
        rows = [run_easy(index, review, expected) for index, (review, expected) in enumerate(EASY_INPUTS)]
        rows.extend(run_hard(index, code) for index, code in enumerate(HARD_INPUTS))

    measurements_path.write_text(json.dumps(rows, indent=2) + "\n")
    (results_dir / "summary.md").write_text(summary(rows))
    print(summary(rows))


if __name__ == "__main__":
    main()
