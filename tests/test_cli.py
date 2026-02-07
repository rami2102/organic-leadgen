# tests/test_cli.py
from click.testing import CliRunner
from leadgen.cli import main


def test_status_command():
    runner = CliRunner()
    result = runner.invoke(main, ["status"])
    assert result.exit_code == 0
    assert "Leadgen system: OK" in result.output
