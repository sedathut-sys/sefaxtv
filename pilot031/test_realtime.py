from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import json,shutil,subprocess,sys,time
from verify import verify
root=Path("pilot031-results").resolve();root.mkdir(exist_ok=True);public=root/"public";public.mkdir(exist_ok=True)
for name in ("index.html","viewer.mjs"):shutil.copyfile(Path("pilot031")/name,public/name)
(public/"vendor").mkdir(exist_ok=True);shutil.copyfile("pilot031/vendor/hls.mjs",public/"vendor/hls.mjs")
server=ThreadingHTTPServer(("127.0.0.1",18764),partial(SimpleHTTPRequestHandler,directory=str(public)))
Thread(target=server.serve_forever,daemon=True).start()
log=(root/"pipeline.log").open("w",encoding="utf-8")
proc=subprocess.Popen([sys.executable,"pilot031/pipeline.py"],stdout=log,stderr=subprocess.STDOUT)
try:
    deadline=time.monotonic()+240
    while not (public/"seg-1.ts").exists():
        if proc.poll() is not None or time.monotonic()>deadline:raise RuntimeError("pipeline startup failed")
        time.sleep(.1)
    with sync_playwright() as p:
        b=p.chromium.launch(channel="chrome")
        page=b.new_page();page.goto("http://127.0.0.1:18764/")
        page.click("#start")
        page.wait_for_function("window.proof.live && window.proof.frames>=150 && window.proof.last-window.proof.first>=8 && window.proof.errors===0",timeout=35000)
        proof=page.evaluate("window.proof")
        print("BROWSER_RESULT",json.dumps(proof),flush=True)
        page.screenshot(path=str(root/"browser.png"))
        page.click("#stop");assert page.locator("#v").evaluate("v=>v.paused && !v.getAttribute('src')")
        b.close()
    assert proc.wait(timeout=30)==0
    checks=verify(root)
    (root/"evidence.json").write_text(json.dumps({"browser":proof,"mux":checks},indent=2))
    print("PASS paced local HLS publication, actual decoded video frames, preserved video and bounded audio fallback",flush=True)
finally:
    if proc.poll() is None:
        proc.terminate()
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.kill();proc.wait()
    log.close();server.shutdown();server.server_close()
    print((root/"pipeline.log").read_text(encoding="utf-8",errors="replace")[-12000:],flush=True)
