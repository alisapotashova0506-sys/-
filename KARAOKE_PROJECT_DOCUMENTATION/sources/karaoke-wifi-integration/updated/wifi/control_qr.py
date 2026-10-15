"""Generate the current home-network control QR locally, without image packages."""
import ipaddress
import struct
import threading
import zlib

from . import network
from .vendor.qrcode import ERROR_CORRECT_M, QRCode

_CACHE_LOCK = threading.Lock()
_cached_url = None
_cached_png = None


def _invalidate():
    global _cached_url, _cached_png
    with _CACHE_LOCK:
        _cached_url = None
        _cached_png = None


def control_url(state=None):
    """Return the confirmed station URL; unavailable/stale state has no QR."""
    if state is None:
        state = network.read_status()
    try:
        if not isinstance(state, dict) or state.get('controller_ok') is not True:
            raise ValueError
        if state.get('connected') is not True or not isinstance(state.get('ip'), str):
            raise ValueError
        address = ipaddress.IPv4Address(state['ip'])
        if (int(address) >> 24 == 0 or address.is_unspecified or address.is_loopback or address.is_link_local
                or address.is_multicast or address.is_reserved):
            raise ValueError
    except (ValueError, TypeError):
        _invalidate()
        raise RuntimeError('Домашний Wi-Fi пока не подключён.') from None
    return 'http://' + str(address) + ':8080/'


def _chunk(kind, data):
    return (struct.pack('>I', len(data)) + kind + data
            + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff))


def _png(url):
    # Version 3 gives a stable 37 x 37 matrix including the four-module border.
    # At six pixels per module the native image is 222 x 222 without resampling.
    code = QRCode(version=3, error_correction=ERROR_CORRECT_M, border=4)
    code.add_data(url, optimize=0)
    code.make(fit=False)
    matrix = code.get_matrix()
    scale = 6
    width = len(matrix) * scale
    rows = []
    for modules in matrix:
        bits = [0 if dark else 1 for dark in modules for _ in range(scale)]
        bits += [1] * (-len(bits) % 8)
        packed = bytes(sum(bits[start + shift] << (7 - shift) for shift in range(8))
                       for start in range(0, len(bits), 8))
        rows.extend([b'\0' + packed] * scale)
    header = struct.pack('>IIBBBBB', width, width, 1, 0, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + _chunk(b'IHDR', header)
            + _chunk(b'IDAT', zlib.compress(b''.join(rows), 9))
            + _chunk(b'IEND', b''))


def control_image(state=None, expected_ip=None):
    """Return (PNG bytes, URL), rejecting an image requested for an old address."""
    global _cached_url, _cached_png
    url = control_url(state)
    if expected_ip is not None and url != 'http://' + str(expected_ip) + ':8080/':
        raise RuntimeError('Адрес домашней сети изменился. Обновите страницу.')
    with _CACHE_LOCK:
        if url != _cached_url:
            png = _png(url)
            _cached_url, _cached_png = url, png
        return _cached_png, url


def get_control_qr(state=None, expected_ip=None):
    return control_image(state, expected_ip)
