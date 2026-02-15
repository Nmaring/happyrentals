import React, { useEffect, useState } from "react";
import { unwrapList } from "../utils/unwrapList";

export default function MaintenancePage(){
  const [items,setItems]=useState([]);
  const [err,setErr]=useState("");
  const [loading,setLoading]=useState(true);
  const [title,setTitle]=useState("");
  const [description,setDescription]=useState("");
  const [priority,setPriority]=useState("normal");
  const [saving,setSaving]=useState(false);

  async function load(){
    setLoading(true); setErr("");
    try{
      const r=await fetch("/api/maintenance");
      const j=await r.json().catch(()=>null);
      if(!r.ok) throw new Error(j?.detail || JSON.stringify(j));
      setItems(unwrapList(j));
    }catch(e){ setErr(String(e)); }
    finally{ setLoading(false); }
  }

  useEffect(()=>{ load(); }, []);

  async function create(e){
    e.preventDefault();
    setSaving(true); setErr("");
    try{
      const r=await fetch("/api/maintenance",{
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body: JSON.stringify({ title, description: description || null, priority })
      });
      const j=await r.json().catch(()=>null);
      if(!r.ok) throw new Error(j?.detail || JSON.stringify(j));
      setTitle(""); setDescription(""); setPriority("normal");
      await load();
    }catch(e){ setErr(String(e)); }
    finally{ setSaving(false); }
  }

  async function setStatus(id,status){
    setErr("");
    try{
      const r=await fetch(`/api/maintenance/${id}`,{
        method:"PUT",
        headers:{ "Content-Type":"application/json" },
        body: JSON.stringify({ status })
      });
      const j=await r.json().catch(()=>null);
      if(!r.ok) throw new Error(j?.detail || JSON.stringify(j));
      await load();
    }catch(e){ setErr(String(e)); }
  }

  return (
    <div className="hr-card">
      <div className="hr-top">
        <div className="hr-title">Maintenance</div>
      </div>

      {err && <div className="hr-alert err" style={{ marginBottom:12 }}>{err}</div>}

      <form onSubmit={create} className="hr-card" style={{ background:"var(--card2)", marginBottom:12 }}>
        <div className="hr-label">Title</div>
        <input className="hr-input" value={title} onChange={(e)=>setTitle(e.target.value)} />

        <div className="hr-label">Description</div>
        <textarea className="hr-textarea" rows={4} value={description} onChange={(e)=>setDescription(e.target.value)} />

        <div className="hr-label">Priority</div>
        <select className="hr-select" value={priority} onChange={(e)=>setPriority(e.target.value)}>
          <option value="low">Low</option>
          <option value="normal">Normal</option>
          <option value="high">High</option>
          <option value="urgent">Urgent</option>
        </select>

        <div style={{ marginTop:12 }}>
          <button className="hr-btn hr-btn-primary" disabled={saving || !title.trim()}>
            {saving ? "Saving…" : "Create request"}
          </button>
        </div>
      </form>

      {loading ? <div>Loading…</div> : (
        <table className="hr-table">
          <thead>
            <tr><th>Request</th><th>Priority</th><th>Status</th><th></th></tr>
          </thead>
          <tbody>
            {items.map(m => (
              <tr key={m.id}>
                <td>
                  <div style={{ fontWeight:800 }}>{m.title}</div>
                  <div style={{ fontSize:12, color:"var(--muted)" }}>{m.description || ""}</div>
                </td>
                <td>{m.priority}</td>
                <td>{m.status}</td>
                <td style={{ textAlign:"right" }}>
                  <button className="hr-btn" onClick={()=>setStatus(m.id,"in_progress")} style={{ marginRight:8 }}>In progress</button>
                  <button className="hr-btn" onClick={()=>setStatus(m.id,"resolved")}>Resolve</button>
                </td>
              </tr>
            ))}
            {items.length===0 && <tr><td colSpan={4} style={{ color:"var(--muted)" }}>No requests yet.</td></tr>}
          </tbody>
        </table>
      )}
    </div>
  );
}
