import { useState, useEffect, useRef, useCallback } from "react";

const FONT_LINK = document.createElement("link");
FONT_LINK.rel = "stylesheet";
FONT_LINK.href = "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@300;400;600;700&display=swap";
document.head.appendChild(FONT_LINK);

const API = "http://localhost:8001";

const TEAM_COLOR = {
  ferrari:"#e8001d",red_bull:"#1e41ff",mercedes:"#00d2be",
  mclaren:"#ff8000",alpine:"#0090ff",aston_martin:"#006f62",
  williams:"#005aff",haas:"#b6babd",alfa:"#900000",alphatauri:"#2b4562",
};
function teamColor(team=""){
  const t=team.toLowerCase().replace(/ /g,"_");
  for(const[k,v]of Object.entries(TEAM_COLOR))if(t.includes(k))return v;
  return "#555";
}

function ProbChart({data,w=480,h=120}){
  if(!data||data.length<2)return(
    <div style={{height:h,display:"flex",alignItems:"center",justifyContent:"center"}}>
      <span style={{color:"#222",fontFamily:"'Share Tech Mono'",fontSize:10,letterSpacing:2}}>NO DATA</span>
    </div>
  );
  const vals=data.map(d=>d.prediction?.probability??50);
  const mn=Math.min(...vals)-3,mx=Math.max(...vals)+3;
  const x=i=>(i/(data.length-1))*w;
  const y=v=>h-((v-mn)/(mx-mn))*h;
  const line=data.map((_,i)=>`${x(i)},${y(vals[i])}`).join(" ");
  const area=`M${x(0)},${y(vals[0])} `+data.map((_,i)=>`L${x(i)},${y(vals[i])}`).join(" ")+` L${x(data.length-1)},${h} L${x(0)},${h}Z`;
  return(
    <svg viewBox={`0 0 ${w} ${h}`} style={{width:"100%",height:h}} preserveAspectRatio="none">
      <defs>
        <linearGradient id="cg" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#e8001d" stopOpacity=".4"/>
          <stop offset="100%" stopColor="#e8001d" stopOpacity="0"/>
        </linearGradient>
        <filter id="gl"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
      </defs>
      <path d={area} fill="url(#cg)"/>
      <polyline points={line} fill="none" stroke="#e8001d" strokeWidth="2.5" filter="url(#gl)"/>
    </svg>
  );
}

const TICKER_DEFAULT=[
  {icon:"★",c:"#ffd700",text:"NEW FASTEST LAP: MAX VERSTAPPEN — 1:32.451"},
  {icon:"▶",c:"#ffeb3b",text:"YELLOW FLAG IN SECTOR 3 — MAGNUSSEN OFF TRACK"},
  {icon:"↺",c:"#fff",text:"PIT WINDOW OPEN FOR MEDIUM TIRE RUNNERS"},
  {icon:"i",c:"#00f5ff",text:"RACE PROGRESS: LAP 16/57 — TRACK TEMP 34.2°C — AIR TEMP 22.8°C"},
];
function Ticker({results}){
  const items=results.length>0
    ?results.slice(-6).filter(r=>r.commentary_llm&&!r.commentary_llm.startsWith("Erreur")&&r.commentary_llm!=="Commentaire en attente...").map(r=>({icon:"▶",c:"#e8001d",text:`LAP ${r.lap} — ${r.commentary_llm.slice(0,90)}...`}))
    :TICKER_DEFAULT;
  const content=[...items,...items,...items];
  return(
    <div style={{position:"fixed",bottom:0,left:0,right:0,height:42,background:"#0a0a0a",borderTop:"1px solid #141414",overflow:"hidden",zIndex:200,display:"flex",alignItems:"center"}}>
      <style>{`@keyframes tk{from{transform:translateX(0)}to{transform:translateX(-33.33%)}}`}</style>
      <div style={{display:"flex",animation:"tk 50s linear infinite",whiteSpace:"nowrap"}}>
        {content.map((it,i)=>(
          <span key={i} style={{fontFamily:"'Share Tech Mono'",fontSize:10,letterSpacing:1,color:"#555",padding:"0 28px",display:"flex",alignItems:"center",gap:10}}>
            <span style={{color:it.c,fontSize:9}}>{it.icon}</span>
            {it.text}
            <span style={{color:"#e8001d",margin:"0 6px"}}>·</span>
          </span>
        ))}
      </div>
    </div>
  );
}

