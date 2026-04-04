import { Component, useState, useEffect, useRef, useCallback, useMemo } from "react";

const TEAM_COLORS = {
  ferrari: "#e8001d", red_bull: "#1e41ff", mercedes: "#00d2be",
  mclaren: "#ff8000", alpine: "#0090ff", aston_martin: "#006f62",
  williams: "#005aff", haas: "#b6babd", alfa: "#900000", alphatauri: "#2b4562",
};

const PERSONA_STYLES = {
  journalist: { label: "JOURNALIST", color: "#e8001d" },
  professor:  { label: "PROFESSOR",  color: "#00e676" },
  engineer:   { label: "ENGINEER",   color: "#00b4ff" },
  fan:        { label: "FAN",        color: "#9c27b0" },
};

const PHASE_STATES = { IDLE: "idle", UPLOADING: "uploading", PROCESSING: "processing", DONE: "done", ERROR: "error" };
const TAB_KEYS     = { COMMENTARY: "commentary", STRATEGY: "strategy", CHAT: "chat" };
const API_BASE_URL = "http://localhost:8001";

const getTeamColor = (team = "") => {
  const n = team.toLowerCase().replace(/\s+/g, "_");
  for (const [k, v] of Object.entries(TEAM_COLORS)) if (n.includes(k)) return v;
  return "#555";
};

const isValidCommentary = (t) => t && !t.startsWith("Erreur") && t !== "Commentaire en attente...";

// ── Custom hook: chat stream ─────────────────────────────────────────────────
const useChatStream = () => {
  const [messages, setMessages]       = useState([]);
  const [streamingText, setStreaming] = useState("");
  const [loading, setLoading]         = useState(false);
  const [error, setError]             = useState("");
  const abortRef = useRef(null);

  const send = useCallback(async (question) => {
    const q = question.trim();
    if (!q || loading) return;
    setError("");
    const newMsgs = [...messages, { role: "user", text: q }];
    setMessages(newMsgs);
    setLoading(true);
    setStreaming("");

    const history = newMsgs.slice(0, -1).map(m => ({
      role: m.role === "user" ? "user" : "assistant",
      content: m.text,
    }));

    abortRef.current = new AbortController();
    let acc = "";

    try {
      const res = await fetch(`${API_BASE_URL}/rag/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q, history }),
        signal: abortRef.current.signal,
      });
      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

      const reader  = res.body.getReader();
      const decoder = new TextDecoder();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        for (const line of decoder.decode(value).split("\n")) {
          if (!line.startsWith("data:")) continue;
          const data = line.slice(5).trim();
          if (data === "[DONE]") continue;
          try {
            const ev = JSON.parse(data);
            if (ev.type === "content_block_delta" && ev.delta?.type === "text_delta") {
              acc += ev.delta.text;
              setStreaming(acc);
            }
          } catch (_e) { /* skip malformed */ }
        }
      }
      setMessages(m => [...m, { role: "assistant", text: acc || "No response." }]);
    } catch (err) {
      if (err.name === "AbortError") {
        if (acc) setMessages(m => [...m, { role: "assistant", text: acc }]);
      } else {
        try {
          const r2 = await fetch(`${API_BASE_URL}/rag/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: q, history }),
          });
          const d = await r2.json();
          setMessages(m => [...m, { role: "assistant", text: d.reponse ?? d.answer ?? "Réponse indisponible." }]);
        } catch (_e) {
          setError("Backend unreachable — start your FastAPI server on port 8001.");
        }
      }
    } finally {
      setLoading(false);
      setStreaming("");
    }
  }, [messages, loading]);

  const stop = useCallback(() => abortRef.current?.abort(), []);
  return { messages, streamingText, loading, error, send, stop };
};

// ── Custom hook: video upload ────────────────────────────────────────────────
const useVideoUpload = () => {
  const [file, setFile]         = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [isDragging, setDrag]   = useState(false);
  const [progress, setProgress] = useState(0);
  const [phase, setPhase]       = useState(PHASE_STATES.IDLE);
  const [error, setError]       = useState("");
  const fileInputRef            = useRef(null);

  const handleDragOver  = useCallback(e => { e.preventDefault(); setDrag(true); }, []);
  const handleDragLeave = useCallback(() => setDrag(false), []);
  const handleDrop      = useCallback(e => {
    e.preventDefault(); setDrag(false);
    const f = e.dataTransfer.files[0];
    if (f?.type.startsWith("video/")) { setFile(f); setVideoUrl(URL.createObjectURL(f)); setError(""); }
    else setError("Please drop a valid video file.");
  }, []);
  const handleFileSelect = useCallback(f => {
    if (!f) return;
    setFile(f); setError(""); setVideoUrl(URL.createObjectURL(f));
  }, []);
  const reset = useCallback(() => {
    setFile(null);
    if (videoUrl) URL.revokeObjectURL(videoUrl);
    setVideoUrl(null); setProgress(0); setPhase(PHASE_STATES.IDLE); setError("");
  }, [videoUrl]);

  return { file, videoUrl, isDragging, progress, phase, error, fileInputRef,
           handleDragOver, handleDragLeave, handleDrop, handleFileSelect,
           reset, setPhase, setProgress, setError };
};

