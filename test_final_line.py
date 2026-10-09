import gzip
import itertools

import pytest

from jaraco.stream.gzip import lines_from_stream, load_streams


@pytest.mark.parametrize(
    ('chunks', 'expected'),
    [
        ([b'first\nlast'], ['first', 'last']),
        ([b'first\nla', b'st'], ['first', 'last']),
        ([b'Ol\xc3', b'\xa9'], ['Olé']),
        ([b'last\r'], ['last\r']),
        ([b'first\n'], ['first']),
        ([], []),
    ],
)
def test_final_line(chunks, expected):
    assert list(lines_from_stream(chunks)) == expected


def test_gzip_payload_without_final_newline():
    payload = gzip.compress(b'first\nlast')
    streams = load_streams([payload[:10], payload[10:]])
    lines = itertools.chain.from_iterable(map(lines_from_stream, streams))
    assert list(lines) == ['first', 'last']


def test_final_line_retains_strict_decoding():
    with pytest.raises(UnicodeDecodeError):
        list(lines_from_stream([b'\xff']))
