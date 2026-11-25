from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from pathlib import Path
from playwright.sync_api import sync_playwright
import sys

root=Path(__file__).resolve().parent
server=ThreadingHTTPServer(("127.0.0.1",18761),partial(SimpleHTTPRequestHandler,directory=str(root)))
Thread(target=server.serve_forever,daemon=True).start()
try:
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True)
        page=b.new_page()
        page.goto("http://127.0.0.1:18761/",wait_until="domcontentloaded")
        assert page.locator("iframe").count()==0
        print("PASS no iframe before selection",flush=True)
        page.click("#start")
        try:
            page.wait_for_function("document.querySelector('#status').dataset.proof==='yes'",timeout=22000)
            print("PASS external VOD player reported sustained progress",flush=True)
        except Exception:
            print("UNKNOWN external VOD playback: "+page.locator("#status").inner_text(),flush=True)
            page.click("#stop")
            assert page.locator("iframe").count()==0
            b.close()
            sys.exit(2)
        page.click("#stop")
        assert page.locator("iframe").count()==0
        assert page.locator("#status").get_attribute("data-proof")=="no"
        print("PASS stop removes frame and clears proof",flush=True)
        b.close()
finally:
    server.shutdown()
    server.server_close()
