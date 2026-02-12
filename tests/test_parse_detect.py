import pytest

def test_detect_parsing_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    import monitor_control.core.ddcutil as d
    from monitor_control.core.ddcutil import RunResult

    def fake_run(cmd: list[str], timeout_s: int = 5) -> RunResult:
        return RunResult(stdout="", stderr="", returncode=0)

    monkeypatch.setattr(d, "_run", fake_run)
    assert d.detect() == []