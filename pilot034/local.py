"""Private loopback capture and progressive dubbing. No third-party network fetch."""
import argparse,concurrent.futures as cf,http.server,json,math,os,queue,re,secrets,shutil,subprocess,tempfile,threading,time,webbrowser,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/"pilot033"))
from session import atomic,playlist,probe,select,verify
MAX_BYTES=8_000_000;MAX_CLIPS=6
class Session:
    def __init__(self,root,domain):
        self.root=Path(root);self.public=self.root/"public";self.private=self.root/"private"
        self.public.mkdir();self.private.mkdir();self.domain=domain
        self.q=queue.Queue(maxsize=2);self.lock=threading.Lock();self.stop=threading.Event();self.done=threading.Event()
        self.finished=False;self.next=0;self.rows=[];self.ready=False;self.status="loading";self.save()
    def save(self,error=None):
        atomic(self.public/"status.json",json.dumps({"state":self.status,"ready":self.ready,"received":self.next,"rows":self.rows,"error":error},ensure_ascii=False))
    def submit(self,i,data):
        with self.lock:
            if not self.ready or self.stop.is_set() or self.finished or i!=self.next or i>=MAX_CLIPS:return False
            if not 0<len(data)<=MAX_BYTES or data[:4]!=b"\x1a\x45\xdf\xa3":return False
            try:self.q.put_nowait((i,data,time.monotonic()))
            except queue.Full:return False
            self.next+=1;return True
    def finish(self):
        with self.lock:self.finished=True
    def run(self):
        try:
            sys.path.insert(0,str(ROOT.parent/"pilot032"))
            from live_worker import Worker
            worker=Worker()
            if self.stop.is_set():return
            self.ready=True;self.status="ready";self.save()
            idle=time.monotonic()+180
            while not self.stop.is_set():
                try:i,data,arrival=self.q.get(timeout=.2)
                except queue.Empty:
                    if self.finished or time.monotonic()>idle:break
                    continue
                idle=time.monotonic()+60
                webm=self.private/f"in-{i}.webm";src=self.private/f"src-{i}.ts";dst=self.private/f"dub-{i}.ts"
                webm.write_bytes(data)
                # Only local WebM with both tracks, fixed resource envelope; no external protocols.
                subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-protocol_whitelist","file,pipe","-f","matroska","-i",str(webm),"-map","0:v:0","-map","0:a:0","-vf","scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2,fps=25","-c:v","libx264","-preset","ultrafast","-pix_fmt","yuv420p","-g","125","-bf","0","-c:a","aac","-ar","48000","-ac","1","-b:a","96k","-t","6.4","-muxdelay","0","-muxpreload","0","-f","mpegts",str(src)],check=True,timeout=12)
                v,a=probe(src);slot=float(v["duration"])
                if not 3.8<=slot<=6.4 or abs(float(a["duration"])-slot)>.25:raise ValueError("capture-duration")
                cutoff=arrival+7;mode="original";reason="deadline";details=None
                if time.monotonic()<cutoff:
                    try:
                        d=worker.run(src,dst,slot,self.domain)
                        if time.monotonic()<=cutoff and verify(src,dst,slot) and time.monotonic()<=cutoff:
                            mode="dub";reason="ready";details=d
                    except Exception as e:reason=type(e).__name__
                if self.stop.is_set():break
                target=self.public/f"seg-{i}.ts";tmp=target.with_suffix(".tmp")
                shutil.copyfile(dst if mode=="dub" else src,tmp);os.replace(tmp,target)
                row={"index":i,"duration":slot,"mode":mode,"reason":reason,"receive_to_publish_s":time.monotonic()-arrival}
                if details:row["compute_seconds"]=details["compute_seconds"];row["translation"]=details["translation"]
                self.rows.append(row);self.status="playing";atomic(self.public/"live.m3u8",playlist(self.rows));self.save()
                print("CAPTURE_PART",json.dumps({k:v for k,v in row.items() if k!="translation"}),flush=True)
            if self.rows:atomic(self.public/"live.m3u8",playlist(self.rows,True))
            self.status="finished";self.ready=False;self.save()
        except Exception as exc:
            self.status="failed";self.ready=False
            if self.rows:atomic(self.public/"live.m3u8",playlist(self.rows,True))
            self.save(type(exc).__name__);print("CAPTURE_FAILED",type(exc).__name__,flush=True)
        finally:self.done.set()
