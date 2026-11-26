"""Real speech recognition -> translation -> WAV on owned synthetic input."""
from pathlib import Path
import json,re,wave,struct
from engine import setup_models,synth,dub
out=Path("pilot027-dub-results");out.mkdir(exist_ok=True)
model=setup_models()
reports=[]
for i,text in enumerate(["The football match starts at seven o'clock.","The weather is cold today. Please close the window."]):
    src=out/f"english-{i+1}.wav";dst=out/f"turkish-{i+1}.wav"
    synth(text,src,"en-us")
    r=dub(model,src,dst);r["reference"]=text
    with wave.open(str(dst),"rb") as w:
        assert w.getsampwidth()==2 and w.getnchannels()==1
        samples=struct.unpack("<"+"h"*w.getnframes(),w.readframes(w.getnframes()))
        assert max(map(abs,samples))>100
    assert r["dub_seconds"]>0.5
    assert r["transcript"] and r["translation"]
    reports.append(r)
    print("DUB_RESULT",json.dumps(r,ensure_ascii=False),flush=True)
(out/"summary.json").write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding="utf-8")
# Minimal semantic anchor gates; not human-level translation or naturalness evaluation.
assert "football" in reports[0]["transcript"].lower() and "futbol" in reports[0]["translation"].lower()
assert "window" in reports[1]["transcript"].lower() and "pencere" in reports[1]["translation"].lower()
print("PASS actual local ASR, EN-TR translation, Turkish waveform and basic semantic anchors",flush=True)
