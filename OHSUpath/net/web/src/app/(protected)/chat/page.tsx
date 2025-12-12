// net/web/src/app/(protected)/chat/page.tsx

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import ChatClient from "@/app/chat/Client";

const COOKIE_NAME = process.env.COOKIE_NAME || "sid";
// Priority: explicit gateway -> public API base -> local fallback
const GW_BASE =
  process.env.GATEWAY_ORIGIN ||
  process.env.NEXT_PUBLIC_API_BASE ||
  "http://localhost:3000";

async function getConversations() {
  const sid = cookies().get(COOKIE_NAME)?.value;
  const url = `${GW_BASE}/api/conversations`;

  const headersObj: Record<string, string> = {};
  if (sid) headersObj.cookie = `${COOKIE_NAME}=${sid}`;

  const res = await fetch(url, { headers: headersObj, cache: "no-store" }).catch(() => null);
  if (!res) throw new Error("Gateway not reachable");
  if (res.status === 401 || res.status === 403) {
    redirect(`/login?next=${encodeURIComponent("/chat")}`);
  }
  if (!res.ok) throw new Error(`Failed to load conversations: ${res.status}`);

  const data = await res.json().catch(() => []);
  const items = Array.isArray(data) ? data : (Array.isArray(data?.items) ? data.items : []);
  return items;
}

export default async function Page() {
  const conversations = await getConversations();
  // No conversation selected => empty input area
  return <ChatClient initialConversations={conversations} selectedPublicId={null} />;
}
