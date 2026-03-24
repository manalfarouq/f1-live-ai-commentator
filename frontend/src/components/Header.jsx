import React from 'react';
import { Zap, Settings, Thermometer, Wind } from 'lucide-react';

const Header = ({ status = 'PRE-RACE', lapInfo = 'LAP 16/57', venue = 'BAHRAIN GP', trackTemp = '34.2°C', airTemp = '22.8°C' }) => {
  
  const getStatusDisplay = () => {
    switch(status.toLowerCase()) {
      case 'analyzing':
        return (
          <div className="flex items-center gap-2">
            <span className="text-white/90">ANALYZING</span>
            <span className="w-1.5 h-1.5 rounded-full bg-[#e8001d] animate-pulse"></span>
          </div>
        );
      case 'completed':
        return <span className="text-[#00e676]">RACE COMPLETE</span>;
      default:
        return <span className="text-[#444]">PRE-RACE</span>;
    }
  };

  return (
    <header className="header-sticky flex items-center justify-between h-[60px] border-b border-[#e8001d] px-6">
      <div className="flex items-center gap-2 w-1/4 shrink-0">
        <Zap className="text-[#e8001d] fill-[#e8001d]" size={20} />
        <h1 className="text-lg font-bold tracking-tighter shrink-0" style={{ fontFamily: 'var(--font-display)' }}>
          F1 LIVE AI COMMENTATOR
        </h1>
      </div>
      
      <div className="flex-1 flex justify-center">
        <div className="flex items-center gap-3 bg-black/40 px-8 py-2 rounded-sm border border-white/5 mx-auto">
          <span className="text-[10px] font-bold tracking-[0.3em] text-white/40 font-mono uppercase">
            • LIVE STREAM • {venue} •
          </span>
          <span className="text-[10px] font-bold tracking-[0.3em] font-mono uppercase">
            {getStatusDisplay()}
          </span>
        </div>
      </div>
      
      <div className="flex items-center justify-end gap-6 w-1/4 shrink-0">
        <div className="flex items-center gap-4 text-[10px] tracking-wider font-mono">
          <div className="flex items-center gap-1.5">
            <Thermometer size={14} className="text-white/20" />
            <span className="text-white/20 uppercase">Track</span>
            <span className="font-bold">{trackTemp}</span>
          </div>
          <div className="flex items-center gap-1.5 ml-2">
            <Wind size={14} className="text-white/20" />
            <span className="text-white/20 uppercase">Air</span>
            <span className="font-bold">{airTemp}</span>
          </div>
        </div>
        <Settings size={18} className="text-white/40 cursor-pointer hover:rotate-90 transition-transform duration-500" />
      </div>
    </header>
  );
};

export default Header;
