"""Targeted dubbing quality and local replay: actual ASR, OPUS and Piper outputs.
No expected text is passed to inference, no user microphone, no external inference API.
"""
import html,json,re,struct,subprocess,sys,time,wave
from pathlib import Path
import torch
from faster_whisper import WhisperModel
from huggingface_hub import hf_hub_download
from piper import PiperVoice
from context import normalize
from timing import plan
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"pilot029"/"dub"))
from engine import Translator
torch.set_num_threads(2);torch.set_num_interop_threads(1)
OUT=Path("pilot030-results");OUT.mkdir(exist_ok=True)
RATE=22050
CASES=[
 ("goalkeeper","football","The goalkeeper saved the penalty in the final minute.",[["kaleci"],["penaltı"],["son dakika"]],[]),
 ("halftime","football","The player scored a goal just before halftime.",[["gol"],["ilk yarı","devre"],["önce","kala","bitmeden"]],["devre arasında","yarım saat"]),
 ("away","football","The visiting team equalized in the second half.",[["deplasman","konuk","misafir"],["eşit","beraber"],["ikinci yarı"]],["ziyaretçi","ziyaret eden"]),
 ("purpose","general","Our goal is to reduce the cost of electricity.",[["hedef","amaç","amac"],["elektrik"],["maliyet","masraf","fiyat"]],["gol"]),
 ("bill","general","There is a penalty for late payment of the bill.",[["ceza","gecikme faizi"],["ödeme","öden"],["fatura","hesap"]],["penaltı"]),
 ("new-football","football","The away team scored just before half-time.",[["deplasman","konuk","misafir"],["gol"],["önce","kala","bitmeden"]],["devre arasında","yarım saat"]),
 ("new-general","general","The goal of this project is to save energy.",[["hedef","amaç","amac"],["enerji"],["tasarruf","koru","biriktir"]],["gol"])
]
HUMAN=("human","general","And so my fellow Americans ask not what your country can do for you, ask what you can do for your country.",[["ülke"],["sizin","senin","siz","sen"],["sor","sorma"]],[])
VOICE_REV="e96841a85b3d633fbeb735addfdd73c2bdf091bb"
VOICE_PATH="tr/tr_TR/fahrettin/medium/tr_TR-fahrettin-medium.onnx"
def espeak(text,path,lang):
    subprocess.run(["espeak-ng","-v",lang,"-s","145","-w",str(path),"--stdin"],input=text,text=True,check=True,timeout=30)
def pcm(path):
    with wave.open(str(path),"rb") as w:
        if w.getnchannels()!=1 or w.getsampwidth()!=2 or w.getframerate()!=RATE:raise ValueError("unexpected WAV format")
        return w.readframes(w.getnframes())
