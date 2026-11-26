from continuity import check
def sample(i): return dict(kind="status-update",seq=2,t=500*i,position=.5*i,playbackState="playing",gate="sustained-progress")
rows=[sample(i) for i in range(61)]
assert check(rows,30100)==(True,"continuous-provider-progress")
assert not check([],30100)[0]
assert not check(rows[:8],30100)[0]
assert not check(rows,33000)[0]
def changed(i,**kw):
    r=[dict(x) for x in rows];r[i].update(kw);return r
assert not check(changed(35,playbackState="paused"),30100)[0]
assert not check(changed(35,position=17),30100)[0]
assert not check(changed(35,position=90),30100)[0]
assert not check(changed(35,seq=3),30100)[0]
assert not check(changed(35,t=float("nan")),30100)[0]
assert not check(changed(35,gate="first-interval"),30100)[0]
assert not check(rows[:10]+rows[17:],30100)[0]
assert not check(rows+[dict(kind="status-change",seq=2,t=14000,state="paused")],30100)[0]
assert not check(rows+[dict(kind="stall",seq=2,t=14000)],30100)[0]
assert not check(rows+[dict(kind="session-ended",seq=2,t=14000)],30100)[0]
slow=[dict(x,position=x["position"]*.5) for x in rows]
assert not check(slow,30100)[0]
print("PASS 15 continuity assertions")
