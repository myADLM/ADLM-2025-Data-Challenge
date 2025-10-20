// net/web/src/app/login/page.tsx

import { cookies, headers } from "next/headers";
import LoginClient from "./LoginClient";

const COOKIE_NAME = process.env.COOKIE_NAME || "sid";
const GW = process.env.GATEWAY_ORIGIN || "";

function originFromHeaders() {
  const h = headers();
  const proto = h.get("x-forwarded-proto") ?? "http";
  const host = h.get("x-forwarded-host") ?? h.get("host") ?? "localhost:4000";
  return `${proto}://${host}`;
}

function safeNext(raw?: string) {
  if (!raw || typeof raw !== "string") return "/chat";
  return raw.startsWith("/") ? raw : "/chat";
}

export default async function Page({ searchParams }: { searchParams: { next?: string; force?: string } }) {
  const sid = cookies().get(COOKIE_NAME)?.value;
  let me: any = null;

  if (sid) {
    const base = GW || originFromHeaders(); // SSR uses absolute URL
    const url = `${base}/api/auth/me`;
    const res = await fetch(url, {
      headers: { cookie: `${COOKIE_NAME}=${sid}` },
      cache: "no-store",
    }).catch(() => null);
    me = res && res.ok ? await res.json() : null;
  }

  return <LoginClient currentUser={me} next={safeNext(searchParams.next)} force={searchParams.force === "1"} />;
}
