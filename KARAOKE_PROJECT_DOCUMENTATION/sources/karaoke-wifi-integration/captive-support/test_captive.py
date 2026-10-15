"""Meaningful HTTP tests without modifying network interfaces or host services."""
import http.client
from contextlib import closing
import importlib.util
import socket
import threading
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "updated/wifi/captive.py"
spec = importlib.util.spec_from_file_location("karaoke_captive", MODULE)
captive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(captive)


class CaptiveTests(unittest.TestCase):
    def setUp(self):
        self.portal = captive.CaptivePortal(bind_address="127.0.0.1", port=0)
        self.assertTrue(self.portal.start(), self.portal.last_error)

    def tearDown(self):
        self.portal.stop()

    def request(self, path, method="GET"):
        with closing(http.client.HTTPConnection("127.0.0.1", self.portal.bound_port,
                                                timeout=2)) as client:
            client.request(method, path)
            response = client.getresponse()
            return response.status, dict(response.getheaders()), response.read()

    def test_probe_redirects(self):
        for path in ("/", "/generate_204", "/gen_204", "/hotspot-detect.html",
                     "/library/test/success.html", "/connecttest.txt",
                     "/ncsi.txt", "/unknown?foo=bar",
                     "http://connectivitycheck.gstatic.com/generate_204"):
            with self.subTest(path=path):
                status, headers, body = self.request(path)
                self.assertEqual(status, 302)
                self.assertEqual(headers["Location"], self.portal.target_url)
                self.assertEqual(headers["Cache-Control"], "no-store, max-age=0")
                self.assertIn(b"http://192.168.100.1:8080/wifi/setup", body)

    def test_head_redirect_has_no_body(self):
        status, headers, body = self.request("/generate_204", "HEAD")
        self.assertEqual(status, 302)
        self.assertGreater(int(headers["Content-Length"]), 0)
        self.assertEqual(body, b"")

    def test_start_stop_are_idempotent_and_release_port(self):
        port = self.portal.bound_port
        self.assertTrue(self.portal.start())
        self.assertEqual(self.portal.bound_port, port)
        self.assertTrue(self.portal.running)
        self.portal.stop()
        self.portal.stop()
        self.assertFalse(self.portal.running)
        with socket.socket() as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            probe.bind(("127.0.0.1", port))
        self.assertTrue(self.portal.start())

    def test_collision_does_not_stop_other_server(self):
        contender = captive.CaptivePortal(bind_address="127.0.0.1",
                                          port=self.portal.bound_port)
        self.assertFalse(contender.start())
        self.assertIn("OSError", contender.last_error)
        self.assertFalse(contender.running)
        self.assertEqual(self.request("/")[0], 302)
        contender.stop()

    def test_unsupported_method_does_not_accept_payload(self):
        self.assertEqual(self.request("/", "POST")[0], 501)

    def test_concurrent_probes(self):
        results = []
        threads = [threading.Thread(target=lambda: results.append(
            self.request("/generate_204")[0])) for _ in range(12)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(results, [302] * 12)

    def test_rejects_wildcard_bind_and_header_injection(self):
        with self.assertRaises(ValueError):
            captive.CaptivePortal(bind_address="0.0.0.0")
        with self.assertRaises(ValueError):
            captive.CaptivePortal(target_url="http://localhost/\r\nEvil: x")


if __name__ == "__main__":
    unittest.main()
