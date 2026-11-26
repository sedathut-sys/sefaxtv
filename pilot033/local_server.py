"""No public listener, no arbitrary files, no browser-supplied source URL."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import re,secrets
def handler(root,token,stop):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def valid(self):
            return self.headers.get("Host")==f"127.0.0.1:{self.server.server_port}"
        def do_GET(self):
            if not self.valid():self.send_error(403);return
            path=urlsplit(self.path).path
            prefix="/"+token+"/"
            if not path.startswith(prefix):self.send_error(404);return
            name=path[len(prefix):] or "index.html"
            types={"index.html":"text/html; charset=utf-8","viewer.mjs":"text/javascript","hls.mjs":"text/javascript","status.json":"application/json","live.m3u8":"application/vnd.apple.mpegurl"}
            mime=types.get(name)
            if mime is None and re.fullmatch(r"seg-[0-9]{1,2}\.ts",name):mime="video/mp2t"
            if mime is None:self.send_error(404);return
            try:data=(root/name).read_bytes()
            except OSError:self.send_error(404);return
            self.send_response(200)
            self.send_header("Content-Type",mime);self.send_header("Content-Length",str(len(data)))
            self.send_header("Cache-Control","no-store");self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Content-Security-Policy","default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; connect-src 'self'; media-src 'self' blob:; worker-src 'self' blob:; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers();self.wfile.write(data)
        def do_POST(self):
            origin=f"http://127.0.0.1:{self.server.server_port}"
            if not self.valid() or self.headers.get("Origin")!=origin or self.path!="/"+token+"/stop":
                self.send_error(403);return
            stop.set();self.send_response(204);self.end_headers()
    return Handler
def serve(root,stop):
    token=secrets.token_urlsafe(24)
    server=ThreadingHTTPServer(("127.0.0.1",0),handler(Path(root),token,stop))
    return server,f"http://127.0.0.1:{server.server_port}/{token}/"
