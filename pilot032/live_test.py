"""One bounded real-source session. Process only newly observed live segments.
Third-party media/transcripts stay in a temporary directory, never CI artifacts.
"""
from pathlib import Path
import concurrent.futures as cf, tempfile, subprocess, json, time, shutil, math,sys
from ingest import initial,newer,get,Denied,Unsupported
from live_worker import Worker
OUT=Path("pilot032-evidence");OUT.mkdir(exist_ok=True)
def probe(path):
    d=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-of","json",str(path)],timeout=12))
    v=next((x for x in d["streams"] if x["codec_type"]=="video"),None)
    a=next((x for x in d["streams"] if x["codec_type"]=="audio"),None)
    if not v or not a or v["codec_name"]!="h264" or a["codec_name"]!="aac":raise Unsupported("requires H264 AAC")
    return v,a
def digest(path,kind):
    return subprocess.check_output(["ffmpeg","-nostdin","-v","error","-i",str(path),"-map","0:"+kind+":0","-f","hash","-hash","sha256","-"],timeout=15).strip()
def main():
    rows=[];observed=[];result="unknown"
    def save():
        r={"result":result,"observed_sequences":observed,"rows":rows,"scope":"new live segments, no media export, not end-to-end viewer latency"}
        (OUT/"summary.json").write_text(json.dumps(r,indent=2))
        print("LIVE_DUB_STATUS",json.dumps(r),flush=True)
    try:
        worker=Worker()
        with tempfile.TemporaryDirectory(prefix="sefaxtv-live-") as td,cf.ThreadPoolExecutor(max_workers=1) as pool:
            root=Path(td);deadline=time.monotonic()+65
            url,p=initial(deadline);last=p.items[-1].seq
            observed.append(last)
            jobs=[]
            # Only future segments, no startup cache. One producer + max two jobs.
            while len(jobs)<3:
                p,items=newer(url,last,deadline)
                for seg in items:
                    if len(jobs)>=3:break
                    if time.monotonic()>=deadline:raise TimeoutError("session")
                    last=seg.seq;observed.append(last)
                    src=root/f"source-{last}.ts";target=root/f"dub-{last}.ts"
                    src.write_bytes(get(seg.url,12_000_000,deadline))
                    v,a=probe(src)
                    if abs(float(v["duration"])-seg.duration)>.3:raise Unsupported("source duration mismatch")
                    arrival=time.monotonic()
                    outstanding=sum(not f.done() for _,_,_,_,f in jobs if f is not None)
                    def task(s,t,dur):
                        data=worker.run(s,t,dur,"general")
                        return data,time.monotonic()
                    future=pool.submit(task,src,target,seg.duration) if outstanding<2 else None
                    jobs.append((seg,src,target,arrival,future))
            for seg,src,target,arrival,future in jobs:
                # Technical deadline from segment acquisition, not broadcaster capture time.
                cutoff=arrival+5;mode="original";reason="queue-full" if future is None else "deadline"
                row={"seq":seg.seq,"source_seconds":seg.duration,"mode":mode,"reason":reason}
                if future is not None:
                    try:
                        data,finish=future.result(timeout=max(0,cutoff-time.monotonic()))
                        if finish<=cutoff:
                            v,a=probe(target)
                            offset=abs(float(v["start_time"])-float(a["start_time"]))
                            delta=abs(float(v["duration"])-float(a["duration"]))
                            if offset>.10 or delta>.15 or digest(src,"v")!=digest(target,"v") or digest(src,"a")==digest(target,"a"):
                                raise ValueError("mux verification")
                            row.update(mode="dub",reason="verified",compute_seconds=data["compute_seconds"],acquisition_to_ready_s=finish-arrival,av_start_delta_s=offset,av_duration_delta_s=delta,asr_words=len(data["transcript"].split()),translation_words=len(data["translation"].split()))
                    except cf.TimeoutError:future.cancel()
                    except Exception as exc:row["reason"]=type(exc).__name__
                rows.append(row)
            result="live-segment-dub-pass" if len(rows)==3 and len(set(observed))==4 and sum(r["mode"]=="dub" for r in rows)>=2 else "insufficient-dub-evidence"
    except Exception as exc:
        result="source-or-processing-failed"
        rows.append({"error":type(exc).__name__,"detail":str(exc)[:120] if isinstance(exc,(Denied,Unsupported)) else ""})
    save()
    return 0 if result=="live-segment-dub-pass" else 2
if __name__=="__main__":sys.exit(main())
