"""Actual browser MediaRecorder -> local HTTP -> real models -> HLS -> decoded frames.
The stream is owned canvas + generated speech, NOT a real display permission test."""
import json,subprocess,tempfile,threading,time,shutil,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from local import Session,serve,assets
out=Path("pilot034-results");out.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory() as td:
    s=Session(td,"football");assets(s)
    subprocess.run(["espeak-ng","-v","en-us","-s","150","-w",str(s.public/"fixture.wav"),"--stdin"],input="The goalkeeper saved the penalty in the final minute.",text=True,check=True)
    server,url=serve(s,fixture=True);threading.Thread(target=server.serve_forever,daemon=True).start()
    t=threading.Thread(target=s.run);t.start()
    try:
        deadline=time.monotonic()+180
        while not s.ready:
            if s.done.is_set() or time.monotonic()>deadline:raise RuntimeError("model initialization")
            time.sleep(.1)
        with sync_playwright() as p:
            b=p.chromium.launch(channel="chrome",args=["--autoplay-policy=no-user-gesture-required"])
            page=b.new_page();page.goto(url)
            result=page.evaluate("""async ()=>{
              const {captureLoop}=await import('./capture.mjs');
              const canvas=document.createElement('canvas');canvas.width=640;canvas.height=360;document.body.append(canvas);
              const ctx=canvas.getContext('2d');let n=0;const timer=setInterval(()=>{ctx.fillStyle='#123456';ctx.fillRect(0,0,640,360);ctx.fillStyle='white';ctx.font='30px sans-serif';ctx.fillText('CONTROLLED SOURCE '+(++n),20,120);},40);
              const ac=new AudioContext();await ac.resume();const buf=await ac.decodeAudioData(await (await fetch('./fixture.wav')).arrayBuffer());
              const dest=ac.createMediaStreamDestination();
              const play=()=>{const source=ac.createBufferSource();source.buffer=buf;source.connect(dest);source.start();};
              play();const sound=setInterval(play,4800);
              const stream=new MediaStream([...canvas.captureStream(25).getVideoTracks(),...dest.stream.getAudioTracks()]);
              try{return await captureLoop(stream,{count:3});}finally{clearInterval(timer);clearInterval(sound);await ac.close();}
            }""")
            print("RECORDER_RESULT",json.dumps(result),flush=True)
            assert len(result)==3 and all(x["size"]>1000 and x["gap"]<500 for x in result)
            page.wait_for_function("!document.querySelector('#play').disabled",timeout=40000);page.click("#play")
            page.evaluate("""()=>{let v=document.querySelector('#v');window.framesSeen=0;function f(){window.framesSeen++;v.requestVideoFrameCallback(f)}v.requestVideoFrameCallback(f)}""")
            page.wait_for_function("window.framesSeen>=80 && document.querySelector('#v').currentTime>3",timeout=30000)
            assert s.done.wait(30)
            assert len(s.rows)==3 and sum(r["mode"]=="dub" for r in s.rows)>=2,s.rows
            report={"capture":result,"rows":[{k:v for k,v in r.items() if k!="translation"} for r in s.rows],"frames":page.evaluate("window.framesSeen"),"scope":"controlled MediaRecorder, not real TV tab permission"}
            (out/"summary.json").write_text(json.dumps(report,indent=2))
            page.screenshot(path=str(out/"visual.png"));page.click("#stop");assert s.stop.wait(3)
            b.close()
            print("PASS actual local browser recording, upload, dublaj, HLS playback and stop",flush=True)
    finally:s.stop.set();t.join();server.shutdown();server.server_close()
