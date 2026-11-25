// Offline human-review helper; not an authorization authority or playback adapter.
export function assess(record,platform,today){
 const reasons=[];
 if(!["web","android","windows"].includes(platform))reasons.push("platform");
 if(record?.decision!=="approved")reasons.push("review-not-approved");
 const a=record?.approval;
 if(!a||typeof a!=="object")return {eligible:false,reasons:[...reasons,"no-approval"]};
 const validDay=x=>typeof x==="string"&&/^\d{4}-\d{2}-\d{2}$/.test(x)&&!Number.isNaN(Date.parse(x+"T00:00:00Z"))&&new Date(x+"T00:00:00Z").toISOString().slice(0,10)===x;
 if(!validDay(today)||!validDay(a.from)||!validDay(a.until)||a.from>today||today>a.until)reasons.push("date");
 for(const k of ["rightsHolderVerified","embed","temporaryCover","playerOnly","mandatoryElementsPreserved","ordinarySecurity","noCost","turkey","publicDistributionReviewed"])if(a[k]!==true)reasons.push(k);
 if(typeof a.evidenceRef!=="string"||!a.evidenceRef.trim())reasons.push("evidenceRef");
 if(!Array.isArray(a.platforms)||!a.platforms.includes(platform))reasons.push("platform-scope");
 const parent=platform==="web"?"https://sedathut-sys.github.io":"https://appassets.androidplatform.net";
 if(!Array.isArray(a.parentOrigins)||!a.parentOrigins.includes(parent))reasons.push("parent-scope");
 // Deliberately accept only an exact, conservative static URL form for the first pilot.
 // No credentials, query, fragment, percent encoding, wildcard, alternate port or dot segments.
 const origin=a.playerOrigin,path=a.playerPath;
 if(typeof origin!=="string"||!/^https:\/\/(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z][a-z0-9-]*[a-z0-9]$/.test(origin)||
 typeof path!=="string"||!/^\/[A-Za-z0-9_-]+(?:\/[A-Za-z0-9_-]+)*(?:\.[A-Za-z0-9]+)?$/.test(path)||a.playerUrl!==origin+path)reasons.push("player-url");
 if(platform==="web"){if(a.webProof!=="documented-progress"||a.webAcceptance!==true)reasons.push("web-proof");}
 else if(a.nativeObservation!==true||a.frameBinding!==true||a[platform+"Acceptance"]!==true)reasons.push("native-proof");
 return {eligible:reasons.length===0,reasons};
}
