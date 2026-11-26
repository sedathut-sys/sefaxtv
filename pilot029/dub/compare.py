"""Compare independent translation models on text and actual synthesized EN audio.
No reference text or expected answer enters inference on the audio path.
"""
import gc,json,math,re,subprocess,time,wave,struct,sys
from pathlib import Path
import torch
from faster_whisper import WhisperModel
from engine import Translator
torch.set_num_threads(2)
torch.set_num_interop_threads(1)
root=Path(__file__).resolve().parent
out=Path("pilot029-dub-results");out.mkdir(exist_ok=True)
cases=json.loads((root/"cases.json").read_text(encoding="utf-8"))
report={"cases":cases,"asr":[],"models":[],"selection":None}
def save():
    (out/"summary.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
def norm(s):
    return re.findall(r"\w+",re.sub(r"\b7\b","seven",re.sub(r"\b2\b","two",s.casefold())))
def wer(ref,hyp):
    a,b=norm(ref),norm(hyp);prev=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        row=[i]
        for j,y in enumerate(b,1):row.append(min(row[-1]+1,prev[j]+1,prev[j-1]+(x!=y)))
        prev=row
    return prev[-1]/max(1,len(a))
def anchor(text,case):
    t=text.lower().replace("i\u0307","i")
    def found(x):
        return bool(re.search(r"(?<!\w)"+re.escape(x)+r"(?!\w)",t)) if x.isdigit() else x in t
    missing=[g for g in case["required"] if not any(found(x) for x in g)]
    forbidden=[x for x in case["forbidden"] if found(x)]
    return {"pass":bool(t.strip()) and not missing and not forbidden,"missing":missing,"forbidden":forbidden}
def synth(text,path,lang):
    subprocess.run(["espeak-ng","-v",lang,"-s","145","-w",str(path),"--stdin"],input=text,text=True,check=True,timeout=30)
def wavecheck(path):
    with wave.open(str(path),"rb") as w:
        if w.getnchannels()!=1 or w.getsampwidth()!=2:raise ValueError("bad format")
        n=w.getnframes();rate=w.getframerate()
        a=struct.unpack("<"+"h"*n,w.readframes(n))
        return n/rate, bool(a) and max(map(abs,a))>100
asr=WhisperModel("base.en",device="cpu",compute_type="int8",cpu_threads=2)
for i,case in enumerate(cases,1):
    src=out/f"en-{i}.wav";synth(case["en"],src,"en-us")
    seconds,_=wavecheck(src);t=time.monotonic()
    segments,_=asr.transcribe(str(src),language="en",beam_size=3,condition_on_previous_text=False)
    transcript=" ".join(s.text.strip() for s in segments).strip()
    row={"id":i,"transcript":transcript,"source_seconds":seconds,"asr_seconds":time.monotonic()-t,"wer":wer(case["en"],transcript)}
    report["asr"].append(row);print("ASR",json.dumps(row,ensure_ascii=False),flush=True)
save();del asr;gc.collect()
for kind in ("opus","m2m"):
    rows=[]
    try:
        t=time.monotonic();model=Translator(kind);load=time.monotonic()-t
        for i,(case,a) in enumerate(zip(cases,report["asr"]),1):
            # Reference translation is isolated, not fed to the audio translation.
            ref_tr=model.translate(case["en"])
            t=time.monotonic();tr=model.translate(a["transcript"]);mt=time.monotonic()-t
            target=out/f"{kind}-tr-{i}.wav";t=time.monotonic();synth(tr,target,"tr");tts=time.monotonic()-t
            seconds,signal=wavecheck(target);rtf=(a["asr_seconds"]+mt+tts)/a["source_seconds"]
            row={"id":i,"reference_translation":ref_tr,"reference_quality":anchor(ref_tr,case),"audio_translation":tr,"audio_quality":anchor(tr,case),"wave_pass":signal and seconds>.5,"dub_seconds":seconds,"mt_seconds":mt,"tts_seconds":tts,"rtf":rtf}
            rows.append(row);print("MT_RESULT",kind,json.dumps(row,ensure_ascii=False),flush=True)
        n=len(cases);passed=sum(r["audio_quality"]["pass"] for r in rows)
        eligible=len(rows)==n and all(r["reference_quality"]["pass"] and r["audio_quality"]["pass"] and r["wave_pass"] and r["rtf"]<=1 and a["wer"]<=.35 for r,a in zip(rows,report["asr"]))
        report["models"].append({"name":kind,"rows":rows,"load_seconds":load,"audio_anchors_pass":passed,"mean_rtf":sum(r["rtf"] for r in rows)/n,"eligible":eligible})
        del model
    except Exception as exc:
        report["models"].append({"name":kind,"rows":rows,"eligible":False,"error":type(exc).__name__})
        print("MODEL_ERROR",kind,type(exc).__name__,str(exc)[:300],flush=True)
    gc.collect();save()
eligible=[m for m in report["models"] if m["eligible"]]
if eligible:report["selection"]=min(eligible,key=lambda m:m["mean_rtf"])["name"]
save()
print("MT_SELECTION",json.dumps({"selection":report["selection"],"models":[{k:v for k,v in m.items() if k!="rows"} for m in report["models"]]},ensure_ascii=False),flush=True)
if not eligible:sys.exit(2)
print("PASS nine synthetic cases, semantic anchors and real WAV, compute RTF gate; no live or human quality acceptance")
