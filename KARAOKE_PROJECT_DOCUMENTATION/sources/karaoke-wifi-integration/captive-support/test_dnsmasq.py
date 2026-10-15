"""Optional isolated DNS integration test; no daemon installation required.

Set DNSMASQ_BINARY to an existing binary. It listens only on loopback on a
random unprivileged port and exits in tearDownClass. Host DNS is not changed.
"""
import os
from pathlib import Path
import random
import socket
import struct
import subprocess
import tempfile
import time
import unittest


@unittest.skipUnless(os.environ.get("DNSMASQ_BINARY"), "Set DNSMASQ_BINARY")
class SharedDnsConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        binary = os.environ["DNSMASQ_BINARY"]
        cls.directory = tempfile.TemporaryDirectory(prefix="karaoke-dns-test-")
        config = Path(cls.directory.name) / "config"
        source = Path(__file__).with_name("karaoke-setup.conf").read_text()
        config.write_text(source + "\nno-resolv\nno-hosts\n")
        subprocess.run([binary, "--test", "--conf-file=" + str(config)],
                       check=True, capture_output=True)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as reserve:
            reserve.bind(("127.0.0.1", 0))
            cls.port = reserve.getsockname()[1]
        cls.process = subprocess.Popen([
            binary, "--keep-in-foreground", "--conf-file=" + str(config),
            "--port=" + str(cls.port), "--listen-address=127.0.0.1",
            "--bind-interfaces", "--pid-file=" + str(Path(cls.directory.name) / "pid")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        deadline = time.monotonic() + 3
        while True:
            if cls.process.poll() is not None:
                raise RuntimeError(cls.process.stderr.read().decode())
            try:
                cls.query("connectivitycheck.gstatic.com", 1)
                break
            except socket.timeout:
                if time.monotonic() >= deadline:
                    cls.process.terminate()
                    cls.process.communicate(timeout=2)
                    raise

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.process.communicate(timeout=2)
        cls.directory.cleanup()

    @classmethod
    def query(cls, hostname, rrtype):
        query_id = random.randrange(65536)
        labels = b"".join(bytes([len(label)]) + label.encode("ascii")
                          for label in hostname.split(".")) + b"\0"
        message = struct.pack("!6H", query_id, 0x0100, 1, 0, 0, 0)
        message += labels + struct.pack("!HH", rrtype, 1)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
            client.settimeout(0.25)
            client.sendto(message, ("127.0.0.1", cls.port))
            response, _ = client.recvfrom(2048)
        assert struct.unpack_from("!H", response)[0] == query_id
        return response

    def test_probe_hosts_resolve_to_setup_ipv4(self):
        for host in ("connectivitycheck.gstatic.com", "captive.apple.com",
                     "www.msftconnecttest.com", "an-unknown-name.invalid"):
            with self.subTest(host=host):
                response = self.query(host, 1)
                self.assertEqual(struct.unpack_from("!H", response, 6)[0], 1)
                self.assertEqual(response[-4:], socket.inet_aton("192.168.100.1"))

    def test_ipv6_query_returns_nodata_offline(self):
        response = self.query("connectivitycheck.gstatic.com", 28)
        flags = struct.unpack_from("!H", response, 2)[0]
        self.assertEqual(flags & 15, 0)  # NOERROR, not SERVFAIL or NXDOMAIN.
        self.assertEqual(struct.unpack_from("!H", response, 6)[0], 0)


if __name__ == "__main__":
    unittest.main()
