import React from 'react';

const TickerItem = ({ iconText, iconColor, text, color = '#ffffff' }) => (
  <div className="flex items-center gap-4 pr-32 shrink-0">
    {iconText && <span style={{ color: iconColor, fontWeight: '900', fontSize: '14px' }}>{iconText}</span>}
    <span className="text-[11px] font-black tracking-[0.2em] whitespace-nowrap uppercase italic" style={{ color }}>
      {text}
    </span>
  </div>
);

const Separator = () => (
  <span style={{ color: '#e8001d', margin: '0 16px', fontWeight: 'bold' }}>·</span>
);

const Ticker = () => {
  return (
    <div className="h-10 bg-[#e8001d] w-full flex items-center overflow-hidden relative shadow-[0_-5px_30px_rgba(232,0,29,0.3)] border-t border-black/10">
      <div className="ticker-animate flex items-center">
        <TickerItem 
          iconText="▶" 
          iconColor="#ffeb3b"
          text="YELLOW FLAG IN SECTOR 3 — MAGNUSSEN OFF TRACK" 
        />
        <Separator />
        <TickerItem 
          iconText="★" 
          iconColor="#ffd700"
          text="NEW FASTEST LAP: MAX VERSTAPPEN - 1:32.451" 
        />
        <Separator />
        <TickerItem 
          iconText="↺" 
          iconColor="#fff"
          text="PIT WINDOW OPEN FOR MEDIUM TIRE RUNNERS" 
        />
        <Separator />
        <TickerItem 
           iconText="★" 
           iconColor="#ffd700"
           text="RACE PROGRESS: LAP 16/57 — TRACK TEMP 34.2°C — AIR TEMP 22.8°C" 
        />
        <Separator />
        {/* DUPLICATE FOR INFINITE LOOP EFFECT */}
        <TickerItem 
          iconText="▶" 
          iconColor="#ffeb3b"
          text="YELLOW FLAG IN SECTOR 3 — MAGNUSSEN OFF TRACK" 
        />
        <Separator />
        <TickerItem 
          iconText="★" 
          iconColor="#ffd700"
          text="NEW FASTEST LAP: MAX VERSTAPPEN - 1:32.451" 
        />
        <Separator />
        <TickerItem 
          iconText="↺" 
          iconColor="#fff"
          text="PIT WINDOW OPEN FOR MEDIUM TIRE RUNNERS" 
        />
        <Separator />
        <TickerItem 
           iconText="★" 
           iconColor="#ffd700"
           text="RACE PROGRESS: LAP 16/57 — TRACK TEMP 34.2°C — AIR TEMP 22.8°C" 
        />
      </div>
      
      <style>{`
        .ticker-animate {
          display: flex;
          animation: ticker-scroll 35s linear infinite;
        }
        @keyframes ticker-scroll {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
      `}</style>
    </div>
  );
};

export default Ticker;
