import React from 'react';

const ProbabilityGraph = ({ percentage = 82 }) => (
  <div className="relative h-16 w-full overflow-hidden rounded-sm bg-black/40 border border-white/5 mb-2">
    <svg viewBox="0 0 100 40" className="w-full h-full" preserveAspectRatio="none">
      <path
        d="M0 40 L0 35 Q10 32, 20 34 T40 30 T60 25 T80 15 T100 10 L100 40 Z"
        fill="rgba(232, 0, 29, 0.2)"
      />
      <path
        d="M0 35 Q10 32, 20 34 T40 30 T60 25 T80 15 T100 10"
        fill="none"
        stroke="var(--f1-red)"
        strokeWidth="2"
      />
    </svg>
    <div className="absolute inset-0 p-3 bg-gradient-to-t from-black/20 to-transparent flex flex-col justify-between">
       <div className="flex items-baseline gap-2">
          <span className="text-[32px] font-bold text-white font-display leading-none leading-[0.8] tracking-tighter" style={{ fontFamily: 'var(--font-display)' }}>{percentage}%</span>
          <span className="text-[14px] text-[#00e676] font-bold leading-none tracking-tight">▲7.4%</span>
       </div>
    </div>
  </div>
);

const TimelineItem = ({ type, text, lap, sector, color = 'var(--f1-red)', isLast }) => {
  return (
    <div className="flex gap-4 relative pb-5 group ml-1">
      {/* Circle dot and Vertical line */}
      <div className="flex flex-col items-center">
        <div className="w-2.5 h-2.5 rounded-full z-10 border border-black shadow-inner" style={{ backgroundColor: color }}></div>
        {!isLast && <div className="w-[1px] h-full bg-[#222] absolute top-1.5 left-[4.5px]"></div>}
      </div>
      
      <div className="flex flex-col gap-0.5 -mt-0.5">
        <span className="text-[11px] font-bold text-white uppercase tracking-[0.1em]">{text}</span>
        <span className="text-[10px] text-[#555] font-mono tracking-widest uppercase font-bold" style={{ fontFamily: 'var(--font-mono)' }}>LAP {lap} · SECTOR {sector}</span>
      </div>
    </div>
  );
}

const LeftPanel = ({ currentData, results }) => {
  const prob = currentData?.prediction?.probability || 82;
  const driverName = currentData?.drivers?.[0]?.code || 'LECLERC';
  const lapNum = currentData?.lap || 16;

  const events = [
    { type: 'box', text: 'BOX BOX', lap: 32, sector: 2, color: '#e8001d' },
    { type: 'yellow', text: 'YELLOW FLAG S2', lap: 28, sector: 2, color: '#ffeb3b' },
    { type: 'fastest', text: 'FASTEST LAP', lap: 15, sector: 2, color: '#9c27b0' },
    { type: 'start', text: 'RACE START', lap: 1, sector: 1, color: '#00e676' }
  ];

  return (
    <div className="left-column h-full overflow-hidden flex flex-col gap-3" style={{ width: '280px' }}>
      {/* Winning Probability */}
      <div className="f1-card p-4 flex flex-col gap-2 shrink-0">
        <h3 className="text-[10px] text-white/40 tracking-[0.3em] font-bold border-l-2 border-[#e8001d] pl-3 uppercase mb-1">Winning Probability</h3>
        <ProbabilityGraph percentage={Math.round(prob)} />
        <div className="px-1">
            <span className="text-[11px] text-[#666] font-mono uppercase font-bold tracking-[0.2em] font-mono" style={{ fontFamily: 'var(--font-mono)' }}>
              {driverName} · LAP {lapNum} UPDATE
            </span>
        </div>
      </div>

      {/* Race Timeline */}
      <div className="f1-card p-4 flex-1 flex flex-col gap-3 min-h-0 bg-[#0d0d0d]">
        <h3 className="text-[10px] text-white/40 tracking-[0.3em] font-bold border-l-2 border-[#e8001d] pl-3 uppercase mb-1">Race Timeline</h3>
        <div className="flex-1 overflow-y-auto pr-2 mt-4 scrollbar-hide">
          {events.map((e, idx) => (
             <TimelineItem 
              key={idx}
              type={e.type} 
              text={e.text} 
              lap={e.lap} 
              sector={e.sector} 
              color={e.color} 
              isLast={idx === events.length - 1}
             />
          ))}
        </div>
      </div>
    </div>
  );
};

export default LeftPanel;
