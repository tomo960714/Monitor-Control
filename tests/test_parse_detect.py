from monitor_control.core.ddcutil import detect

def test_detect_parsing_empty(monkeypatch):
    import monitor_control.core.ddcutil as d

    class R:
        stdout =""
        stderr = ""
        returncode = 0

    monkeypatch.setattr(d, "_run", lambda *args, **kwargs: R())
    assert d.detect() == []