from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from pathlib import Path
from urllib.parse import urlsplit
from collections import Counter
from playwright.sync_api import sync_playwright, TimeoutError
import json, sys

root=Path(__file__).resolve().parent
server=ThreadingHTTPServer(("127.0.0.1",18761),partial(SimpleHTTPRequestHandler,directory=str(root)))
Thread(target=server.serve_forever,daemon=True).start()

def origin(url):
    p=urlsplit(url)
    return f"{p.scheme}://{p.hostname}" if p.scheme in ("https","http") else p.scheme

def run(browser, mode):
    context=browser.new_context()
    page=context.new_page()
    counts=Counter()
    page.on("response",lambda r:counts.update([(origin(r.url),r.request.resource_type,str(r.status))]))
    page.on("requestfailed",lambda r:counts.update([(origin(r.url),r.resource_type,"requestfailed")]))
    page.on("pageerror",lambda e:print("PAGE_ERROR",type(e).__name__,flush=True))
    page.on("console",lambda m:print(m.text,flush=True) if m.text.startswith("SEFA017 ") else None)
    try:
        page.goto("http://127.0.0.1:18761/",wait_until="domcontentloaded")
        assert page.locator("iframe").count()==0
        print("PASS no iframe before selection",mode,flush=True)
        page.click("#"+mode)
        if mode=="manual":
            try:
                page.wait_for_function("!document.querySelector('#play').disabled",timeout=23000)
                page.click("#play")
            except TimeoutError:
                print("Manual API play unavailable: ready not confirmed",flush=True)
        try:
            page.wait_for_function("document.querySelector('#status').dataset.proof==='yes' || ['ready-not-confirmed','ready-rejected','sdk-missing','sdk-init-error','no-status-events','no-playing-status','no-sustained-progress'].includes(document.querySelector('#status').dataset.result)",timeout=44000)
        except TimeoutError:
            pass
        proof=page.locator("#status").get_attribute("data-proof")=="yes"
        result=page.locator("#status").get_attribute("data-result")
        print("RESULT",mode,result,"PASS" if proof else "UNKNOWN",flush=True)
        print("NETWORK",mode,json.dumps([{"origin":o,"resource":t,"status":s,"count":n} for (o,t,s),n in sorted(counts.items())]),flush=True)
        page.click("#stop")
        assert page.locator("iframe").count()==0
        assert page.locator("#status").get_attribute("data-proof")=="no"
        print("PASS stop cleanup",mode,flush=True)
        return proof
    finally:
        context.close()

try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        auto=run(browser,"auto")
        manual=run(browser,"manual")
        browser.close()
        print("SUMMARY",json.dumps({"auto":auto,"manual_api":manual}),flush=True)
        sys.exit(0 if auto and manual else 2)
finally:
    server.shutdown()
    server.server_close()
