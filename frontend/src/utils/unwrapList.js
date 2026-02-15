export function unwrapList(x) {
  if (!x) return [];
  const data = x?.data ?? x; // axios or fetch JSON
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.value)) return data.value;
  if (data && Array.isArray(data.items)) return data.items;
  if (data && Array.isArray(data.results)) return data.results;
  return [];
}
