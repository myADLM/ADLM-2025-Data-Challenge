// net/web/src/app/(protected)/chat/[public_chat_id]/page.tsx

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import ChatClient from "@/app/chat/Client";

const COOKIE_NAME = process.env.COOKIE_NAME || "sid";
const GW_BASE =
  process.env.GATEWAY_ORIGIN ||
  process.env.NEXT_PUBLIC_API_BASE ||
  "http://localhost:3000";

async function getConversations(cookieVal?: string) {
  const url = `${GW_BASE}/api/conversations`;
  const headersObj: Record<string, string> = {};
  if (cookieVal) headersObj.cookie = `${COOKIE_NAME}=${cookieVal}`;

  const res = await fetch(url, { headers: headersObj, cache: "no-store" }).catch(() => null);
  if (!res) return []; // gateway unreachable -> let client fetch later
  if (res.status === 401 || res.status === 403) {
    // Redirect to login with target page
    redirect(`/login?next=${encodeURIComponent("/chat")}`);
  }
  if (res.status === 429) return []; // rate-limited -> degrade to empty list; client can poll later
  if (!res.ok) return [];

  const data = await res.json().catch(() => []);
  return Array.isArray(data) ? data : (Array.isArray((data as any)?.items) ? (data as any).items : []);
}

export default async function Page({ params }: { params: { public_chat_id: string } }) {
  const sid = cookies().get(COOKIE_NAME)?.value;
  const conversations = await getConversations(sid);
  return (
    <ChatClient
      initialConversations={conversations}
      selectedPublicId={params.public_chat_id}
    />
  );
}
