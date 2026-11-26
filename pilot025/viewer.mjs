import {Controller} from './controller.mjs';
import {openChannel,ORIGIN} from './channel-adapter.mjs';
import {ProgressGate} from './progress.mjs';
const $=id=>document.getElementById(id),host=$('host'),status=$('status');
function peer(emit){
 const frame=document.createElement('iframe'),gate=new ProgressGate();
 frame.title='Blender Foundation video';frame.allow='autoplay; fullscreen; picture-in-picture';frame.allowFullscreen=true;frame.referrerPolicy='strict-origin-when-cross-origin';
 frame.src=ORIGIN+'/videos/embed/pAQiVCgv2CsLg79KKXUoMw?api=1&autoplay=1&muted=1&p2p=0';
 let loaded=false,closed=false,ch=null,proved=false;
 frame.addEventListener('load',()=>{if(closed)return;if(loaded)emit('denied');loaded=true;});
 host.append(frame);
 try{ch=openChannel({source:frame.contentWindow,emit:d=>{
  if(closed)return;
  if(d.kind==='ready'){emit('ready');return;}
  if(d.kind==='ready-rejected'){emit('denied');return;}
  if(d.kind==='status-change'&&d.state!=='playing'){gate.reset();if(proved&&d.state==='paused')emit('pause');return;}
  if(d.kind==='status-update'&&gate.sample(d,performance.now())){proved=true;emit('proof');}
 }});}catch(e){frame.remove();throw e;}
 return{close(){closed=true;ch?.close();frame.remove();}};
}
function own(stall){return emit=>{
 const canvas=document.createElement('canvas');canvas.width=640;canvas.height=360;canvas.style.width='100%';canvas.style.height='100%';host.append(canvas);
 const ctx=canvas.getContext('2d');let started=performance.now(),last=started,raf=0,closed=false;
 function draw(now){if(closed)return;if(stall&&now-started>1800)return;
  ctx.fillStyle='#13243b';ctx.fillRect(0,0,640,360);ctx.fillStyle='#67c9ef';ctx.fillRect((now/10)%560,45,80,70);ctx.fillStyle='white';ctx.font='25px system-ui';ctx.fillText('SEFAXTV · KENDİ LAB GÖRÜNTÜMÜZ',55,190);ctx.fillText(new Date().toLocaleTimeString('tr-TR'),230,230);
  if(now-last>=500){last=now;emit('proof');}if(!closed)raf=requestAnimationFrame(draw);
 }
 raf=requestAnimationFrame(draw);return{close(){closed=true;cancelAnimationFrame(raf);canvas.remove();}};
};}
const controller=new Controller({drivers:{peer,stall:own(true),own:own(false)},show:(s,source)=>{status.dataset.state=s;status.dataset.source=source||'';status.textContent=({idle:'Durduruldu',connecting:'Bağlanıyor',ready:'Hazır; oynatma henüz kanıtlanmadı',playing:'İlerleme kanıtı alındı',exhausted:'Kaynak kalmadı',denied:'Sağlayıcı reddi; durduruldu',paused:'Duraklatıldı; yeniden seç',manual:'Manuel oynat',unsupported:'Desteklenmeyen kaynak'})[s]||s;}});
$('select').onclick=()=>controller.select(['peer']);$('stall').onclick=()=>controller.select(['stall','own']);$('stop').onclick=()=>controller.stop();
setInterval(()=>controller.tick(),250);
document.addEventListener('visibilitychange',()=>{if(document.hidden)controller.stop();});window.addEventListener('pagehide',()=>controller.stop());
