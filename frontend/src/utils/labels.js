export function tenantName(t) {
  if (!t) return "";
  const name = `${t.first_name || ""} ${t.last_name || ""}`.trim();
  return name || t.full_name || t.name || `Tenant #${t.id ?? ""}`;
}

export function propertyName(p) {
  if (!p) return "";
  return p.name || `Property #${p.id ?? ""}`;
}

export function unitName(u) {
  if (!u) return "";
  return u.unit_number || u.unitNumber || `Unit #${u.id ?? ""}`;
}

export function unitLabel(u, propMap) {
  if (!u) return "";
  const p = propMap?.get?.(String(u.property_id)) || null;
  const pname = propertyName(p) || `Property #${u.property_id ?? ""}`;
  return `${pname} — ${unitName(u)}`;
}

export function leaseLabel(l, unitMap, tenantMap, propMap) {
  if (!l) return "";
  const u = unitMap?.get?.(String(l.unit_id)) || null;
  const t = tenantMap?.get?.(String(l.tenant_id)) || null;
  const uLabel = u ? unitLabel(u, propMap) : `Unit #${l.unit_id ?? ""}`;
  const tName = tenantName(t) || `Tenant #${l.tenant_id ?? ""}`;
  return `Lease #${l.id ?? ""} — ${uLabel} — ${tName}`;
}
