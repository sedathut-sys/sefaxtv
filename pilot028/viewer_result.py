"""Independent acceptance of actual video-frame evidence; no ready-only success."""
def accepted(state, continuous, proof, limited=False):
    if limited or state!="playing" or continuous!="yes" or not isinstance(proof,dict):
        return False
    import math
    def finite(key,minimum):
        x=proof.get(key)
        return type(x) in (int,float) and math.isfinite(x) and x>=minimum
    return (proof.get("live") is True and finite("seconds",30) and finite("mediaSeconds",27)
            and finite("frames",30) and finite("intervals",30) and finite("width",1) and finite("height",1))

if __name__=="__main__":
    p=dict(seconds=30.4822,mediaSeconds=30.48,frames=762,intervals=60,live=True,width=640,height=360)
    assert accepted("playing","yes",p)
    assert not accepted("ready","yes",p)
    assert not accepted("playing","no",p)
    assert not accepted("playing","yes",None)
    assert not accepted("playing","yes",p,True)
    for key,value in [("seconds",29.99),("mediaSeconds",26.9),("frames",0),("intervals",29),("live",False),("width",0),("seconds",float("nan")),("frames",True)]:
        assert not accepted("playing","yes",{**p,key:value})
    print("PASS corrected result mapping and independent frame evidence checks")
