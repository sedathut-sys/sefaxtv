package com.sefaxtv.lab;
public final class ProbeGateTest {
 static int passed;
 static void test(boolean b,String name){if(!b)throw new AssertionError(name);passed++;System.out.println("PASS "+name);}
 public static void main(String[] args){
  ProbeGate g=new ProbeGate();String t="0123456789abcdef0123456789abcdef", t2="fedcba9876543210fedcba9876543210";
  String u=ProbeGate.FIXTURE+"#seq=1&token="+t+"&mode=stall",u2=ProbeGate.FIXTURE+"#seq=2&token="+t2+"&mode=play";
  test(!g.start(1,t,u),"not ready");g.ready(true);
  test(!g.start(1,t,"https://other.invalid/"),"foreign URL");test(!g.start(1,"bad",u),"bad token");test(g.start(1,t,u),"owned fixture start");
  test(!g.proof(1,t,u,1,"frames",1,.1,3),"weak frame proof");test(!g.proof(1,t,u,1,"time",1,.24,0),"weak time proof");test(!g.proof(1,t,u,1,"frames",1,.2,0),"no new frame");test(!g.proof(1,t,u,1,"time",1,.25,1),"time method invalid frames");
  test(!g.proof(1,t,u,1,"loaded",1,.25,0),"load not evidence");test(!g.proof(1,t2,u,1,"time",1,.25,0),"wrong token");test(!g.proof(1,t,u2,1,"time",1,.25,0),"wrong URL");
  test(g.proof(1,t,u,1,"frames",1,.2,2),"valid frame");test(!g.proof(1,t,u,1,"time",1.5,.25,0),"counter replay");test(!g.proof(1,t,u,2,"time",.9,.25,0),"media rollback");test(!g.proof(1,t,u,2,"time",Double.NaN,.25,0),"NaN");test(g.proof(1,t,u,2,"time",1.5,.25,0),"valid heartbeat");
  test(!g.start(1,t,u),"sequence reuse");test(g.start(2,t2,u2),"new session");test(!g.proof(1,t,u,3,"time",2,.25,0),"stale proof");test(!g.stop(1,t),"stale stop");test(g.proof(2,t2,u2,1,"time",.5,.25,0),"backup starts");test(g.stop(2,t2),"active stop");test(!g.proof(2,t2,u2,2,"time",1,.25,0),"proof after stop");
  g.newDocument();test(!g.start(1,t,u),"lifecycle stops gate");g.ready(true);test(g.start(1,t,u),"new document can start");g.ready(false);test(!g.proof(1,t,u,1,"time",1,.25,0),"background proof rejected");
  System.out.println("TOTAL "+passed);
 }
}
