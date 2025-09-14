// net/web/src/app/chat/Client.tsx

"use client";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { startSSE } from "@/lib/sse";
import { useRouter } from "next/navigation";

type AccessRole = "owner" | "editor" | "viewer";
type UserBrief = { id: number; email?: string | null; name?: string | null };

type Conv = {
  id: string; // public_chat_id
  title?: string | null;
  last_message?: string | null;
  created_at?: number | string | null;
  updated_at?: number | string | null;
  last_message_at?: number | string | null;
  access_role?: AccessRole;
  shared_by?: UserBrief | null;
  [k: string]: any;
};
type Msg = { role: "user" | "assistant" | "system" | "info"; text: string };

/** Unified sort timestamp: last_message_at > updated_at > created_at */
function ts(c: Conv): number {
  const n = (v: any) => (v == null ? 0 : Number(v));
  return n(c.last_message_at ?? c.updated_at ?? c.created_at ?? 0);
}
function byDesc(a: Conv, b: Conv) { return ts(b) - ts(a); }
function labelOf(c: Conv) { return c.title || c.id; }
function sanitizeChunk(t: string): string {
  const s = (t ?? "").trim();
  if (!s) return "";
  if (s.startsWith("{") && s.endsWith("}")) { try { JSON.parse(s); return ""; } catch {} }
  if (/^You said:/i.test(s)) return "";
  if (/^This is a placeholder answer\./i.test(s)) return "";
  return t;
}
/** Deduplicate, merge, and sort */
function dedupeAndSort(list: Conv[]): Conv[] {
  const map = new Map<string, Conv>();
  for (const c of list) map.set(c.id, { ...(map.get(c.id) || {}), ...c });
  return Array.from(map.values()).sort(byDesc);
}
/** Upsert one conversation and sort */
function upsert(list: Conv[], item: Conv): Conv[] {
  const i = list.findIndex(x => x.id === item.id);
  if (i >= 0) {
    const next = [...list];
    next[i] = { ...next[i], ...item };
    return dedupeAndSort(next);
  }
  return dedupeAndSort([item, ...list]);
}

