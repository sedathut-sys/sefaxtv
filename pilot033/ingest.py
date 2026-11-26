"""Narrow, bounded, publisher-published HLS ingestion. No auth, bypass or redirects."""
from urllib.parse import urljoin,urlsplit
from urllib.request import Request,build_opener,HTTPRedirectHandler
from urllib.error import HTTPError
from dataclasses import dataclass
import math,re,time,socket,ipaddress
from urllib.request import ProxyHandler
SOURCE=None
HOST=None
SCHEME="https"
def configure(url):
    global SOURCE,HOST
    u=urlsplit(url)
    if u.scheme!="https" or not u.hostname or u.username or u.password or u.fragment or u.port not in (None,443) or not u.path.endswith(".m3u8") or u.query:
        raise Denied("public HTTPS manifest required, no tokens or query")
    assert_public(u.hostname)
    SOURCE=url;HOST=(u.hostname,443)
def assert_public(host):
    ips={a[4][0] for a in socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)}
    if not ips or any(not ipaddress.ip_address(i).is_global for i in ips):raise Denied("non-public destination")
class Unsupported(Exception):pass
class Denied(Exception):pass
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise Denied("redirect")
def allowed(base,uri):
    url=urljoin(base,uri);u=urlsplit(url)
    if u.scheme!=SCHEME or (u.hostname,u.port or 443)!=HOST or u.username or u.password or u.fragment or u.query:
        raise Denied("unapproved origin")
    return url
def get(url,limit,deadline=None):
    allowed(SOURCE,url)
    assert_public(urlsplit(url).hostname)
    deadline=time.monotonic()+12 if deadline is None else min(deadline,time.monotonic()+12)
    if deadline<=time.monotonic():raise TimeoutError("deadline")
    try:
        with build_opener(ProxyHandler({}),NoRedirect()).open(Request(url,headers={"User-Agent":"SefaXTV-lab/0.33","Accept":"*/*"}),timeout=min(8,max(.1,deadline-time.monotonic()))) as r:
            if r.status!=200:raise Unsupported("http-status")
            chunks=[];total=0
            while True:
                if time.monotonic()>=deadline:raise TimeoutError("download deadline")
                b=r.read(min(65536,limit+1-total))
                if not b:break
                total+=len(b)
                if total>limit:raise Unsupported("size limit")
                chunks.append(b)
            return b"".join(chunks)
    except HTTPError as e:
        if e.code in (401,403,429):raise Denied("HTTP "+str(e.code)) from None
        raise Unsupported("HTTP "+str(e.code)) from None
@dataclass(frozen=True)
class Segment:
    seq:int
    duration:float
    url:str
@dataclass(frozen=True)
class Playlist:
    target:int
    items:list
def lines(text):
    v=[s.strip() for s in text.splitlines() if s.strip()]
    if not v or v[0]!="#EXTM3U":raise Unsupported("not HLS")
    return v
def master(url,text):
    v=lines(text)
    # Audio renditions and encrypted/LL-HLS variants need a different adapter.
    if any(x.startswith(("#EXT-X-MEDIA:","#EXT-X-SESSION-KEY")) for x in v):raise Unsupported("alternate rendition or key")
    choices=[]
    for i,x in enumerate(v):
        if x.startswith("#EXT-X-STREAM-INF:"):
            m=re.search(r"(?:^|[:,])BANDWIDTH=(\d+)(?:,|$)",x)
            if not m or i+1==len(v) or v[i+1].startswith("#"):raise Unsupported("invalid master")
            bandwidth=int(m.group(1))
            if 0<bandwidth<=2500000:choices.append((bandwidth,allowed(url,v[i+1])))
    if not any(x.startswith("#EXT-X-STREAM-INF:") for x in v):return None
    if not choices:raise Unsupported("no bounded variant")
    return min(choices)[1]
def parse(url,text):
    v=lines(text)
    if any(x.startswith(("#EXT-X-ENDLIST","#EXT-X-PLAYLIST-TYPE:VOD")) for x in v):raise Unsupported("not live")
    if any(x.startswith(("#EXT-X-KEY:","#EXT-X-MAP:","#EXT-X-BYTERANGE:","#EXT-X-PART:","#EXT-X-GAP","#EXT-X-DISCONTINUITY","#EXT-X-SKIP","#EXT-X-STREAM-INF:")) for x in v):raise Unsupported("unsupported HLS feature")
    seq=None;target=None;duration=None;items=[]
    for x in v[1:]:
        if x.startswith("#EXT-X-MEDIA-SEQUENCE:"):seq=int(x.split(":",1)[1])
        elif x.startswith("#EXT-X-TARGETDURATION:"):target=int(x.split(":",1)[1])
        elif x.startswith("#EXTINF:"):
            if duration is not None:raise Unsupported("missing segment")
            duration=float(x.split(":",1)[1].split(",",1)[0])
            if not math.isfinite(duration) or not 1<=duration<=10:raise Unsupported("segment duration")
        elif not x.startswith("#"):
            if duration is None or seq is None:raise Unsupported("segment without sequence")
            uri=allowed(url,x)
            if not urlsplit(uri).path.lower().endswith(".ts"):raise Unsupported("not TS")
            items.append(Segment(seq+len(items),duration,uri));duration=None
    if target is None or not 1<=target<=10 or seq is None or seq<0 or duration is not None or not 1<=len(items)<=30:raise Unsupported("playlist bounds")
    return Playlist(target,items)
def read(url,deadline=None):
    return get(url,256000,deadline).decode("utf-8-sig")
def initial(deadline=None):
    t=read(SOURCE,deadline);u=master(SOURCE,t)
    if u:return u,parse(u,read(u,deadline))
    return SOURCE,parse(SOURCE,t)
def newer(url,last,deadline):
    while time.monotonic()<deadline:
        p=parse(url,read(url,deadline))
        items=[x for x in p.items if x.seq>last]
        if items:
            if items[0].seq!=last+1:raise Unsupported("sequence gap")
            return p,items
        time.sleep(min(max(1,p.target/2),max(0,deadline-time.monotonic())))
    raise TimeoutError("no new segment")
