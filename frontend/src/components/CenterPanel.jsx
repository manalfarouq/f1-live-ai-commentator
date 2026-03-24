import React from 'react';
import { Play, Maximize2, Upload, AlertTriangle, Flag, Cpu } from 'lucide-react';

const VictoryChart = ({ blueCurve = [], orangeCurve = [] }) => (
  <div className="relative h-28 w-full bg-[#111] overflow-hidden rounded border border-white/5">
    <div className="absolute top-2 right-2 text-[8px] font-bold text-white/40 tracking-widest border border-white/10 px-1.5 py-0.5 rounded uppercase">
      MODEL: GEMINI-1.5-FLASH
    </div>
    <svg viewBox="0 0 100 40" className="w-full h-full" preserveAspectRatio="none">
       {/* Axis lines */}
       <line x1="0" y1="35" x2="100" y2="35" stroke="rgba(255,255,255,0.05)" strokeWidth="0.5" />
       {/* Main Red Curve (instead of cyan) */}
       <defs>
          <linearGradient id="redGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#e8001d" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#e8001d" stopOpacity="0" />
          </linearGradient>
       </defs>
       <path
        d="M0 35 Q10 15, 20 25 T40 10 T60 20 T80 5 T100 15 L100 40 L0 40 Z"
        fill="url(#redGradient)"
      />
      <path
        d="M0 35 Q10 15, 20 25 T40 10 T60 20 T80 5 T100 15"
        fill="none"
        stroke="#e8001d"
        strokeWidth="2"
      />
      {/* Orange/Dotted Curve */}
       <path
        d="M0 35 Q15 30, 30 32 T55 25 T85 10 T100 5"
        fill="none"
        stroke="#ff9100"
        strokeWidth="1.5"
        strokeDasharray="2,2"
      />
    </svg>
    <div className="absolute bottom-2 left-2 flex gap-4 text-[9px] font-mono tracking-tighter uppercase text-white/40 font-bold">
       <div className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-[#e8001d]"></div> FERRARI (LEC)</div>
       <div className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full border border-[#ff9100] border-dashed"></div> RED BULL (VER)</div>
    </div>
  </div>
);

const DriverTimingRow = ({ pos, color, name, team, interval, isPurple }) => {
  const teamColors = {
    'Ferrari': '#e8001d',
    'Red Bull': '#001aef',
    'Mercedes': '#00d2be',
    'McLaren': '#ff8700'
  };
  const teamColor = teamColors[team] || color;

  return (
    <div className="flex items-center gap-3 py-2 px-3 border-b border-white/5 hover:bg-white/5 transition-colors group">
      <div className="w-[24px] h-[24px] flex items-center justify-center bg-[#222] text-[12px] font-mono font-bold text-white shrink-0">
        {pos}
      </div>
      <div className="w-[3px] h-[20px] shrink-0" style={{ backgroundColor: teamColor }}></div>
      <div className="flex flex-col flex-1 truncate">
        <span className="font-bold uppercase tracking-tight text-[14px] text-white font-body leading-tight truncate">{name}</span>
        <span className="text-[11px] text-[#666] uppercase whitespace-nowrap">{team}</span>
      </div>
      <div className="text-right flex flex-col items-end">
        <span className={`text-[12px] font-mono leading-none ${interval === 'LEADER' ? 'text-[#00e676]' : 'text-white'}`}>
          {interval}
        </span>
        {isPurple && <span className="text-[8px] text-purple-400 font-bold mt-1 tracking-widest">PURPLE</span>}
      </div>
    </div>
  );
};

const CenterPanel = ({ videoSrc, uploadedFile, isAnalyzing, progress, yoloAlert, onFileSelect }) => {
  return (
    <div className="center-column h-full">
      {/* Video / Frame / Upload Area */}
      <div 
        className="f1-card flex-1 min-h-[400px] relative bg-[#0a0a0a] flex items-center justify-center overflow-hidden aspect-video group"
      >
        {!uploadedFile ? (
          <div 
            onClick={onFileSelect}
            className="absolute inset-0 m-6 flex flex-col items-center justify-center gap-4 rounded-xl border-2 border-dashed border-white/5 group-hover:border-[#e8001d]/60 group-hover:bg-[#e8001d]/5 transition-all cursor-pointer"
          >
             <div className="p-5 rounded-full bg-white/5 text-white/20 group-hover:text-[#e8001d] transition-all">
               <Upload size={48} />
             </div>
             <div className="flex flex-col items-center text-center">
               <span className="font-black tracking-[0.2em] text-sm text-white/40 transition-colors group-hover:text-white uppercase italic">Drag & Drop Your Race Footage</span>
               <span className="text-[10px] text-white/20 uppercase tracking-[0.2em] mt-2 font-mono">MP4 · MKV · AVI</span>
             </div>
          </div>
        ) : (
          <div className="w-full h-full relative">
            {/* Main view area */}
            <div className="w-full h-full bg-[#111] flex items-center justify-center">
              {videoSrc ? (
                 <img src={videoSrc} className="w-full h-full object-cover" alt="Race Feed" />
              ) : isAnalyzing ? (
                 <div className="flex flex-col items-center gap-6">
                    <span className="text-[#333] font-bold font-display text-2xl tracking-[0.4em] uppercase italic">Analysing Stream...</span>
                    {/* Floating analyzing effect */}
                    <div className="relative w-48 h-48 flex items-center justify-center">
                       <div className="absolute inset-0 border-4 border-[#e8001d]/20 rounded-full"></div>
                       <div className="absolute inset-0 border-t-4 border-[#e8001d] rounded-full animate-spin"></div>
                       <Cpu size={40} className="text-[#e8001d] animate-pulse" />
                    </div>
                 </div>
              ) : (
                 <div className="flex flex-col items-center gap-6">
                    <span className="text-white/60 font-bold font-mono text-sm tracking-[0.2em] uppercase italic">{uploadedFile.name}</span>
                    <button className="bg-[#e8001d] text-white px-8 py-3 font-display font-black tracking-[0.2em] rounded-sm hover:scale-105 transition-transform flex items-center gap-3">
                       <Play size={18} fill="white" /> ANALYZE
                    </button>
                    <span className="text-[#333] font-bold font-display text-lg tracking-[0.3em] uppercase mt-8">Waiting for Race Feed...</span>
                 </div>
              )}
            </div>

            {/* Upload Overlay when processing */}
            {isAnalyzing && (
               <div className="absolute inset-0 bg-black/60 backdrop-blur-sm flex flex-col items-center justify-center gap-4 z-20">
                  <div className="flex flex-col items-center gap-2">
                     <span className="text-xs font-bold tracking-[0.3em] text-[#e8001d] uppercase">Analyzing Footage...</span>
                     <div className="w-64 h-1.5 bg-white/10 rounded-full overflow-hidden mt-6">
                        <div className="h-full bg-[#e8001d] transition-all duration-500" style={{ width: `${progress}%` }}></div>
                     </div>
                     <span className="text-[10px] mono font-mono mt-3 text-white/40 tracking-widest">{progress}% COMPLETE</span>
                  </div>
               </div>
            )}

            {/* Overlays */}
            {!isAnalyzing && videoSrc && (
              <div className="absolute top-6 left-6 z-10 flex flex-col gap-2">
                 <div className="flex flex-col bg-black/80 backdrop-blur-md px-5 py-4 rounded-sm border-l-4 border-white shadow-2xl">
                     <div className="flex items-center gap-2 mb-2">
                        <div className="w-2 h-2 rounded-full bg-[#e8001d] animate-pulse"></div>
                        <span className="text-[10px] font-black tracking-[0.2em] text-white/40 uppercase">Current Focus</span>
                     </div>
                     <div className="flex flex-col">
                        <span className="text-2xl font-black uppercase tracking-tight font-display leading-none text-white mb-2 italic">Max Verstappen</span>
                        <div className="flex items-baseline gap-2">
                           <span className="text-[10px] mono text-white/30 tracking-[0.2em] font-bold">SPEED</span>
                           <span className="text-lg font-bold text-[#e8001d] mono">312 KM/H</span>
                        </div>
                     </div>
                 </div>
              </div>
            )}

            {/* YOLO ALERT OVERLAY */}
            {!isAnalyzing && yoloAlert && (
               <div className="absolute top-6 right-6 z-10 bg-[#ffeb3b] text-black px-6 py-4 flex items-center gap-5 rounded-sm shadow-2xl border-b-4 border-black/20">
                  <AlertTriangle size={24} fill="black" />
                  <div className="flex flex-col">
                     <span className="text-[12px] font-black uppercase tracking-[0.1em]">{yoloAlert.text || 'YELLOW FLAG DETECTED'}</span>
                     <span className="text-[11px] font-bold mono uppercase opacity-70">SECTOR 2 · TURN 11</span>
                  </div>
               </div>
            )}

            {/* Progress / Status Bottom Overlay */}
            <div className="absolute bottom-0 left-0 right-0 p-8 bg-gradient-to-t from-black/90 to-transparent flex flex-col gap-4">
               <div className="w-full h-1 bg-white/10 rounded-full relative overflow-hidden">
                   <div 
                    className="absolute h-full bg-[#e8001d] transition-all duration-1000" 
                    style={{ width: isAnalyzing ? `${progress}%` : '72%' }}
                   ></div>
               </div>
               <div className="flex items-center justify-between">
                  <div className="flex items-center gap-6">
                     <div className="flex items-center gap-2 bg-[#e8001d] px-4 py-1.5 rounded-sm">
                        <div className="w-2 h-2 rounded-full bg-white animate-pulse"></div>
                        <span className="text-[10px] font-black tracking-[0.2em] text-white uppercase">Live Stream</span>
                     </div>
                     <span className="text-[14px] mono font-bold uppercase tracking-[0.3em] text-white/50">LAP 16 / 57</span>
                  </div>
                  <div className="flex items-center gap-6">
                     <button className="text-white/30 hover:text-white transition-colors"><Play size={20} fill="currentColor" /></button>
                     <button className="text-white/30 hover:text-white transition-colors"><Maximize2 size={20} /></button>
                  </div>
               </div>
            </div>
          </div>
        )}
      </div>

      <div className="flex gap-4 h-[220px]">
        {/* Victory Probability */}
        <div className="f1-card flex-1 p-5 flex flex-col gap-4 bg-[#0d0d0d]">
           <h3 className="text-xs text-white/40 tracking-widest font-bold border-l-2 border-[#e8001d] pl-3 uppercase">Victory Probability</h3>
           <VictoryChart />
        </div>

        {/* Live Timing */}
        <div className="f1-card flex-1 p-0 flex flex-col overflow-hidden bg-[#0d0d0d]">
           <div className="flex justify-between items-center p-4 border-b border-white/5 bg-white/[0.02]">
              <h3 className="text-xs text-white/40 tracking-widest font-bold border-l-2 border-[#00e676] pl-3 uppercase">Live Timing</h3>
              <div className="flex items-center gap-1.5 bg-purple-900/40 px-3 py-1 rounded border border-purple-400/20">
                 <Flag size={11} className="text-purple-400" />
                 <span className="text-[10px] font-black text-purple-400 tracking-tighter uppercase">Sector 1: Purple</span>
              </div>
           </div>
           <div className="flex-1 overflow-y-auto scrollbar-hide py-2">
              <DriverTimingRow pos={1} name="C. LECLERC" team="Ferrari" interval="LEADER" />
              <DriverTimingRow pos={2} name="M. VERSTAPPEN" team="Red Bull" interval="+1.452" />
              <DriverTimingRow pos={3} name="L. HAMILTON" team="Mercedes" interval="+4.891" isPurple={true} />
              <DriverTimingRow pos={4} name="S. PEREZ" team="Red Bull" interval="+5.234" />
              <DriverTimingRow pos={5} name="O. PIASTRI" team="McLaren" interval="+6.112" />
           </div>
        </div>
      </div>
    </div>
  );
};

export default CenterPanel;
