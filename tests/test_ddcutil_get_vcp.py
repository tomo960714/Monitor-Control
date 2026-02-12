import pytest

from monitor_control.core import ddcutil
from monitor_control.core.ddcutil import DDCParseError, RunResult
from monitor_control.core.models import VCPValue

def test_get_vcp_numeric_parses_current_and_max_values(
    monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_run(cmd: list[str], timeout_s: int = 5) -> RunResult:
        return RunResult(
            stdout="VCP code 0x10 (Brightness): current value = 50, max value = 100",
            stderr="",
            returncode=0,
        )
    
    monkeypatch.setattr(ddcutil, "_run", fake_run)
    v = ddcutil.get_vcp("10",display=1)

    assert v==VCPValue(code="10", current=50, maximum=100)

def test_get_vcp_status_sl_hex_parses_current(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(cmd: list[str], timeout_s: int = 5) -> RunResult:
        return RunResult(
            stdout="VCP code 0xd6 (Power mode): DPM: On,  DPMS: Off (sl=0x01)\n",
            stderr="",
            returncode=0,
        )

    monkeypatch.setattr(ddcutil, "_run", fake_run)
    v = ddcutil.get_vcp("D6", display=1)

    assert v.code == "D6"
    assert v.current == 1
    assert v.maximum == 0

def test_get_vcp_raises_when_unparseable(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(cmd: list[str], timeout_s: int = 5) -> RunResult:
        return RunResult(stdout="some weird output\n", stderr="", returncode=0)

    monkeypatch.setattr(ddcutil, "_run", fake_run)

    with pytest.raises(DDCParseError):
        ddcutil.get_vcp("D6", display=1)