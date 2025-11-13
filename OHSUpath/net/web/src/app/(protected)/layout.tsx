// net/web/src/app/(protected)/layout.tsx

import { cookies, headers } from "next/headers";
import { redirect } from "next/navigation";

const COOKIE_NAME = process.env.COOKIE_NAME || "sid";
const GW = process.env.GATEWAY_ORIGIN || ""; // optional: direct gateway origin

function originFromHeaders() {
  const h = headers();
  const proto = h.get("x-forwarded-proto") ?? "http";
  const host = h.get("x-forwarded-host") ?? h.get("host") ?? "localhost:4000";
  return `${proto}://${host}`;
}

export default async function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const sid = cookies().get(COOKIE_NAME)?.value;
  if (!sid) redirect(`/login?next=${encodeURIComponent("/chat")}`);

  const base = GW || originFromHeaders(); // Important: SSR must use absolute URL
  const url = `${base}/api/auth/me`;
  const res = await fetch(url, {
    headers: sid ? { cookie: `${COOKIE_NAME}=${sid}` } : undefined,
    cache: "no-store",
  }).catch(() => null);

  if (!res || res.status === 401 || res.status === 403) {
    redirect(`/login?next=${encodeURIComponent("/chat")}`);
  }
  return <>{children}</>;
}
