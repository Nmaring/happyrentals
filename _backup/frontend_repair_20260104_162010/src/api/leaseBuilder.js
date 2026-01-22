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

export async function getLeaseRules(stateCode) {
  const { data } = await api.get(`/lease-builder/rules/${stateCode}`);
  return data;
}

export async function renderLeaseDraft(payload) {
  const { data } = await api.post(`/lease-builder/render`, payload);
  return data;
}

