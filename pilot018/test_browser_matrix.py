"""Public player UI comparison; never read external frame DOM/media internals or bypass policies."""
from collections import Counter
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import argparse, json, re, sys

parser=argparse.ArgumentParser()
parser.add_argument("--browser",choices=["chromium","chrome","chrome-headed"],required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parent.parent/"pilot017"
output=Path("pilot018-results");output.mkdir(exist_ok=True)
server=ThreadingHTTPServer(("127.0.0.1",18761),partial(SimpleHTTPRequestHandler,directory=str(root)))
Thread(target=server.serve_forever,daemon=True).start()

def origin(url):
    p=urlsplit(url)
    return f"{p.scheme}://{p.hostname}" if p.scheme in ("https","http") else p.scheme

def error_code(value):
    m=re.search(r"(?:net::)?ERR_[A-Z0-9_]+|NS_ERROR_[A-Z0-9_]+",str(value))
    return m.group(0) if m else "other"

def mime(value):
    v=(value or "").split(";")[0].strip().lower()
    return v if re.fullmatch(r"[a-z0-9.+-]+/[a-z0-9.+-]+",v) else "unknown"

def run(browser,mode):
    context=browser.new_context(locale="en-US")
    page=context.new_page()
    counts=Counter()
    def response(r):
        counts[(origin(r.url),r.request.resource_type,str(r.status),mime(r.headers.get("content-type")))]+=1
    def failure(r):
        counts[(origin(r.url),r.resource_type,error_code(r.failure),"unknown")]+=1
    page.on("response",response)
    page.on("requestfailed",failure)
    page.on("console",lambda m:print(m.text,flush=True) if m.text.startswith("SEFA017 ") else (
        print("CONSOLE_ERROR_CODE",error_code(m.text),flush=True) if m.type=="error" else None))
    page.on("pageerror",lambda e:print("PAGE_ERROR",error_code(e),flush=True))
    result="unknown"
    try:
        page.goto("http://127.0.0.1:18761/",wait_until="domcontentloaded")
        assert page.locator("iframe").count()==0
        print("PASS no iframe before selection",args.browser,mode,flush=True)
        # Only our own page is evaluated. These are browser capabilities, not remote media inspection.
        caps=page.evaluate("""()=>{const v=document.createElement('video');return {
          h264:v.canPlayType('video/mp4; codecs="avc1.42E01E, mp4a.40.2"'),
          vp9:v.canPlayType('video/webm; codecs="vp9, opus"'),
          mse:typeof MediaSource==='function',
          h264MSE:typeof MediaSource==='function'&&MediaSource.isTypeSupported('video/mp4; codecs="avc1.42E01E, mp4a.40.2"')
        }}""")
        print("CAPABILITIES",json.dumps(caps),flush=True)
        page.click("#auto" if mode=="auto" else "#manual")
        if mode=="ui-play":
            try:
                page.wait_for_function("!document.querySelector('#play').disabled",timeout=22000)
                # Only the provider's visible, accessible Play control is clicked as a user would.
                # No DOM/media properties or script execution inside the provider frame.
                control=page.frame_locator("#host iframe").get_by_role("button",name=re.compile(r"^play(?: video)?$",re.I)).first
                control.click(timeout=7000)
                print("UI_PLAY_CLICKED",flush=True)
            except PlaywrightTimeout:
                result="ui-play-unavailable"
                print("UI_PLAY_UNAVAILABLE",flush=True)
        if result!="ui-play-unavailable":
            try:
                page.wait_for_function("document.querySelector('#status').dataset.proof==='yes'",timeout=16000)
                page.wait_for_timeout(3500)
                result="provider-progress" if page.locator("#status").get_attribute("data-proof")=="yes" else "progress-lost"
            except PlaywrightTimeout:
                result=page.locator("#status").get_attribute("data-result") or "unknown"
                if result=="provider-progress": result="progress-not-sustained"
        print("RESULT",args.browser,mode,result,flush=True)
        print("NETWORK",json.dumps([dict(origin=o,resource=t,status=s,mime=m,count=n) for (o,t,s,m),n in sorted(counts.items())]),flush=True)
        page.screenshot(path=str(output/f"{args.browser}-{mode}.png"))
        page.click("#stop")
        assert page.locator("iframe").count()==0
        assert page.locator("#status").get_attribute("data-proof")=="no"
        print("PASS cleanup",args.browser,mode,flush=True)
        return result=="provider-progress"
    finally:
        context.close()

try:
    with sync_playwright() as p:
        opts={"headless":args.browser!="chrome-headed"}
        if args.browser!="chromium":opts["channel"]="chrome"
        browser=p.chromium.launch(**opts)
        print("BROWSER",args.browser,browser.version,flush=True)
        try:
            auto=run(browser,"auto")
            manual=run(browser,"ui-play")
        finally:
            browser.close()
        print("SUMMARY",json.dumps({"browser":args.browser,"auto":auto,"ui_play":manual}),flush=True)
        sys.exit(0 if auto and manual else 2)
finally:
    server.shutdown()
    server.server_close()