const PERSONA={
  journalist:{label:"JOURNALIST",color:"#e8001d"},
  professor:{label:"PROFESSOR",color:"#00e676"},
  engineer:{label:"ENGINEER",color:"#00b4ff"},
  fan:{label:"FAN",color:"#9c27b0"},
};
function CommentItem({persona,text,lap}){
  const p=PERSONA[persona];
  const isErr=text?.startsWith("Erreur lors");
  const isPend=!text||text==="Commentaire en attente...";
  return(
    <div style={{padding:"14px 0",borderBottom:"1px solid #141414"}}>
      <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:7}}>
        <span style={{width:6,height:6,borderRadius:"50%",background:p.color,display:"inline-block",flexShrink:0}}/>
        <span style={{fontFamily:"'Share Tech Mono'",fontSize:10,letterSpacing:2,color:p.color}}>{p.label}</span>
        <span style={{marginLeft:"auto",fontFamily:"'Share Tech Mono'",fontSize:9,color:"#252525"}}>LAP {lap}</span>
      </div>
      <p style={{fontFamily:"'Rajdhani'",fontSize:14,lineHeight:1.65,margin:0,color:isErr||isPend?"#2a2a2a":"#999",fontStyle:isPend?"italic":"normal"}}>
        {isErr?"⚠ Quota API atteint":isPend?"⏳ Génération en cours...":text}
      </p>
    </div>
  );
}

const IND_CFG={
  green_flag:{label:"GREEN FLAG",sub:"Track Clear",bg:"#0d2a0d",ac:"#4caf50",icon:"⚑"},
  yellow_flag:{label:"YELLOW FLAG",sub:"Caution",bg:"#2a2000",ac:"#ffeb3b",icon:"⚑"},
  red_flag:{label:"RED FLAG",sub:"Session Stopped",bg:"#1a0000",ac:"#e8001d",icon:"⊘"},
  safety_car:{label:"SAFETY CAR",sub:"Lap Incident",bg:"#1f1a00",ac:"#ffc107",icon:"◈"},
  vsc:{label:"VIRTUAL SC",sub:"VSC Active",bg:"#1f1a00",ac:"#ffc107",icon:"⚡"},
  fastest_lap:{label:"FASTEST LAP",sub:"Purple Sector",bg:"#110022",ac:"#9c27b0",icon:"◈"},
  checkered:{label:"FINISH",sub:"Race Complete",bg:"#1a1a1a",ac:"#fff",icon:"⚑"},
};
function IndCard({name}){
  const c=IND_CFG[name]||{label:name.replace(/_/g," ").toUpperCase(),sub:"",bg:"#111",ac:"#444",icon:"◆"};
  return(
    <div style={{background:c.bg,border:`1px solid ${c.ac}22`,borderLeft:`3px solid ${c.ac}`,borderRadius:2,padding:"8px 12px",display:"flex",alignItems:"center",justifyContent:"space-between",minWidth:150}}>
      <div>
        <div style={{fontFamily:"'Orbitron'",fontWeight:700,fontSize:11,color:c.ac,letterSpacing:1}}>{c.label}</div>
        {c.sub&&<div style={{fontFamily:"'Share Tech Mono'",fontSize:9,color:"#333",marginTop:1}}>{c.sub}</div>}
      </div>
      <span style={{fontSize:14,opacity:.6,color:c.ac}}>{c.icon}</span>
    </div>
  );
}

const DEMO_DRIVERS=[
  {position:1,name:"C. LECLERC",team:"Ferrari",interval:"LEADER"},
  {position:2,name:"M. VERSTAPPEN",team:"Red Bull",interval:"+1.452"},
  {position:3,name:"L. HAMILTON",team:"Mercedes",interval:"+4.891"},
  {position:4,name:"S. PEREZ",team:"Red Bull",interval:"+5.234"},
  {position:5,name:"O. PIASTRI",team:"McLaren",interval:"+6.112"},
];

