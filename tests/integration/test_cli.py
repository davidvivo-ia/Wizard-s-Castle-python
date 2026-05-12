"""Tests de la CLI con Typer."""

from __future__ import annotations

from typer.testing import CliRunner

from wizards_castle.presentation.cli import app

runner = CliRunner()


def test_demo_command_runs() -> None:
    result = runner.invoke(app, ["demo", "--seed", "42", "--quiet"])
    assert result.exit_code == 0
    assert "Demo" in result.stdout


def test_analyze_command() -> None:
    result = runner.invoke(app, ["analyze", "--seed", "42"])
    assert result.exit_code == 0
    assert "seed=42" in result.stdout
    assert "Entrada" in result.stdout


def test_demo_classic_mode() -> None:
    result = runner.invoke(app, ["demo", "--seed", "1", "--classic", "--quiet"])
    assert result.exit_code == 0
    assert "classic" in result.stdout