def serve(s,fixture=False):
    token=secrets.token_urlsafe(24)
    class Handler(http.server.BaseHTTPRequestHandler):
        def setup(self):super().setup();self.connection.settimeout(10)
        def log_message(self,*args):pass
        def valid(self,post=False):
            host=f"127.0.0.1:{self.server.server_port}"
            return self.headers.get("Host")==host and (not post or self.headers.get("Origin")=="http://"+host)
        def path_name(self):
            prefix="/"+token+"/"
            if not self.path.startswith(prefix) or "?" in self.path or "#" in self.path:return None
            return self.path[len(prefix):] or "index.html"
        def do_GET(self):
            if not self.valid():self.send_error(403);return
            name=self.path_name()
            types={"index.html":"text/html; charset=utf-8","app.mjs":"text/javascript","capture.mjs":"text/javascript","hls.mjs":"text/javascript","status.json":"application/json","live.m3u8":"application/vnd.apple.mpegurl"}
            if fixture:types["fixture.wav"]="audio/wav"
            mime=types.get(name)
            if name and re.fullmatch(r"seg-[0-5]\.ts",name):mime="video/mp2t"
            if not mime:self.send_error(404);return
            try:data=(s.public/name).read_bytes()
            except OSError:self.send_error(404);return
            self.send_response(200);self.send_header("Content-Type",mime);self.send_header("Content-Length",str(len(data)))
            self.send_header("Cache-Control","no-store");self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Referrer-Policy","no-referrer")
            self.send_header("Content-Security-Policy","default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; connect-src 'self'; media-src 'self' blob:; worker-src 'self' blob:; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers();self.wfile.write(data)
        def do_POST(self):
            if not self.valid(True):self.send_error(403);return
            name=self.path_name()
            if name=="stop":s.stop.set();s.finish()
            elif name=="finish":s.finish()
            elif name and re.fullmatch(r"clip/[0-5]",name):
                if self.headers.get("Content-Type")!="video/webm" or self.headers.get("Transfer-Encoding"):self.send_error(415);return
                try:n=int(self.headers.get("Content-Length","0"))
                except ValueError:self.send_error(400);return
                if not 0<n<=MAX_BYTES:self.send_error(413);return
                try:data=self.rfile.read(n)
                except OSError:self.send_error(408);return
                if len(data)!=n or not s.submit(int(name[-1]),data):self.send_error(409);return
            else:self.send_error(404);return
            self.send_response(204);self.end_headers()
    server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
    return server,f"http://127.0.0.1:{server.server_port}/{token}/"
def assets(s):
    for n in ("index.html","app.mjs","capture.mjs","hls.mjs"):shutil.copyfile(ROOT/n,s.public/n)
def main():
    p=argparse.ArgumentParser();p.add_argument("--domain",choices=["general","football"],default="general");a=p.parse_args()
    if not all(shutil.which(x) for x in ("ffmpeg","ffprobe")):p.error("FFmpeg ve ffprobe PATH üzerinde gerekli")
    with tempfile.TemporaryDirectory(prefix="sefaxtv-tab-") as td:
        s=Session(td,a.domain);assets(s);server,url=serve(s)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        worker=threading.Thread(target=s.run);worker.start()
        print("Yerel test:",url,flush=True);webbrowser.open(url)
        try:
            while not s.done.wait(.3):pass
            # Keep the last playlist available until the user closes or 75 s passes.
            s.stop.wait(75)
        except KeyboardInterrupt:s.stop.set()
        finally:s.stop.set();worker.join();server.shutdown();server.server_close()
if __name__=="__main__":main()
