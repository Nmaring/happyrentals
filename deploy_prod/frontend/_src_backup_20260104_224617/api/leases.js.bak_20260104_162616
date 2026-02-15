import api from "./api";

function normalizeLeaseDraft(d) {
  const lease = { ...(d || {}) };

  // defaults
  lease.lease_type = lease.lease_type || (lease.end_date ? "fixed_term" : "month_to_month");
  lease.rent_due_day = lease.rent_due_day ?? lease.rentDueDay ?? 1;
  lease.late_fee_type = lease.late_fee_type || "none";
  lease.late_fee_value = lease.late_fee_value ?? 0;

  // clamp due day to 1..28 (Feb-safe)
  const dd = Number(lease.rent_due_day);
  lease.rent_due_day = Number.isFinite(dd) ? Math.min(28, Math.max(1, dd)) : 1;

  // lease type rules
  if (lease.lease_type !== "fixed_term") {
    lease.end_date = null;
  } else {
    // fixed_term should have end_date; leave as-is if provided
    // (backend will enforce requirement if missing)
  }

  // normalize common alt keys (just in case)
  if (lease.rent_amount == null && lease.rentAmount != null) lease.rent_amount = lease.rentAmount;
  if (lease.start_date == null && lease.startDate != null) lease.start_date = lease.startDate;
  if (lease.end_date == null && lease.endDate != null && lease.lease_type === "fixed_term") lease.end_date = lease.endDate;

  // state left as-is; can be null
  if (lease.state === "") lease.state = null;

  return lease;
}

// GET /leases?tenant_id=&unit_id=
export async function fetchLeases(params = {}) {
  const { tenant_id, unit_id } = params;
  const qs = new URLSearchParams();
  if (tenant_id) qs.set("tenant_id", String(tenant_id));
  if (unit_id) qs.set("unit_id", String(unit_id));
  const url = qs.toString() ? `/leases?${qs.toString()}` : "/leases";
  const res = await api.get(url);
  return res.data;
}

export async function createLease(payload) {
  const res = await api.post("/leases", normalizeLeaseDraft(payload));
  return res.data;
}

export async function updateLease(id, payload) {
  const res = await api.put(`/leases/${id}`, normalizeLeaseDraft(payload));
  return res.data;
}

export async function deleteLease(id) {
  const res = await api.delete(`/leases/${id}`);
  return res.data;
}




