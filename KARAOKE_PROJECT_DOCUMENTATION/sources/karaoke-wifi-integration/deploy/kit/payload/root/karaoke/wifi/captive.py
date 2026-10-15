#!/usr/bin/env python3
"""HTTP captive-portal redirects for an active KARAOKE setup access point.

This helper opens only an HTTP listener. NetworkManager and the controller own
the access point and DNS. A failed bind is reported; another process is never
stopped or replaced. Start it after 192.168.100.1 exists, stop it before the AP
is taken down. Phone operating systems decide whether to display a portal.
"""

import html
import ipaddress
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


class _PortalServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 32


class CaptivePortal:
    """Idempotent, non-blocking start and graceful stop of an AP-only listener."""

    def __init__(self, bind_address="192.168.100.1", port=80,
                 target_url="http://192.168.100.1:8080/wifi/setup"):
        address = ipaddress.IPv4Address(bind_address)
        if address.is_unspecified:
            raise ValueError("The portal must bind a specific local IPv4 address")
        if not isinstance(port, int) or not 0 <= port <= 65535:
            raise ValueError("Invalid HTTP port")
        target = urlsplit(target_url)
        if (target.scheme != "http" or not target.hostname or
                any(c in target_url for c in "\r\n")):
            raise ValueError("Expected a plain HTTP setup URL")
        self.bind_address = str(address)
        self.port = port
        self.target_url = target_url
        self.last_error = ""
        self._server = None
        self._thread = None
        self._lock = threading.Lock()

    @property
    def running(self):
        with self._lock:
            return self._thread is not None and self._thread.is_alive()

    @property
    def bound_port(self):
        """The actual listener port (useful for port=0 in isolated tests)."""
        with self._lock:
            return self._server.server_port if self._server is not None else None

    def start(self):
        """Return True while listening, or False with last_error on failure."""
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return True
            if self._server is not None:
                self._server.server_close()
                self._server = None
                self._thread = None

            target_url = self.target_url
            body = ("<!doctype html><html lang=\"ru\"><meta charset=\"utf-8\">"
                    "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
                    "<title>KARAOKE — Wi-Fi</title>"
                    "<p><a href=\"" + html.escape(target_url, quote=True) +
                    "\">Настроить Wi-Fi / Set up Wi-Fi</a></p></html>").encode("utf-8")

            class Handler(BaseHTTPRequestHandler):
                protocol_version = "HTTP/1.0"

                def setup(self):
                    self.request.settimeout(5)
                    super().setup()

                def _redirect(self, head_only=False):
                    # Probe URLs differ between Android, iOS and Windows.
                    # Redirect every GET/HEAD, including absolute probe URLs.
                    self.send_response(302)
                    self.send_header("Location", target_url)
                    self.send_header("Cache-Control", "no-store, max-age=0")
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.send_header("Connection", "close")
                    self.end_headers()
                    if not head_only:
                        try:
                            self.wfile.write(body)
                        except (BrokenPipeError, ConnectionResetError):
                            pass

                def do_GET(self):
                    self._redirect()

                def do_HEAD(self):
                    self._redirect(head_only=True)

                def log_message(self, format, *args):
                    # Connectivity probes are routine and may contain hostnames.
                    pass

            server = None
            try:
                server = _PortalServer((self.bind_address, self.port), Handler)
                thread = threading.Thread(
                    target=server.serve_forever,
                    kwargs={"poll_interval": 0.2},
                    name="karaoke-captive-http", daemon=True)
                thread.start()
            except (OSError, RuntimeError) as error:
                if server is not None:
                    server.server_close()
                self.last_error = "%s: %s" % (type(error).__name__, error)
                return False
            self._server = server
            self._thread = thread
            self.last_error = ""
            return True

    def stop(self):
        """Stop accepting requests and release the bound port; safe to repeat."""
        with self._lock:
            server, thread = self._server, self._thread
            self._server = None
            self._thread = None
            if server is not None:
                if thread is not None and thread.is_alive():
                    server.shutdown()
                server.server_close()
                if thread is not None and thread is not threading.current_thread():
                    thread.join(timeout=2)
