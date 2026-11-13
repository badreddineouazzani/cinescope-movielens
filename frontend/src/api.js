export async function fetchApi(path, params = {}, signal) {
  const query = new URLSearchParams(params).toString();
  const url = "/api/" + path + (query ? "?" + query : "");
  const response = await fetch(url, { signal });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(typeof body.detail === "string" ? body.detail : "Impossible de charger ces données.");
  }
  return response.json();
}
