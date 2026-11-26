"""0.30 model stack, actual PCM extracted from an owned video segment."""
from pathlib import Path
import sys,subprocess,wave,time,struct
import torch
from faster_whisper import WhisperModel
from huggingface_hub import hf_hub_download
from piper import PiperVoice
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"pilot029"/"dub"))
from engine import Translator
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"pilot030"))
from context import normalize
REV="e96841a85b3d633fbeb735addfdd73c2bdf091bb"
VOICE="tr/tr_TR/fahrettin/medium/tr_TR-fahrettin-medium.onnx"
RATE=22050
class Worker:
    def __init__(self):
        torch.set_num_threads(2);torch.set_num_interop_threads(1)
        onnx=hf_hub_download("rhasspy/piper-voices",VOICE,revision=REV)
        config=hf_hub_download("rhasspy/piper-voices",VOICE+".json",revision=REV)
        self.voice=PiperVoice.load(onnx,config_path=config)
        self.asr=WhisperModel("small.en",device="cpu",compute_type="int8",cpu_threads=2)
        self.mt=Translator("opus")
    def run(self,source,out,slot,domain):
        started=time.monotonic()
        wav=out.with_suffix(".en.wav")
        subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-i",str(source),"-vn","-ac","1","-ar",str(RATE),str(wav)],check=True,timeout=10)
        segments,_=self.asr.transcribe(str(wav),language="en",beam_size=5,condition_on_previous_text=False)
        text=" ".join(s.text.strip() for s in segments).strip()
        if not text:raise ValueError("no speech")
        tr=self.mt.translate(normalize(text,domain))
        if not tr.strip():raise ValueError("no translation")
        dub=out.with_suffix(".tr.wav")
        with wave.open(str(dub),"wb") as w:self.voice.synthesize_wav(tr,w)
        with wave.open(str(dub),"rb") as w:
            if w.getframerate()!=RATE or w.getsampwidth()!=2 or w.getnchannels()!=1:raise ValueError("bad wave format")
            data=w.readframes(w.getnframes())
        if not data or max(map(abs,struct.unpack("<"+"h"*(len(data)//2),data)))<=100:raise ValueError("silent dub")
        duration=len(data)/(2*RATE);speed=max(1,duration/(slot-.10))
        if speed>1.25:raise ValueError("dub too long")
        fitted=out.with_suffix(".fit.wav")
        subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-i",str(dub),"-af",f"atempo={speed:.8f}","-ar",str(RATE),"-ac","1",str(fitted)],check=True,timeout=10)
        with wave.open(str(fitted),"rb") as w:
            if w.getnframes()/w.getframerate()>slot:raise ValueError("fit too long")
        # Copy the original H.264 pictures; pad only the audio tail. No speech truncation.
        subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-i",str(source),"-i",str(fitted),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-ar","48000","-ac","1","-b:a","96k","-af","apad","-t",str(slot),"-muxdelay","0","-muxpreload","0","-f","mpegts",str(out)],check=True,timeout=10)
        return {"transcript":text,"translation":tr,"dub_seconds":duration,"speed":speed,"compute_seconds":time.monotonic()-started}
