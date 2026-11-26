from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent
server=ThreadingHTTPServer(("127.0.0.1",18761),partial(SimpleHTTPRequestHandler,directory=str(root)))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  b=p.chromium.launch()
  page=b.new_page()
  page.goto("http://127.0.0.1:18761/")
  assert page.locator("iframe").count()==0
  page.click("#stall")
  page.wait_for_function("document.querySelector('#status').dataset.state==='playing'")
  page.wait_for_function("document.querySelector('#status').dataset.source==='own'&&document.querySelector('#status').dataset.state==='playing'",timeout=20000)
  assert page.locator("canvas").count()==1
  page.click("#stop")
  assert page.locator("canvas, iframe").count()==0
  print("PASS smart viewer owned visual stall and fallback, one source, stop",flush=True)
  b.close()
finally:
 server.shutdown();server.server_close()
