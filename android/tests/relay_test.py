from pathlib import Path
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1]
html=(root/'app/src/main/assets/index.html').read_text()
# Only test harness substitutes local about:srcdoc for the blocked virtual HTTPS origin.
# It exercises the true event.source gate with real child window messages.
h=html.replace('location.href===NATIVE_APP ?', 'true ?').replace('frame.src=s.nativeUrl;',"frame.srcdoc='<html><body>Owned fixture relay test</body></html>';")
h=h.replace("event.origin!==new URL(NATIVE_PLAYER).origin", "event.origin!=='null'").replace('s.frame.contentWindow.location.href!==s.nativeUrl',"s.frame.contentWindow.location.href!=='about:srcdoc'")
bootstrap='''<script>window.hostLog=[];window.SefaXTVNative={postMessage(raw){const d=JSON.parse(raw);hostLog.push(d);if(d.type==='host:hello')queueMicrotask(()=>hostProof({type:'host:ready',fixture:'https://appassets.androidplatform.net/assets/lab-player.html'}));if(d.type==='probe:evidence')hostProof(d.evidence);}};window.hostProof=d=>SefaXTVNative.onmessage({data:JSON.stringify({protocol:'sefaxtv-probe-v1',...d})});</script>'''
h=h.replace("<script>\n'use strict';",bootstrap+"<script>\n'use strict';",1)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=b.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(h);page.wait_for_function('nativeReady && setupDone');assert page.locator('#screen iframe').count()==0
 page.locator('details summary').click();page.locator('#nativeLab').click();page.wait_for_function('active.loaded');cmd=page.evaluate('hostLog.find(x=>x.type==="probe:start")');base={'protocol':'sefaxtv-probe-v1','type':'video:advanced','seq':cmd['seq'],'token':cmd['token'],'url':cmd['url'],'counter':1,'method':'time','mediaTime':1.0,'delta':0.25,'frameDelta':0}
 frame=page.locator('#screen iframe').content_frame
 send=lambda d:frame.locator('body').evaluate('(el,d)=>parent.postMessage(d,"*")',d)
 # unrelated source window, correct-looking payload
 page.evaluate("""d=>{const f=document.createElement("iframe");f.srcdoc="<body>other</body>";f.onload=()=>{f.contentWindow.payload=d;f.contentWindow.eval('parent.postMessage(payload,"*")')};document.body.append(f)}""",base)
 page.wait_for_timeout(150);assert page.evaluate('hostLog.filter(d=>d.type==="probe:evidence").length')==0
 for patch in [{'token':'0'*32},{'seq':0},{'url':'https://evil.invalid/'},{'type':'loaded'},{'protocol':'wrong'}]:
  send(dict(base,**patch));page.wait_for_timeout(30)
 assert page.evaluate('hostLog.filter(d=>d.type==="probe:evidence").length')==0;assert not page.locator('#cover').evaluate('(x)=>x.hidden')
 print('PASS relay rejects unrelated window, 5 malformed/stale messages')
 send(base);page.wait_for_function('document.getElementById("cover").hidden');assert page.evaluate('hostLog.filter(d=>d.type==="probe:evidence").length')==1
 print('PASS real child postMessage -> mock host -> cover')
 page.locator('[data-id=kapak]').click();page.wait_for_timeout(100);page.evaluate('d=>hostProof(d)',dict(base,counter=2,mediaTime=2));assert not page.locator('#cover').evaluate('(x)=>x.hidden');assert page.evaluate('hostLog.some(d=>d.type==="probe:stop")')
 print('PASS channel switch cancels previous native session')
 assert not errors,errors;b.close()
