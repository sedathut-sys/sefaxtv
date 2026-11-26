"""One opt-in official VOD iframe session; no retries or autoplay policy changes."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
from threading import Thread
from collections import Counter
from urllib.parse import urlsplit
import sys, json, time
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"pilot019"))
from continuity import check

root=Path(__file__).resolve().parent
out=Path("pilot023-results");out.mkdir(exist_ok=True)
server=ThreadingHTTPServer(("127.0.0.1",18761),partial(SimpleHTTPRequestHandler,directory=str(root)))
Thread(target=server.serve_forever,daemon=True).start()
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(channel="chrome",headless=True)
        page=browser.new_page()
        rows=[];counts=Counter();rate_limited=False
        def response(r):
            global rate_limited
            u=urlsplit(r.url)
            if u.hostname=="video.blender.org":
                counts[(r.request.resource_type,r.status)]+=1
                if r.status==429:rate_limited=True
        def console(m):
            if m.text.startswith("SEFA017 ") and m.location.get("url","").startswith("http://127.0.0.1:18761/diagnostic.mjs"):
                row=json.loads(m.text[8:]);rows.append(row)
                if row.get("kind")!="status-update":print(m.text,flush=True)
        page.on("response",response)
        page.on("console",console)
        page.goto("http://127.0.0.1:18761/",wait_until="domcontentloaded")
        assert page.locator("iframe").count()==0
        print("BROWSER",browser.version,flush=True)
        page.click("#auto")
        deadline=time.monotonic()+75
        result="unknown"
        while time.monotonic()<deadline:
            if rate_limited:
                result="provider-rate-limited";break
            state=page.locator("#status").get_attribute("data-result")
            if state in ("ready-not-confirmed","ready-rejected","no-sustained-progress","unexpected-frame-reload","progress-stalled"):
                result=state;break
            ok,reason=check(rows,page.evaluate("performance.now()"))
            if ok and page.locator("#status").get_attribute("data-proof")=="yes":
                result="continuous-provider-progress";break
            page.wait_for_timeout(100)
        if rate_limited:result="provider-rate-limited"
        # Stop first; no repeat and no extra provider session.
        page.click("#stop")
        assert page.locator("iframe").count()==0
        assert page.locator("#status").get_attribute("data-proof")=="no"
        if rate_limited:result="provider-rate-limited"
        samples=[r for r in rows if r.get("kind")=="status-update"]
        report={"result":result,"rate_limited":rate_limited,"samples":len(samples),"first":samples[0] if samples else None,"last":samples[-1] if samples else None,"network":[{"resource":t,"status":s,"count":n} for (t,s),n in sorted(counts.items())]}
        (out/"events.json").write_text(json.dumps(rows,indent=2),encoding="utf-8")
        (out/"summary.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
        print("RESULT",json.dumps(report),flush=True)
        print("PASS stop cleanup",flush=True)
        browser.close()
        sys.exit(0 if result=="continuous-provider-progress" else 2)
finally:
    server.shutdown();server.server_close()
