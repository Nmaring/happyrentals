import React, { useEffect, useState } from "react";

export default function BillingPage(){
  const [usage, setUsage] = useState(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(true);
  const [plan, setPlan] = useState("per_unit");

  async function load(){
    setLoading(true); setErr("");
    try{
      const r = await fetch("/api/billing/usage");
      const j = await r.json().catch(()=>null);
      if(!r.ok) throw new Error(j?.detail || JSON.stringify(j));
      setUsage(j);
      setPlan(j.plan_type || "per_unit");
    }catch(e){
      setErr(String(e));
    }finally{
      setLoading(false);
    }
  }

  useEffect(()=>{ load(); }, []);

  async function savePlan(){
    setErr("");
    try{
      const r = await fetch("/api/billing/set-plan",{
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body: JSON.stringify({ plan_type: plan })
      });
      const j = await r.json().catch(()=>null);
      if(!r.ok) throw new Error(j?.detail || JSON.stringify(j));
      await load();
    }catch(e){ setErr(String(e)); }
  }

  async function checkout(){
    setErr("");
    try{
      const r = await fetch("/api/billing/checkout",{
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body: JSON.stringify({ plan_type: plan })
      });
      const j = await r.json().catch(()=>null);
      if(!r.ok) throw new Error(j?.detail || JSON.stringify(j));
      if(j?.url) window.location.href = j.url;
      else throw new Error("Stripe not configured yet (server returned no checkout URL).");
    }catch(e){ setErr(String(e)); }
  }

  return (
    <div className="hr-card">
      <div className="hr-top">
        <div className="hr-title">Billing</div>
        {usage?.status && <div className="hr-pill">status: {usage.status}</div>}
      </div>

      {err && <div className="hr-alert err" style={{ marginBottom:12 }}>{err}</div>}

      {loading ? <div>Loading…</div> : (
        <>
          <div className="hr-row hr-row-3" style={{ marginBottom:12 }}>
            <div className="hr-alert">
              <div className="hr-label">Plan</div>
              <div style={{ fontWeight:800 }}>{usage?.plan_type}</div>
            </div>
            <div className="hr-alert">
              <div className="hr-label">Billable units</div>
              <div style={{ fontWeight:800 }}>{usage?.billable_units ?? 0}</div>
            </div>
            <div className="hr-alert">
              <div className="hr-label">Billable tenants</div>
              <div style={{ fontWeight:800 }}>{usage?.billable_tenants ?? 0}</div>
            </div>
          </div>

          <div className="hr-label">Choose billing model</div>
          <select className="hr-select" value={plan} onChange={(e)=>setPlan(e.target.value)}>
            <option value="per_unit">Per unit per month</option>
            <option value="per_tenant">Per tenant per month</option>
            <option value="flat">Flat monthly</option>
          </select>

          <div style={{ display:"flex", gap:10, marginTop:12, flexWrap:"wrap" }}>
            <button className="hr-btn" onClick={savePlan}>Save plan</button>
            <button className="hr-btn hr-btn-primary" onClick={checkout}>Subscribe (Stripe)</button>
          </div>

          <div style={{ color:"var(--muted)", fontSize:12, marginTop:12 }}>
            Tenants never pay. Only the landlord organization pays based on the selected model.
          </div>
        </>
      )}
    </div>
  );
}
