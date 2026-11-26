import concurrent.futures as cf, threading, tempfile, time, urllib.request, urllib.error, json
from pathlib import Path
from ingest import allowed,parse,Denied,Unsupported
import ingest
from session import select,playlist
from local_server import serve
ingest.HOST=("publisher.example",443);ingest.SOURCE="https://publisher.example/live.m3u8"
p="#EXTM3U\n#EXT-X-TARGETDURATION:5\n#EXT-X-MEDIA-SEQUENCE:8\n#EXTINF:4.8,\nseg8.ts\n"
assert parse(ingest.SOURCE,p).items[0].seq==8
for u in ("http://publisher.example/s.ts","https://evil.example/s.ts","https://publisher.example/s.ts?token=x","https://127.0.0.1/s.ts"):
    try:allowed(ingest.SOURCE,u)
    except Denied:continue
    raise AssertionError(u)
f=cf.Future();f.set_result(({"compute_seconds":1},time.monotonic()))
assert select(f,time.monotonic()+1,lambda:True)[0]=="dub"
assert select(f,time.monotonic()-1,lambda:True)[0]=="original"
assert select(f,time.monotonic()+1,lambda:False)[0]=="original"
assert select(None,time.monotonic()+1,lambda:True)[0]=="original"
pl=playlist([{"duration":4.8},{"duration":5.1}],True)
assert "#EXT-X-TARGETDURATION:6" in pl and "#EXT-X-DISCONTINUITY" in pl and "#EXT-X-ENDLIST" in pl
with tempfile.TemporaryDirectory() as td:
    root=Path(td);(root/"index.html").write_text("test");(root/"secret.txt").write_text("secret")
    stop=threading.Event();s,url=serve(root,stop)
    threading.Thread(target=s.serve_forever,daemon=True).start()
    try:
        assert urllib.request.urlopen(url).read()==b"test"
        for path in ("secret.txt","../secret.txt","%2e%2e/secret.txt"):
            try:urllib.request.urlopen(url+path)
            except urllib.error.HTTPError as e:assert e.code==404
            else:raise AssertionError("private path")
        try:urllib.request.urlopen(urllib.request.Request(url+"stop",method="POST"))
        except urllib.error.HTTPError as e:assert e.code==403
        else:raise AssertionError("cross origin stop")
        origin=url.split("/",3)[0]+"//"+url.split("/",3)[2]
        assert urllib.request.urlopen(urllib.request.Request(url+"stop",method="POST",headers={"Origin":origin})).status==204
        assert stop.is_set()
    finally:s.shutdown();s.server_close()
print("PASS source-origin restrictions, deadline selection, playlist, loopback server isolation and stop")
