'use strict';
const host=document.getElementById('host'),status=document.getElementById('status');
let active=null,seq=0;
const BASE='https://video.blender.org/videos/embed/pAQiVCgv2CsLg79KKXUoMw';
function stop(message='Durduruldu. Yeni bir deney seçebilirsin.'){
 ++seq;active=null;host.replaceChildren();const s=document.createElement('span');s.className='muted';s.textContent='Oynatıcı kapalı';host.append(s);status.textContent=message;
}
function start(auto){
 stop();const n=++seq,frame=document.createElement('iframe');active=frame;
 frame.title='Blender Foundation resmî video oynatıcısı';frame.allow='autoplay; fullscreen; picture-in-picture';frame.allowFullscreen=true;frame.referrerPolicy='strict-origin-when-cross-origin';
 frame.addEventListener('load',()=>{if(active===frame&&n===seq)status.textContent=auto?'Oynatıcı yüklendi. Görüntünün kendiliğinden başladığını kontrol et.':'Oynatıcı yüklendi. Kendi Play düğmesine dokun.';});
 frame.addEventListener('error',()=>{if(active===frame&&n===seq)status.textContent='Yükleme hatası bildirildi. Durdurup tekrar deneyebilirsin.';});
 frame.src=BASE+'?api=1&autoplay='+(auto?'1':'0')+'&muted=1&p2p=0';
 status.textContent=auto?'Otomatik oynatma isteniyor…':'Manuel oynatıcı yükleniyor…';host.replaceChildren(frame);
}
document.getElementById('auto').onclick=()=>start(true);
document.getElementById('manual').onclick=()=>start(false);
document.getElementById('stop').onclick=()=>stop();
document.addEventListener('visibilitychange',()=>{if(document.hidden&&active)stop('Sekme gizlendi; yeniden seçim gerekiyor.');});
window.addEventListener('pagehide',()=>{if(active)stop();});
const v=document.createElement('video');
const h=v.canPlayType('video/mp4; codecs="avc1.42E01E, mp4a.40.2"');
document.getElementById('cap').textContent='Tarayıcının bildirdiği H.264/AAC desteği: '+(h||'bildirilmedi')+' (bu bilgi oynatma kanıtı değildir).';