// ── ProbChart ────────────────────────────────────────────────────────────────
const ProbChart = ({ data, w = 480, h = 120 }) => {
  if (!data || data.length < 2) return (
    <div style={{ height: h, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <span style={{ fontFamily: "'Share Tech Mono'", fontSize: 10, color: "#333", letterSpacing: 2 }}>NO DATA</span>
    </div>
  );
  const vals = data.map(d => d.prediction?.probability ?? 50);
  const mn = Math.min(...vals) - 3, mx = Math.max(...vals) + 3;
  const PAD_L = 28, PAD_B = 18, cw = w - PAD_L, ch = h - PAD_B;
  const x = i => PAD_L + (i / (data.length - 1)) * cw;
  const y = v => ch - ((v - mn) / (mx - mn)) * ch;
  const line = data.map((_, i) => `${x(i)},${y(vals[i])}`).join(" ");
  const area = `M${x(0)},${y(vals[0])} ` + data.map((_, i) => `L${x(i)},${y(vals[i])}`).join(" ") +
    ` L${x(data.length - 1)},${ch} L${x(0)},${ch}Z`;
  const yTicks = [mn, mn + (mx - mn) / 2, mx].map(v => ({ v, yPos: y(v) }));
  const xStep  = Math.max(1, Math.floor(data.length / 4));
  const xTicks = data.filter((_, i) => i % xStep === 0 || i === data.length - 1);
  return (
    <svg viewBox={`0 0 ${w} ${h}`} style={{ width: "100%", height: h }} preserveAspectRatio="none">
      <defs>
        <linearGradient id="cg" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#e8001d" stopOpacity=".35" />
          <stop offset="100%" stopColor="#e8001d" stopOpacity="0" />
        </linearGradient>
        <filter id="gl"><feGaussianBlur stdDeviation="2" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
      </defs>
      {yTicks.map((t, i) => (
        <g key={i}>
          <line x1={PAD_L} y1={t.yPos} x2={w} y2={t.yPos} stroke="#1a1a1a" strokeWidth="1" />
          <text x={PAD_L - 4} y={t.yPos + 3} textAnchor="end" fill="#444" fontSize="8" fontFamily="'Share Tech Mono'">{t.v.toFixed(0)}%</text>
        </g>
      ))}
      {xTicks.map((r, i) => {
        const idx = data.indexOf(r);
        return <text key={i} x={x(idx)} y={h - 2} textAnchor="middle" fill="#333" fontSize="8" fontFamily="'Share Tech Mono'">L{r.lap}</text>;
      })}
      <path d={area} fill="url(#cg)" />
      <polyline points={line} fill="none" stroke="#e8001d" strokeWidth="2.5" filter="url(#gl)" />
    </svg>
  );
};

// ── CommentItem ──────────────────────────────────────────────────────────────
const CommentItem = ({ persona, text, lap }) => {
  if (!isValidCommentary(text)) return null;
  const p = PERSONA_STYLES[persona] || PERSONA_STYLES.journalist;
  return (
    <div style={{ padding: "12px 0", borderBottom: "1px solid #141414" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
        <span style={{ width: 6, height: 6, borderRadius: "50%", background: p.color, flexShrink: 0 }} />
        <span style={{ fontFamily: "'Share Tech Mono'", fontSize: 10, letterSpacing: 2, color: p.color }}>{p.label}</span>
        <span style={{ marginLeft: "auto", fontFamily: "'Share Tech Mono'", fontSize: 9, color: "#333" }}>LAP {lap}</span>
      </div>
      <p style={{ fontFamily: "'Rajdhani'", fontSize: 14, lineHeight: 1.65, margin: 0, color: "#aaa" }}>{text}</p>
    </div>
  );
};

// ── Ticker ───────────────────────────────────────────────────────────────────
const Ticker = ({ results }) => {
  const DEFAULT = [
    { icon: "★", c: "#ffd700", text: "NEW FASTEST LAP: MAX VERSTAPPEN — 1:32.451" },
    { icon: "⚑", c: "#ffeb3b", text: "YELLOW FLAG IN SECTOR 3 — MAGNUSSEN OFF TRACK" },
    { icon: "↺", c: "#fff",    text: "PIT WINDOW OPEN FOR MEDIUM TIRE RUNNERS" },
    { icon: "i", c: "#00f5ff", text: "RACE PROGRESS: LAP 16/57 — TRACK TEMP 34.2°C — AIR TEMP 22.8°C" },
  ];
  const items = results.length > 0
    ? results.slice(-6).filter(r => isValidCommentary(r.commentary_llm)).map(r => ({ icon: "▶", c: "#e8001d", text: `LAP ${r.lap} — ${r.commentary_llm}` }))
    : DEFAULT;
  const content = [...items, ...items, ...items];
  const dur = Math.max(30, content.length * 8);
  return (
    <div style={{ position: "fixed", bottom: 0, left: 0, right: 0, height: 36, background: "#080808", borderTop: "1px solid #1a1a1a", overflow: "hidden", zIndex: 200, display: "flex", alignItems: "center" }}>
      <style>{`@keyframes tk{from{transform:translateX(0)}to{transform:translateX(-33.33%)}}`}</style>
      <div style={{ flexShrink: 0, padding: "0 12px", background: "#e8001d", height: "100%", display: "flex", alignItems: "center" }}>
        <span style={{ fontFamily: "'Orbitron'", fontWeight: 900, fontSize: 9, letterSpacing: 2, color: "#fff" }}>LIVE</span>
      </div>
      <div style={{ flex: 1, overflow: "hidden" }}>
        <div style={{ display: "flex", animation: `tk ${dur}s linear infinite`, whiteSpace: "nowrap" }}>
          {content.map((it, i) => (
            <span key={i} style={{ fontFamily: "'Share Tech Mono'", fontSize: 10, color: "#666", padding: "0 24px", display: "inline-flex", alignItems: "center", gap: 8 }}>
              <span style={{ color: it.c, fontSize: 9 }}>{it.icon}</span>{it.text}
              <span style={{ color: "#e8001d", margin: "0 4px" }}>·</span>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

// ── ChatRAG — FIX: bouton ASK visible + indicateur "..." pendant l'attente ──
const ChatRAG = () => {
  const { messages, streamingText, loading, error, send, stop } = useChatStream();
  const [input, setInput] = useState("");
  const endRef = useRef();

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, streamingText]);

  const handleSend = async () => {
    const q = input.trim();
    if (!q || loading) return;
    setInput("");
    await send(q);
  };

  return (
    <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column", overflow: "hidden" }}>
      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "10px 14px", display: "flex", flexDirection: "column", gap: 10, minHeight: 0 }}>
        {messages.length === 0 && !loading && (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%" }}>
            <span style={{ fontFamily: "'Share Tech Mono'", fontSize: 9, color: "#222", letterSpacing: 2, textAlign: "center", lineHeight: 2.4 }}>
              ASK ANYTHING ABOUT F1<br />RULES · STRATEGY · HISTORY
            </span>
          </div>
        )}
        {error && (
          <div style={{ padding: "10px 12px", background: "#1a0000", border: "1px solid #e8001d44", borderLeft: "3px solid #e8001d", fontFamily: "'Share Tech Mono'", fontSize: 9, color: "#e8001d", lineHeight: 1.8 }}>
            ⚠ {error}
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: msg.role === "user" ? "flex-end" : "flex-start" }}>
            {msg.role === "assistant" && (
              <span style={{ fontFamily: "'Share Tech Mono'", fontSize: 8, color: "#e8001d", letterSpacing: 2, marginBottom: 3 }}>◈ AI EXPERT</span>
            )}
            <div style={{
              maxWidth: "82%", padding: "9px 13px", borderRadius: 3,
              background: msg.role === "user" ? "#1a0000" : "#111",
              border: `1px solid ${msg.role === "user" ? "#e8001d44" : "#222"}`,
              borderLeft: msg.role === "assistant" ? "3px solid #e8001d" : "none",
              fontFamily: "'Rajdhani'", fontSize: 13, lineHeight: 1.6,
              color: msg.role === "user" ? "#ff6060" : "#bbb",
            }}>
              {msg.text}
            </div>
          </div>
        ))}

        {/* ── Loading indicator "..." ─────────────────────────────────────── */}
        {loading && (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start" }}>
            <span style={{ fontFamily: "'Share Tech Mono'", fontSize: 8, color: "#e8001d", letterSpacing: 2, marginBottom: 3 }}>◈ AI EXPERT</span>
            <div style={{ maxWidth: "82%", padding: "9px 13px", borderRadius: 3, background: "#111", border: "1px solid #222", borderLeft: "3px solid #e8001d", fontFamily: "'Rajdhani'", fontSize: 13, lineHeight: 1.6, color: "#bbb" }}>
              {streamingText
                ? <>{streamingText}<span style={{ animation: "blink 1s infinite" }}>▌</span></>
                : (
                  /* Dots animation while waiting for first token */
                  <span style={{ display: "inline-flex", gap: 4, alignItems: "center" }}>
                    {[0, 1, 2].map(j => (
                      <span key={j} style={{ width: 6, height: 6, borderRadius: "50%", background: "#e8001d", display: "inline-block", animation: "blink 1.2s infinite", animationDelay: `${j * 0.4}s` }} />
                    ))}
                  </span>
                )
              }
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* ── Input + bouton ASK toujours visible ──────────────────────────── */}
      <div style={{ borderTop: "1px solid #1a1a1a", padding: "10px 14px", background: "#0a0a0a", flexShrink: 0, display: "flex", gap: 8, alignItems: "center" }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && !e.shiftKey && handleSend()}
          placeholder="Ask about F1 rules, strategy…"
          disabled={loading}
          style={{
            flex: 1, background: "#0d0d0d", border: "1px solid #1e1e1e",
            borderLeft: "2px solid #e8001d", padding: "9px 11px",
            fontFamily: "'Share Tech Mono'", fontSize: 10, color: "#bbb",
            outline: "none", letterSpacing: 1, borderRadius: 0,
            opacity: loading ? 0.6 : 1,
          }}
        />
        {loading
          ? (
            <button onClick={stop} style={{ background: "#1a0000", border: "1px solid #e8001d", padding: "9px 14px", fontFamily: "'Orbitron'", fontSize: 9, letterSpacing: 1, color: "#e8001d", cursor: "pointer", flexShrink: 0, minWidth: 52 }}>
              ■ STOP
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              style={{
                background: input.trim() ? "#e8001d" : "#1a1a1a",
                border: "none", padding: "9px 14px",
                fontFamily: "'Orbitron'", fontSize: 9, letterSpacing: 1,
                color: input.trim() ? "#fff" : "#444",
                cursor: input.trim() ? "pointer" : "not-allowed",
                transition: "background .2s, color .2s",
                flexShrink: 0, minWidth: 52,
              }}
            >
              ASK
            </button>
          )
        }
      </div>
    </div>
  );
};

// ── ErrorBoundary ────────────────────────────────────────────────────────────
class ErrorBoundary extends Component {
  constructor(p) { super(p); this.state = { hasError: false, error: null }; }
  static getDerivedStateFromError(e) { return { hasError: true, error: e }; }
  render() {
    if (this.state.hasError) return (
      <div style={{ background: "#080808", color: "#e8001d", height: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 16, fontFamily: "monospace" }}>
        <span style={{ fontSize: 32 }}>⚠</span>
        <div style={{ fontSize: 13 }}>RENDER ERROR — {this.state.error?.message}</div>
        <button onClick={() => this.setState({ hasError: false })} style={{ background: "#e8001d", color: "#fff", border: "none", padding: "8px 20px", cursor: "pointer", fontFamily: "Orbitron", fontSize: 10, letterSpacing: 2 }}>↺ RELOAD</button>
      </div>
    );
    return this.props.children;
  }
}

// ── Main Dashboard ───────────────────────────────────────────────────────────
const F1Dashboard = () => {
  const [results, setResults]       = useState([]);
  const [selectedLap, setSelectedLap] = useState(null);
  const [activeTab, setActiveTab]   = useState(TAB_KEYS.COMMENTARY);
  const [phase, setPhase]           = useState(PHASE_STATES.IDLE);
  const [jobId, setJobId]           = useState(null);
  const [errMsg, setErrMsg]         = useState("");
  const [progress, setProgress]     = useState(0);

  const videoUpload   = useVideoUpload();
  const commentaryRef = useRef();
  const lapScrollRef  = useRef();
  const pollRef       = useRef();

  const currentResult = useMemo(
    () => results.find(r => r.lap === selectedLap) ?? results[results.length - 1],
    [results, selectedLap]
  );
  const commentedResults  = useMemo(() => results.filter(r => isValidCommentary(r.commentary_llm)), [results]);
  const visibleCommentary = useMemo(
    () => selectedLap ? results.filter(r => r.lap <= selectedLap) : commentedResults,
    [results, selectedLap, commentedResults]
  );
  const withComment = commentedResults.length;

  const lastWithDrivers = [...results].reverse().find(r => r.drivers?.length > 0);
  const drivers = currentResult?.drivers?.length > 0 ? currentResult.drivers : lastWithDrivers?.drivers ?? [];

  // Fonts
  useEffect(() => {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@300;400;600;700&display=swap";
    document.head.appendChild(link);
  }, []);

  // Polling
  const poll = useCallback(async id => {
    try {
      const res  = await fetch(`${API_BASE_URL}/video/status/${id}`);
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      if (data.resultats?.length) { setResults(data.resultats); setProgress(Math.min(95, data.resultats.length)); }
      if (data.status === "terminé") { setPhase(PHASE_STATES.DONE); setProgress(100); clearInterval(pollRef.current); }
      if (data.status === "erreur")  { setPhase(PHASE_STATES.ERROR); setErrMsg(data.message ?? "Erreur"); clearInterval(pollRef.current); }
    } catch (e) { setPhase(PHASE_STATES.ERROR); setErrMsg(e.message); clearInterval(pollRef.current); }
  }, []);

  const upload = async () => {
    if (!videoUpload.file) return;
    setPhase(PHASE_STATES.UPLOADING); setProgress(0); setResults([]); setErrMsg("");
    const fd = new FormData(); fd.append("file", videoUpload.file);
    try {
      const res  = await fetch(`${API_BASE_URL}/video/analyze`, { method: "POST", body: fd });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setJobId(data.job_id); setPhase(PHASE_STATES.PROCESSING); setProgress(5);
      pollRef.current = setInterval(() => poll(data.job_id), 3000);
    } catch (e) { setPhase(PHASE_STATES.ERROR); setErrMsg(e.message); }
  };

  useEffect(() => () => clearInterval(pollRef.current), []);
  useEffect(() => { if (phase === PHASE_STATES.PROCESSING && results.length > 0) setSelectedLap(results[results.length - 1].lap); }, [results, phase]);
  useEffect(() => { if (commentaryRef.current) commentaryRef.current.scrollTop = commentaryRef.current.scrollHeight; }, [visibleCommentary]);
  useEffect(() => {
    if (lapScrollRef.current && selectedLap) {
      const el = lapScrollRef.current.querySelector(`[data-lap="${selectedLap}"]`);
      el?.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
    }
  }, [selectedLap]);

  const handleReset = useCallback(() => {
    setResults([]); setSelectedLap(null); setPhase(PHASE_STATES.IDLE); setJobId(null); setProgress(0); setErrMsg(""); videoUpload.reset();
  }, [videoUpload]);

  const statusText  = phase === PHASE_STATES.PROCESSING ? "ANALYZING" : phase === PHASE_STATES.DONE ? "RACE COMPLETE" : "PRE-RACE";
  const statusColor = phase === PHASE_STATES.PROCESSING ? "#e8001d" : phase === PHASE_STATES.DONE ? "#00e676" : "#444";
  const indicators  = currentResult?.indicators ? Object.entries(currentResult.indicators).filter(([, v]) => v).map(([k]) => k) : [];

  return (
    <div style={{ width: "100vw", height: "100vh", background: "#080808", color: "#fff", overflow: "hidden", display: "flex", flexDirection: "column", fontFamily: "'Rajdhani', sans-serif", paddingBottom: 36 }}>
      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 3px; height: 3px; }
        ::-webkit-scrollbar-thumb { background: #e8001d; }
        ::-webkit-scrollbar-track { background: #0a0a0a; }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
        @keyframes fadeup { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
        video::-webkit-media-controls { display:none!important }
      `}</style>

      {/* HEADER */}
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 20px", height: 48, background: "#0a0a0a", borderBottom: "1px solid #1a1a1a", position: "sticky", top: 0, zIndex: 300, flexShrink: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 28, height: 28, background: "#e8001d", borderRadius: 3, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <span style={{ fontFamily: "'Orbitron'", fontWeight: 900, fontSize: 11, color: "#fff" }}>F1</span>
          </div>
          <span style={{ fontFamily: "'Orbitron'", fontWeight: 700, fontSize: 13, letterSpacing: 2, color: "#fff" }}>LIVE AI COMMENTATOR</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, fontFamily: "'Share Tech Mono'", fontSize: 10, color: "#555", letterSpacing: 1 }}>
          <span style={{ color: "#e8001d" }}>·</span><span>LIVE STREAM</span>
          <span style={{ color: "#e8001d" }}>·</span><span>BAHRAIN GP</span>
          <span style={{ color: "#e8001d" }}>·</span>
          <span style={{ color: statusColor, display: "flex", alignItems: "center", gap: 5 }}>
            {phase === PHASE_STATES.PROCESSING && <span style={{ width: 5, height: 5, borderRadius: "50%", background: "#e8001d", display: "inline-block", animation: "blink 1s infinite" }} />}
            {statusText}
          </span>
          {results.length > 0 && <><span style={{ color: "#e8001d" }}>·</span><span style={{ color: "#777" }}>LAP {currentResult?.lap ?? 0}</span></>}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 20, fontFamily: "'Share Tech Mono'", fontSize: 10, color: "#555" }}>
          <span>TRACK <span style={{ color: "#888" }}>34.2°C</span></span>
          <span>AIR <span style={{ color: "#888" }}>22.8°C</span></span>
        </div>
      </header>

      {/* MAIN GRID */}
      <div style={{ flex: 1, display: "grid", gridTemplateColumns: "230px 1fr 330px", overflow: "hidden", minHeight: 0 }}>

        {/* LEFT PANEL */}
        <div style={{ borderRight: "1px solid #1a1a1a", display: "flex", flexDirection: "column", overflow: "hidden", background: "#0a0a0a" }}>
          <div style={{ padding: "14px 16px", borderBottom: "1px solid #1a1a1a", flexShrink: 0 }}>
            <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 9, letterSpacing: 3, color: "#444", marginBottom: 8 }}>WINNING PROBABILITY</div>
            <ProbChart data={results} w={200} h={72} />
            <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginTop: 6 }}>
              <span style={{ fontFamily: "'Orbitron'", fontWeight: 900, fontSize: 28, color: "#fff" }}>{currentResult?.prediction?.probability?.toFixed(0) ?? "—"}%</span>
              <span style={{ fontFamily: "'Share Tech Mono'", fontSize: 11, color: "#00e676" }}>{currentResult ? `▲${((currentResult.prediction?.probability ?? 50) - 50).toFixed(1)}` : "—"}</span>
            </div>
            <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 9, color: "#333", marginTop: 3 }}>{jobId ? `JOB #${jobId.slice(0, 8).toUpperCase()}` : "PRE-RACE"}</div>
          </div>

          <div style={{ padding: "12px 16px", borderBottom: "1px solid #1a1a1a", flexShrink: 0 }}>
            <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 9, letterSpacing: 3, color: "#444", marginBottom: 10 }}>LIVE TELEMETRY (OCR)</div>
            {drivers.slice(0, 4).map((d, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, padding: "5px 0", borderBottom: "1px solid #111" }}>
                <span style={{ fontFamily: "'Share Tech Mono'", fontSize: 9, color: "#444", width: 12, flexShrink: 0 }}>{d.position ?? i + 1}</span>
                <span style={{ width: 3, height: 16, background: getTeamColor(d.team ?? ""), flexShrink: 0 }} />
                <span style={{ fontFamily: "'Share Tech Mono'", fontSize: 11, color: "#ccc", flex: 1, fontWeight: 700 }}>
                  {((d.name ?? d.code ?? `P${i + 1}`).toUpperCase().split(" ").pop() || "").slice(0, 3)}
                </span>
                <span style={{ fontFamily: "'Share Tech Mono'", fontSize: 10, color: i === 0 ? "#00e676" : "#666" }}>
                  {d.interval ?? (i === 0 ? "LEADER" : "—")}
                </span>
              </div>
            ))}
          </div>

          <div style={{ padding: "12px 16px", borderBottom: "1px solid #1a1a1a", flexShrink: 0 }}>
            <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 9, letterSpacing: 3, color: "#444", marginBottom: 12 }}>RACE TIMELINE</div>
            <div style={{ position: "relative", paddingLeft: 18 }}>
              <div style={{ position: "absolute", left: 5, top: 4, bottom: 4, width: 1, background: "#1a1a1a" }} />
              {[
                { c: "#e8001d", l: "BOX BOX",        s: "LAP 32 · SECTOR 2" },
                { c: "#ffeb3b", l: "YELLOW FLAG S2",  s: "LAP 28 · SECTOR 2" },
                { c: "#9c27b0", l: "FASTEST LAP",     s: "LAP 15 · SECTOR 2" },
                { c: "#00e676", l: "RACE START",       s: "LAP 1 · SECTOR 1"  },
              ].map((ev, i) => (
                <div key={i} style={{ marginBottom: 14, position: "relative" }}>
                  <div style={{ position: "absolute", left: -14, top: 3, width: 8, height: 8, borderRadius: "50%", background: ev.c }} />
                  <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 10, color: ev.c, fontWeight: 700 }}>{ev.l}</div>
                  <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 9, color: "#444", marginTop: 2 }}>{ev.s}</div>
                </div>
              ))}
            </div>
          </div>

          {currentResult && (
            <div style={{ padding: "12px 16px", background: "#0a0a0a", flexShrink: 0 }}>
              <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 9, letterSpacing: 3, color: "#444", marginBottom: 4 }}>ML PREDICTION</div>
              <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 8, color: "#e8001d", marginBottom: 10 }}>
                ANALYZED: {(currentResult.drivers?.[0]?.name ?? currentResult.drivers?.[0]?.code ?? "TRACKED DRIVER").toUpperCase()}
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                <div style={{ width: 52, height: 52, borderRadius: "50%", border: "2px solid #1a1a1a", display: "flex", alignItems: "center", justifyContent: "center", background: "#0d0d0d", flexShrink: 0 }}>
                  <span style={{ fontFamily: "'Orbitron'", fontWeight: 900, fontSize: 18, color: "#ffd700" }}>P{currentResult.prediction?.position_predite ?? "—"}</span>
                </div>
                <div>
                  <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 10, color: "#888" }}>{currentResult.prediction?.probability?.toFixed(1)}% CONF.</div>
                  <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 9, color: "#444", marginTop: 2 }}>≈ {currentResult.prediction?.position_exacte?.toFixed(2)}</div>
                  <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 9, color: "#333", marginTop: 1 }}>T={currentResult.timestamp}s</div>
                </div>
              </div>
              <div style={{ height: 2, background: "#111", marginTop: 10 }}>
                <div style={{ height: "100%", width: `${currentResult.prediction?.probability ?? 0}%`, background: "linear-gradient(90deg,#e8001d,#ffd700)", transition: "width .8s" }} />
              </div>
            </div>
          )}
          <div style={{ flex: 1 }} />
        </div>

        {/* CENTER PANEL */}
        <div style={{ display: "flex", flexDirection: "column", borderRight: "1px solid #1a1a1a", overflow: "hidden" }}>
          {/* Video */}
          <div style={{ position: "relative", background: "#000", borderBottom: "1px solid #1a1a1a", flex: "0 0 auto", aspectRatio: "16/9", maxHeight: "55vh", overflow: "hidden", outline: videoUpload.isDragging ? "2px solid #e8001d" : "none" }}
            onDragOver={videoUpload.handleDragOver} onDragLeave={videoUpload.handleDragLeave} onDrop={videoUpload.handleDrop}>
            <input ref={videoUpload.fileInputRef} type="file" accept="video/*" style={{ display: "none" }} onChange={e => videoUpload.handleFileSelect(e.target.files?.[0])} />
            {videoUpload.videoUrl && (
              <>
                <video src={videoUpload.videoUrl} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }} autoPlay muted playsInline controls={false} />
                <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to right,rgba(0,0,0,.4) 0%,rgba(0,0,0,.05) 50%,rgba(0,0,0,.4) 100%)", pointerEvents: "none" }} />
              </>
            )}
            {phase === PHASE_STATES.IDLE && !videoUpload.videoUrl && (
              <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 12, cursor: "pointer" }} onClick={() => videoUpload.fileInputRef.current?.click()}>
                <div style={{ width: 48, height: 48, border: `2px solid ${videoUpload.isDragging ? "#e8001d" : "#222"}`, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <span style={{ fontSize: 20, color: videoUpload.isDragging ? "#e8001d" : "#333" }}>↑</span>
                </div>
                <div style={{ fontFamily: "'Orbitron'", fontSize: 11, letterSpacing: 3, color: "#333" }}>DRAG & DROP YOUR RACE FOOTAGE</div>
                <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 10, color: "#222", letterSpacing: 3 }}>MP4 · MKV · AVI</div>
              </div>
            )}
            {phase === PHASE_STATES.IDLE && videoUpload.videoUrl && (
              <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "flex-end", paddingBottom: 24, gap: 10 }}>
                <div style={{ fontFamily: "'Orbitron'", fontSize: 10, letterSpacing: 2, color: "#ffd700", maxWidth: "70%", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{videoUpload.file?.name}</div>
                <button onClick={upload} style={{ fontFamily: "'Orbitron'", fontSize: 10, letterSpacing: 3, background: "#e8001d", color: "#fff", border: "none", padding: "10px 32px", cursor: "pointer" }}>▶ ANALYZE</button>
              </div>
            )}
            {phase === PHASE_STATES.UPLOADING && (
              <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 14, background: "rgba(0,0,0,.7)" }}>
                <div style={{ fontFamily: "'Orbitron'", fontSize: 10, letterSpacing: 3, color: "#e8001d" }}>UPLOADING...</div>
                <div style={{ width: "55%", height: 2, background: "#1a1a1a" }}><div style={{ height: "100%", width: `${progress}%`, background: "linear-gradient(90deg,#e8001d,#ffd700)", transition: "width .5s" }} /></div>
              </div>
            )}
            {phase === PHASE_STATES.PROCESSING && (
              <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, padding: "6px 14px", background: "linear-gradient(0,rgba(0,0,0,.9),transparent)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                  <span style={{ width: 5, height: 5, borderRadius: "50%", background: "#e8001d", animation: "blink 1s infinite" }} />
                  <span style={{ fontFamily: "'Orbitron'", fontSize: 9, letterSpacing: 2, color: "#e8001d" }}>ANALYZING — FRAME {results.length}</span>
                  <span style={{ marginLeft: "auto", fontFamily: "'Share Tech Mono'", fontSize: 9, color: "#555" }}>{progress}%</span>
                </div>
                <div style={{ height: 2, background: "#1a1a1a" }}><div style={{ height: "100%", width: `${progress}%`, background: "linear-gradient(90deg,#e8001d,#ffd700)", transition: "width .5s" }} /></div>
              </div>
            )}
            {(phase === PHASE_STATES.PROCESSING || phase === PHASE_STATES.DONE) && currentResult && (
              <div style={{ position: "absolute", top: 12, left: 12, background: "rgba(0,0,0,.82)", border: "1px solid #222", padding: "7px 11px", backdropFilter: "blur(4px)" }}>
                <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 8, color: "#555", letterSpacing: 2, marginBottom: 2 }}>ANALYZED DRIVER</div>
                <div style={{ fontFamily: "'Rajdhani'", fontSize: 15, fontWeight: 700, color: "#fff" }}>{currentResult.drivers?.[0]?.name ?? "RACE ANALYSIS"}</div>
                <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 9, color: "#666", marginTop: 2 }}>PREDICTED P{currentResult.prediction?.position_predite} · {currentResult.prediction?.probability?.toFixed(1)}% CONF.</div>
              </div>
            )}
            {phase === PHASE_STATES.ERROR && (
              <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 10, background: "rgba(0,0,0,.88)" }}>
                <span style={{ color: "#e8001d", fontSize: 24 }}>⚠</span>
                <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 10, color: "#e8001d", textAlign: "center", maxWidth: "70%" }}>{errMsg}</div>
                <button onClick={handleReset} style={{ fontFamily: "'Orbitron'", fontSize: 9, letterSpacing: 2, background: "transparent", color: "#444", border: "1px solid #222", padding: "7px 18px", cursor: "pointer" }}>RESET</button>
              </div>
            )}
          </div>

          {/* Lap scrubber */}
          {results.length > 0 && (
            <div style={{ borderBottom: "1px solid #1a1a1a", background: "#0a0a0a", flexShrink: 0 }}>
              <div ref={lapScrollRef} style={{ display: "flex", gap: 3, overflowX: "auto", padding: "6px 10px", scrollbarWidth: "thin" }}>
                {results.map(r => {
                  const hc = isValidCommentary(r.commentary_llm);
                  const active = r.lap === selectedLap;
                  return (
                    <div key={r.lap} data-lap={r.lap} onClick={() => setSelectedLap(r.lap)}
                      style={{ flexShrink: 0, width: 32, height: 32, background: active ? "#e8001d" : "#111", border: `1px solid ${active ? "#e8001d" : "#1a1a1a"}`, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", fontFamily: "'Share Tech Mono'", fontSize: 9, color: active ? "#fff" : "#444", position: "relative", transition: "all .15s" }}>
                      {r.lap}
                      {hc && <span style={{ position: "absolute", top: 2, right: 2, width: 3, height: 3, borderRadius: "50%", background: "#ffd700" }} />}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Charts */}
          <div style={{ flex: 1, display: "grid", gridTemplateColumns: "1fr 1fr", overflow: "hidden", minHeight: 0 }}>
            <div style={{ borderRight: "1px solid #1a1a1a", padding: "12px 14px", overflow: "hidden", display: "flex", flexDirection: "column" }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8, flexShrink: 0 }}>
                <div>
                  <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 9, letterSpacing: 3, color: "#e8001d", marginBottom: 2 }}>VICTORY PROBABILITY</div>
                  <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 8, color: "#333" }}>MODEL: LIGHTGBM v5 · MAE 1.33</div>
                </div>
                <span style={{ fontFamily: "'Share Tech Mono'", fontSize: 8, color: "#333" }}>{withComment}/{results.length}</span>
              </div>
              <div style={{ flex: 1, minHeight: 0 }}><ProbChart data={results} w={400} h={100} /></div>
              {results.length > 1 && (
                <div style={{ display: "flex", gap: 12, marginTop: 6, fontFamily: "'Share Tech Mono'", fontSize: 9, flexShrink: 0 }}>
                  <span style={{ color: "#444" }}>MIN <span style={{ color: "#e8001d" }}>{Math.min(...results.map(d => d.prediction?.probability ?? 50)).toFixed(1)}%</span></span>
                  <span style={{ color: "#444" }}>MAX <span style={{ color: "#00e676" }}>{Math.max(...results.map(d => d.prediction?.probability ?? 50)).toFixed(1)}%</span></span>
                </div>
              )}
            </div>
            <div style={{ padding: "12px 14px", overflow: "auto" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 9, letterSpacing: 3, color: "#444" }}>LIVE TIMING</div>
                <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 8, color: "#9c27b0", border: "1px solid #9c27b033", padding: "2px 7px" }}>◈ SECTOR 1: PURPLE</div>
              </div>
              {drivers.slice(0, 6).map((d, i) => (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, padding: "7px 0", borderBottom: "1px solid #111" }}>
                  <span style={{ fontFamily: "'Share Tech Mono'", fontSize: 9, color: "#444", width: 12, flexShrink: 0 }}>{d.position ?? i + 1}</span>
                  <span style={{ width: 3, height: 22, background: getTeamColor(d.team ?? ""), flexShrink: 0 }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontFamily: "'Rajdhani'", fontSize: 13, fontWeight: 700, color: "#ccc", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{(d.name ?? d.code ?? "—").toUpperCase()}</div>
                    <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 8, color: "#444", marginTop: 1 }}>{(d.team ?? "—").toUpperCase()}</div>
                  </div>
                  <span style={{ fontFamily: "'Share Tech Mono'", fontSize: 10, color: i === 0 ? "#00e676" : "#666", flexShrink: 0 }}>{d.interval ?? (i === 0 ? "LEADER" : "—")}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* RIGHT PANEL */}
        <div style={{ display: "flex", flexDirection: "column", background: "#0a0a0a", overflow: "hidden" }}>
          <div style={{ display: "flex", borderBottom: "1px solid #1a1a1a", flexShrink: 0 }}>
            {[["commentary", "AI COMMENTARY"], ["strategy", "STRATEGY"], ["chat", "RAG CHAT"]].map(([key, label]) => (
              <button key={key} onClick={() => setActiveTab(key)}
                style={{ flex: 1, padding: "12px 0", background: "transparent", border: "none", borderBottom: activeTab === key ? "2px solid #e8001d" : "2px solid transparent", fontFamily: "'Share Tech Mono'", fontSize: 8, letterSpacing: 1, color: activeTab === key ? "#fff" : "#444", cursor: "pointer", transition: "all .2s" }}>
                {label}
              </button>
            ))}
          </div>

          <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column", overflow: "hidden" }}>
            {activeTab === "commentary" && (
              <div ref={commentaryRef} style={{ flex: 1, overflowY: "auto", padding: "0 14px" }}>
                {visibleCommentary.length === 0
                  ? <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%" }}><span style={{ fontFamily: "'Share Tech Mono'", fontSize: 10, color: "#222", letterSpacing: 3 }}>WAITING FOR RACE FEED...</span></div>
                  : visibleCommentary.map((r, i) => (
                    <div key={`${r.lap}-${i}`} style={{ animation: "fadeup .35s ease forwards", opacity: 0, animationDelay: `${i * .04}s`, animationFillMode: "forwards" }}>
                      <CommentItem persona="journalist" text={r.commentary_llm}      lap={r.lap} />
                      <CommentItem persona="professor"  text={r.commentary_rag}      lap={r.lap} />
                      <CommentItem persona="engineer"   text={r.commentary_engineer} lap={r.lap} />
                      <CommentItem persona="fan"        text={r.commentary_fan}      lap={r.lap} />
                    </div>
                  ))
                }
              </div>
            )}
            {activeTab === "strategy" && (
              <div style={{ flex: 1, overflowY: "auto", padding: "0 14px" }}>
                {visibleCommentary.length === 0
                  ? <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%" }}><span style={{ fontFamily: "'Share Tech Mono'", fontSize: 10, color: "#222", letterSpacing: 3 }}>NO DATA YET...</span></div>
                  : visibleCommentary.map((r, i) => (
                    <div key={i} style={{ padding: "12px 0", borderBottom: "1px solid #1a1a1a" }}>
                      <div style={{ fontFamily: "'Share Tech Mono'", fontSize: 9, color: "#444", marginBottom: 8 }}>LAP {r.lap} · P{r.prediction?.position_predite} · {r.prediction?.probability?.toFixed(1)}%</div>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                        {Object.entries(r.indicators ?? {}).filter(([, v]) => v).map(([k]) => (
                          <span key={k} style={{ fontFamily: "'Share Tech Mono'", fontSize: 8, color: "#e8001d", background: "#1a0000", padding: "4px 8px", border: "1px solid #e8001d33" }}>{k}</span>
                        ))}
                        {!Object.values(r.indicators ?? {}).some(Boolean) && <span style={{ fontFamily: "'Share Tech Mono'", fontSize: 9, color: "#222" }}>NO INDICATORS DETECTED</span>}
                      </div>
                    </div>
                  ))
                }
              </div>
            )}
            {/* ChatRAG always mounted, hidden when not active — preserves conversation */}
            <div style={{ display: activeTab === "chat" ? "flex" : "none", flex: 1, minHeight: 0, flexDirection: "column" }}>
              <ChatRAG />
            </div>
          </div>

          {phase === PHASE_STATES.DONE && activeTab !== "chat" && (
            <div style={{ padding: "10px 14px", borderTop: "1px solid #1a1a1a", background: "#0d0d0d", flexShrink: 0 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontFamily: "'Share Tech Mono'", fontSize: 9, color: "#444" }}>
                <span>FRAMES <span style={{ color: "#666" }}>{results.length}</span></span>
                <span>COMMENTS <span style={{ color: "#00e676" }}>{withComment}</span></span>
                <span onClick={handleReset} style={{ color: "#e8001d", cursor: "pointer" }}>↺ NEW RACE</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <Ticker results={results} />
    </div>
  );
};

export default function App() {
  return <ErrorBoundary><F1Dashboard /></ErrorBoundary>;
}