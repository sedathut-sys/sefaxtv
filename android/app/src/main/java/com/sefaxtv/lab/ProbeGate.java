package com.sefaxtv.lab;

/** Pure Java session gate, independently testable without Android SDK. */
final class ProbeGate {
    static final String ORIGIN = "https://appassets.androidplatform.net";
    static final String APP = ORIGIN + "/assets/index.html";
    static final String FIXTURE = ORIGIN + "/assets/lab-player.html";
    static final String PROTOCOL = "sefaxtv-probe-v1";
    private long high, seq, counter;
    private String token, url;
    private double media;
    private boolean ready;
    void ready(boolean value) { ready=value; if(!value) clear(); }
    void newDocument() { ready=false; high=0; clear(); }
    private void clear() { seq=counter=0; token=url=null; media=-1; }
    boolean start(long s, String t, String u) {
        if(!ready || s<=high || s>9007199254740991L || t==null || !t.matches("[a-f0-9]{32}") || u==null) return false;
        String prefix=FIXTURE+"#seq="+s+"&token="+t+"&mode=";
        if(!(u.equals(prefix+"play")||u.equals(prefix+"stall")||u.equals(prefix+"ready"))) return false;
        clear(); high=seq=s; token=t; url=u; return true;
    }
    boolean matches(long s,String t,String u) { return ready && seq>0 && seq==s && token.equals(t) && url.equals(u); }
    boolean stop(long s,String t) { if(!ready||seq==0||seq!=s||!token.equals(t))return false; clear(); return true; }
    boolean proof(long s,String t,String u,long c,String method,double mt,double delta,long frames) {
        if(!matches(s,t,u)||c<=counter||c>=1000000000L||!Double.isFinite(mt)||mt<=media||mt<=0||mt>1e9||!Double.isFinite(delta)||delta>mt+0.000001||delta<=0) return false;
        if("frames".equals(method)) { if(frames<1||delta<.16)return false; }
        else if("time".equals(method)) { if(frames!=0||delta<.25)return false; }
        else return false;
        counter=c; media=mt; return true;
    }
}
