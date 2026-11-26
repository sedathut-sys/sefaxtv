from ingest import *
base=SOURCE
p="#EXTM3U\n#EXT-X-TARGETDURATION:5\n#EXT-X-MEDIA-SEQUENCE:8\n#EXTINF:4.8,\nseg8.ts\n#EXTINF:4.8,\nseg9.ts\n"
x=parse(base,p);assert [s.seq for s in x.items]==[8,9]
assert x.items[0].url.endswith("/seg8.ts")
assert master(base,"#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=1000000\nhi.m3u8\n#EXT-X-STREAM-INF:BANDWIDTH=300000\nlow.m3u8\n").endswith("low.m3u8")
for t in (p+"#EXT-X-ENDLIST\n",p.replace("seg8.ts","https://other.example/a.ts"),p.replace("seg8.ts","http://127.0.0.1/a.ts"),p.replace("#EXTINF:4.8,","#EXT-X-KEY:METHOD=AES-128,URI=\"key\"\n#EXTINF:4.8,",1),p.replace("seg8.ts","seg8.m4s"),p.replace("4.8","nan")):
    try:parse(base,t)
    except (Unsupported,Denied,ValueError):continue
    raise AssertionError("invalid playlist accepted")
print("PASS bounded unencrypted TS parser and origin/DRM/VOD rejection")
