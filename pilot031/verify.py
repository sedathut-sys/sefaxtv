"""Verify actual muxed outputs: source video hash, audio choice, packet timeline."""
import hashlib,json,math,subprocess
from pathlib import Path
def streamhash(path,kind):
    return subprocess.check_output(["ffmpeg","-v","error","-i",str(path),"-map",f"0:{kind}:0","-f","hash","-hash","sha256","-"],timeout=20).decode().strip()
def probe(path):
    d=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-of","json",str(path)],timeout=15))
    v=next(s for s in d["streams"] if s["codec_type"]=="video")
    a=next(s for s in d["streams"] if s["codec_type"]=="audio")
    assert v["codec_name"]=="h264" and a["codec_name"]=="aac"
    offset=abs(float(v["start_time"])-float(a["start_time"]))
    duration_delta=abs(float(v["duration"])-float(a["duration"]))
    assert offset<=.10 and duration_delta<=.15,(offset,duration_delta)
    return offset,duration_delta
def verify(root):
    root=Path(root);d=json.loads((root/"summary.json").read_text());rows=d["rows"];assert len(rows)==5
    assert rows[-1]["mode"]=="original" and rows[-1]["reason"]=="deadline"
    assert sum(r["mode"]=="dub" for r in rows)>=2
    checks=[]
    for r in rows:
        i=r["index"];dst=root/"public"/f"seg-{i}.ts";src=root/"private"/f"orig-{i}.ts"
        assert -.05<=r["publish_lateness_s"]<=.35
        assert streamhash(dst,"v")==streamhash(src,"v"),i
        if r["mode"]=="original":assert dst.read_bytes()==src.read_bytes()
        else:
            assert streamhash(dst,"a")!=streamhash(src,"a")
            assert r["data"]["translation"].strip() and r["data"]["speed"]<=1.25
        offset,delta=probe(dst)
        checks.append({"index":i,"mode":r["mode"],"av_start_delta_s":offset,"av_duration_delta_s":delta})
    assert "#EXT-X-ENDLIST" in (root/"public"/"live.m3u8").read_text()
    print("MUX_RESULT",json.dumps(checks),flush=True)
    return checks
