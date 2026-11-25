"""Owned synthetic two-origin test. No real channel, external URLs or permission bypass.
Run: python -m pip install playwright==1.52.0; python -m playwright install chromium;
     python acceptance/test_two_origins.py
Loopback HTTP is used only for isolated tests; production acceptance requires HTTPS.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import json

APP = "http://127.0.0.1:18741"
PLAYER = "http://127.0.0.1:18742"
OTHER = "http://127.0.0.1:18743"
HOST = """<!doctype html><meta charset=utf-8><title>Owned iframe acceptance</title>
<style>#tv{position:relative;width:640px;height:360px}iframe,#cover{position:absolute;inset:0;width:100%;height:100%;border:0}#cover{background:#142438;color:white;display:grid;place-items:center}#cover[hidden]{display:none}</style>
<button id=start>Play owned test</button><button id=ready>Ready only</button><button id=fail>Failure then backup</button><button id=stall>Stall then backup</button>
<div id=tv><div id=cover>WAIT</div></div><script>
const PLAYER=__PLAYER__;let seq=0, active=null;const tv=document.querySelector('#tv'),cover=document.querySelector('#cover');
const events=[];let timer;
function stop(){clearInterval(timer);active?.frame.remove();active=null;cover.hidden=false;}
function start(modes){stop();if(!modes.length)return;const mode=modes[0],frame=document.createElement('iframe'),id=++seq,token=crypto.randomUUID();
 active={frame,id,token,mode,remaining:modes.slice(1),last:-1,counter:0,at:performance.now(),proved:false,loaded:false};
 const a=active;frame.allow='autoplay';frame.sandbox='allow-scripts allow-same-origin';frame.src=PLAYER+'/player?'+new URLSearchParams({mode,seq:id,token});
 frame.addEventListener('load',()=>{if(active===a){a.loaded=true;events.push('load');}});tv.prepend(frame);
 timer=setInterval(()=>{if(active===a&&performance.now()-a.at>(a.proved?8000:10000)){events.push(a.proved?'stall':'unknown');start(a.remaining);}},100);
}
window.addEventListener('message',e=>{const a=active,d=e.data;if(!a||e.origin!==PLAYER||e.source!==a.frame.contentWindow||!d||d.seq!==a.id||d.token!==a.token)return;
 if(d.type==='error'&&d.code==='owned-test-failure'){events.push('failure');start(a.remaining);return;}
 if(d.type!=='proof'||!a.loaded||!Number.isSafeInteger(d.counter)||d.counter<=a.counter||!Number.isFinite(d.mediaTime)||d.mediaTime<=a.last||!Number.isFinite(d.delta)||d.delta<.16||!Number.isSafeInteger(d.frameDelta)||d.frameDelta<1)return;
 a.counter=d.counter;a.last=d.mediaTime;a.at=performance.now();a.proved=true;cover.hidden=true;events.push('proof');
});
document.querySelector('#start').onclick=()=>start(['play']);document.querySelector('#ready').onclick=()=>start(['ready']);
document.querySelector('#fail').onclick=()=>start(['fail','play']);document.querySelector('#stall').onclick=()=>start(['stall','play']);
</script>""".replace("__PLAYER__",json.dumps(PLAYER))
FIXTURE = """<!doctype html><meta charset=utf-8><style>body{margin:0}video{width:100vw;height:100vh;object-fit:contain}</style>
<video muted autoplay playsinline></video><script>
const p=new URLSearchParams(location.search),mode=p.get('mode'),seq=Number(p.get('seq')),token=p.get('token'),APP=__APP__;
const send=d=>parent.postMessage({seq,token,...d},APP);
if(mode==='fail'){setTimeout(()=>send({type:'error',code:'owned-test-failure'}),250);}
else if(mode==='ready'){send({type:'ready'});}
else{
 const c=document.createElement('canvas');c.width=640;c.height=360;const ctx=c.getContext('2d'),v=document.querySelector('video');
 let tick=0;const drawing=setInterval(()=>{ctx.fillStyle=tick%2?'#165':'#236';ctx.fillRect(0,0,640,360);ctx.fillStyle='white';ctx.font='32px sans-serif';ctx.fillText('OWNED LAB '+tick++,30,80);},60);
 v.srcObject=c.captureStream(16);v.play().catch(()=>{});
 let baseline=null,counter=0,lastSent=-Infinity;
 function frame(now,m){if(!v.paused&&!v.ended&&v.readyState>=2&&v.videoWidth>0){
  if(!baseline)baseline=m;
  if(m.mediaTime-baseline.mediaTime>=.16&&m.presentedFrames>baseline.presentedFrames&&now-lastSent>=600){
   send({type:'proof',counter:++counter,mediaTime:m.mediaTime,delta:m.mediaTime-baseline.mediaTime,frameDelta:m.presentedFrames-baseline.presentedFrames});baseline=m;lastSent=now;
  }
 }v.requestVideoFrameCallback(frame);}
 v.requestVideoFrameCallback(frame);
 if(mode==='stall')setTimeout(()=>{clearInterval(drawing);v.pause();v.srcObject.getTracks().forEach(t=>t.stop());},2600);
}
</script>""".replace("__APP__",json.dumps(APP))
DENIED = '<!doctype html><iframe id=denied src="'+PLAYER+'/player?mode=play&seq=1&token=denied"></iframe>'
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        port=self.server.server_port
        if port==18741: body=HOST
        elif port==18742 and self.path.startswith('/player?'): body=FIXTURE
        elif port==18743: body=DENIED
        else: self.send_error(404);return
        self.send_response(200)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        if port==18742: self.send_header('Content-Security-Policy','frame-ancestors '+APP)
        self.end_headers();self.wfile.write(body.encode())
    def log_message(self,*args): pass

def main():
    servers=[ThreadingHTTPServer(('127.0.0.1',p),Handler) for p in (18741,18742,18743)]
    for s in servers: Thread(target=s.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            page=browser.new_page();page.goto(APP)
            assert page.locator('#tv iframe').count()==0
            page.click('#ready');page.wait_for_function('active.loaded')
            page.wait_for_timeout(400);assert not page.evaluate('cover.hidden')
            print('PASS load/ready never opens cover',flush=True)
            page.click('#start');page.wait_for_function('cover.hidden',timeout=10000)
            assert page.locator('#tv iframe').count()==1
            assert page.evaluate("(()=>{try{void active.frame.contentWindow.document;return false}catch{return true}})()")
            print('PASS real video frames across distinct origins; same-origin restriction intact',flush=True)
            page.click('#ready');page.wait_for_function('active.loaded')
            page.evaluate("""()=>dispatchEvent(new MessageEvent('message',{origin:'http://127.0.0.1:18743',source:active.frame.contentWindow,data:{type:'proof',seq:active.id,token:active.token,counter:1,mediaTime:1,delta:.2,frameDelta:2}}))""")
            page.evaluate("""()=>dispatchEvent(new MessageEvent('message',{origin:PLAYER,source:active.frame.contentWindow,data:{type:'proof',seq:active.id-1,token:active.token,counter:1,mediaTime:1,delta:.2,frameDelta:2}}))""")
            page.evaluate("""()=>dispatchEvent(new MessageEvent('message',{origin:PLAYER,source:window,data:{type:'proof',seq:active.id,token:active.token,counter:1,mediaTime:1,delta:.2,frameDelta:2}}))""")
            assert not page.evaluate('cover.hidden')
            print('PASS wrong origin, wrong window and stale sequence rejected',flush=True)
            page.click('#fail');page.wait_for_function("active.mode==='play'&&cover.hidden",timeout=10000)
            assert page.evaluate("events.includes('failure')") and page.locator('#tv iframe').count()==1
            print('PASS definite error to one backup',flush=True)
            page.click('#stall');page.wait_for_function("active.mode==='stall'&&cover.hidden",timeout=10000)
            page.wait_for_function("active.mode==='play'&&cover.hidden",timeout=18000)
            assert page.evaluate("events.includes('stall')") and page.locator('#tv iframe').count()==1
            print('PASS stall to one backup',flush=True)
            denied=browser.new_page();messages=[];denied.on('console',lambda m:messages.append(m.text))
            denied.goto(OTHER);denied.wait_for_timeout(500)
            assert any('frame-ancestors' in m and ('violat' in m.lower() or 'refus' in m.lower()) for m in messages),messages
            print('PASS CSP frame-ancestors denies other parent',flush=True)
            browser.close()
    finally:
        for s in servers:s.shutdown();s.server_close()
if __name__=='__main__':main()
