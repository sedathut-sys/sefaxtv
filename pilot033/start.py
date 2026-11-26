import argparse,threading,tempfile,shutil,webbrowser,subprocess,time
from pathlib import Path
from urllib.parse import urlsplit
from ingest import configure
from local_server import serve
from session import run
def main():
    p=argparse.ArgumentParser(description="SefaXTV private local live dubbing")
    p.add_argument("--source",required=True,help="Publisher-published permitted HTTPS HLS URL")
    p.add_argument("--publisher-page",required=True,help="Official source page documenting the stream")
    p.add_argument("--domain",choices=["general","football"],default="general")
    p.add_argument("--confirm-permitted-source",action="store_true")
    a=p.parse_args()
    if not a.confirm_permitted_source or urlsplit(a.publisher_page).scheme!="https":p.error("Confirm permitted source and official HTTPS publisher page.")
    configure(a.source)
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):p.error("FFmpeg and ffprobe required on PATH.")
    assets=Path(__file__).resolve().parent
    if not (assets/"hls.mjs").exists():p.error("Use the packaged release with bundled HLS player.")
    with tempfile.TemporaryDirectory(prefix="sefaxtv-local-") as td:
        root=Path(td);public=root/"public";private=root/"private";public.mkdir();private.mkdir()
        for name in ("index.html","viewer.mjs","hls.mjs"):shutil.copyfile(assets/name,public/name)
        stop=threading.Event();server,url=serve(public,stop)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        worker=threading.Thread(target=run,args=(public,private,stop,a.domain))
        print("Yerel sayfa:",url,flush=True);webbrowser.open(url)
        worker.start()
        try:
            while worker.is_alive():worker.join(.3)
            print("Oturum tamamlandı. Sayfayı kapatmak için Ctrl+C. Dosyalar geçicidir.",flush=True)
            # Allow the final short playlist to play; no new ingestion.
            time.sleep(35)
        except KeyboardInterrupt:stop.set();worker.join()
        finally:stop.set();server.shutdown();server.server_close()
if __name__=="__main__":main()
