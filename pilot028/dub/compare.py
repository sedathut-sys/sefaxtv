"""Actual model comparison on identical, owned English waveforms.
Reference text is never supplied to ASR or the end-to-end translation.
"""
import gc,json,re,time,wave,struct
from pathlib import Path
from faster_whisper import WhisperModel
from argostranslate import package,translate
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"pilot027"/"dub"))
from engine import dub,synth,duration
OUT=Path("pilot028-dub-results");OUT.mkdir(exist_ok=True)
CASES=[
 {"text":"The football match starts at seven o'clock.","en":[["football"],["seven","7"]],"tr":[["futbol"],["yedi","7"]]},
 {"text":"The weather is cold today. Please close the window.","en":[["cold"],["window"]],"tr":[["soğuk"],["pencere"]]},
 {"text":"The goalkeeper saved the penalty in the final minute.","en":[["goalkeeper","goal keeper"],["penalty"]],"tr":[["kaleci"],["penaltı"]]},
 {"text":"The home team won the match by two goals.","en":[["home team"],["two","2"],["goals"]],"tr":[["ev sahibi"],["iki","2"],["gol"]]}
]
def norm(s):
    s=s.casefold()
    s=re.sub(r"\b7\b","seven",s);s=re.sub(r"\b2\b","two",s)
    return re.findall(r"[\w]+",s)
def wer(ref,hyp):
    a,b=norm(ref),norm(hyp);prev=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        row=[i]
        for j,y in enumerate(b,1):row.append(min(row[-1]+1,prev[j]+1,prev[j-1]+(x!=y)))
        prev=row
    return prev[-1]/max(1,len(a))
def anchors(text,groups):
    s=text.casefold()
    return all(any((re.search(r"(?<!\w)"+re.escape(x)+r"(?!\w)",s) if x.isdigit() else x in s) for x in g) for g in groups)
def nonempty_wave(path):
    with wave.open(str(path),"rb") as w:
        if w.getsampwidth()!=2 or w.getnchannels()!=1:return False
        data=w.readframes(w.getnframes())
        return bool(data) and max(map(abs,struct.unpack("<"+"h"*(len(data)//2),data)))>100 and duration(path)>.5
def save(obj):
    (OUT/"summary.json").write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
package.update_package_index()
candidates=[p for p in package.get_available_packages() if p.from_code=="en" and p.to_code=="tr" and p.package_version=="1.5"]
if len(candidates)!=1:raise RuntimeError("Expected EN-TR 1.5 model unavailable")
package.install_from_path(candidates[0].download())
report={"reference_translation":[],"models":[],"selection":None}
for i,c in enumerate(CASES):
    src=OUT/f"english-{i+1}.wav";synth(c["text"],src,"en-us")
    tr=translate.translate(c["text"],"en","tr")
    report["reference_translation"].append({"reference":c["text"],"translation":tr,"anchors_pass":anchors(tr,c["tr"])})
save(report)
for name in ("tiny.en","base.en","small.en"):
    t=time.monotonic()
    model=WhisperModel(name,device="cpu",compute_type="int8",cpu_threads=2)
    load_seconds=time.monotonic()-t
    rows=[]
    for i,c in enumerate(CASES):
        src=OUT/f"english-{i+1}.wav";dst=OUT/f"{name}-turkish-{i+1}.wav"
        try:
            r=dub(model,src,dst)
            r.update(reference=c["text"],wer=wer(c["text"],r["transcript"]),asr_anchors=anchors(r["transcript"],c["en"]),translation_anchors=anchors(r["translation"],c["tr"]),wave_pass=nonempty_wave(dst))
        except Exception as exc:
            r={"reference":c["text"],"error":type(exc).__name__,"asr_anchors":False,"translation_anchors":False,"wave_pass":False}
        rows.append(r);print("DUB_COMPARE",name,json.dumps(r,ensure_ascii=False),flush=True)
    complete=all("wer" in r for r in rows)
    eligible=complete and all(r["asr_anchors"] and r["translation_anchors"] and r["wave_pass"] and r["wer"]<=.35 and r["rtf"]<=1 for r in rows)
    report["models"].append({"name":name,"load_seconds":load_seconds,"rows":rows,"mean_wer":sum(r["wer"] for r in rows)/len(rows) if complete else None,"mean_rtf":sum(r["rtf"] for r in rows)/len(rows) if complete else None,"eligible":eligible})
    save(report);del model;gc.collect()
eligible=[m for m in report["models"] if m["eligible"]]
if eligible:
    best=min(eligible,key=lambda x:(x["mean_wer"],x["mean_rtf"]))
    report["selection"]=best["name"]
save(report)
print("MODEL_SELECTION",json.dumps({"selection":report["selection"],"scores":[{k:v for k,v in m.items() if k!="rows"} for m in report["models"]],"reference_translation":report["reference_translation"]},ensure_ascii=False),flush=True)
if not eligible:raise SystemExit(2)
print("PASS limited synthetic dubbing quality and compute speed gate; not live or naturalness acceptance")
