from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent
servers=[ThreadingHTTPServer(("127.0.0.1",p),partial(SimpleHTTPRequestHandler,directory=str(root))) for p in (18761,18763)]
for s in servers:Thread(target=s.serve_forever,daemon=True).start()
try:
    with sync_playwright() as p:
        browser=p.chromium.launch()
        page=browser.new_page()
        page.goto("http://127.0.0.1:18761/fixture-parent.html")
        page.wait_for_function("typeof window.startTest==='function'")
        assert page.locator("iframe").count()==0
        page.evaluate("startTest()")
        page.wait_for_function("window.result.ready&&window.result.proof",timeout=10000)
        page.evaluate("inject()")
        page.wait_for_function("rejected()>=2",timeout=10000)
        page.evaluate("stopTest()")
        assert page.evaluate("!result.ready&&!result.proof")
        print("PASS actual JSChannel two-origin handshake, readiness, progress, wrong origin/window, cleanup",flush=True)
        browser.close()
finally:
    for s in servers:s.shutdown();s.server_close()
