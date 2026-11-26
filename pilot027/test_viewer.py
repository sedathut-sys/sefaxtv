from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
from urllib.parse import urlsplit
from collections import Counter
import time,json,sys
root=Path(__file__).resolve().parent
out=Path("pilot027-results");out.mkdir(exist_ok=True)
server=ThreadingHTTPServer(("127.0.0.1",18761),partial(SimpleHTTPRequestHandler,directory=str(root)))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  b=p.chromium.launch(channel="chrome")
  page=b.new_page()
  limited=[];proof=[];counts=Counter()
  def response(r):
   if urlsplit(r.url).scheme=="https":
    counts[(r.request.resource_type,r.status)]+=1
    if r.status==429:limited.append(True)
  def console(m):
   if m.text.startswith("SEFA-HLS ") and m.location.get("url","").startswith("http://127.0.0.1:18761/hls-driver.mjs"):proof.append(json.loads(m.text[9:]))
  page.on("response",response);page.on("console",console)
  page.goto("http://127.0.0.1:18761/")
  assert page.locator("video").count()==0
  page.click("#stall")
  page.wait_for_function("document.querySelector('#status').dataset.source==='stall'&&document.querySelector('#status').dataset.state==='playing'")
  page.wait_for_function("document.querySelector('#status').dataset.source==='own'&&document.querySelector('#status').dataset.state==='playing'",timeout=20000)
  assert page.locator("canvas").count()==1
  page.click("#stop")
  assert page.locator("canvas,video").count()==0
  print("PASS local fallback and one active source",flush=True)
  page.click("#start")
  deadline=time.monotonic()+75;result="unknown"
  while time.monotonic()<deadline:
   if limited:result="rate-limited";break
   state=page.locator("#status").get_attribute("data-state")
   if state in ("exhausted","denied","unsupported","manual"):result=state;break
   if state=="playing" and page.locator("#proof").get_attribute("data-continuous")=="yes" and proof:result=state;break
   page.wait_for_timeout(100)
  if result=="continuous-frames":page.screenshot(path=str(out/"visual.png"))
  page.click("#stop");assert page.locator("video").count()==0
  if limited:result="rate-limited"
  report={"result":result,"proof":proof[-1] if proof else None,"network":[{"resource":t,"status":s,"count":n} for (t,s),n in sorted(counts.items())]}
  (out/"summary.json").write_text(json.dumps(report,indent=2))
  print("LIVE_RESULT",json.dumps(report),flush=True)
  b.close()
  sys.exit(0 if result=="continuous-frames" else 2)
finally:
 server.shutdown();server.server_close()
