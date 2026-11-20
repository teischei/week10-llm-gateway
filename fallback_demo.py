"""Show that a failed primary model call uses the configured fallback once."""
from pathlib import Path

import gateway_app


def main() -> None:
    result = gateway_app.call_model(
        "ollama/model-that-does-not-exist",
        "Reply with one word that describes the color of the sky.",
    )
    message = (
        "Primary model ollama/model-that-does-not-exist failed. "
        f"Fallback model {gateway_app.FALLBACK_MODEL} responded {result}\n"
    )
    Path("results").mkdir(exist_ok=True)
    Path("results/fallback_demo.txt").write_text(message)
    print(message, end="")


if __name__ == "__main__":
    main()
