"""Deterministic bounded replay schedule; no live capture or video control."""
import math
def plan(start,end,ready,dub_duration,delay=6.0,max_speed=1.25):
    if not all(math.isfinite(x) for x in (start,end,ready,dub_duration,delay,max_speed)) or start<0 or end<=start or ready<end or delay<0 or max_speed<1:
        raise ValueError("invalid timing")
    target=start+delay
    slot=end-start
    if ready>target or dub_duration<=0 or dub_duration/slot>max_speed:
        return {"mode":"original","start":target,"end":end+delay,"speed":1.0}
    return {"mode":"dub","start":target,"end":end+delay,"speed":max(1.0,dub_duration/slot)}
if __name__=="__main__":
    assert plan(0,3,4,3.3)["mode"]=="dub"
    assert abs(plan(0,3,4,3.3)["speed"]-1.1)<1e-9
    assert plan(0,3,6.01,3)["mode"]=="original"
    assert plan(0,3,4,4)["mode"]=="original"
    assert plan(4,7,8,3)["start"]==10
    print("PASS bounded schedule, late/long output falls back to original")
