import React from 'react';
import { Flag, ShieldAlert, Ban, Timer } from 'lucide-react';

const IncidentCard = ({ type = 'YELLOW FLAG', text = 'Lap Incident', icon: CustomIcon }) => {
  const configs = {
    'GREEN FLAG': { 
      bg: '#4caf50', 
      label: 'Track Clear', 
      icon: Flag, 
      textColor: 'white' 
    },
    'SAFETY CAR': { 
      bg: '#ffeb3b', 
      label: 'Lap Incident', 
      icon: ShieldAlert, 
      textColor: 'black' 
    },
    'RED FLAG': { 
      bg: '#e8001d', 
      label: 'Session Stopped', 
      icon: Ban, 
      textColor: 'white' 
    },
    'FASTEST LAP': { 
      bg: '#9c27b0', 
      label: '1:29:359', 
      icon: Timer, 
      textColor: 'white' 
    }
  };

  const current = configs[type] || configs['SAFETY CAR'];
  const Icon = current.icon;

  return (
    <div 
      className="absolute top-4 right-4 z-40 w-56 p-4 rounded-xl shadow-2xl animate-in slide-in-from-right-4 duration-500"
      style={{ 
        backgroundColor: current.bg, 
        color: current.textColor 
      }}
    >
      <div className="flex justify-between items-start mb-3">
        <div className="flex flex-col">
           <span className="text-[12px] font-black tracking-tighter italic opacity-80 leading-none">F1 OFFICIAL NEWS</span>
           <span className="text-[8px] font-bold uppercase tracking-[0.2em] mt-1 opacity-60">Formula 1 Bahrain Grand Prix</span>
        </div>
        <div className="text-[8px] font-bold border rounded-sm px-1 py-0.5 opacity-60 uppercase" style={{ borderColor: current.textColor }}>RACE</div>
      </div>
      
      <div className="flex items-center justify-between gap-4 mt-6">
        <div className="flex flex-col">
          <h4 className="text-xl font-black italic tracking-tighter leading-none mb-1 font-display uppercase">{type}</h4>
          <span className="text-[10px] uppercase tracking-widest font-bold opacity-80 mono">{text || current.label}</span>
        </div>
        <Icon size={32} strokeWidth={3} className={type === 'SAFETY CAR' ? 'animate-pulse' : ''} />
      </div>
      
      {/* Small F1 graphic line in bottom right */}
      <div className="absolute bottom-2 right-4 flex gap-0.5 opacity-20">
         <div className="w-1.5 h-1 bg-current"></div>
         <div className="w-3 h-1 bg-current"></div>
         <div className="w-6 h-1 bg-current"></div>
      </div>
    </div>
  );
};

export default IncidentCard;