/** Make an auto title from the first input (first sentence / up to 48 chars; strip extra whitespace/quotes/backticks/URLs) */
function makeAutoTitle(input: string): string {
  let t = (input || "")
    .replace(/https?:\/\/\S+/gi, "")
    .replace(/[`'"]+/g, "")
    .replace(/\s+/g, " ")
    .trim();
  const m = t.match(/(.+?[\.?!,;:])\s/);
  if (m && m[1] && m[1].length >= 4) t = m[1];
  if (t.length > 48) t = t.slice(0, 48).trimEnd() + "...";
  if (!t) t = "New Chat";
  return t;
}

export default function ChatClient({
  initialConversations = [] as any[],
  selectedPublicId = null as string | null,
}) {
  const router = useRouter();

  const initial = useMemo<Conv[]>(
    () => {
      const raw = Array.isArray(initialConversations)
        ? initialConversations
        : (Array.isArray((initialConversations as any)?.items) ? (initialConversations as any).items : []);
      return dedupeAndSort(raw as Conv[]);
    },
    [initialConversations]
  );

  const [convs, setConvs] = useState<Conv[]>(initial);
  const [activeTab, setActiveTab] = useState<"all" | "owned" | "collab" | "readonly">("all");
  const [selectedId, setSelectedId] = useState<string | null>(selectedPublicId);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const selectedConv = useMemo(() => convs.find((c) => c.id === selectedId) ?? null, [convs, selectedId]);

  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const esRef = useRef<{ close: () => void } | null>(null);
  const [streaming, setStreaming] = useState(false);

  // -- counts by role and current tab count -- //
  const counts = useMemo(() => {
    const owned = convs.filter(c => c.access_role === "owner").length;
    const collab = convs.filter(c => c.access_role === "editor").length;
    const readonly = convs.filter(c => c.access_role === "viewer").length;
    return { total: convs.length, owned, collab, readonly };
  }, [convs]);

  const currentCount = useMemo(() => {
    switch (activeTab) {
      case "owned": return counts.owned;
      case "collab": return counts.collab;
      case "readonly": return counts.readonly;
      default: return counts.total;
    }
  }, [activeTab, counts]);

  // sync selected id on route param change
  useEffect(() => { setSelectedId(selectedPublicId); }, [selectedPublicId]);

  // load history on first mount or when switching
  useEffect(() => {
    if (selectedPublicId) loadConvMessages(selectedPublicId);
    else setMsgs([]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedPublicId]);

  const refreshConvs = useCallback(async () => {
    const res = await fetch("/api/conversations", { cache: "no-store" }).catch(() => null);
    if (!res || !res.ok) return;
    const data = await res.json().catch(() => []);
    const items: Conv[] = Array.isArray(data) ? data : (Array.isArray(data?.items) ? data.items : []);
    setConvs(dedupeAndSort(items));
  }, []);

  const loadConvMessages = useCallback(async (publicId: string) => {
    const res = await fetch(`/api/conversations/${publicId}`, { cache: "no-store" }).catch(() => null);
    if (res && res.ok) {
      const data = await res.json().catch(() => null);
      const arr = Array.isArray(data?.messages) ? data.messages : (Array.isArray(data) ? data : []);
      if (arr.length) {
        const mapped: Msg[] = arr.map((r: any) => ({
          role: (r.role as Msg["role"]) || (r.is_user ? "user" : "assistant"),
          text: r.text || r.content || "",
        }));
        setMsgs(mapped); return;
      }
    }
    setMsgs([]);
  }, []);

  // tab filter
  const filteredConvs = useMemo(() => {
    if (activeTab === "all") return convs;
    if (activeTab === "owned") return convs.filter(c => c.access_role === "owner");
    if (activeTab === "collab") return convs.filter(c => c.access_role === "editor");
    return convs.filter(c => c.access_role === "viewer");
  }, [convs, activeTab]);

  const selectConv = useCallback(async (publicId: string) => {
    esRef.current?.close(); setStreaming(false);
    setSelectedId(publicId);
    router.push(`/chat/${publicId}`);
    await loadConvMessages(publicId);
  }, [router, loadConvMessages]);

  const newChat = useCallback(() => {
    esRef.current?.close(); setStreaming(false);
    setSelectedId(null); setMsgs([]); setInput("");
    router.push(`/chat`);
  }, [router]);

  const renameConv = useCallback(async (c: Conv) => {
    const current = labelOf(c);
    const title = window.prompt("Rename conversation", current) ?? "";
    const trimmed = title.trim();
    if (!trimmed || trimmed === current) return;
    const res = await fetch(`/api/conversations/${c.id}`, {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ title: trimmed }),
    }).catch(() => null);
    if (res && res.ok) {
      const updated = await res.json().catch(()=>null);
      if (updated) setConvs(prev => upsert(prev, updated));
    }
  }, []);

  const shareConv = useCallback(async (c: Conv) => {
    const email = window.prompt("Share with (email):")?.trim();
    if (!email) return;
    const role = (window.prompt("Role? editor/viewer (default viewer)") || "viewer").trim().toLowerCase();
    const finalRole = (role === "editor" ? "editor" : "viewer");
    const res = await fetch(`/api/conversations/${c.id}/shares`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ email, role: finalRole }),
    }).catch(() => null);
    if (res && (res.status === 204 || res.ok)) {
      await refreshConvs();
      alert(`Shared with ${email} as ${finalRole}.`);
    } else {
      alert("Share failed.");
    }
  }, [refreshConvs]);

  /** Ensure a conversation exists. Returns { id, isNew }. Also upserts the list. */
  async function ensureConversation(): Promise<{ id: string; isNew: boolean }> {
    if (selectedId) return { id: selectedId, isNew: false };

    const res = await fetch("/api/conversations", {
      method: "POST",
      headers: { "content-type": "application/json" },
      credentials: "include",
    }).catch(() => null as any);

    if (!res || !res.ok) throw new Error(`create conversation failed: ${res?.status ?? "network error"}`);
    const data = await res.json().catch(() => null as any);
    const id = data?.id as string | undefined;
    if (!id) throw new Error("upstream did not return id");

    setConvs(prev => upsert(prev, data));
    setSelectedId(id);
    router.replace(`/chat/${id}`);
    return { id, isNew: true };
  }

  /** Send message: URL -> /api/query/stream/:id, body -> { content }. For a new conversation, auto rename after first input. */
  const send = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed || streaming) return;
    if (selectedConv?.access_role === "viewer") {
      alert("This chat is read-only.");
      return;
    }

    setMsgs((m) => [...m, { role: "user", text: trimmed }, { role: "assistant", text: "" }]);
    setInput(""); setStreaming(true);

    let convInfo: { id: string; isNew: boolean };
    try {
      convInfo = await ensureConversation();
    } catch (e: any) {
      setStreaming(false);
      setMsgs((m) => [...m, { role: "info", text: `[error] ${String(e?.message || e)}` }]);
      return;
    }

    // For a new conversation: auto rename (non-blocking)
    if (convInfo.isNew) {
      const autoTitle = makeAutoTitle(trimmed);
      (async () => {
        const res = await fetch(`/api/conversations/${convInfo.id}`, {
          method: "PATCH",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ title: autoTitle }),
        }).catch(() => null);
        if (res && res.ok) {
          const updated = await res.json().catch(()=>null);
          if (updated) setConvs(prev => upsert(prev, updated));
        }
      })();
    }

    const url = `/api/query/stream/${encodeURIComponent(convInfo.id)}`;
    const payload = { content: trimmed };

    esRef.current?.close();
    esRef.current = startSSE(url, payload, {
      onMessage: (t: string) => {
        const add = sanitizeChunk(t);
        if (!add) return;
        setMsgs((m) => {
          let idx = -1;
          for (let i = m.length - 1; i >= 0; i--) if (m[i].role === "assistant") { idx = i; break; }
          if (idx === -1) return [...m, { role: "assistant", text: add }];
          const cur = m[idx];
          return [...m.slice(0, idx), { ...cur, text: (cur.text ?? "") + add }, ...m.slice(idx + 1)];
        });
      },
      onClose: async () => {
        setStreaming(false);
        setMsgs((m) => {
          if (!m.length) return m;
          const last = m[m.length - 1];
          if (last.role === "assistant" && !last.text.trim()) return m.slice(0, -1);
          return m;
        });
        await refreshConvs(); // refresh after backend updates timestamp
      },
      onError: (e: unknown) => {
        setStreaming(false);
        setMsgs((m) => [...m, { role: "info", text: `[error] ${String(e)}` }]);
      },
    });
  }, [input, streaming, selectedConv, refreshConvs]);

  useEffect(() => () => { esRef.current?.close(); }, []);

  return (
    <div style={{ height: "100vh", display: "grid", gridTemplateColumns: sidebarOpen ? "300px 1fr" : "0 1fr" }}>
      {/* Sidebar */}
      <aside style={{ borderRight: "1px solid #eee", overflow: "hidden", background: "#fafafa" }}>
        <div style={{ display: "flex", gap: 8, padding: 10, borderBottom: "1px solid #eee", alignItems: "center" }}>
          <button onClick={newChat} style={{ padding: "6px 10px" }}>New chat</button>
          {/* Show current tab count (and total for non-All tabs) */}
          <div style={{ marginLeft: "auto", fontSize: 12, opacity: .7 }}>
            {currentCount} conversations{activeTab !== "all" ? ` (of ${counts.total})` : ""}
          </div>
        </div>

        {/* Tabs */}
        <div style={{ display: "flex", gap: 6, padding: "8px 10px", borderBottom: "1px solid #eee", fontSize: 13 }}>
          {[
            ["all","All"],["owned","Owned"],["collab","Collaborating"],["readonly","Read-only"],
          ].map(([k, label]) => (
            <button key={k}
              onClick={() => setActiveTab(k as any)}
              style={{
                padding: "4px 8px",
                borderRadius: 6,
                border: "1px solid #ddd",
                background: activeTab===k ? "#e7f0ff" : "#fff",
                fontWeight: activeTab===k ? 700 : 500
              }}
            >{label}</button>
          ))}
        </div>

        <div style={{ height: "calc(100% - 90px)", overflow: "auto" }}>
          {filteredConvs.length === 0 ? (
            <div style={{ padding: 12, opacity: 0.6 }}>
              {activeTab === "owned" ? "You haven't started any chats yet."
              : activeTab === "collab" ? "No chats shared with you to edit."
              : activeTab === "readonly" ? "No read-only shares yet."
              : "No conversations."}
            </div>
          ) : (
            filteredConvs.map((c) => {
              const active = c.id === selectedId;
              const badge = c.access_role === "owner" ? "Owned"
                : c.access_role === "editor" ? `Collaborating${c.shared_by?.name ? ` - shared by ${c.shared_by.name}` : ""}`
                : `Read-only${c.shared_by?.name ? ` - shared by ${c.shared_by.name}` : ""}`;
              return (
                <div key={c.id} style={{ borderBottom: "1px solid #eee", background: active ? "#eef6ff" : "transparent" }}>
                  <div onClick={() => selectConv(c.id)} style={{ cursor: "pointer", padding: "10px 12px" }} title={labelOf(c)}>
                    <div style={{ fontWeight: 600, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{labelOf(c)}</div>
                    <div style={{ fontSize: 11, color: "#666" }}>{badge}</div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </aside>

      {/* Main */}
      <main style={{ display: "grid", gridTemplateRows: "auto 1fr auto" }}>
        <div style={{ display: "flex", gap: 8, alignItems: "center", padding: "10px 12px", borderBottom: "1px solid #eee" }}>
          <button onClick={() => setSidebarOpen((v) => !v)} style={{ padding: "6px 10px" }}>
            {sidebarOpen ? "Hide sidebar" : "Show sidebar"}
          </button>

          {/* Title */}
          <div style={{ fontWeight: 700, flex: 1, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {selectedConv ? labelOf(selectedConv) : "New conversation"}
          </div>

          {/* Only show when a conversation is selected and user has permission */}
          {!!selectedConv && (selectedConv.access_role === "owner" || selectedConv.access_role === "editor") && (
            <div style={{ display: "flex", gap: 8 }}>
              <button
                onClick={() => renameConv(selectedConv)}
                style={{ padding: "6px 10px" }}
                title="Rename this conversation"
              >
                Rename
              </button>
              <button
                onClick={() => shareConv(selectedConv)}
                style={{ padding: "6px 10px" }}
                title="Share this conversation"
              >
                Share
              </button>
            </div>
          )}
        </div>

        {/* Read-only banner */}
        {selectedConv?.access_role === "viewer" && (
          <div style={{ padding: "8px 12px", background: "#fffbe6", borderBottom: "1px solid #eee", fontSize: 13 }}>
            Read-only - {selectedConv.shared_by?.name || selectedConv.shared_by?.email ? `shared by ${selectedConv.shared_by?.name || selectedConv.shared_by?.email}` : "shared with you"}
          </div>
        )}

        {/* Messages */}
        <div style={{ overflow: "auto", padding: 16 }}>
          {msgs.length === 0 ? (
            <div style={{ opacity: .6 }}>Say something to start...</div>
          ) : (
            <div style={{ display: "grid", gap: 8 }}>
              {msgs.map((m, i) => (
                <div key={i} style={{ padding: "10px 12px", borderRadius: 8, border: "1px solid #eee", background: m.role === "user" ? "#fff" : "#f7f7f7" }}>
                  <div style={{ whiteSpace: "pre-wrap" }}>{m.text}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Composer */}
        <div style={{ padding: 12, borderTop: "1px solid #eee" }}>
          <div style={{ display: "flex", gap: 8 }}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") send(); }}
              placeholder={selectedConv?.access_role === "viewer" ? "Read-only chat" : "Type your message..."}
              style={{ flex: 1, padding: "8px 12px" }}
              disabled={streaming || selectedConv?.access_role === "viewer"}
            />
            <button onClick={send} disabled={streaming || selectedConv?.access_role === "viewer"} style={{ minWidth: 96 }}>
              {streaming ? "Sending..." : "Send"}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
