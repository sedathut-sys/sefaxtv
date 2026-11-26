// Only the explicit user-selected tab stream is processed. No automatic capture.
export const CLIP_MS=4800,MAX_CLIPS=6,MAX_BYTES=8_000_000;
export function recordClip(stream,ms=CLIP_MS){
 return new Promise((resolve,reject)=>{
  const type=['video/webm;codecs=vp8,opus','video/webm'].find(t=>MediaRecorder.isTypeSupported(t));
  if(!type){reject(new Error('WebM desteklenmiyor'));return;}
  let r,timer,started=performance.now(),parts=[],size=0;
  try{r=new MediaRecorder(stream,{mimeType:type,videoBitsPerSecond:800000,audioBitsPerSecond:64000});}
  catch(e){reject(e);return;}
  const finish=()=>{clearTimeout(timer);for(const t of stream.getTracks())t.removeEventListener('ended',finish);if(r.state!=='inactive')r.stop();};
  r.ondataavailable=e=>{size+=e.data.size;if(size<=MAX_BYTES)parts.push(e.data);else finish();};
  r.onerror=e=>{finish();reject(e.error||new Error('Kayıt hatası'));};
  r.onstop=()=>{clearTimeout(timer);for(const t of stream.getTracks())t.removeEventListener('ended',finish);
   const elapsed=performance.now()-started;
   if(size>MAX_BYTES||size===0||elapsed<ms-350||elapsed>ms+1500){reject(new Error('Eksik veya aşırı uzun parça'));return;}
   resolve({blob:new Blob(parts,{type:'video/webm'}),elapsed,start:started,end:performance.now()});};
  for(const t of stream.getTracks())t.addEventListener('ended',finish,{once:true});
  r.start();timer=setTimeout(finish,ms);
 });
}
export async function captureLoop(stream,{count=MAX_CLIPS,onClip=()=>{},stopped=()=>false}={}){
 if(!stream.getVideoTracks().length||!stream.getAudioTracks().length)throw Error('Sekme sesi ve görüntüsü gerekli');
 let uploads=[],prev=null,results=[];
 try{
  for(let i=0;i<count&&!stopped();i++){
   if(stream.getTracks().some(t=>t.readyState!=='live'))break;
   const clip=await recordClip(stream);
   if(stopped())break;
   const gap=prev===null?0:clip.start-prev;prev=clip.end;
   // At most one outstanding local upload; stop instead of accumulating recordings.
   if(uploads.length){await uploads.shift();}
   const up=fetch('./clip/'+i,{method:'POST',headers:{'Content-Type':'video/webm'},body:clip.blob}).then(r=>{if(!r.ok)throw Error('Yerel işlem kuyruğu: '+r.status);});
   // Prevent an unhandled rejection while the following clip is recording.
   up.catch(()=>{});uploads.push(up);
   results.push({index:i,elapsed:clip.elapsed,gap,size:clip.blob.size});onClip(results.at(-1));
  }
  await Promise.all(uploads);
  const r=await fetch('./finish',{method:'POST'});if(!r.ok)throw Error('Oturum kapanışı başarısız');
  return results;
 }finally{for(const t of stream.getTracks())t.stop();}
}
