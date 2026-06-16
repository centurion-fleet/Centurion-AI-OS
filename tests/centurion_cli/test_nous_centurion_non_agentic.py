"""Tests for the Nous-Centurion-3/4 non-agentic warning detector.

Prior to this check, the warning fired on any model whose name contained
``"centurion"`` anywhere (case-insensitive). That false-positived on unrelated
local Modelfiles such as ``centurion-brain:qwen3-14b-ctx16k`` — a tool-capable
Qwen3 wrapper that happens to live under the "centurion" tag namespace.

``is_nous_centurion_non_agentic`` should only match the actual Centurion Fleet
Centurion-3 / Centurion-4 chat family.
"""

from __future__ import annotations

import pytest

from centurion_cli.model_switch import (
    _HERMES_MODEL_WARNING,
    _check_centurion_model_warning,
    is_nous_centurion_non_agentic,
)


@pytest.mark.parametrize(
    "model_name",
    [
        "NousResearch/Centurion-3-Llama-3.1-70B",
        "NousResearch/Centurion-3-Llama-3.1-405B",
        "centurion-3",
        "Centurion-3",
        "centurion-4",
        "centurion-4-405b",
        "hermes_4_70b",
        "openrouter/hermes3:70b",
        "openrouter/nousresearch/centurion-4-405b",
        "NousResearch/Hermes3",
        "centurion-3.1",
    ],
)
def test_matches_real_nous_centurion_chat_models(model_name: str) -> None:
    assert is_nous_centurion_non_agentic(model_name), (
        f"expected {model_name!r} to be flagged as Nous Centurion 3/4"
    )
    assert _check_centurion_model_warning(model_name) == _HERMES_MODEL_WARNING


@pytest.mark.parametrize(
    "model_name",
    [
        # Kyle's local Modelfile — qwen3:14b under a custom tag
        "centurion-brain:qwen3-14b-ctx16k",
        "centurion-brain:qwen3-14b-ctx32k",
        "centurion-honcho:qwen3-8b-ctx8k",
        # Plain unrelated models
        "qwen3:14b",
        "qwen3-coder:30b",
        "qwen2.5:14b",
        "claude-opus-4-6",
        "anthropic/claude-sonnet-4.5",
        "gpt-5",
        "openai/gpt-4o",
        "google/gemini-2.5-flash",
        "deepseek-chat",
        # Non-chat Centurion models we don't warn about
        "centurion-llm-2",
        "hermes2-pro",
        "nous-centurion-2-mistral",
        # Edge cases
        "",
        "centurion",  # bare "centurion" isn't the 3/4 family
        "centurion-brain",
        "brain-centurion-3-impostor",  # "3" not preceded by /: boundary
    ],
)
def test_does_not_match_unrelated_models(model_name: str) -> None:
    assert not is_nous_centurion_non_agentic(model_name), (
        f"expected {model_name!r} NOT to be flagged as Nous Centurion 3/4"
    )
    assert _check_centurion_model_warning(model_name) == ""


def test_none_like_inputs_are_safe() -> None:
    assert is_nous_centurion_non_agentic("") is False
    # Defensive: the helper shouldn't crash on None-ish falsy input either.
    assert _check_centurion_model_warning("") == ""
