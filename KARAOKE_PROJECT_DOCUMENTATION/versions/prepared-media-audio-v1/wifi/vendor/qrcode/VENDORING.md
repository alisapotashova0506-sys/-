python-qrcode 8.2
=================

Source: https://pypi.org/project/qrcode/8.2/
Copyright (c) 2011, Lincoln Loop. Distributed under BSD-3-Clause; the full
upstream license and historical MIT attribution are retained in LICENSE.

Only the QR matrix encoder is included. Relative imports replace top-level
qrcode imports. The QRCode class omits printing, neighbor context and image
factory methods; its image_factory constructor argument is also removed.
Encoding, error correction, layout and mask selection are unchanged.
PNG output is provided separately by wifi/control_qr.py using the Python
standard library. Neither Pillow nor pypng is required on the TV box.