export default function F1Dashboard(){
  const[file,setFile]=useState(null);
  const[jobId,setJobId]=useState(null);
  const[phase,setPhase]=useState("idle");
  const[progress,setProgress]=useState(0);
  const[results,setResults]=useState([]);
  const[selLap,setSelLap]=useState(null);
  const[drag,setDrag]=useState(false);
  const[tab,setTab]=useState("commentary");
  const[errMsg,setErrMsg]=useState("");
  const fileRef=useRef();
  const pollRef=useRef();
  const cmtRef=useRef();
  const lapRef=useRef();

  const cur=results.find(r=>r.lap===selLap)??results[results.length-1];

  // Auto-follow latest lap during processing
  useEffect(()=>{
    if(phase==="processing"&&results.length>0){
      setSelLap(results[results.length-1].lap);
    }
  },[results,phase]);

  useEffect(()=>{if(cmtRef.current)cmtRef.current.scrollTop=cmtRef.current.scrollHeight;},[selLap,results]);
  useEffect(()=>{
    if(lapRef.current&&selLap){
      const el=lapRef.current.querySelector(`[data-lap="${selLap}"]`);
      el?.scrollIntoView({behavior:"smooth",inline:"center",block:"nearest"});
    }
  },[selLap]);

  const poll=useCallback(async(id)=>{
    try{
      const res=await fetch(`${API}/video/status/${id}`);
      if(!res.ok)throw new Error(await res.text());
      const data=await res.json();
      if(data.resultats?.length){
        setResults(data.resultats);
        setProgress(Math.min(95,data.resultats.length));
        // selLap géré par useEffect auto-follow
      }
      if(data.status==="terminé"){setPhase("done");setProgress(100);clearInterval(pollRef.current);}
      if(data.status==="erreur"){setPhase("error");setErrMsg(data.message??"Erreur");clearInterval(pollRef.current);}
    }catch(e){setPhase("error");setErrMsg(e.message);clearInterval(pollRef.current);}
  },[]);

  const upload=async()=>{
    if(!file)return;
    setPhase("uploading");setProgress(0);setResults([]);setErrMsg("");
    const fd=new FormData();fd.append("file",file);
    try{
      const res=await fetch(`${API}/video/analyze`,{method:"POST",body:fd});
      if(!res.ok)throw new Error(await res.text());
      const data=await res.json();
      setJobId(data.job_id);setPhase("processing");setProgress(5);
      pollRef.current=setInterval(()=>poll(data.job_id),3000);
    }catch(e){setPhase("error");setErrMsg(e.message);}
  };

  useEffect(()=>()=>clearInterval(pollRef.current),[]);

  const onDrop=e=>{
    e.preventDefault();setDrag(false);
    const f=e.dataTransfer.files[0];
    if(f?.type.startsWith("video/"))setFile(f);
  };

  const indicators=cur?.indicators?Object.entries(cur.indicators).filter(([,v])=>v).map(([k])=>k):[];
  const withComment=results.filter(r=>r.commentary_llm&&!r.commentary_llm.startsWith("Erreur")&&r.commentary_llm!=="Commentaire en attente...").length;
  const statusText=phase==="processing"?"ANALYZING":phase==="done"?"RACE COMPLETE":"PRE-RACE";
  const statusColor=phase==="processing"?"#e8001d":phase==="done"?"#00e676":"#333";
  const toShow=selLap?results.filter(r=>r.lap===selLap):results.slice(-10);
  const drivers=cur?.drivers?.length>0?cur.drivers:DEMO_DRIVERS;

  return(
    <div style={{background:"#080808",minHeight:"100vh",color:"#fff",fontFamily:"'Rajdhani',sans-serif",overflow:"hidden",paddingBottom:42}}>
      <style>{`
        *{box-sizing:border-box;margin:0;padding:0}
        ::-webkit-scrollbar{width:3px;height:3px}
        ::-webkit-scrollbar-track{background:#0a0a0a}
        ::-webkit-scrollbar-thumb{background:#e8001d}
        @keyframes blink{0%,100%{opacity:1}50%{opacity:0}}
        @keyframes fadeup{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
      `}</style>

      {/* HEADER */}
      <header style={{display:"flex",alignItems:"center",justifyContent:"space-between",padding:"0 20px",height:48,background:"#0a0a0a",borderBottom:"1px solid #141414",position:"sticky",top:0,zIndex:300}}>
        <div style={{display:"flex",alignItems:"center",gap:10}}>
          <div style={{width:28,height:28,background:"#e8001d",borderRadius:3,display:"flex",alignItems:"center",justifyContent:"center"}}>
            <span style={{fontFamily:"'Orbitron'",fontWeight:900,fontSize:11,color:"#fff"}}>F1</span>
          </div>
          <span style={{fontFamily:"'Orbitron'",fontWeight:700,fontSize:13,letterSpacing:2,color:"#fff"}}>LIVE AI COMMENTATOR</span>
        </div>
        <div style={{display:"flex",alignItems:"center",gap:8,fontFamily:"'Share Tech Mono'",fontSize:10,color:"#333",letterSpacing:1}}>
          <span style={{color:"#e8001d"}}>·</span>
          <span>LIVE STREAM</span>
          <span style={{color:"#e8001d"}}>·</span>
          <span>BAHRAIN GP</span>
          <span style={{color:"#e8001d"}}>·</span>
          <span style={{color:statusColor,display:"flex",alignItems:"center",gap:5}}>
            {phase==="processing"&&<span style={{width:5,height:5,borderRadius:"50%",background:"#e8001d",display:"inline-block",animation:"blink 1s infinite"}}/>}
            {statusText}
          </span>
          {results.length>0&&<><span style={{color:"#e8001d"}}>·</span><span style={{color:"#666"}}>LAP {cur?.lap??0}</span></>}
        </div>
        <div style={{display:"flex",alignItems:"center",gap:20,fontFamily:"'Share Tech Mono'",fontSize:10,color:"#333"}}>
          <span>TRACK <span style={{color:"#555"}}>34.2°C</span></span>
          <span>AIR <span style={{color:"#555"}}>22.8°C</span></span>
          <span style={{color:"#252525",cursor:"pointer",fontSize:14}}>⚙</span>
        </div>
      </header>

      {/* MAIN 3-COL GRID */}
      <div style={{display:"grid",gridTemplateColumns:"230px 1fr 330px",height:"calc(100vh - 90px)",overflow:"hidden"}}>

        {/* ═══ LEFT ═══ */}
        <div style={{borderRight:"1px solid #141414",display:"flex",flexDirection:"column",overflow:"hidden"}}>

          {/* Winning Probability */}
          <div style={{padding:"14px 16px",borderBottom:"1px solid #141414",flexShrink:0}}>
            <div style={{fontFamily:"'Share Tech Mono'",fontSize:9,letterSpacing:3,color:"#252525",marginBottom:8,textTransform:"uppercase"}}>Winning Probability</div>
            <ProbChart data={results} w={200} h={72}/>
            <div style={{display:"flex",alignItems:"baseline",gap:8,marginTop:6}}>
              <span style={{fontFamily:"'Orbitron'",fontWeight:900,fontSize:28,color:"#fff"}}>{cur?.prediction?.probability?.toFixed(0)??"—"}%</span>
              <span style={{fontFamily:"'Share Tech Mono'",fontSize:11,color:"#00e676"}}>▲{cur?((cur.prediction?.probability??50)-50).toFixed(1):"0.0"}</span>
            </div>
            <div style={{fontFamily:"'Share Tech Mono'",fontSize:9,color:"#222",marginTop:3,letterSpacing:1}}>
              {jobId?`JOB #${jobId.slice(0,8).toUpperCase()}`:"LECLERC · LAP 16 UPDATE"}
            </div>
          </div>

          {/* Live Telemetry */}
          <div style={{padding:"12px 16px",borderBottom:"1px solid #141414",flexShrink:0}}>
            <div style={{fontFamily:"'Share Tech Mono'",fontSize:9,letterSpacing:3,color:"#252525",marginBottom:10}}>Live Telemetry (OCR)</div>
            {drivers.slice(0,4).map((d,i)=>(
              <div key={i} style={{display:"flex",alignItems:"center",gap:8,padding:"5px 0",borderBottom:"1px solid #0d0d0d"}}>
                <span style={{fontFamily:"'Share Tech Mono'",fontSize:9,color:"#222",width:12,flexShrink:0}}>{d.position??i+1}</span>
                <span style={{width:3,height:16,background:teamColor(d.team??""),flexShrink:0}}/>
                <span style={{fontFamily:"'Share Tech Mono'",fontSize:11,color:"#aaa",flex:1,fontWeight:700}}>
                  {((d.name??d.code??`P${i+1}`).toUpperCase().split(" ").pop()||"").slice(0,3)}
                </span>
                <span style={{fontFamily:"'Share Tech Mono'",fontSize:10,color:i===0?"#00e676":"#444"}}>
                  {d.interval??(i===0?"LEADER":"—")}
                </span>
              </div>
            ))}
          </div>

          {/* Race Timeline */}
          <div style={{padding:"12px 16px",borderBottom:"1px solid #141414",flexShrink:0}}>
            <div style={{fontFamily:"'Share Tech Mono'",fontSize:9,letterSpacing:3,color:"#252525",marginBottom:12}}>Race Timeline</div>
            <div style={{position:"relative",paddingLeft:18}}>
              <div style={{position:"absolute",left:5,top:4,bottom:4,width:1,background:"#141414"}}/>
              {[{c:"#e8001d",l:"BOX BOX",s:"LAP 32 · SECTOR 2"},{c:"#ffeb3b",l:"YELLOW FLAG S2",s:"LAP 28 · SECTOR 2"},{c:"#9c27b0",l:"FASTEST LAP",s:"LAP 15 · SECTOR 2"},{c:"#00e676",l:"RACE START",s:"LAP 1 · SECTOR 1"}].map((ev,i)=>(
                <div key={i} style={{marginBottom:14,position:"relative"}}>
                  <div style={{position:"absolute",left:-14,top:3,width:8,height:8,borderRadius:"50%",background:ev.c}}/>
                  <div style={{fontFamily:"'Share Tech Mono'",fontSize:10,color:ev.c,fontWeight:700,letterSpacing:.5}}>{ev.l}</div>
                  <div style={{fontFamily:"'Share Tech Mono'",fontSize:9,color:"#252525",marginTop:2}}>{ev.s}</div>
                </div>
              ))}
            </div>
          </div>

          {/* ML Prediction */}
          {cur&&(
            <div style={{padding:"12px 16px",background:"#0a0a0a",flexShrink:0}}>
              <div style={{fontFamily:"'Share Tech Mono'",fontSize:9,letterSpacing:3,color:"#252525",marginBottom:10}}>ML Prediction</div>
              <div style={{display:"flex",alignItems:"center",gap:14}}>
                <div style={{width:52,height:52,borderRadius:"50%",border:"2px solid #1a1a1a",display:"flex",alignItems:"center",justifyContent:"center",background:"#0d0d0d",flexShrink:0}}>
                  <span style={{fontFamily:"'Orbitron'",fontWeight:900,fontSize:18,color:"#ffd700",lineHeight:1}}>P{cur.prediction?.position_predite??"—"}</span>
                </div>
                <div>
                  <div style={{fontFamily:"'Share Tech Mono'",fontSize:10,color:"#666"}}>{cur.prediction?.probability?.toFixed(1)}% CONF.</div>
                  <div style={{fontFamily:"'Share Tech Mono'",fontSize:9,color:"#252525",marginTop:2}}>≈ {cur.prediction?.position_exacte?.toFixed(2)}</div>
                  <div style={{fontFamily:"'Share Tech Mono'",fontSize:9,color:"#252525",marginTop:1}}>T={cur.timestamp}s</div>
                </div>
              </div>
              <div style={{height:2,background:"#111",marginTop:10}}>
                <div style={{height:"100%",width:`${cur.prediction?.probability??0}%`,background:"linear-gradient(90deg,#e8001d,#ffd700)",transition:"width .8s"}}/>
              </div>
            </div>
          )}

          <div style={{flex:1}}/>
        </div>

        {/* ═══ CENTER ═══ */}
        <div style={{display:"flex",flexDirection:"column",borderRight:"1px solid #141414",overflow:"hidden"}}>

          {/* Video / Upload zone */}
          <div
            style={{position:"relative",background:"#0d0d0d",borderBottom:"1px solid #141414",cursor:phase==="idle"?"pointer":"default",flex:"0 0 auto",aspectRatio:"16/9",maxHeight:"40vh",overflow:"hidden",outline:drag?"2px solid #e8001d":"none"}}
            onClick={()=>phase==="idle"&&fileRef.current?.click()}
            onDragOver={e=>{e.preventDefault();setDrag(true);}}
            onDragLeave={()=>setDrag(false)}
            onDrop={onDrop}
          >
            <input ref={fileRef} type="file" accept="video/*" style={{display:"none"}} onChange={e=>setFile(e.target.files[0])}/>

            {phase==="idle"&&(
              <div style={{position:"absolute",inset:0,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",gap:12}}>
                <div style={{width:48,height:48,border:`2px solid ${drag?"#e8001d":"#1e1e1e"}`,borderRadius:"50%",display:"flex",alignItems:"center",justifyContent:"center",transition:"all .2s"}}>
                  <span style={{fontSize:20,color:drag?"#e8001d":"#252525"}}>↑</span>
                </div>
                {file?(
                  <>
                    <div style={{fontFamily:"'Orbitron'",fontSize:11,letterSpacing:2,color:"#ffd700",textAlign:"center",maxWidth:"60%",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{file.name}</div>
                    <div style={{fontFamily:"'Share Tech Mono'",fontSize:9,color:"#333",letterSpacing:2}}>{(file.size/1e6).toFixed(1)} MB · READY</div>
                    <button onClick={e=>{e.stopPropagation();upload();}} style={{fontFamily:"'Orbitron'",fontSize:10,letterSpacing:3,background:"#e8001d",color:"#fff",border:"none",padding:"10px 32px",cursor:"pointer",marginTop:4,textTransform:"uppercase"}}>▶ ANALYZE</button>
                  </>
                ):(
                  <>
                    <div style={{fontFamily:"'Orbitron'",fontSize:11,letterSpacing:3,color:"#252525",textTransform:"uppercase"}}>Drag & Drop Your Race Footage</div>
                    <div style={{fontFamily:"'Share Tech Mono'",fontSize:10,color:"#1a1a1a",letterSpacing:3}}>MP4 · MKV · AVI</div>
                  </>
                )}
              </div>
            )}

            {(phase==="uploading"||phase==="processing")&&(
              <div style={{position:"absolute",inset:0,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",gap:14,background:"#080808"}}>
                <div style={{fontFamily:"'Orbitron'",fontSize:10,letterSpacing:3,color:"#e8001d"}}>
                  {phase==="uploading"?"UPLOADING...":`ANALYZING — FRAME ${results.length}`}
                </div>
                <div style={{width:"55%",height:2,background:"#141414"}}>
                  <div style={{height:"100%",width:`${progress}%`,background:"linear-gradient(90deg,#e8001d,#ffd700)",transition:"width .5s"}}/>
                </div>
                <div style={{fontFamily:"'Share Tech Mono'",fontSize:9,color:"#252525",letterSpacing:2}}>{progress}%</div>
              </div>
            )}

            {(phase==="done"||(phase==="processing"&&results.length>0))&&cur&&(
              <>
                <div style={{position:"absolute",inset:0,background:"radial-gradient(ellipse at 30% 50%, #0d0815 0%, #080808 70%)"}}/>
                <div style={{position:"absolute",top:14,left:14,background:"rgba(0,0,0,.8)",border:"1px solid #1a1a1a",padding:"8px 12px",backdropFilter:"blur(6px)"}}>
                  <div style={{fontFamily:"'Share Tech Mono'",fontSize:8,color:"#333",letterSpacing:2,marginBottom:3}}>CURRENT FOCUS</div>
                  <div style={{fontFamily:"'Rajdhani'",fontSize:14,fontWeight:700,color:"#fff"}}>{cur.drivers?.[0]?.name??"RACE ANALYSIS"}</div>
                  <div style={{fontFamily:"'Share Tech Mono'",fontSize:9,color:"#555",marginTop:2}}>PREDICTED P{cur.prediction?.position_predite} · {cur.prediction?.probability?.toFixed(1)}%</div>
                </div>
                {indicators.length>0&&(
                  <div style={{position:"absolute",top:14,right:14,display:"flex",flexDirection:"column",gap:5}}>
                    {indicators.map(k=><IndCard key={k} name={k}/>)}
                  </div>
                )}
                <div style={{position:"absolute",bottom:0,left:0,right:0,padding:"6px 14px",background:"linear-gradient(0,#000,transparent)",display:"flex",alignItems:"center",gap:10}}>
                  <span style={{fontFamily:"'Share Tech Mono'",fontSize:9,color:"#333"}}>LIVE RACE</span>
                  <div style={{flex:1,height:2,background:"#1a1a1a",position:"relative"}}>
                    <div style={{position:"absolute",left:0,top:0,height:"100%",width:`${(cur.lap/(results.length||1))*100}%`,background:"#e8001d"}}/>
                  </div>
                  <span style={{fontFamily:"'Share Tech Mono'",fontSize:9,color:"#444"}}>LAP {cur.lap}</span>
                </div>
              </>
            )}

            {phase==="error"&&(
              <div style={{position:"absolute",inset:0,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",gap:10}}>
                <span style={{color:"#e8001d",fontSize:24}}>⚠</span>
                <div style={{fontFamily:"'Share Tech Mono'",fontSize:10,color:"#e8001d",letterSpacing:1,textAlign:"center",maxWidth:"70%"}}>{errMsg}</div>
                <button onClick={()=>{setPhase("idle");setFile(null);}} style={{fontFamily:"'Orbitron'",fontSize:9,letterSpacing:2,background:"transparent",color:"#333",border:"1px solid #1a1a1a",padding:"7px 18px",cursor:"pointer",marginTop:6}}>RESET</button>
              </div>
            )}
          </div>

          {/* Lap chips bar */}
          {results.length>0&&(
            <div style={{borderBottom:"1px solid #141414",background:"#0a0a0a",flexShrink:0}}>
              <div ref={lapRef} style={{display:"flex",gap:3,overflowX:"auto",padding:"6px 10px",scrollbarWidth:"thin"}}>
                {results.map(r=>{
                  const hc=r.commentary_llm&&!r.commentary_llm.startsWith("Erreur")&&r.commentary_llm!=="Commentaire en attente...";
                  const active=r.lap===selLap;
                  return(
                    <div key={r.lap} data-lap={r.lap} onClick={()=>setSelLap(r.lap)}
                      style={{flexShrink:0,width:32,height:32,background:active?"#e8001d":"#111",border:`1px solid ${active?"#e8001d":"#1a1a1a"}`,display:"flex",alignItems:"center",justifyContent:"center",cursor:"pointer",fontFamily:"'Share Tech Mono'",fontSize:9,color:active?"#fff":"#333",position:"relative",transition:"all .15s"}}>
                      {r.lap}
                      {hc&&<span style={{position:"absolute",top:2,right:2,width:3,height:3,borderRadius:"50%",background:"#ffd700"}}/>}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Bottom panels: Victory Prob + Live Timing */}
          <div style={{flex:1,display:"grid",gridTemplateColumns:"1fr 1fr",overflow:"hidden",minHeight:0}}>

            {/* Victory Probability */}
            <div style={{borderRight:"1px solid #141414",padding:"12px 14px",overflow:"hidden",display:"flex",flexDirection:"column"}}>
              <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:8,flexShrink:0}}>
                <div>
                  <div style={{fontFamily:"'Share Tech Mono'",fontSize:9,letterSpacing:3,color:"#e8001d",marginBottom:2}}>VICTORY PROBABILITY</div>
                  <div style={{fontFamily:"'Share Tech Mono'",fontSize:8,color:"#1e1e1e",letterSpacing:1}}>MODEL: GEMINI-2.5-FLASH</div>
                </div>
                <span style={{fontFamily:"'Share Tech Mono'",fontSize:8,color:"#1e1e1e"}}>{withComment}/{results.length}</span>
              </div>
              <div style={{flex:1,minHeight:0}}>
                <ProbChart data={results} w={400} h={100}/>
              </div>
              {results.length>1&&(
                <div style={{display:"flex",gap:12,marginTop:6,fontFamily:"'Share Tech Mono'",fontSize:9,flexShrink:0}}>
                  <span style={{color:"#222"}}>MIN <span style={{color:"#e8001d"}}>{Math.min(...results.map(d=>d.prediction?.probability??50)).toFixed(1)}%</span></span>
                  <span style={{color:"#222"}}>MAX <span style={{color:"#00e676"}}>{Math.max(...results.map(d=>d.prediction?.probability??50)).toFixed(1)}%</span></span>
                </div>
              )}
            </div>

            {/* Live Timing */}
            <div style={{padding:"12px 14px",overflow:"auto"}}>
              <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:10,flexShrink:0}}>
                <div style={{fontFamily:"'Share Tech Mono'",fontSize:9,letterSpacing:3,color:"#252525"}}>LIVE TIMING</div>
                <div style={{fontFamily:"'Share Tech Mono'",fontSize:8,color:"#9c27b0",border:"1px solid #9c27b033",padding:"2px 7px",letterSpacing:1}}>◈ SECTOR 1: PURPLE</div>
              </div>
              {drivers.slice(0,6).map((d,i)=>(
                <div key={i} style={{display:"flex",alignItems:"center",gap:8,padding:"7px 0",borderBottom:"1px solid #0d0d0d"}}>
                  <span style={{fontFamily:"'Share Tech Mono'",fontSize:9,color:"#252525",width:12,flexShrink:0}}>{d.position??i+1}</span>
                  <span style={{width:3,height:22,background:teamColor(d.team??""),flexShrink:0}}/>
                  <div style={{flex:1,minWidth:0}}>
                    <div style={{fontFamily:"'Rajdhani'",fontSize:12,fontWeight:700,color:"#bbb",letterSpacing:.5,whiteSpace:"nowrap",overflow:"hidden",textOverflow:"ellipsis"}}>{(d.name??d.code??"—").toUpperCase()}</div>
                    <div style={{fontFamily:"'Share Tech Mono'",fontSize:8,color:"#222",marginTop:1}}>{(d.team??"—").toUpperCase()}</div>
                  </div>
                  <span style={{fontFamily:"'Share Tech Mono'",fontSize:10,color:(d.interval==="LEADER"||i===0)?"#00e676":"#444",flexShrink:0}}>
                    {d.interval??(i===0?"LEADER":"—")}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ═══ RIGHT ═══ */}
        <div style={{display:"flex",flexDirection:"column",background:"#0a0a0a",overflow:"hidden"}}>

          {/* Tabs */}
          <div style={{display:"flex",borderBottom:"1px solid #141414",flexShrink:0}}>
            {[["commentary","AI COMMENTARY"],["strategy","STRATEGY INSIGHTS"]].map(([key,label])=>(
              <button key={key} onClick={()=>setTab(key)} style={{flex:1,padding:"13px 0",background:"transparent",border:"none",borderBottom:tab===key?"2px solid #e8001d":"2px solid transparent",fontFamily:"'Share Tech Mono'",fontSize:9,letterSpacing:2,color:tab===key?"#fff":"#252525",cursor:"pointer",transition:"all .2s",textTransform:"uppercase"}}>
                {label}
              </button>
            ))}
          </div>

          {/* Commentary feed */}
          <div ref={cmtRef} style={{flex:1,overflowY:"auto",padding:"0 14px"}}>
            {toShow.length===0?(
              <div style={{display:"flex",alignItems:"center",justifyContent:"center",height:"100%"}}>
                <span style={{fontFamily:"'Share Tech Mono'",fontSize:10,color:"#1e1e1e",letterSpacing:3}}>WAITING FOR RACE FEED...</span>
              </div>
            ):(
              toShow.map((r,i)=>(
                <div key={`${r.lap}-${i}`} style={{animation:"fadeup .35s ease forwards",opacity:0,animationDelay:`${i*.04}s`,animationFillMode:"forwards"}}>
                  {tab==="commentary"&&(
                    <>
                      <CommentItem persona="journalist" text={r.commentary_llm} lap={r.lap}/>
                      {r.commentary_rag&&r.commentary_rag!=="Commentaire en attente..."&&!r.commentary_rag.startsWith("Erreur")&&(
                        <CommentItem persona="professor" text={r.commentary_rag} lap={r.lap}/>
                      )}
                    </>
                  )}
                  {tab==="strategy"&&(
                    <div style={{padding:"12px 0",borderBottom:"1px solid #141414"}}>
                      <div style={{fontFamily:"'Share Tech Mono'",fontSize:9,color:"#252525",marginBottom:8}}>LAP {r.lap} · P{r.prediction?.position_predite} · {r.prediction?.probability?.toFixed(1)}%</div>
                      <div style={{display:"flex",flexWrap:"wrap",gap:6}}>
                        {Object.entries(r.indicators??{}).filter(([,v])=>v).map(([k])=>(
                          <IndCard key={k} name={k}/>
                        ))}
                        {!Object.values(r.indicators??{}).some(Boolean)&&(
                          <span style={{fontFamily:"'Share Tech Mono'",fontSize:9,color:"#1e1e1e"}}>NO INDICATORS DETECTED</span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>

          {/* Bottom summary */}
          {phase==="done"&&(
            <div style={{padding:"10px 14px",borderTop:"1px solid #141414",background:"#0d0d0d",flexShrink:0}}>
              <div style={{display:"flex",justifyContent:"space-between",fontFamily:"'Share Tech Mono'",fontSize:9,color:"#252525"}}>
                <span>FRAMES <span style={{color:"#555"}}>{results.length}</span></span>
                <span>COMMENTS <span style={{color:"#00e676"}}>{withComment}</span></span>
                <span onClick={()=>{setPhase("idle");setFile(null);setResults([]);setJobId(null);setSelLap(null);}} style={{color:"#e8001d",cursor:"pointer",letterSpacing:1}}>↺ NEW RACE</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <Ticker results={results}/>
    </div>
  );
}