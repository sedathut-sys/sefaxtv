import {readFileSync} from 'node:fs';
import {assess} from './eligibility.mjs';
const records=JSON.parse(readFileSync(new URL('./candidates.json',import.meta.url),'utf8'));
function runTests(assess,records){
 let count=0;
 function check(name,value){if(!value)throw Error("FAIL "+name);count++;}
 const day="2026-11-25",base={decision:"approved",approval:{from:"2026-11-01",until:"2026-12-01",rightsHolderVerified:true,embed:true,temporaryCover:true,playerOnly:true,mandatoryElementsPreserved:true,ordinarySecurity:true,noCost:true,turkey:true,publicDistributionReviewed:true,evidenceRef:"synthetic fixture only",platforms:["web","android","windows"],parentOrigins:["https://sedathut-sys.github.io","https://appassets.androidplatform.net"],playerUrl:"https://test.invalid/player",playerOrigin:"https://test.invalid",playerPath:"/player",webProof:"documented-progress",webAcceptance:true,nativeObservation:true,frameBinding:true,androidAcceptance:true,windowsAcceptance:true}};
 for(const r of records)for(const p of ["web","android","windows"])check(r.id+" "+p+" blocked",!assess(r,p,day).eligible);
 for(const p of ["web","android","windows"])check("synthetic "+p,assess(base,p,day).eligible);
 for(const k of ["rightsHolderVerified","embed","temporaryCover","playerOnly","mandatoryElementsPreserved","ordinarySecurity","noCost","turkey","publicDistributionReviewed","webAcceptance"])check("missing "+k,!assess({...base,approval:{...base.approval,[k]:false}},"web",day).eligible);
 for(const [k,v] of [["until","2026-11-24"],["from","2026-11-26"],["until","2026-11-31"],["evidenceRef",""],["playerUrl","http://test.invalid/player"],["playerUrl","https://other.invalid/player"],["playerUrl","https://test.invalid/player?token=hidden"],["playerUrl","https://test.invalid/other"],["playerUrl","https://u:p@test.invalid/player"],["parentOrigins",[]],["platforms",["android"]],["webProof","load-only"]])check("reject "+k+" "+v,!assess({...base,approval:{...base.approval,[k]:v}},"web",day).eligible);
 for(const k of ["nativeObservation","frameBinding","androidAcceptance"])check("android "+k,!assess({...base,approval:{...base.approval,[k]:false}},"android",day).eligible);
 check("wrong platform",!assess(base,"other",day).eligible);
 return count;
}
console.log('PASS '+runTests(assess,records)+' offline acceptance assertions');
