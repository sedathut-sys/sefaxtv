import {Controller} from './controller.mjs';
import {hlsDriver} from './hls-driver.mjs';
const $=id=>document.getElementById(id),host=$('host'),status=$('status'),proof=$('proof');
function own(stall){return emit=>{const canvas=document.createElement('canvas');canvas.width=640;canvas.height=360;host.append(canvas);const ctx=canvas.getContext('2d');let started=performance.now(),last=started,raf=0,closed=false;
 function draw(now){if(closed||stall&&now-started>1800)return;ctx.fillStyle='#13243b';ctx.fillRect(0,0,640,360);ctx.fillStyle='#67c9ef';ctx.fillRect((now/10)%560,45,80,70);ctx.fillStyle='white';ctx.font='25px system-ui';ctx.fillText('YEREL TEST · TV YAYINI DEĞİL',60,190);if(now-last>=500){last=now;emit('proof');}if(!closed)raf=requestAnimationFrame(draw);}
 raf=requestAnimationFrame(draw);return{close(){closed=true;cancelAnimationFrame(raf);canvas.remove();}};};}
function report(r){proof.textContent=r?'Canlı kare ilerlemesi: '+r.seconds.toFixed(1)+' sn · '+r.frames+' kare':'';proof.dataset.continuous=r&&r.seconds>=30&&r.mediaSeconds>=27&&r.frames>=30&&r.intervals>=30?'yes':'no';}
const c=new Controller({drivers:{live:emit=>hlsDriver(host,report,emit),stall:own(true),own:own(false)},show:(s,source)=>{status.dataset.state=s;status.dataset.source=source||'';status.textContent=({idle:'Durduruldu',connecting:'Bağlanıyor',ready:'Yayın hazır; kare kanıtı bekleniyor',playing:'Görüntü ilerliyor',exhausted:'Kaynak kalmadı',denied:'Erişim sınırlı veya desteklenmiyor; durduruldu',manual:'Duraklatıldı veya manuel başlatma bekleniyor',paused:'Duraklatıldı',unsupported:'Desteklenmeyen kaynak'})[s]||s;}});
$('start').onclick=()=>c.select(['live']);$('stall').onclick=()=>c.select(['stall','own']);$('stop').onclick=()=>c.stop();
setInterval(()=>c.tick(),250);document.addEventListener('visibilitychange',()=>{if(document.hidden)c.stop();});window.addEventListener('pagehide',()=>c.stop());
