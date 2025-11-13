// net/web/src/lib/api.ts

const BASE = process.env.NEXT_PUBLIC_API_BASE || "/api";

async function http(method: "GET"|"POST", path: string, body?: any) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text().catch(()=>"");
    throw new Error(`${res.status} ${res.statusText} ${text}`.trim());
  }
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? res.json() : res.text();
}

export const api = {
  get: (p: string) => http("GET", p),
  post: (p: string, b?: any) => http("POST", p, b),
  base: BASE,
};
