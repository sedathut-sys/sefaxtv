"""Wall-clock-paced local source fixture -> deadline-bounded dubbed HLS.
Not a third-party live feed. No inference before each source segment is released.
"""
import concurrent.futures as cf,json,math,os,shutil,subprocess,time
from pathlib import Path
from voice_worker import Worker
ROOT=Path("pilot031-results").resolve();PUBLIC=ROOT/"public";PRIVATE=ROOT/"private"
SLOT=4.8;DELAY=9.0
CASES=[
 ("The captain lifted the trophy after the final.","football","navy"),
 ("The referee added three minutes of extra time.","football","darkgreen"),
 ("The striker scored from outside the penalty area.","football","maroon"),
 ("The train will arrive at the station at noon.","general","purple"),
 ("The final whistle has just been blown.","football","teal")
]
def cmd(args):subprocess.run(["ffmpeg","-nostdin","-v","error","-y",*args],check=True,timeout=25)
def atomic(path,data):
    tmp=path.with_suffix(path.suffix+".tmp");tmp.write_text(data,encoding="utf-8");os.replace(tmp,path)
def playlist(count,ended=False):
    lines=["#EXTM3U","#EXT-X-VERSION:3","#EXT-X-TARGETDURATION:5","#EXT-X-MEDIA-SEQUENCE:0","#EXT-X-PLAYLIST-TYPE:EVENT","#EXT-X-INDEPENDENT-SEGMENTS"]
    for i in range(count):
        if i:lines.append("#EXT-X-DISCONTINUITY")
        lines.extend([f"#EXTINF:{SLOT:.3f},",f"seg-{i}.ts"])
    if ended:lines.append("#EXT-X-ENDLIST")
    atomic(PUBLIC/"live.m3u8","\n".join(lines)+"\n")
def sleep_until(target):
    while (remaining:=target-time.monotonic())>0:time.sleep(min(remaining,.05))
def make_fixture():
    for i,(text,_,color) in enumerate(CASES):
        src=PRIVATE/f"src-{i}.wav";mp4=PRIVATE/f"src-{i}.mp4";ts=PRIVATE/f"orig-{i}.ts"
        subprocess.run(["espeak-ng","-v","en-us","-s","150","-w",str(src),"--stdin"],input=text,text=True,check=True,timeout=15)
        import wave
        with wave.open(str(src),"rb") as w:
            if w.getnframes()/w.getframerate()>SLOT:raise ValueError("source speech too long")
        cmd(["-f","lavfi","-i",f"color=c={color}:s=640x360:r=25","-i",str(src),"-map","0:v","-map","1:a","-vf",f"drawtext=text='SOURCE {i+1}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:fontsize=48:fontcolor=white:x=80:y=120","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-g","120","-bf","0","-c:a","aac","-ar","48000","-ac","1","-b:a","96k","-af","apad","-t",str(SLOT),str(mp4)])
        cmd(["-i",str(mp4),"-map","0:v:0","-map","0:a:0","-c","copy","-muxdelay","0","-muxpreload","0","-f","mpegts",str(ts)])
def main():
    ROOT.mkdir(exist_ok=True);PUBLIC.mkdir(exist_ok=True);PRIVATE.mkdir(exist_ok=True)
    make_fixture();worker=Worker()
    # Browser and source use the same monotonic wall-clock run. No precomputed translations.
    t0=time.monotonic();atomic(ROOT/"ready.json",json.dumps({"count":len(CASES),"slot":SLOT,"delay":DELAY}))
    reports=[];futures={};pool=cf.ThreadPoolExecutor(max_workers=1)
    def task(i):
        data=worker.run(PRIVATE/f"src-{i}.mp4",PRIVATE/f"dub-{i}.ts",SLOT,CASES[i][1])
        if i==len(CASES)-1:time.sleep(6.0) # intentional late-result fault injection, last slot only
        return data,time.monotonic()
    try:
        events=sorted([(SLOT*(i+1),0,i) for i in range(len(CASES))]+[(DELAY+SLOT*i,1,i) for i in range(len(CASES))])
        for at,kind,i in events:
            target=t0+at;sleep_until(target)
            if kind==0:
                # Single running + one queued maximum; never wait for queue or grow unbounded.
                outstanding=sum(not f.done() for f in futures.values())
                if outstanding<2:futures[i]=pool.submit(task,i)
                print("RELEASE",i,round(time.monotonic()-t0,3),flush=True)
                continue
            f=futures.get(i);mode="original";reason="queue-full" if f is None else "deadline";data=None
            if f is not None and f.done():
                try:
                    d,finished=f.result()
                    if finished<=target:
                        mode="dub";reason="ready";data=d
                except Exception as e:reason="worker-"+type(e).__name__
            elif f is not None:f.cancel()
            src=PRIVATE/(f"dub-{i}.ts" if mode=="dub" else f"orig-{i}.ts")
            dst=PUBLIC/f"seg-{i}.ts";tmp=dst.with_suffix(".tmp");shutil.copyfile(src,tmp);os.replace(tmp,dst)
            published=time.monotonic()-t0
            row={"index":i,"mode":mode,"reason":reason,"release_s":SLOT*(i+1),"deadline_s":at,"published_s":published,"publish_lateness_s":published-at,"data":data}
            reports.append(row);playlist(len(reports),len(reports)==len(CASES))
            atomic(ROOT/"summary.json",json.dumps({"slot":SLOT,"delay":DELAY,"rows":reports},ensure_ascii=False,indent=2))
            print("PUBLISH",json.dumps(row,ensure_ascii=False),flush=True)
    finally:pool.shutdown(wait=True,cancel_futures=True)
if __name__=="__main__":main()
