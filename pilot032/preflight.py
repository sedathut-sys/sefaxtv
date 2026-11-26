"""One bounded source check before heavyweight model setup."""
from ingest import initial,Denied,Unsupported
from pathlib import Path
import json,time,sys
out=Path("pilot032-evidence");out.mkdir(exist_ok=True)
try:
    u,p=initial(time.monotonic()+15)
    r={"result":"manifest-candidate","target":p.target,"segments":len(p.items)}
except Exception as e:
    r={"result":"source-unavailable-or-unsupported","error":type(e).__name__,"detail":str(e)[:140] if isinstance(e,(Denied,Unsupported)) else ""}
(out/"preflight.json").write_text(json.dumps(r,indent=2))
print("PREFLIGHT",json.dumps(r),flush=True)
if r["result"]!="manifest-candidate":sys.exit(2)
