from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
from urllib.parse import urlsplit
import time,json,sys
root=Path(__file__).resolve().parent
server=ThreadingHTTPServer(("127.0.0.1",18761),partial(SimpleHTTPRequestHandler,directory=str(root)))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  b=p.chromium.launch(channel="chrome")
  page=b.new_page()
  limited=[];proof=[]
  def response(r):
   if r.status==429 and urlsplit(r.url).hostname.endswith((".youtube.com",".googlevideo.com")):limited.append(True)
  def console(m):
   if m.text.startswith("SEFA-LIVE ") and m.location.get("url","").startswith("http://127.0.0.1:18761/live.js"):proof.append(json.loads(m.text[10:]))
  page.on("response",response);page.on("console",console)
  page.goto("http://127.0.0.1:18761/live.html")
  assert page.locator("iframe").count()==0
  page.click("#start")
  deadline=time.monotonic()+70;result="unknown"
  while time.monotonic()<deadline:
   if limited:result="rate-limited";break
   state=page.locator("#status").get_attribute("data-state")
   if state.startswith("player-error") or state in ("manual","api-unavailable"):result=state;break
   if state=="continuous-provider-progress" and proof:result=state;break
   page.wait_for_timeout(200)
  page.click("#stop");assert page.locator("iframe").count()==0
  if limited:result="rate-limited"
  print("LIVE_RESULT",json.dumps({"result":result,"proof":proof[-1] if proof else None}),flush=True)
  b.close()
  sys.exit(0 if result=="continuous-provider-progress" else 2)
finally:
 server.shutdown();server.server_close()
