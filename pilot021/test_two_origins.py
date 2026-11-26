from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parent
servers=[ThreadingHTTPServer(("127.0.0.1",port),partial(SimpleHTTPRequestHandler,directory=str(root))) for port in (18762,18763)]
for s in servers:Thread(target=s.serve_forever,daemon=True).start()
try:
    with sync_playwright() as p:
        browser=p.chromium.launch()
        for mode in ("notice","reply","reject"):
            page=browser.new_page()
            page.goto("http://127.0.0.1:18762/fixture-parent.html")
            page.wait_for_function("typeof window.testStart==='function'")
            assert page.locator("iframe").count()==0
            page.evaluate("(mode)=>window.testStart(mode)",mode)
            if mode=="reject":
                page.wait_for_function("window.result.failed")
                page.evaluate("window.injectWrong()")
                page.wait_for_function("window.result.rejected>=2")
                assert page.evaluate("!window.result.ready&&!window.result.proof")
            else:
                page.wait_for_function("window.result.proof",timeout=10000)
                assert page.evaluate("window.result.ready&&window.result.handshake===1")
            assert page.evaluate("window.result.queryCount===1")
            page.evaluate("window.stopTest()")
            assert page.evaluate("!window.result.ready&&!window.result.proof")
            print("PASS own two-origin fixture",mode,flush=True)
            page.close()
        browser.close()
finally:
    for s in servers:s.shutdown();s.server_close()