def seconds(buf):return len(buf)/(RATE*2)
def signal(buf):
    return bool(buf) and max(map(abs,struct.unpack("<"+"h"*(len(buf)//2),buf)))>100
def silence(t):return b"\0"*(round(t*RATE)*2)
def write(path,buf):
    with wave.open(str(path),"wb") as w:
        w.setparams((1,2,RATE,0,"NONE","not compressed"));w.writeframes(buf)
def norm(s):
    return re.findall(r"\w+",s.casefold())
def wer(ref,hyp):
    a,b=norm(ref),norm(hyp);v=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        r=[i]
        for j,y in enumerate(b,1):r.append(min(r[-1]+1,v[j]+1,v[j-1]+(x!=y)))
        v=r
    return v[-1]/max(1,len(a))
def quality(text,required,forbidden):
    t=text.lower().replace("i\u0307","i")
    missing=[g for g in required if not any(x in t for x in g)]
    banned=[x for x in forbidden if x in t]
    return {"pass":bool(t.strip()) and not missing and not banned,"missing":missing,"forbidden":banned}
def fit(path,speed):
    if speed<=1:return pcm(path)
    data=subprocess.check_output(["ffmpeg","-v","error","-i",str(path),"-af",f"atempo={speed:.8f}","-ac","1","-ar",str(RATE),"-f","s16le","-"],timeout=20)
    return data
# Downloads are initialization only; all actual inference is local.
onnx=hf_hub_download("rhasspy/piper-voices",VOICE_PATH,revision=VOICE_REV)
config=hf_hub_download("rhasspy/piper-voices",VOICE_PATH+".json",revision=VOICE_REV)
voice=PiperVoice.load(onnx,config_path=config)
asr=WhisperModel("small.en",device="cpu",compute_type="int8",cpu_threads=2)
mt=Translator("opus")
rows=[];original=b"";replay=b"";cursor=0.0;worker_free=0.0
def save():
    (OUT/"summary.json").write_text(json.dumps({"rows":rows,"delay_seconds":6,"note":"file replay, not live TV"},ensure_ascii=False,indent=2),encoding="utf-8")
for ident,domain,reference,req,bad in CASES+[HUMAN]:
    src=OUT/f"{ident}-en.wav";piper=OUT/f"{ident}-piper.wav";legacy=OUT/f"{ident}-espeak.wav"
    if ident=="human":
        subprocess.run(["ffmpeg","-v","error","-i","pilot030/jfk.flac","-ac","1","-ar",str(RATE),str(src)],check=True,timeout=30)
    else:espeak(reference,src,"en-us")
    raw=pcm(src);dur=seconds(raw)
    t=time.monotonic()
    segments,_=asr.transcribe(str(src),language="en",beam_size=5,condition_on_previous_text=False)
    segments=list(segments);text=" ".join(s.text.strip() for s in segments).strip()
    asr_time=time.monotonic()-t
    if not text:raise RuntimeError("no recognized speech")
    t=time.monotonic();translation=mt.translate(normalize(text,domain));mt_time=time.monotonic()-t
    if not translation.strip():raise RuntimeError("no translation")
    t=time.monotonic()
    with wave.open(str(piper),"wb") as w:voice.synthesize_wav(translation,w)
    piper_time=time.monotonic()-t
    espeak(translation,legacy,"tr")
    dub=pcm(piper);legacy_pcm=pcm(legacy)
    if not signal(dub) or not signal(legacy_pcm):raise RuntimeError("silent synthesis")
    total=asr_time+mt_time+piper_time
    end=cursor+dur
    ready=max(end,worker_free)+total
    worker_free=ready
    p=plan(cursor,end,ready,seconds(dub))
    # Actual audio file replay: fixed delay, no overlapping source slots.
    # Signal length after atempo is checked; never cut the end of speech to fit.
    chunk=fit(piper,p["speed"]) if p["mode"]=="dub" else raw
    if len(chunk)>len(raw):p["mode"]="original";p["speed"]=1.0;chunk=raw
    chunk+=b"\0"*(len(raw)-len(chunk))
    original+=raw+silence(.5);replay+=chunk+silence(.5)
    row={"id":ident,"domain":domain,"reference":reference,"transcript":text,"translation":translation,"wer":wer(reference,text),"quality":quality(translation,req,bad),"source_seconds":dur,"piper_seconds":seconds(dub),"asr_seconds":asr_time,"mt_seconds":mt_time,"tts_seconds":piper_time,"compute_seconds":total,"rtf":total/dur,"simulated_ready":ready,"schedule":p,"source_type":"archival human speech" if ident=="human" else "synthetic English","wave_pass":True}
    rows.append(row);save();print("DUB_SAMPLE",json.dumps(row,ensure_ascii=False),flush=True)
    cursor=end+.5
write(OUT/"original-sequence.wav",original)
write(OUT/"delayed-replay.wav",silence(6)+replay)
parts=['<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SeFaTV 0.30 ses karşılaştırması</title><style>body{font:16px system-ui;max-width:850px;margin:24px auto;padding:16px;background:#101827;color:#eee}audio{width:100%}section{border-top:1px solid #445;padding:12px 0}</style><h1>Türkçe dublaj ses karşılaştırması</h1><p>Dosya bazlı deney; gerçek canlı TV değil. Çeviri ve doğal ses kalite değerlendirmesi henüz yapılmadı. Orijinal ile eSpeak ve Piper aynı tanınan konuşmadan üretilmiştir.</p>']
for r in rows:
    ident=r["id"]
    parts.append('<section><h2>'+html.escape(ident)+'</h2><p>İngilizce tanıma: '+html.escape(r["transcript"])+'</p><p>Türkçe çeviri: '+html.escape(r["translation"])+'</p>')
    for label,suffix in [("Orijinal","en"),("Eski ses (eSpeak)","espeak"),("Yeni ses (Piper)","piper")]:
        parts.append('<p>'+label+'</p><audio controls preload="none" src="'+ident+'-'+suffix+'.wav"></audio>')
    parts.append('</section>')
parts.append('<h2>Sıralı oynatma deneyi</h2><p>Orijinal ses</p><audio controls preload="none" src="original-sequence.wav"></audio><p>6 saniye başlangıç tamponlu kayıt; sığmayan veya geç kalan parçada orijinal ses kullanılır.</p><audio controls preload="none" src="delayed-replay.wav"></audio><p>İnsan konuşması: OpenAI Whisper jfk.flac test kaydı (JFK 1961 konuşması); yapay Türkçe ses orijinal konuşmacının sesi değildir.</p></html>')
(OUT/"index.html").write_text("".join(parts),encoding="utf-8")
save()
print("DUB_SUMMARY",json.dumps({"samples":len(rows),"anchors_pass":sum(r["quality"]["pass"] for r in rows),"asr_wer_pass":sum(r["wer"]<=.35 for r in rows),"wave_pass":sum(r["wave_pass"] for r in rows),"rtf_mean":sum(r["rtf"] for r in rows)/len(rows),"replay_dub_slots":sum(r["schedule"]["mode"]=="dub" for r in rows)},ensure_ascii=False),flush=True)
if not all(r["quality"]["pass"] and r["wer"]<=.35 and r["rtf"]<=1 for r in rows):sys.exit(2)
print("PASS targeted file-based quality gate; live TV and human listening not validated")
