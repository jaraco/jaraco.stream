import io
import sys

from jaraco.stream import Tee


class RecordingStream(io.StringIO):
    def __init__(self):
        super().__init__()
        self.flush_count = 0

    def flush(self):
        self.flush_count += 1
        super().flush()


class ManagedTee(Tee):
    # Restore stdout explicitly, independently of garbage collection timing.
    def __del__(self):
        pass


def test_print_flush_reaches_both_outputs(tmp_path, monkeypatch):
    stdout = RecordingStream()
    monkeypatch.setattr(sys, 'stdout', stdout)
    target = tmp_path / 'output.txt'
    tee = ManagedTee(target, 'w')
    try:
        print('buffered message', flush=True)
        assert stdout.getvalue() == 'buffered message\n'
        assert stdout.flush_count == 1
        assert target.read_text(encoding='utf-8') == 'buffered message\n'
    finally:
        sys.stdout = stdout
        tee.file.close()
