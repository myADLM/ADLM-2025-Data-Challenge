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
  created_at?: number | string | null;
  updated_at?: number | string | null;
  last_message_at?: number | string | null;
  access_role?: AccessRole;
  shared_by?: UserBrief | null;
  unread_count?: number;
  activity_at?: number | string | null; // server-provided activity hint
  [k: string]: any;
};

type Msg = { role: "user" | "assistant" | "system" | "info"; text: string; created_at?: number };

/** Polling & backoff config */
const POLL_LIST_MS = 12000; // conversation list
const POLL_MSG_MS  = 4000;  // messages
const BACKOFF_BASE_MS = 5000;
const BACKOFF_MAX_MS  = 60000;
const READ_TO_MIN_INTERVAL_MS = 8000; // at most once per 8s per conversation (read/read_to throttling)

/** Prefer activity_at; fallback to last_message_at > updated_at > created_at */
function ts(c: Conv): number {
  const n = (v: any) => (v == null ? 0 : Number(v));
  return n((c as any).activity_at ?? c.last_message_at ?? c.updated_at ?? c.created_at ?? 0);
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
/** Make an auto title from first input */
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

function RoleBadge({ c }: { c: Conv }) {
  if (!c) return null;
  if (c.access_role === "editor") {
    return (
      <span
        title="You can edit and send messages in this shared chat."
        style={{
          marginLeft: 8,
          padding: "2px 8px",
          borderRadius: 999,
          border: "1px solid #cfe8ff",
          background: "#eaf4ff",
          color: "#1456a0",
          fontSize: 12,
          whiteSpace: "nowrap",
          alignSelf: "center",
          flexShrink: 0,
        }}
      >
        Collaborating{c.shared_by?.name ? `, shared by ${c.shared_by.name}` : ""}
      </span>
    );
  }
  if (c.access_role === "viewer") {
    return (
      <span
        title="Read-only: you can't send messages or rename this chat."
        style={{
          marginLeft: 8,
          padding: "2px 8px",
          borderRadius: 999,
          border: "1px solid #f5d0d0",
          background: "#ffecec",
          color: "#9b1c1c",
          fontSize: 12,
          whiteSpace: "nowrap",
          alignSelf: "center",
          flexShrink: 0,
        }}
      >
        Read-only{c.shared_by?.name ? `, shared by ${c.shared_by.name}` : ""}
      </span>
    );
  }
  return null; // owner: not show
}

const latestTs = (arr: Msg[]) => arr.reduce((mx, m) => Math.max(mx, Number(m.created_at || 0)), 0);

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
  const msgsRef = useRef<Msg[]>([]);
  useEffect(() => { msgsRef.current = msgs; }, [msgs]);

  const [input, setInput] = useState("");
  const [queuedInput, setQueuedInput] = useState<string | null>(null); // queued content
  const queuedRef = useRef<string | null>(null);
  useEffect(() => { queuedRef.current = queuedInput; }, [queuedInput]);

  const esRef = useRef<{ close: () => void } | null>(null);
  const [streaming, setStreaming] = useState(false);
  const flushingRef = useRef(false);

  // detect remote SSE streaming
  const [remoteStreaming, setRemoteStreaming] = useState(false);
  const remoteStreamTouchedAtRef = useRef(0);
  const prevAssistantLenRef = useRef(0);

  // remember locally sent user messages (for "New" marker correction)
  const localSentRef = useRef<Array<{ text: string; ts: number }>>([]);

  // unread anchor
  const [lastSeenAt, setLastSeenAt] = useState<number>(0);
  const unreadAnchorIndexRef = useRef<number | null>(null);
  const msgRefs = useRef<Map<number, HTMLDivElement | null>>(new Map());
  // on first load: if no unread anchor, scroll to bottom
  const needsInitialScrollRef = useRef<boolean>(false);

  // === Local shadow "seen": override server unread to avoid sticky unread in shared chats ===
  const shadowSeenRef = useRef<Map<string, number>>(new Map()); // convId -> seen_ts

  // counts by role and current tab count
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

  // sync selected id when route param changes
  useEffect(() => { setSelectedId(selectedPublicId); }, [selectedPublicId]);

  // ------ backoff state & refresh de-dup ------
  const listBackoffRef = useRef<number>(0);
  const msgBackoffRef  = useRef<number>(0);
  const refreshConvsInFlightRef = useRef<Promise<void> | null>(null);

  // ------ read/read_to throttle memory ------
  const lastReadSentTsRef = useRef<Map<string, number>>(new Map());   // sent ts values
  const lastReadSentAtMsRef = useRef<Map<string, number>>(new Map()); // last send time (ms)

  const isRemotelyStreaming = useCallback(
    () => (Date.now() - remoteStreamTouchedAtRef.current) < 7000,
    []
  );
  const isBusy = useCallback(
    () => streaming || isRemotelyStreaming(),
    [streaming, isRemotelyStreaming]
  );

  // list refresh (with 429 backoff & in-flight merge)
  const refreshConvs = useCallback(async () => {
    if (refreshConvsInFlightRef.current) return refreshConvsInFlightRef.current;
    const run = async () => {
      const res = await fetch("/api/conversations", { cache: "no-store" }).catch(() => null);
      if (!res) return;
      if (res.status === 429) {
        listBackoffRef.current = Math.min(BACKOFF_MAX_MS, listBackoffRef.current ? listBackoffRef.current * 2 : BACKOFF_BASE_MS);
        return;
      }
      listBackoffRef.current = 0;
      if (!res.ok) return;
      const data = await res.json().catch(() => []);
      const items: Conv[] = Array.isArray(data) ? data : (Array.isArray((data as any)?.items) ? (data as any).items : []);
      setConvs(dedupeAndSort(items));
    };
    const p = run().finally(() => { refreshConvsInFlightRef.current = null; });
    refreshConvsInFlightRef.current = p;
    return p;
  }, []);

  // ===== Mark as read (use /read; maintain local shadow "seen") =====
  const markRead = useCallback(async (pubId: string, seenTs: number, force = false) => {
    if (!pubId) return;
    const lastSentTs = lastReadSentTsRef.current.get(pubId) || 0;
    const lastSentAt = lastReadSentAtMsRef.current.get(pubId) || 0;
    const now = Date.now();
    if (!force) {
      if (seenTs <= lastSentTs) return;
      if (now - lastSentAt < READ_TO_MIN_INTERVAL_MS) return;
    }
    try {
      const r = await fetch(`/api/conversations/${pubId}/read`, { method: "POST" });
      if (r.status === 429) {
        msgBackoffRef.current = Math.min(BACKOFF_MAX_MS, msgBackoffRef.current ? msgBackoffRef.current * 2 : BACKOFF_BASE_MS);
        return;
      }
      // regardless of immediate server effect, override unread locally first
      shadowSeenRef.current.set(pubId, seenTs);
      setConvs(prev => prev.map(c => c.id === pubId ? ({ ...c, unread_count: 0 }) : c));
      if (r.ok) {
        lastReadSentTsRef.current.set(pubId, seenTs);
        lastReadSentAtMsRef.current.set(pubId, now);
      }
    } catch {}
  }, []);

  // Current conversation: load + compute unread anchor + mark read
  const loadConvMessages = useCallback(async (publicId: string) => {
    const res = await fetch(`/api/conversations/${publicId}`, { cache: "no-store" }).catch(() => null);
    if (res && res.status === 429) { msgBackoffRef.current = Math.min(BACKOFF_MAX_MS, msgBackoffRef.current ? msgBackoffRef.current * 2 : BACKOFF_BASE_MS); return; }
    if (res && res.ok) {
      const data = await res.json().catch(() => null);
      const arr = Array.isArray((data as any)?.messages) ? (data as any).messages : (Array.isArray(data) ? data : []);
      const mapped: Msg[] = (arr || []).map((r: any) => ({
        role: (r.role as Msg["role"]) || (r.is_user ? "user" : "assistant"),
        text: r.text || r.content || "",
        created_at: Number(r.created_at || 0),
      }));
      setMsgs(mapped);
      // on first render of this entry, if no unread anchor, scroll to bottom
      needsInitialScrollRef.current = true;

      const ls = Number((data as any)?.last_seen_at || 0);
      setLastSeenAt(ls);

      const idx = mapped.findIndex(m => (Number(m.created_at || 0) > ls));
      unreadAnchorIndexRef.current = idx >= 0 ? idx : null;

      const last = latestTs(mapped);
      // local shadow "seen": override immediately upon entering
      if (last > 0) {
        shadowSeenRef.current.set(publicId, last);
        await markRead(publicId, last); // background marker
      }

      // update list timestamps & local unread
      setConvs(prev => prev.map(c => c.id === publicId ? { ...c, last_message_at: Math.max(Number(c.last_message_at||0), last), unread_count: 0 } : c));

      // remote stream detection (assistant text length changes)
      const lastMsg = mapped[mapped.length - 1];
      if (lastMsg?.role === "assistant") {
        const len = (lastMsg.text || "").length;
        if (len !== prevAssistantLenRef.current) {
          prevAssistantLenRef.current = len;
          remoteStreamTouchedAtRef.current = Date.now();
        }
      } else {
        prevAssistantLenRef.current = 0;
      }
      setRemoteStreaming((Date.now() - remoteStreamTouchedAtRef.current) < 7000);
      return;
    }
    setMsgs([]); setLastSeenAt(0); unreadAnchorIndexRef.current = null;
  }, [markRead]);

  // After render: if unread anchor -> scroll to it; else on first entry -> scroll to bottom
  useEffect(() => {
    const idx = unreadAnchorIndexRef.current;
    if (idx != null && idx >= 0) {
      const el = msgRefs.current.get(idx);
      if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
      unreadAnchorIndexRef.current = null;
      needsInitialScrollRef.current = false; // handled
      return;
    }
    if (needsInitialScrollRef.current) {
      const lastEl = msgRefs.current.get(msgs.length - 1);
      if (lastEl) lastEl.scrollIntoView({ behavior: "auto", block: "end" });
      needsInitialScrollRef.current = false;
    }
  }, [msgs]);

  // load on mount / route change
  useEffect(() => {
    if (selectedPublicId) loadConvMessages(selectedPublicId);
    else { setMsgs([]); setLastSeenAt(0); }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedPublicId]);

  // tab filter
  const filteredConvs = useMemo(() => {
    if (activeTab === "all") return convs;
    if (activeTab === "owned") return convs.filter(c => c.access_role === "owner");
    if (activeTab === "collab") return convs.filter(c => c.access_role === "editor");
    return convs.filter(c => c.access_role === "viewer");
  }, [convs, activeTab]);

  // Poll conversation list
  useEffect(() => {
    let timer: any;
    const tick = async () => {
      if (!document.hidden) await refreshConvs();
      const next = listBackoffRef.current || POLL_LIST_MS;
      timer = setTimeout(tick, next);
    };
    tick();
    return () => { clearTimeout(timer); };
  }, [refreshConvs]);

  // Poll messages for current conversation + detect remote streaming + flush queue
  useEffect(() => {
    if (!selectedId) return;
    let timer: any;
    let cancelled = false;

    const poll = async () => {
      if (document.hidden) {
        timer = setTimeout(poll, POLL_MSG_MS);
        return;
      }
      const res = await fetch(`/api/conversations/${selectedId}`, { cache: "no-store" }).catch(() => null);
      if (cancelled) return;
      if (res && res.status === 429) {
        msgBackoffRef.current = Math.min(BACKOFF_MAX_MS, msgBackoffRef.current ? msgBackoffRef.current * 2 : BACKOFF_BASE_MS);
      } else if (res && res.ok) {
        msgBackoffRef.current = 0;
        const data = await res.json().catch(() => null);
        const arr = Array.isArray((data as any)?.messages) ? (data as any).messages : (Array.isArray(data) ? data : []);
        const mapped: Msg[] = (arr || []).map((r: any) => ({
          role: (r.role as Msg["role"]) || (r.is_user ? "user" : "assistant"),
          text: r.text || r.content || "",
          created_at: Number(r.created_at || 0),
        }));
        const curLast = latestTs(msgsRef.current);
        const newLast = latestTs(mapped);
        if (newLast > curLast) {
          setMsgs(mapped);
          // upon entry or when pulling newer messages, raise shadow seen and mark /read in background
          shadowSeenRef.current.set(selectedId, newLast);
          if (newLast > 0) { (async () => { await markRead(selectedId, newLast); })(); }

          const ls = Number((data as any)?.last_seen_at || 0);
          setLastSeenAt(ls);
          setConvs(prev => prev.map(c => c.id === selectedId ? { ...c, unread_count: 0, last_message_at: Math.max(Number(c.last_message_at||0), newLast) } : c));
        }

        // remote stream detection
        const lastMsg = mapped[mapped.length - 1];
        if (lastMsg?.role === "assistant") {
          const len = (lastMsg.text || "").length;
          if (len !== prevAssistantLenRef.current) {
            prevAssistantLenRef.current = len;
            remoteStreamTouchedAtRef.current = Date.now();
          }
        } else {
          prevAssistantLenRef.current = 0;
        }
        setRemoteStreaming((Date.now() - remoteStreamTouchedAtRef.current) < 7000);
      }

      // If queued and not busy -> flush
      if (queuedRef.current && !isBusy() && !flushingRef.current) {
        flushingRef.current = true;
        const nextToSend = queuedRef.current!;
        setQueuedInput(null);
        await sendNow(nextToSend);
        flushingRef.current = false;
      }

      const next = msgBackoffRef.current || POLL_MSG_MS;
      timer = setTimeout(poll, next);
    };
    poll();
    return () => { cancelled = true; clearTimeout(timer); };
  }, [selectedId, markRead, isBusy]);

  // When leaving a conversation, send a final /read (force)
  const prevSelectedRef = useRef<string | null>(null);
  useEffect(() => {
    const prev = prevSelectedRef.current;
    if (prev && prev !== selectedId) {
      const last = latestTs(msgsRef.current);
      if (last > 0) { (async () => { await markRead(prev, last, true); })(); }
    }
    prevSelectedRef.current = selectedId;
  }, [selectedId, markRead]);

  const selectConv = useCallback(async (publicId: string) => {
    esRef.current?.close(); setStreaming(false);
    setSelectedId(publicId);
    router.push(`/chat/${publicId}`);
    await loadConvMessages(publicId);
  }, [router, loadConvMessages]);

  const newChat = useCallback(() => {
    esRef.current?.close(); setStreaming(false);
    setSelectedId(null); setMsgs([]); setInput(""); setQueuedInput(null);
    setLastSeenAt(0); unreadAnchorIndexRef.current = null;
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

  const refreshConvsAndLocal = useCallback(async () => {
    await refreshConvs();
    if (selectedId) {
      const last = latestTs(msgsRef.current);
      if (last > 0) await markRead(selectedId, last, true);
    }
  }, [refreshConvs, selectedId, markRead]);

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

  async function ensureConversation(): Promise<{ id: string; isNew: boolean }> {
    if (selectedId) return { id: selectedId, isNew: false };

    const res = await fetch("/api/conversations", {
      method: "POST",
      headers: { "content-type": "application/json" },
      credentials: "include",
    }).catch(() => null as any);

    if (!res || !res.ok) throw new Error(`create conversation failed: ${res?.status ?? "network error"}`);
    const data = await res.json().catch(() => null as any);
    const id = (data as any)?.id as string | undefined;
    if (!id) throw new Error("upstream did not return id");

    setConvs(prev => upsert(prev, data as any));
    setSelectedId(id);
    router.replace(`/chat/${id}`);
    return { id, isNew: true };
  }

  // Send immediately (queue check happens elsewhere)
  const sendNow = useCallback(async (text: string) => {
    if (!text) return;
    if (selectedConv?.access_role === "viewer") {
      alert("This chat is read-only.");
      return;
    }

    const tsNow = Date.now();
    // remember my own user message locally, for New marker calculations
    localSentRef.current.push({ text, ts: tsNow });

    setMsgs((m) => [...m, { role: "user", text, created_at: tsNow }, { role: "assistant", text: "" }]);
    setStreaming(true);

    let convInfo: { id: string; isNew: boolean };
    try {
      convInfo = await ensureConversation();
    } catch (e: any) {
      setStreaming(false);
      setMsgs((m) => [...m, { role: "info", text: `[error] ${String(e?.message || e)}` }]);
      return;
    }

    // after sending, set last_seen to now; update shadow seen and send /read
    setLastSeenAt(tsNow);
    shadowSeenRef.current.set(convInfo.id, tsNow);
    markRead(convInfo.id, tsNow, true);
    setConvs(prev => prev.map(c => c.id === convInfo.id ? { ...c, unread_count: 0 } : c));

    // auto-rename for the first input of a new conversation
    if (convInfo.isNew) {
      const autoTitle = makeAutoTitle(text);
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
    const payload = { content: text };

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
        await refreshConvsAndLocal();

        // after stream ends: if there is a queued message -> send next
        if (queuedRef.current && !isBusy() && !flushingRef.current) {
          flushingRef.current = true;
          const next = queuedRef.current!;
          setQueuedInput(null);
          await sendNow(next);
          flushingRef.current = false;
        }
      },
      onError: (e: unknown) => {
        setStreaming(false);
        setMsgs((m) => [...m, { role: "info", text: `[error] ${String(e)}` }]);
      },
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedConv, ensureConversation, refreshConvsAndLocal, isBusy]);

  // On user send: if busy -> enqueue; else -> send now
  const send = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed) return;
    setInput("");

    if (isBusy()) {
      setQueuedInput(prev => prev ? `${prev}\n\n${trimmed}` : trimmed);
      return;
    }
    await sendNow(trimmed);
  }, [input, isBusy, sendNow]);

  useEffect(() => () => { esRef.current?.close(); }, []);

  // ----- Render helpers -----
  const isProbablyMine = useCallback((m: Msg) => {
    if (m.role !== "user") return false;
    const t = Number(m.created_at || 0);
    return localSentRef.current.some(s =>
      s.text === m.text && Math.abs(t - s.ts) < 15000
    );
  }, []);

  // Unread for display (overridden by shadow seen)
  const displayUnread = useCallback((c: Conv) => {
    const shadow = shadowSeenRef.current.get(c.id) || 0;
    const lastActivity = ts(c);
    if (shadow >= lastActivity) return 0;
    return Number(c.unread_count || 0);
  }, []);

  const buttonLabel = streaming
    ? "Sending..."
    : queuedInput
      ? "Queued"
      : remoteStreaming
        ? "Wait..."
        : "Send";

  return (
    <div style={{ height: "100dvh", display: "grid", gridTemplateColumns: sidebarOpen ? "300px 1fr" : "0 1fr", minHeight: 0 }}>
      {/* Sidebar */}
      <aside
        aria-hidden={!sidebarOpen}
        style={{
          borderRight: sidebarOpen ? "1px solid #eee" : "none", // when collapsed: no border
          background: "#fafafa",
          display: "flex",
          flexDirection: "column",
          minHeight: 0,
          overflow: sidebarOpen ? "visible" : "hidden", // clip overflow when collapsed
          visibility: sidebarOpen ? "visible" : "hidden", // hidden when collapsed
          pointerEvents: sidebarOpen ? "auto" : "none", // no pointer events when collapsed
          opacity: sidebarOpen ? 1 : 0,
          transition: "opacity 120ms ease"
        }}
      >
        <div style={{ display: "flex", gap: 8, padding: 10, borderBottom: "1px solid #eee", alignItems: "center" }}>
          <button onClick={newChat} style={{ padding: "6px 10px" }}>New chat</button>
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

        <div style={{ flex: 1, minHeight: 0, overflow: "auto" }}>
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
              const unread = displayUnread(c);
              const badge = c.access_role === "owner" ? "Owned"
                : c.access_role === "editor" ? `Collaborating${c.shared_by?.name ? ` - shared by ${c.shared_by.name}` : ""}`
                : `Read-only${c.shared_by?.name ? ` - shared by ${c.shared_by.name}` : ""}`;
              return (
                <div key={c.id} style={{ borderBottom: "1px solid #eee", background: active ? "#eef6ff" : "transparent" }}>
                  <div
                    onClick={() => selectConv(c.id)}
                    style={{ cursor: "pointer", padding: "10px 12px", display: "grid", gridTemplateColumns: "1fr auto", gap: 8, alignItems: "center" }}
                    title={labelOf(c)}
                  >
                    <div style={{ minWidth: 0 }}>
                      <div style={{
                        fontWeight: unread > 0 ? 800 : 600,
                        whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis"
                      }}>
                        {labelOf(c)}
                      </div>
                      <div style={{ fontSize: 11, color: "#666" }}>{badge}</div>
                    </div>
                    {unread > 0 && (
                      <div style={{
                        justifySelf: "end",
                        minWidth: 22, padding: "2px 6px", borderRadius: 999,
                        border: "1px solid #f1c0c0", background: "#ffe6e6", color: "#b40000",
                        fontSize: 12, textAlign: "center", fontWeight: 800,
                      }}>
                        {unread > 99 ? "99+" : unread}
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </aside>

      {/* Main */}
      <main style={{ display: "grid", gridTemplateRows: "auto 1fr auto", minHeight: 0 }}>
        <div style={{ display: "flex", gap: 8, alignItems: "center", padding: "10px 12px", borderBottom: "1px solid #eee" }}>
          <button onClick={() => setSidebarOpen((v) => !v)} style={{ padding: "6px 10px" }}>
            {sidebarOpen ? "Hide sidebar" : "Show sidebar"}
          </button>

          {/* Show Role badge between title and action buttons (non-owner only) */}
          {selectedConv && <RoleBadge c={selectedConv} />}

          <div style={{ fontWeight: 700, flex: 1, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {selectedConv ? labelOf(selectedConv) : "New conversation"}
          </div>

          {!!selectedConv && (selectedConv.access_role === "owner" || selectedConv.access_role === "editor") && (
            <div style={{ display: "flex", gap: 8 }}>
              <button onClick={() => renameConv(selectedConv)} style={{ padding: "6px 10px" }} title="Rename this conversation">Rename</button>
              <button onClick={() => shareConv(selectedConv)}  style={{ padding: "6px 10px" }} title="Share this conversation">Share</button>
            </div>
          )}
        </div>

        {/* Messages */}
        <div style={{ overflow: "auto", padding: 16, minHeight: 0 }}>
          {msgs.length === 0 ? (
            <div style={{ opacity: .6 }}>Say something to start...</div>
          ) : (
            <div style={{ display: "grid", gap: 8 }}>
              {msgs.map((m, i) => {
                const created = Number(m.created_at || 0);
                const prevCreated = Number((msgs[i - 1] as any)?.created_at || 0);
                const mine = isProbablyMine(m);
                const prevMine = i>0 ? isProbablyMine(msgs[i-1]) : false;

                const isUnreadStart =
                  lastSeenAt > 0 &&
                  created > lastSeenAt &&
                  !mine &&
                  (i === 0 || prevCreated <= lastSeenAt || prevMine);

                return (
                  <div key={i}>
                    {isUnreadStart && (
                      <div style={{ textAlign: "center", margin: "8px 0" }}>
                        <span style={{
                          padding: "2px 8px", fontSize: 12, borderRadius: 16,
                          background: "#e8f0ff", border: "1px solid #cfe0ff", color: "#2055c4"
                        }}>New</span>
                      </div>
                    )}
                    <div
                      ref={(el) => { msgRefs.current.set(i, el); }}
                      style={{
                        padding: "10px 12px", borderRadius: 8, border: "1px solid #eee",
                        background: m.role === "user" ? "#fff" : "#f7f7f7", whiteSpace: "pre-wrap"
                      }}
                    >
                      {m.text}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Composer */}
        <div style={{ padding: 12, borderTop: "1px solid #eee" }}>
          <div style={{ display: "flex", gap: 8 }}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); (async () => { await send(); })(); } }}
              placeholder={
                selectedConv?.access_role === "viewer"
                  ? "Read-only chat"
                  : remoteStreaming
                    ? (queuedInput ? "AI is answering... your message is queued" : "AI is answering... press Enter to queue")
                    : "Type your message..."
              }
              style={{ flex: 1, padding: "8px 12px" }}
              disabled={selectedConv?.access_role === "viewer"}
            />
            <button
              onClick={() => { (async () => { await send(); })(); }}
              disabled={selectedConv?.access_role === "viewer"}
              style={{ minWidth: 96 }}
            >
              {buttonLabel}
            </button>
          </div>
          {!!queuedInput && (
            <div style={{ marginTop: 6, fontSize: 12, color: "#666" }}>
              Queued: <span style={{ opacity: .85 }}>{queuedInput.slice(0, 80)}{queuedInput.length>80?"...":""}</span>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
