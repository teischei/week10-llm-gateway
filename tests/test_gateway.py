import unittest
from unittest.mock import patch

import gateway_app


class GatewayTests(unittest.TestCase):
    def test_easy_task_uses_easy_model(self):
        with patch("gateway_app.call_model", return_value="positive") as call_model:
            gateway_app.route("easy", "great product")

        call_model.assert_called_once_with(gateway_app.EASY_MODEL, "great product")

    def test_hard_task_uses_hard_model(self):
        with patch("gateway_app.call_model", return_value="use an empty check") as call_model:
            gateway_app.route("hard", "def avg(xs): return sum(xs) / len(xs)")

        call_model.assert_called_once_with(
            gateway_app.HARD_MODEL,
            "def avg(xs): return sum(xs) / len(xs)",
        )

    def test_failed_primary_uses_fallback_once(self):
        calls = []

        def completion(**kwargs):
            calls.append(kwargs["model"])
            if kwargs["model"] == "test/primary":
                raise TimeoutError("timed out")
            return {"choices": [{"message": {"content": "fallback answer"}}]}

        with patch("gateway_app.litellm.completion", side_effect=completion), patch.object(
            gateway_app, "FALLBACK_MODEL", "test/fallback"
        ):
            result = gateway_app.call_model("test/primary", "hello")

        self.assertEqual(result, "fallback answer")
        self.assertEqual(calls, ["test/primary", "test/fallback"])

    def test_failed_fallback_does_not_loop(self):
        with patch("gateway_app.litellm.completion", side_effect=TimeoutError("timed out")), patch.object(
            gateway_app, "FALLBACK_MODEL", "test/fallback"
        ):
            with self.assertRaises(RuntimeError):
                gateway_app.call_model("test/fallback", "hello")


if __name__ == "__main__":
    unittest.main()
