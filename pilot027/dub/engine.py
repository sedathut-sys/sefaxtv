"""Local, file-based EN->TR prototype. No service API, no voice imitation."""
import time, subprocess, wave
from pathlib import Path
from faster_whisper import WhisperModel
from argostranslate import package, translate
def setup_models():
    package.update_package_index()
    candidates=[p for p in package.get_available_packages() if p.from_code=="en" and p.to_code=="tr" and p.package_version=="1.5"]
    if len(candidates)!=1: raise RuntimeError("Expected EN-TR 1.5 model unavailable")
    package.install_from_path(candidates[0].download())
    return WhisperModel("tiny.en",device="cpu",compute_type="int8",cpu_threads=2)
def duration(path):
    with wave.open(str(path),"rb") as w:return w.getnframes()/w.getframerate()
def synth(text,path,lang):
    subprocess.run(["espeak-ng","-v",lang,"-s","145","-w",str(path),"--stdin"],input=text,text=True,check=True,timeout=30)
def dub(model,source,target):
    start=time.monotonic()
    segments,info=model.transcribe(str(source),language="en",beam_size=3,condition_on_previous_text=False)
    transcript=" ".join(s.text.strip() for s in segments).strip()
    asr=time.monotonic()-start
    if not transcript:raise RuntimeError("No recognized speech")
    tr=translate.translate(transcript,"en","tr").strip()
    mt=time.monotonic()-start-asr
    if not tr or tr.casefold()==transcript.casefold():raise RuntimeError("Missing translation")
    synth(tr,target,"tr")
    tts=time.monotonic()-start-asr-mt
    total=time.monotonic()-start
    original=duration(source);dubbed=duration(target)
    return {"transcript":transcript,"translation":tr,"source_seconds":original,"dub_seconds":dubbed,"asr_seconds":asr,"translation_seconds":mt,"tts_seconds":tts,"total_seconds":total,"rtf":total/original}
