"""Strict VOD telemetry continuity; never treats a sticky proof flag as continuous playback."""
import math
def check(rows,now,seconds=30):
    samples=[r for r in rows if r.get("kind")=="status-update"]
    start=next((i for i,r in enumerate(samples) if r.get("gate")=="sustained-progress"),None)
    if start is None: return False,"no-first-proof"
    samples=samples[start:]
    first=samples[0];last=samples[-1]
    seq=first.get("seq")
    if any(r.get("seq")!=seq for r in samples): return False,"session-changed"
    for r in samples:
        t=r.get("t");p=r.get("position")
        if r.get("playbackState")!="playing" or r.get("gate")!="sustained-progress" or not isinstance(t,(int,float)) or isinstance(t,bool) or not math.isfinite(t) or not isinstance(p,(int,float)) or isinstance(p,bool) or not math.isfinite(p) or p<0:
            return False,"invalid-or-interrupted-sample"
    for a,b in zip(samples,samples[1:]):
        dt=(b["t"]-a["t"])/1000;delta=b["position"]-a["position"]
        if not (.15<=dt<=2.5 and .16<=delta<=dt*2+.25): return False,"invalid-interval"
    if any(r.get("seq")==seq and r.get("t",-1)>=first["t"] and (r.get("kind") in ("stall","session-ended") or (r.get("kind")=="status-change" and r.get("state") not in (None,"playing"))) for r in rows):
        return False,"interrupted-state"
    elapsed=(last["t"]-first["t"])/1000
    if elapsed<seconds: return False,"window-too-short"
    if not isinstance(now,(int,float)) or not math.isfinite(now) or not 0<=now-last["t"]<=2000: return False,"stale-last-sample"
    if len(samples)<seconds+1: return False,"too-few-samples"
    if last["position"]-first["position"]<seconds*.9: return False,"insufficient-media-advance"
    return True,"continuous-provider-progress"
