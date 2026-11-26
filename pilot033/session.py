"""Bounded private local live dubbing session. Source configured in CLI only."""
from pathlib import Path
import concurrent.futures as cf, threading, queue, time, json, math, os, shutil, subprocess
from ingest import initial,newer,get,Unsupported
def atomic(path,data):
    tmp=path.with_suffix(path.suffix+".tmp");tmp.write_text(data,encoding="utf-8");os.replace(tmp,path)
def playlist(rows,ended=False):
    target=max([1]+[math.ceil(r["duration"]) for r in rows])
    lines=["#EXTM3U","#EXT-X-VERSION:3",f"#EXT-X-TARGETDURATION:{target}","#EXT-X-MEDIA-SEQUENCE:0","#EXT-X-PLAYLIST-TYPE:EVENT"]
    for i,r in enumerate(rows):
        if i:lines.append("#EXT-X-DISCONTINUITY")
        lines.extend([f'#EXTINF:{r["duration"]:.6f},',f"seg-{i}.ts"])
    if ended:lines.append("#EXT-X-ENDLIST")
    return "\n".join(lines)+"\n"
def probe(path):
    d=json.loads(subprocess.check_output(["ffprobe","-v","error","-protocol_whitelist","file,pipe","-f","mpegts","-show_streams","-of","json",str(path)],timeout=8))
    v=next((x for x in d["streams"] if x["codec_type"]=="video"),None)
    a=next((x for x in d["streams"] if x["codec_type"]=="audio"),None)
    if not v or not a or v["codec_name"]!="h264" or a["codec_name"]!="aac":raise Unsupported("H264 AAC required")
    return v,a
def verify(source,target,slot):
    v,a=probe(target);orig,_=probe(source)
    if (v["width"],v["height"])!=(orig["width"],orig["height"]):return False
    if abs(float(v["start_time"])-float(a["start_time"]))>.10 or abs(float(v["duration"])-float(a["duration"]))>.15:return False
    return abs(float(v["duration"])-slot)<=.3
def select(future,cutoff,verify_fn):
    if future is None:return "original","queue-full",None
    try:
        data,finished=future.result(timeout=max(0,cutoff-time.monotonic()))
        if finished>cutoff:return "original","deadline",None
        if not verify_fn():return "original","mux-check",None
        if time.monotonic()>cutoff:return "original","deadline",None
        return "dub","ready",data
    except cf.TimeoutError:
        future.cancel();return "original","deadline",None
    except Exception as e:return "original",type(e).__name__,None
def run(public,private,stop,domain="general",count=8):
    rows=[];status={"state":"checking","rows":[]}
    def save(state,reason=None):
        status.update(state=state,rows=rows.copy())
        if reason:status["reason"]=reason
        atomic(public/"status.json",json.dumps(status,ensure_ascii=False))
    save("checking")
    try:
        initial(time.monotonic()+15)
        if stop.is_set():return
        save("loading-models")
        # Import only after a successful source check.
        import sys
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"pilot032"))
        from live_worker import Worker
        worker=Worker()
        if stop.is_set():return
        save("receiving")
        q=queue.Queue(maxsize=3);error=[];pending=set();lock=threading.Lock()
        pool=cf.ThreadPoolExecutor(max_workers=1)
        def producer():
            try:
                deadline=time.monotonic()+100
                url,p=initial(deadline);last=p.items[-1].seq;i=0
                while i<count and not stop.is_set():
                    p,items=newer(url,last,deadline)
                    for s in items:
                        if i>=count or stop.is_set():break
                        if time.monotonic()>=deadline:raise TimeoutError("session limit")
                        last=s.seq;src=private/f"source-{i}.ts";dst=private/f"dub-{i}.ts"
                        src.write_bytes(get(s.url,12_000_000,deadline))
                        v,a=probe(src)
                        if abs(float(v["duration"])-s.duration)>.3:raise Unsupported("source duration mismatch")
                        arrival=time.monotonic()
                        cutoff=arrival+5
                        def task(src,dst,slot):
                            data=worker.run(src,dst,slot,domain)
                            return data,time.monotonic()
                        with lock:
                            pending.difference_update({f for f in pending if f.done()})
                            f=pool.submit(task,src,dst,s.duration) if len(pending)<2 else None
                            if f is not None:pending.add(f)
                        try:q.put((i,s,src,dst,cutoff,f),timeout=1)
                        except queue.Full:raise RuntimeError("publish queue full")
                        i+=1
            except Exception as e:error.append(type(e).__name__)
            finally:
                while not stop.is_set():
                    try:q.put(None,timeout=.2);break
                    except queue.Full:continue
        t=threading.Thread(target=producer,daemon=True);t.start()
        try:
            while not stop.is_set():
                try:item=q.get(timeout=.2)
                except queue.Empty:continue
                if item is None:break
                i,s,src,dst,cutoff,f=item
                mode,reason,data=select(f,cutoff,lambda:verify(src,dst,s.duration))
                if stop.wait(max(0,cutoff-time.monotonic())):break
                target=public/f"seg-{i}.ts";tmp=target.with_suffix(".tmp")
                shutil.copyfile(dst if mode=="dub" else src,tmp);os.replace(tmp,target)
                row={"index":i,"duration":s.duration,"mode":mode,"reason":reason}
                if data:row["compute_seconds"]=round(data["compute_seconds"],3)
                rows.append(row);atomic(public/"live.m3u8",playlist(rows));save("playing")
                print("PART",json.dumps(row),flush=True)
        finally:
            stop.set();t.join(timeout=20);pool.shutdown(wait=True,cancel_futures=True)
            if t.is_alive():raise RuntimeError("producer shutdown timeout")
        if rows:atomic(public/"live.m3u8",playlist(rows,True))
        save("finished" if not error else "source-ended",error[0] if error else None)
    except Exception as e:
        if rows:atomic(public/"live.m3u8",playlist(rows,True))
        save("failed",type(e).__name__);print("SESSION_FAILED",type(e).__name__,flush=True)
