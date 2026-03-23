import React, { useState, useEffect, useRef } from 'react';

const PersonaBadge = ({ persona, time }) => {
  const personaColors = {
    JOURNALIST: '#e8001d',
    PROFESSOR: '#00e676',
    ENGINEER: '#00f5ff',
    FAN: '#9c27b0'
  };
  
  return (
    <div className="flex items-center justify-between mb-2 pt-4 first:pt-0 border-t border-white/5 first:border-0 first:mt-0 mt-4">
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: personaColors[persona] }}></div>
        <span className="text-[10px] font-black uppercase tracking-[0.2em] leading-none" style={{ color: personaColors[persona] }}>
          {persona}
        </span>
      </div>
      <span className="text-[9px] mono text-white/10 uppercase tracking-widest font-bold" style={{ fontFamily: 'var(--font-mono)' }}>{time}</span>
    </div>
  );
};

const ChatMessage = ({ persona, text, time, isLoading, isError }) => {
  if (isLoading) {
    return (
      <div className="pb-4 last:border-0 italic text-[11px] text-[#444444] pt-5 font-mono tracking-widest flex items-center gap-2" style={{ fontFamily: 'var(--font-mono)' }}>
         <div className="w-1.5 h-1.5 rounded-full bg-white/5 animate-pulse"></div>
         ⏳ GÉNÉRATION EN COURS...
      </div>
    );
  }
  
  if (isError) {
    return (
      <div className="pb-4 last:border-0 text-[11px] text-[#555555] pt-5 font-mono uppercase tracking-widest flex items-center gap-2" style={{ fontFamily: 'var(--font-mono)' }}>
         <span className="opacity-60">⚠ QUOTA API ATTEINT</span>
      </div>
    );
  }

  return (
    <div className="pb-6 last:border-0">
      <PersonaBadge persona={persona} time={time} />
      <p className="text-[13px] text-white/80 leading-relaxed font-body tracking-wide font-medium">
        {text}
      </p>
    </div>
  );
};

const RightPanel = ({ currentData }) => {
  const [activeTab, setActiveTab] = useState('commentary');
  const chatEndRef = useRef(null);
  
  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [currentData]);

  const getTime = (ts) => {
    if (!ts) {
      const now = new Date();
      return now.toLocaleTimeString('en-GB', { hour12: false });
    }
    const date = new Date(ts * 1000);
    return date.toLocaleTimeString('en-GB', { hour12: false });
  };

  const timestamp = getTime(currentData?.timestamp);

  return (
    <div className="right-column h-full flex flex-col overflow-hidden" style={{ width: '360px' }}>
      <div className="f1-card flex-1 flex flex-col bg-[#111111] overflow-hidden">
        {/* Tabs */}
        <div className="grid grid-cols-2 border-b border-white/[0.03]">
          <button 
            onClick={() => setActiveTab('commentary')}
            className={`py-4 text-[10px] font-black tracking-[0.2em] transition-all uppercase ${activeTab === 'commentary' ? 'text-[#ffffff] border-b-2 border-[#e8001d] bg-transparent' : 'text-[#444444] border-b-2 border-transparent bg-transparent hover:text-white/60'}`}
          >
            AI COMMENTARY
          </button>
          <button 
             onClick={() => setActiveTab('strategy')}
             className={`py-4 text-[10px] font-black tracking-[0.2em] transition-all uppercase ${activeTab === 'strategy' ? 'text-[#ffffff] border-b-2 border-[#e8001d] bg-transparent' : 'text-[#444444] border-b-2 border-transparent bg-transparent hover:text-white/60'}`}
          >
            STRATEGY INSIGHTS
          </button>
        </div>

        {/* Console / Chat Area */}
        <div className="flex-1 overflow-y-auto p-6 scrollbar-hide">
          {!currentData ? (
             <div className="flex-1 flex flex-col items-center justify-center text-center mt-20">
               <span className="text-[#333333] font-bold font-mono tracking-[0.4em] uppercase text-xs" style={{ fontFamily: 'var(--font-mono)' }}>Waiting for Race Feed...</span>
             </div>
          ) : (
             <>
                <div className="flex items-center gap-2 mb-8 opacity-20">
                   <div className="w-full h-[1px] bg-white"></div>
                   <span className="text-[9px] font-bold uppercase tracking-[0.4em] shrink-0 font-mono" style={{ fontFamily: 'var(--font-mono)' }}>Session Live</span>
                   <div className="w-full h-[1px] bg-white"></div>
                </div>

                <ChatMessage 
                  persona="JOURNALIST" 
                  text={currentData.commentary_llm} 
                  isLoading={currentData.commentary_llm === "Commentaire en attente..."}
                  isError={currentData.commentary_llm?.includes('Erreur lors')}
                  time={timestamp} 
                />
                
                <ChatMessage 
                  persona="PROFESSOR" 
                  text={currentData.commentary_rag}
                  isLoading={currentData.commentary_rag === "Commentaire en attente..."}
                  isError={currentData.commentary_rag?.includes('Erreur lors')}
                  time={timestamp} 
                />

                <div ref={chatEndRef} />
             </>
          )}
        </div>
      </div>
    </div>
  );
};

export default RightPanel;
