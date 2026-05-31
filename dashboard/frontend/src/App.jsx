import { useState, useEffect } from "react"

const API = "http://localhost:8080"

function Card({ title, children }) {
  return (
    <div style={{background:"#1a1a1a",padding:"20px",borderRadius:"8px",border:"1px solid #333",marginBottom:"16px"}}>
      <h3 style={{color:"#00ff88",marginTop:0}}>{title}</h3>
      {children}
    </div>
  )
}

export default function App() {
  const [status, setStatus] = useState(null)
  const [benchmarks, setBenchmarks] = useState(null)
  const [logs, setLogs] = useState([])
  const [activity, setActivity] = useState([])
  const [instruction, setInstruction] = useState("")
  const [sent, setSent] = useState(false)

  const fetchAll = () => {
    fetch(`${API}/status`).then(r=>r.json()).then(setStatus).catch(()=>{})
    fetch(`${API}/benchmarks`).then(r=>r.json()).then(setBenchmarks).catch(()=>{})
    fetch(`${API}/logs`).then(r=>r.json()).then(d=>setLogs(d.logs||[])).catch(()=>{})
    fetch(`${API}/activity`).then(r=>r.json()).then(d=>setActivity(d.activity||[])).catch(()=>{})
  }

  useEffect(() => {
    fetchAll()
    const interval = setInterval(fetchAll, 10000)
    return () => clearInterval(interval)
  }, [])

  const sendInstruction = () => {
    if (!instruction.trim()) return
    fetch(`${API}/instructions`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({instruction})
    }).then(() => {
      setSent(true)
      setInstruction("")
      setTimeout(() => setSent(false), 3000)
    })
  }

  const phases = [
    {num:1,name:"Foundation",done:true},
    {num:2,name:"Teacher AI",done:true},
    {num:3,name:"Student on Modal",done:true},
    {num:4,name:"Memory System",done:true},
    {num:5,name:"Dashboard",done:true},
    {num:6,name:"Training System",done:true},
    {num:7,name:"Autonomous Loop",done:true},
  ]

  return (
    <div style={{background:"#0f0f0f",color:"#fff",minHeight:"100vh",padding:"24px",fontFamily:"monospace",maxWidth:"1200px",margin:"0 auto"}}>

      <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"24px"}}>
        <div>
          <h1 style={{color:"#00ff88",margin:0}}>AAES Dashboard</h1>
          <p style={{color:"#555",margin:"4px 0 0"}}>Autonomous AI Engineering System — 100% Complete</p>
        </div>
        <button onClick={fetchAll} style={{background:"#00ff8822",color:"#00ff88",border:"1px solid #00ff88",borderRadius:"6px",padding:"8px 16px",cursor:"pointer",fontFamily:"monospace"}}>
          Refresh
        </button>
      </div>

      <Card title="Project Progress — 100% Complete">
        <div style={{display:"flex",gap:"8px",flexWrap:"wrap"}}>
          {phases.map(p => (
            <div key={p.num} style={{flex:1,minWidth:"120px",background:"#00ff8822",border:"1px solid #00ff88",borderRadius:"6px",padding:"10px",textAlign:"center"}}>
              <div style={{fontSize:"11px",color:"#888"}}>Phase {p.num}</div>
              <div style={{fontSize:"12px",color:"#00ff88",marginTop:"4px"}}>{p.name}</div>
              <div style={{marginTop:"6px"}}>✅</div>
            </div>
          ))}
        </div>
      </Card>

      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:"16px"}}>
        <Card title="System Status">
          <p style={{margin:"4px 0"}}>
            {status ? status.status : "Connecting..."}
            <span style={{background:"#00ff8822",color:"#00ff88",border:"1px solid #00ff88",borderRadius:"4px",padding:"2px 8px",fontSize:"12px",marginLeft:"8px"}}>ONLINE</span>
          </p>
          <p style={{color:"#888",margin:"4px 0"}}>Version: {status?.version ?? "-"}</p>
        </Card>

        <Card title="Benchmarks">
          <p style={{margin:"4px 0"}}>Total Tasks: <strong>{benchmarks?.total_tasks ?? "-"}</strong></p>
          <p style={{margin:"4px 0"}}>Passed: <strong>{benchmarks?.passed ?? "-"}</strong></p>
          <p style={{margin:"4px 0"}}>Accuracy: <strong style={{color:"#00ff88"}}>{benchmarks?.accuracy ?? "-"}%</strong></p>
        </Card>

        <Card title="Models">
          <p style={{margin:"4px 0"}}>Teacher: <span style={{color:"#00ff88"}}>Llama3 70B</span></p>
          <p style={{margin:"4px 0"}}>Student: <span style={{color:"#00ff88"}}>Llama3 3B (Modal)</span></p>
          <p style={{margin:"4px 0",color:"#888",fontSize:"12px"}}>Memory: ChromaDB</p>
        </Card>
      </div>

      <Card title="Live Teacher Activity">
        <div style={{maxHeight:"200px",overflowY:"auto"}}>
          {activity.length === 0
            ? <p style={{color:"#555"}}>No activity yet — loop may not be posting updates.</p>
            : [...activity].reverse().map((a,i) => (
              <div key={i} style={{borderBottom:"1px solid #222",padding:"6px 0",display:"flex",gap:"12px"}}>
                <span style={{color:"#555",fontSize:"12px",minWidth:"60px"}}>{a.time}</span>
                <span style={{color:"#aaa",fontSize:"13px"}}>{a.message}</span>
              </div>
            ))
          }
        </div>
      </Card>

      <Card title="Instruct the Teacher">
        <p style={{color:"#888",fontSize:"13px",margin:"0 0 12px"}}>Tell the Teacher what to focus on:</p>
        <div style={{display:"flex",gap:"8px"}}>
          <input
            value={instruction}
            onChange={e => setInstruction(e.target.value)}
            onKeyDown={e => e.key === "Enter" && sendInstruction()}
            placeholder="e.g. Focus on async programming tasks..."
            style={{flex:1,background:"#111",color:"#fff",border:"1px solid #333",borderRadius:"6px",padding:"10px",fontFamily:"monospace",fontSize:"13px"}}
          />
          <button onClick={sendInstruction}
            style={{background:"#00ff8822",color:"#00ff88",border:"1px solid #00ff88",borderRadius:"6px",padding:"10px 20px",cursor:"pointer",fontFamily:"monospace"}}>
            Send
          </button>
        </div>
        {sent && <p style={{color:"#00ff88",margin:"8px 0 0",fontSize:"13px"}}>Instruction sent!</p>}
      </Card>

      <Card title="Training Logs">
        {logs.length === 0
          ? <p style={{color:"#555"}}>No logs yet.</p>
          : logs.slice(-10).reverse().map((log,i) => (
            <div key={i} style={{borderBottom:"1px solid #2a2a2a",padding:"10px 0",display:"grid",gridTemplateColumns:"1fr auto"}}>
              <p style={{color:"#aaa",margin:"2px 0",fontSize:"13px"}}>{log.prompt}</p>
              <span style={{color: log.evaluation_score >= 1 ? "#00ff88" : "#ff6644",fontSize:"12px"}}>
                Score: {log.evaluation_score}
              </span>
            </div>
          ))
        }
      </Card>

      <p style={{color:"#333",fontSize:"11px",textAlign:"center",marginTop:"24px"}}>
        AAES v{status?.version ?? "-"} | Auto-refresh every 10s | Owner: Brian Kosgei
      </p>
    </div>
  )
}
