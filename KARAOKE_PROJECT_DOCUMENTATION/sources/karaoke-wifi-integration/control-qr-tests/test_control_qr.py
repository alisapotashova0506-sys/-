"""Run with PYTHONPATH=../updated; QR decode checks use cloud-only OpenCV."""
import struct
import unittest
from unittest import mock

from wifi import control_qr


def state(ip='192.168.1.102', **changes):
    value = {'controller_ok': True, 'connected': True, 'ip': ip}
    value.update(changes)
    return value


class ControlQRTests(unittest.TestCase):
    def tearDown(self):
        control_qr._invalidate()

    def test_reads_controller_status_when_not_passed(self):
        with mock.patch.object(control_qr.network, 'read_status', return_value=state()) as read:
            self.assertEqual(control_qr.control_url(), 'http://192.168.1.102:8080/')
            read.assert_called_once_with()

    def test_accepts_private_shared_and_public_lan_addresses(self):
        for ip in ('192.168.1.102', '10.0.1.2', '172.31.10.11', '100.64.1.2',
                   '8.8.8.8', '223.255.255.254'):
            with self.subTest(ip=ip):
                self.assertEqual(control_qr.control_url(state(ip)), 'http://' + ip + ':8080/')

    def test_disconnected_stale_or_missing_state_rejected(self):
        for value in (None, {}, [], state(connected=False), state(controller_ok=False),
                      state(connected='yes'), state(controller_ok=1)):
            with self.subTest(state=value):
                with mock.patch.object(control_qr.network, 'read_status', return_value=value):
                    with self.assertRaises(RuntimeError):
                        control_qr.control_image(value)

    def test_rejects_unusable_and_malformed_addresses(self):
        for ip in ('0.0.0.0', '0.1.2.3', '127.0.0.1', '169.254.1.2',
                   '224.0.0.1', '255.255.255.255', '::1', '192.168.1.1/24',
                   '192.168.1.1\n', 'example.com', '', None, 3232235878):
            with self.subTest(ip=ip):
                with self.assertRaises(RuntimeError):
                    control_qr.control_image(state(ip))

    def test_cache_reuses_image_until_address_changes(self):
        with mock.patch.object(control_qr, '_png', wraps=control_qr._png) as render:
            first = control_qr.control_image(state())
            self.assertIs(control_qr.control_image(state())[0], first[0])
            changed = control_qr.control_image(state('192.168.1.103'))
            self.assertNotEqual(changed, first)
            self.assertEqual(render.call_count, 2)

    def test_disconnect_invalidates_cache(self):
        with mock.patch.object(control_qr, '_png', wraps=control_qr._png) as render:
            control_qr.control_image(state())
            with self.assertRaises(RuntimeError):
                control_qr.control_image(state(connected=False))
            control_qr.control_image(state())
            self.assertEqual(render.call_count, 2)

    def test_query_address_must_match_current_home_ip(self):
        with self.assertRaises(RuntimeError):
            control_qr.control_image(state(), expected_ip='192.168.1.99')
        png, url = control_qr.control_image(state(), expected_ip='192.168.1.102')
        self.assertTrue(png.startswith(b'\x89PNG\r\n\x1a\n'))
        self.assertEqual(url, 'http://192.168.1.102:8080/')

    def test_native_image_is_222_square_one_bit_grayscale(self):
        png, _ = control_qr.control_image(state())
        self.assertEqual(struct.unpack('>IIBBBBB', png[16:29]), (222, 222, 1, 0, 0, 0, 0))

    def test_alias_preserves_contract(self):
        self.assertEqual(control_qr.get_control_qr(state()), control_qr.control_image(state()))

    def test_decodes_actual_png_after_home_address_changes(self):
        try:
            import cv2
            import numpy
        except ImportError:
            self.skipTest('OpenCV is a cloud-only independent decoder')
        for ip in ('192.168.1.102', '10.0.0.42', '100.64.1.5', '8.8.8.8', '223.255.255.254'):
            with self.subTest(ip=ip):
                png, url = control_qr.control_image(state(ip))
                image = cv2.imdecode(numpy.frombuffer(png, dtype=numpy.uint8), cv2.IMREAD_GRAYSCALE)
                payload, points, _ = cv2.QRCodeDetector().detectAndDecode(image)
                self.assertIsNotNone(points)
                self.assertEqual(payload, url)


if __name__ == '__main__':
    unittest.main()
