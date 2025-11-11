// net/web/src/app/chat/Client.tsx

"use client";
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
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
  activity_at?: number | string | null;
  [k: string]: any;
};

type SourceDoc = {
  doc_id: string;
  title: string;
  source_url: string;
  page: number | null;
  snippet?: string | null;
  mime_type?: string | null;
  file_size?: number | null;
};

type Msg = {
  role: "user" | "assistant" | "system";
  text: string;
  created_at?: number;
  sources?: SourceDoc[];
  user_id?: number | null;
  user_name?: string | null;
  user_email?: string | null;
};

type Member = {
  user: UserBrief;
  role: "owner" | "editor" | "viewer";
  invited_by: UserBrief;
  created_at: number;
};

type Me = { id: number; email?: string | null; name?: string | null };

/** Polling & backoff config */
const POLL_LIST_MS = 12000;
const POLL_MSG_MS  = 4000;
const BACKOFF_BASE_MS = 5000;
const BACKOFF_MAX_MS  = 60000;
const READ_TO_MIN_INTERVAL_MS = 8000;

const MOBILE_BP = 768; // Mobile breakpoint for phone screens
const HYST = 18;

const getViewportW = () =>
  typeof document !== "undefined" ? document.documentElement.clientWidth : 0;

/** ----- helpers ----- */
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
function dedupeAndSort(list: Conv[]): Conv[] {
  const map = new Map<string, Conv>();
  for (const c of list) map.set(c.id, { ...(map.get(c.id) || {}), ...c });
  return Array.from(map.values()).sort(byDesc);
}

/** Key: compare conversation list signatures to detect "actual changes"; avoid setState when unchanged to prevent flicker */
const convSig = (c: Conv) =>
  `${c.id}|${Number(c.last_message_at)||0}|${Number(c.unread_count)||0}|${c.access_role||""}|${labelOf(c)}`;
function sameConvs(a: Conv[], b: Conv[]): boolean {
  if (a === b) return true;
  if (a.length !== b.length) return false;
  const mb = new Map(b.map(x => [x.id, convSig(x)]));
  for (const x of a) if (mb.get(x.id) !== convSig(x)) return false;
  return true;
}
function setConvsIfChanged(
  setter: React.Dispatch<React.SetStateAction<Conv[]>>,
  producer: (prev: Conv[]) => Conv[]
) {
  setter(prev => {
    const next = producer(prev);
    return sameConvs(prev, next) ? prev : next;
  });
}

function upsert(list: Conv[], item: Conv): Conv[] {
  const i = list.findIndex(x => x.id === item.id);
  if (i >= 0) {
    const next = [...list];
    next[i] = { ...next[i], ...item };
    return dedupeAndSort(next);
  }
  return dedupeAndSort([item, ...list]);
}

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
          marginLeft: 8, padding: "2px 8px", borderRadius: 999,
          border: "1px solid #cfe8ff", background: "#eaf4ff",
          color: "#1456a0", fontSize: 12, whiteSpace: "nowrap", alignSelf: "center", flexShrink: 0,
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
          marginLeft: 8, padding: "2px 8px", borderRadius: 999,
          border: "1px solid #f5d0d0", background: "#ffecec",
          color: "#9b1c1c", fontSize: 12, whiteSpace: "nowrap", alignSelf: "center", flexShrink: 0,
        }}
      >
        Read-only{c.shared_by?.name ? `, shared by ${c.shared_by.name}` : ""}
      </span>
    );
  }
  return null;
}

const latestTs = (arr: Msg[]) => arr.reduce((mx, m) => Math.max(mx, Number(m.created_at || 0)), 0);
const displayName = (u?: UserBrief | null) => (u?.name || u?.email || String(u?.id ?? ""));
const emailOf = (u?: UserBrief | null) => (u?.email || "");
const isEmail = (s: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s);

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

  // Start with "all" to avoid hydration mismatch, then load from sessionStorage after mount
  const [activeTab, setActiveTabState] = useState<"all" | "owned" | "collab" | "readonly">("all");

  // Load saved tab after hydration
  useEffect(() => {
    const saved = sessionStorage.getItem("chatActiveTab");
    if (saved && (saved === "all" || saved === "owned" || saved === "collab" || saved === "readonly")) {
      setActiveTabState(saved as any);
    }
  }, []);

  const setActiveTab = useCallback((tab: "all" | "owned" | "collab" | "readonly") => {
    setActiveTabState(tab);
    if (typeof window !== "undefined") {
      sessionStorage.setItem("chatActiveTab", tab);
    }
  }, []);

  const [selectedId, setSelectedId] = useState<string | null>(selectedPublicId);
  const [editingTitle, setEditingTitle] = useState(false);
  const [editTitleValue, setEditTitleValue] = useState("");
  // Initialize with true for consistent SSR/client hydration
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const selectedConv = useMemo(() => convs.find((c) => c.id === selectedId) ?? null, [convs, selectedId]);

  const sidebarScrollRef = useRef<HTMLDivElement | null>(null);

  // me
  const [me, setMe] = useState<Me | null>(null);
  useEffect(() => {
    (async () => {
      const res = await fetch("/api/auth/me", { cache: "no-store" }).catch(() => null);
      if (res && res.ok) {
        const u = await res.json().catch(() => null);
        if (u && typeof u.id !== "undefined") {
          console.log("[AUTH] Loaded me:", u);
          setMe({ ...u, id: Number(u.id) });
        } else {
          console.log("[AUTH] No user data in response");
        }
      } else {
        console.log("[AUTH] Failed to fetch /api/auth/me");
      }
    })();
  }, []);

  const [msgs, setMsgs] = useState<Msg[]>([]);
  const msgsRef = useRef<Msg[]>([]);
  useEffect(() => { msgsRef.current = msgs; }, [msgs]);

  const [input, setInput] = useState("");
  const [queuedInput, setQueuedInput] = useState<string | null>(null);
  const queuedRef = useRef<string | null>(null);
  useEffect(() => { queuedRef.current = queuedInput; }, [queuedInput]);

  const esRef = useRef<{ close: () => void } | null>(null);
  const [streaming, setStreaming] = useState(false);
  const flushingRef = useRef(false);

  const [remoteStreaming, setRemoteStreaming] = useState(false);
  const remoteStreamTouchedAtRef = useRef(0);
  const prevAssistantLenRef = useRef(0);

  const localSentRef = useRef<Array<{ text: string; ts: number }>>([]);

  const [lastSeenAt, setLastSeenAt] = useState<number>(0);
  const unreadAnchorIndexRef = useRef<number | null>(null);
  const msgRefs = useRef<Map<number, HTMLDivElement | null>>(new Map());
  const needsInitialScrollRef = useRef<boolean>(false);

  const shadowSeenRef = useRef<Map<string, number>>(new Map());

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

  useEffect(() => {
    setSelectedId(selectedPublicId);

    // Restore sidebar scroll position after navigation
    if (sidebarScrollRef.current) {
      const savedScroll = sessionStorage.getItem("sidebarScrollTop");
      if (savedScroll) {
        setTimeout(() => {
          if (sidebarScrollRef.current) {
            sidebarScrollRef.current.scrollTop = Number(savedScroll);
          }
        }, 0);
      }
    }
  }, [selectedPublicId]);

  const listBackoffRef = useRef<number>(0);
  const msgBackoffRef  = useRef<number>(0);
  const refreshConvsInFlightRef = useRef<Promise<void> | null>(null);

  const lastReadSentTsRef = useRef<Map<string, number>>(new Map());
  const lastReadSentAtMsRef = useRef<Map<string, number>>(new Map());

  const isRemotelyStreaming = useCallback(
    () => (Date.now() - remoteStreamTouchedAtRef.current) < 7000,
    []
  );
  const isBusy = useCallback(
    () => streaming || isRemotelyStreaming(),
    [streaming, isRemotelyStreaming]
  );

  /** Conversation list polling: only update when there are actual changes to avoid flicker */
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
      const next = dedupeAndSort(items);
      setConvsIfChanged(setConvs, () => next);
    };
    const p = run().finally(() => { refreshConvsInFlightRef.current = null; });
    refreshConvsInFlightRef.current = p;
    return p;
  }, []);

  /** Mark as read: only update local list when it actually changes */
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
      shadowSeenRef.current.set(pubId, seenTs);
      setConvsIfChanged(setConvs, (prev) => {
        let changed = false;
        const next = prev.map(c => {
          if (c.id !== pubId) return c;
          if ((c.unread_count || 0) === 0) return c;
          changed = true;
          return { ...c, unread_count: 0 };
        });
        return changed ? next : prev;
      });
      if (r.ok) {
        lastReadSentTsRef.current.set(pubId, seenTs);
        lastReadSentAtMsRef.current.set(pubId, now);
      }
    } catch {}
  }, []);

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
        user_id: r.user_id != null ? Number(r.user_id) : null,
        user_name: r.user_name ?? null,
        user_email: r.user_email ?? null,
        sources: r.sources ?? [],
      }));
      console.log("[LOAD] Loaded messages:", mapped.map(m => ({ role: m.role, user_id: m.user_id, sources: m.sources?.length ?? 0, text: m.text.substring(0, 30) })));
      setMsgs(mapped);
      needsInitialScrollRef.current = true;

      const ls = Number((data as any)?.last_seen_at || 0);
      setLastSeenAt(ls);

      const idx = mapped.findIndex(m => (Number(m.created_at || 0) > ls));
      unreadAnchorIndexRef.current = idx >= 0 ? idx : null;

      const last = latestTs(mapped);
      if (last > 0) {
        shadowSeenRef.current.set(publicId, last);
        await markRead(publicId, last);
      }

      setConvsIfChanged(setConvs, (prev) => {
        let changed = false;
        const next = prev.map(c => {
          if (c.id !== publicId) return c;
          const lm = Math.max(Number(c.last_message_at||0), last);
          if (lm === Number(c.last_message_at||0) && (c.unread_count || 0) === 0) return c;
          changed = true;
          return { ...c, last_message_at: lm, unread_count: 0 };
        });
        return changed ? next : prev;
      });

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

  useEffect(() => {
    const idx = unreadAnchorIndexRef.current;
    if (idx != null && idx >= 0) {
      const el = msgRefs.current.get(idx);
      if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
      unreadAnchorIndexRef.current = null;
      needsInitialScrollRef.current = false;
      return;
    }
    if (needsInitialScrollRef.current) {
      const lastEl = msgRefs.current.get(msgs.length - 1);
      if (lastEl) lastEl.scrollIntoView({ behavior: "auto", block: "end" });
      needsInitialScrollRef.current = false;
    }
  }, [msgs]);

  useEffect(() => {
    if (selectedPublicId) loadConvMessages(selectedPublicId);
    else { setMsgs([]); setLastSeenAt(0); }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedPublicId]);

  const filteredConvs = useMemo(() => {
    if (activeTab === "all") return convs;
    if (activeTab === "owned") return convs.filter(c => c.access_role === "owner");
    if (activeTab === "collab") return convs.filter(c => c.access_role === "editor");
    return convs.filter(c => c.access_role === "viewer");
  }, [convs, activeTab]);

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
          user_id: r.user_id != null ? Number(r.user_id) : null,
          user_name: r.user_name ?? null,
          user_email: r.user_email ?? null,
          sources: r.sources ?? [],
        }));
        const curLast = latestTs(msgsRef.current);
        const newLast = latestTs(mapped);
        // Don't replace messages while streaming to prevent UI jumps
        if (newLast > curLast) {
          setMsgs(mapped);
          shadowSeenRef.current.set(selectedId, newLast);
          if (newLast > 0) { (async () => { await markRead(selectedId, newLast); })(); }

          const ls = Number((data as any)?.last_seen_at || 0);
          setLastSeenAt(ls);

          setConvsIfChanged(setConvs, (prev) => {
            let changed = false;
            const next = prev.map(c => {
              if (c.id !== selectedId) return c;
              const lm = Math.max(Number(c.last_message_at||0), newLast);
              if (lm === Number(c.last_message_at||0) && (c.unread_count || 0) === 0) return c;
              changed = true;
              return { ...c, unread_count: 0, last_message_at: lm };
            });
            return changed ? next : prev;
          });
        }

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
    if (publicId === selectedId) return; // Already selected

    // Save sidebar scroll position before navigation
    if (sidebarScrollRef.current) {
      sessionStorage.setItem("sidebarScrollTop", String(sidebarScrollRef.current.scrollTop));
    }

    esRef.current?.close(); setStreaming(false);
    setSelectedId(publicId);
    router.replace(`/chat/${publicId}`, { scroll: false });
    await loadConvMessages(publicId);
  }, [router, loadConvMessages, selectedId]);

  const newChat = useCallback(() => {
    esRef.current?.close(); setStreaming(false);
    setSelectedId(null); setMsgs([]); setInput(""); setQueuedInput(null);
    setLastSeenAt(0); unreadAnchorIndexRef.current = null;
    router.push(`/chat`);
  }, [router]);

  const startEditingTitle = useCallback((c: Conv) => {
    const current = labelOf(c);
    setEditTitleValue(current);
    setEditingTitle(true);
  }, []);

  const saveTitle = useCallback(async () => {
    if (!selectedConv) return;
    const trimmed = editTitleValue.trim();
    const current = labelOf(selectedConv);
    setEditingTitle(false);
    if (!trimmed || trimmed === current) return;
    const res = await fetch(`/api/conversations/${selectedConv.id}`, {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ title: trimmed }),
    }).catch(() => null);
    if (res && res.ok) {
      const updated = await res.json().catch(()=>null);
      if (updated) setConvs(prev => upsert(prev, updated));
    }
  }, [selectedConv, editTitleValue]);

  const cancelEditingTitle = useCallback(() => {
    setEditingTitle(false);
    setEditTitleValue("");
  }, []);

  // Close editing when switching conversations
  useEffect(() => {
    setEditingTitle(false);
    setEditTitleValue("");
  }, [selectedId]);

  const refreshConvsAndLocal = useCallback(async () => {
    await refreshConvs();
    if (selectedId) {
      const last = latestTs(msgsRef.current);
      if (last > 0) await markRead(selectedId, last, true);
    }
  }, [refreshConvs, selectedId, markRead]);

  // ======== Share panel state & actions ========
  const [shareOpen, setShareOpen] = useState(false);
  const [members, setMembers] = useState<Member[]>([]);
  const [ownerUser, setOwnerUser] = useState<UserBrief | null>(null);
  const [shareBusy, setShareBusy] = useState(false);
  const [shareError, setShareError] = useState<string | null>(null);

  const [shareEmail, setShareEmail] = useState("");
  const [newRole, setNewRole] = useState<"unassigned" | "editor" | "viewer">("unassigned");

  const loadShares = useCallback(async (pubId: string) => {
    setShareError(null);
    setShareBusy(true);
    try {
      const res = await fetch(`/api/conversations/${pubId}/shares`, { cache: "no-store" });
      if (res.status === 403) { setMembers([]); setOwnerUser(null); setShareError("Only owner/editor can view members."); }
      else if (!res.ok) { setMembers([]); setOwnerUser(null); setShareError(`Failed to load (${res.status})`); }
      else {
        const data = await res.json().catch(() => null);
        let arr: Member[] = [];
        let owner: UserBrief | null = null;
        if (Array.isArray(data)) {
          arr = data as Member[];
          const ow = arr.find(x => x.role === "owner");
          if (ow) owner = ow.user || null;
        } else if (data && typeof data === "object") {
          if (Array.isArray((data as any).members)) arr = (data as any).members as Member[];
          if ((data as any).owner) owner = (data as any).owner as UserBrief;
          if (!owner) {
            const ow = arr.find(x => x.role === "owner");
            if (ow) owner = ow.user || null;
          }
        }
        setMembers(Array.isArray(arr) ? arr : []);
        setOwnerUser(owner ?? (selectedConv?.shared_by ?? null));
      }
    } catch (e:any) {
      setMembers([]); setOwnerUser(null);
      setShareError(String(e?.message || e));
    } finally { setShareBusy(false); }
  }, [selectedConv?.shared_by]);

  const openSharePanel = useCallback(async () => {
    if (!selectedId) return;
    setShareOpen((prev) => !prev);
    if (!shareOpen) {
      await loadShares(selectedId);
    }
  }, [selectedId, loadShares, shareOpen]);

  useEffect(() => {
    if (shareOpen && selectedId) { (async () => { await loadShares(selectedId); })(); }
  }, [shareOpen, selectedId, loadShares]);

  const addMember = useCallback(async () => {
    if (!selectedId) return;
    const emailRaw = shareEmail.trim();
    const email = emailRaw.toLowerCase();
    if (!email) { setShareError("Enter an email address."); return; }
    if (!isEmail(email)) { setShareError("Invalid email address."); return; }
    if (newRole === "unassigned") { setShareError("Choose a role before adding."); return; }

    setShareBusy(true); setShareError(null);
    try {
      const r = await fetch(`/api/conversations/${selectedId}/shares`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ email, role: newRole }),
      });

      if (r.status === 404) { setShareError("Email address not registered."); }
      else if (r.status === 403) { setShareError("Only owner/editor can share."); }
      else if (r.status === 409) { setShareError("This user already has access."); }
      else if (!r.ok && r.status !== 204) { setShareError(`Failed (${r.status})`); }

      if (r.ok || r.status === 204) {
        await loadShares(selectedId);
        setShareEmail("");
        setNewRole("unassigned");
      }
    } catch (e:any) {
      setShareError(String(e?.message || e));
    } finally { setShareBusy(false); }
  }, [selectedId, shareEmail, newRole, loadShares]);

  const changeRole = useCallback(async (userId: number, role: "editor" | "viewer") => {
    if (!selectedId) return;
    setShareBusy(true); setShareError(null);
    try {
      const r = await fetch(`/api/conversations/${selectedId}/shares/${userId}`, {
        method: "PATCH",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ role }),
      });
      if (!r.ok && r.status !== 204) setShareError(`Failed to update (${r.status})`);
      await loadShares(selectedId);
    } catch (e:any) {
      setShareError(String(e?.message || e));
    } finally { setShareBusy(false); }
  }, [selectedId, loadShares]);

  const removeMember = useCallback(async (userId: number) => {
    if (!selectedId) return;
    if (!confirm("Remove this member?")) return;
    setShareBusy(true); setShareError(null);
    try {
      const r = await fetch(`/api/conversations/${selectedId}/shares/${userId}`, { method: "DELETE" });
      if (r.status === 400) setShareError("Cannot remove owner.");
      else if (!r.ok && r.status !== 204) setShareError(`Failed to remove (${r.status})`);
      await loadShares(selectedId);
    } catch (e:any) {
      setShareError(String(e?.message || e));
    } finally { setShareBusy(false); }
  }, [selectedId, loadShares]);

  // ======== Send flow ========
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

  const sendNow = useCallback(async (text: string) => {
    if (!text) return;
    if (selectedConv?.access_role === "viewer") {
      alert("This chat is read-only.");
      return;
    }
    const tsNow = Date.now();
    localSentRef.current.push({ text, ts: tsNow });
    setMsgs((m) => [...m, {
      role: "user",
      text,
      created_at: tsNow,
      user_id: me?.id ?? null,
      user_name: me?.name ?? null,
      user_email: me?.email ?? null
    }, { role: "assistant", text: "" }]);
    setStreaming(true);

    let convInfo: { id: string; isNew: boolean };
    try {
      convInfo = await ensureConversation();
    } catch (e: any) {
      setStreaming(false);
      console.error("Failed to create conversation:", e);
      return;
    }

    setLastSeenAt(tsNow);
    shadowSeenRef.current.set(convInfo.id, tsNow);
    markRead(convInfo.id, tsNow, true);
    setConvsIfChanged(setConvs, (prev) => {
      let changed = false;
      const next = prev.map(c => {
        if (c.id !== convInfo.id) return c;
        if ((c.unread_count || 0) === 0) return c;
        changed = true;
        return { ...c, unread_count: 0 };
      });
      return changed ? next : prev;
    });

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
      onEvent: (e: { event?: string; data: string; id?: string }) => {
        // Handle special events
        if (e.event) {
          if (e.event === "sources") {
            // Parse and store sources
            try {
              const sources = JSON.parse(e.data) as SourceDoc[];
              console.log("[SSE] Received sources event with", sources.length, "sources:", sources);
              setMsgs((m) => {
                let idx = -1;
                for (let i = m.length - 1; i >= 0; i--) {
                  if (m[i].role === "assistant") { idx = i; break; }
                }
                if (idx === -1) {
                  console.warn("[SSE] No assistant message found to attach sources to");
                  return m;
                }
                const cur = m[idx];
                console.log("[SSE] Attaching", sources.length, "sources to message at index", idx);
                const updated = [...m.slice(0, idx), { ...cur, sources }, ...m.slice(idx + 1)];
                console.log("[SSE] Updated message now has sources:", updated[idx].sources);
                return updated;
              });
            } catch (err) {
              console.error("[SSE] Failed to parse sources:", err);
            }
          } else if (e.event === "metadata") {
            console.log("Received metadata:", e.data);
          }
          return; // Skip non-data events
        }

        // Regular data event - append to message
        const add = sanitizeChunk(e.data);
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
        setRemoteStreaming(false);  // Clear remote streaming state
        prevAssistantLenRef.current = 0;  // Reset length tracker
        setMsgs((m) => {
          if (!m.length) return m;
          const last = m[m.length - 1];
          if (last.role === "assistant" && !last.text.trim()) return m.slice(0, -1);
          return m;
        });
        await refreshConvsAndLocal();

        if (queuedRef.current && !isBusy() && !flushingRef.current) {
          flushingRef.current = true;
          const nextToSend = queuedRef.current!;
          setQueuedInput(null);
          await sendNow(nextToSend);
          flushingRef.current = false;
        }
      },
      onError: (e: unknown) => {
        setStreaming(false);
        setRemoteStreaming(false);
        prevAssistantLenRef.current = 0;
        console.error("Stream error:", e);
      },
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedConv, ensureConversation, refreshConvsAndLocal, isBusy]);

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

  const isProbablyMine = useCallback((m: Msg) => {
    if (m.role !== "user") return false;
    const t = Number(m.created_at || 0);
    return localSentRef.current.some(s =>
      s.text === m.text && Math.abs(t - s.ts) < 15000
    );
  }, []);

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

  const [mounted, setMounted] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [sidebarInitialized, setSidebarInitialized] = useState(false);
  const [layoutReady, setLayoutReady] = useState(false);
  useEffect(() => { setMounted(true); }, []);
  useEffect(() => {
    if (!mounted) return;
    const check = () => {
      const w = getViewportW();
      setIsMobile(prev => prev ? (w < MOBILE_BP + HYST) : (w < MOBILE_BP - HYST));
    };
    check();
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check);
  }, [mounted]);

  // Initialize sidebar state after mount based on screen size and localStorage
  // This runs once after hydration to set the correct initial state
  useEffect(() => {
    if (!mounted) return;

    const currentIsMobile = getViewportW() < MOBILE_BP;
    if (currentIsMobile) {
      // Mobile: always start closed
      setSidebarOpen(false);
    } else {
      // Desktop: check localStorage for user preference
      const saved = localStorage.getItem('chatSidebarOpen');
      setSidebarOpen(saved !== null ? saved === 'true' : true);
    }

    // Make layout visible after state is set (next frame to ensure state has updated)
    requestAnimationFrame(() => {
      setLayoutReady(true);
    });
  }, [mounted]); // Only run once after mount

  // Toggle sidebar with localStorage persistence (desktop only)
  const toggleSidebar = useCallback(() => {
    // Enable transitions on first user interaction
    if (!sidebarInitialized) {
      setSidebarInitialized(true);
    }

    setSidebarOpen((v) => {
      const newValue = !v;
      // Only save to localStorage on desktop
      if (!isMobile) {
        localStorage.setItem('chatSidebarOpen', String(newValue));
      }
      return newValue;
    });
  }, [isMobile, sidebarInitialized]);

  // Auto-close sidebar on mobile when selecting a conversation
  useEffect(() => {
    if (isMobile && selectedId) {
      setSidebarOpen(false);
    }
  }, [isMobile, selectedId]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setShareOpen(false); };
    if (shareOpen) window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [shareOpen]);

  return (
    <div
      style={{
        height: "100dvh",
        display: "grid",
        gridTemplateColumns: isMobile
          ? "1fr"
          : `${sidebarOpen ? "300px" : "0"} 1fr${(mounted && !isMobile && shareOpen) ? " 240px" : ""}`,
        minHeight: 0,
        transition: sidebarInitialized ? "grid-template-columns 160ms ease" : "none",
        background: "#f9fafb",
        position: "relative",
        opacity: layoutReady ? 1 : 0
      }}
    >
      {/* Mobile overlay backdrop when sidebar is open */}
      {mounted && isMobile && sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0, 0, 0, 0.5)",
            zIndex: 998,
            transition: "opacity 200ms ease"
          }}
        />
      )}

      {/* Sidebar */}
      <aside
        aria-hidden={!sidebarOpen}
        style={{
          ...(isMobile ? {
            // Mobile: sidebar as overlay
            position: "fixed",
            top: 0,
            left: 0,
            bottom: 0,
            width: 300,
            zIndex: 999,
            transform: sidebarOpen ? "translateX(0)" : "translateX(-100%)",
            transition: sidebarInitialized ? "transform 250ms ease" : "none",
            borderRight: "1px solid #e5e7eb",
            boxShadow: sidebarOpen ? "2px 0 12px rgba(0,0,0,0.15)" : "none"
          } : {
            // Desktop: sidebar in grid
            borderRight: sidebarOpen ? "1px solid #e5e7eb" : "none",
            overflow: sidebarOpen ? "visible" : "hidden",
            visibility: sidebarOpen ? "visible" : "hidden",
            pointerEvents: sidebarOpen ? "auto" : "none",
            opacity: sidebarOpen ? 1 : 0,
            transition: sidebarInitialized ? "opacity 120ms ease" : "none",
            boxShadow: sidebarOpen ? "2px 0 8px rgba(0,0,0,0.05)" : "none"
          }),
          background: "#fff",
          display: "flex",
          flexDirection: "column",
          minHeight: 0
        }}
      >
        <div style={{
          display: "flex",
          gap: 8,
          padding: 12,
          borderBottom: "1px solid #e5e7eb",
          alignItems: "center",
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        }}>
          <button onClick={newChat} style={{
            padding: "8px 16px",
            background: "#fff",
            color: "#667eea",
            border: "none",
            borderRadius: 8,
            cursor: "pointer",
            fontWeight: 600,
            fontSize: 14,
            boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
            transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = "translateY(-2px) scale(1.05)";
            e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.2)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = "translateY(0) scale(1)";
            e.currentTarget.style.boxShadow = "0 2px 8px rgba(0,0,0,0.15)";
          }}
          onMouseDown={(e) => e.currentTarget.style.transform = "scale(0.95)"}
          onMouseUp={(e) => e.currentTarget.style.transform = "translateY(-2px) scale(1.05)"}>
            New Chat
          </button>
          <div style={{ marginLeft: "auto", fontSize: 12, color: "#fff", opacity: 0.9 }}>
            {currentCount} {currentCount === 1 ? "chat" : "chats"}
          </div>
        </div>

        <div style={{ display: "flex", gap: 6, padding: "10px", borderBottom: "1px solid #e5e7eb", fontSize: 13, background: "#fafafa" }}>
          {[
            ["all","All"],["owned","Owned"],["collab","Collaborating"],["readonly","Read-only"],
          ].map(([k, label]) => (
            <button key={k}
              onClick={() => setActiveTab(k as any)}
              style={{
                padding: "6px 12px",
                borderRadius: 8,
                border: "none",
                background: activeTab===k ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" : "#fff",
                color: activeTab===k ? "#fff" : "#555",
                fontWeight: activeTab===k ? 600 : 500,
                cursor: "pointer",
                fontSize: 12,
                boxShadow: activeTab===k ? "0 2px 8px rgba(102, 126, 234, 0.35)" : "0 1px 3px rgba(0,0,0,0.08)",
                transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
              }}
              onMouseEnter={(e) => {
                if (activeTab !== k) {
                  e.currentTarget.style.background = "#f0f4ff";
                  e.currentTarget.style.transform = "translateY(-1px)";
                  e.currentTarget.style.boxShadow = "0 2px 6px rgba(0,0,0,0.12)";
                }
              }}
              onMouseLeave={(e) => {
                if (activeTab !== k) {
                  e.currentTarget.style.background = "#fff";
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow = "0 1px 3px rgba(0,0,0,0.08)";
                }
              }}
            >{label}</button>
          ))}
        </div>

        <div ref={sidebarScrollRef} style={{ flex: 1, minHeight: 0, overflow: "auto" }}>
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
                <div key={c.id} style={{ borderBottom: "1px solid #e5e7eb", background: active ? "#eef6ff" : "transparent" }}>
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
      <main style={{ display: "grid", gridTemplateRows: "auto 1fr auto", minHeight: 0, background: "#fff" }}>
        <div style={{
          display: "flex",
          gap: 8,
          alignItems: "center",
          padding: "12px 16px",
          borderBottom: "1px solid #e5e7eb",
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
        }}>
          <button
            onClick={toggleSidebar}
            title={isMobile ? "Open conversation list" : (sidebarOpen ? "Hide sidebar" : "Show sidebar")}
            style={{
            padding: "8px",
            background: "rgba(255,255,255,0.15)",
            color: "#fff",
            border: "1px solid rgba(255,255,255,0.3)",
            borderRadius: 6,
            cursor: "pointer",
            fontWeight: 400,
            flexShrink: 0,
            fontSize: 18,
            lineHeight: 1,
            width: 36,
            height: 36,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            transition: "all 0.2s ease"
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "rgba(255,255,255,0.25)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = "rgba(255,255,255,0.15)";
          }}
        >
          {isMobile ? "☰" : (sidebarOpen ? "◀" : "▶")}
        </button>

          {selectedConv && <RoleBadge c={selectedConv} />}

          {editingTitle ? (
            <input
              type="text"
              value={editTitleValue}
              onChange={(e) => setEditTitleValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") saveTitle();
                if (e.key === "Escape") cancelEditingTitle();
              }}
              onBlur={saveTitle}
              autoFocus
              style={{
                flex: 1,
                minWidth: 0,
                padding: "4px 8px",
                border: "2px solid #fff",
                borderRadius: 6,
                fontSize: 15,
                fontWeight: 600,
                background: "#fff",
                color: "#667eea",
                outline: "none"
              }}
            />
          ) : (
            <div
              onClick={() => {
                if (selectedConv && (selectedConv.access_role === "owner" || selectedConv.access_role === "editor")) {
                  startEditingTitle(selectedConv);
                }
              }}
              style={{
                fontWeight: 600,
                fontSize: 15,
                flex: 1,
                minWidth: 0,
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
                color: "#fff",
                cursor: (selectedConv && (selectedConv.access_role === "owner" || selectedConv.access_role === "editor")) ? "pointer" : "default",
                padding: "4px 8px",
                borderRadius: 6,
                transition: "all 0.2s ease"
              }}
              onMouseEnter={(e) => {
                if (selectedConv && (selectedConv.access_role === "owner" || selectedConv.access_role === "editor")) {
                  e.currentTarget.style.background = "rgba(255,255,255,0.15)";
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "transparent";
              }}
              title={(selectedConv && (selectedConv.access_role === "owner" || selectedConv.access_role === "editor")) ? "Click to rename" : undefined}
            >
              {selectedConv ? labelOf(selectedConv) : "OHSUpath Reader"}
            </div>
          )}

          {!!selectedConv && (selectedConv.access_role === "owner" || selectedConv.access_role === "editor") && (
            <div style={{ display: "flex", gap: 8 }}>
              <button onClick={openSharePanel} style={{
                padding: "8px 16px",
                background: shareOpen ? "#fff" : "rgba(255,255,255,0.9)",
                color: "#667eea",
                border: shareOpen ? "2px solid #fff" : "none",
                borderRadius: 8,
                cursor: "pointer",
                fontWeight: 600,
                fontSize: 13,
                transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                boxShadow: shareOpen ? "0 4px 12px rgba(0,0,0,0.25)" : "0 2px 6px rgba(0,0,0,0.15)"
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-2px) scale(1.05)";
                e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.25)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0) scale(1)";
                e.currentTarget.style.boxShadow = shareOpen ? "0 4px 12px rgba(0,0,0,0.25)" : "0 2px 6px rgba(0,0,0,0.15)";
              }}
              onMouseDown={(e) => e.currentTarget.style.transform = "scale(0.95)"}
              onMouseUp={(e) => e.currentTarget.style.transform = "translateY(-2px) scale(1.05)"}
              title="Share this conversation">
                {shareOpen ? "Close Share" : "Share"}
              </button>
            </div>
          )}
        </div>

        {/* Messages */}
        <div style={{ overflow: "auto", padding: 20, minHeight: 0, background: "#f9fafb" }}>
          {msgs.length === 0 ? (
            <div style={{ textAlign: "center", padding: "40px 20px", color: "#999" }}>
              <div style={{ fontSize: 18, marginBottom: 8, fontWeight: 600 }}>Start a Conversation</div>
              <div style={{ fontSize: 14 }}>Ask me anything about the documents</div>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 12, maxWidth: 900, margin: "0 auto" }}>
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

                // Determine message type and styling
                const isUserMessage = m.role === "user";
                const isAssistant = m.role === "assistant";
                // A message is mine if: (1) it's in localSentRef, OR (2) user_id matches me.id (when both are non-null)
                // Use loose equality (==) to handle string vs number type mismatches
                const isMine = mine || (isUserMessage && m.user_id != null && me?.id != null && m.user_id == me.id);
                const isCollaborator = isUserMessage && !isMine;

                // Debug logging
                if (isUserMessage) {
                  console.log(`[Message #${i}] mine=${mine}, m.user_id=${m.user_id} (${typeof m.user_id}), me?.id=${me?.id} (${typeof me?.id}), isMine=${isMine}, text="${m.text.substring(0, 30)}..."`);
                }

                // Get display name
                let displayName = "";
                if (isAssistant) {
                  displayName = "AI Assistant";
                } else if (isMine) {
                  displayName = "You";
                } else if (isCollaborator) {
                  displayName = m.user_name || m.user_email || "Collaborator";
                }

                // Message colors
                let bgColor = "#fff";
                let textColor = "#333";
                let borderColor = "#e5e7eb";
                if (isMine) {
                  bgColor = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)";
                  textColor = "#fff";
                  borderColor = "none";
                } else if (isCollaborator) {
                  bgColor = "#e8f5e9";
                  textColor = "#1b5e20";
                  borderColor = "#a5d6a7";
                } else if (isAssistant) {
                  bgColor = "#fff";
                  textColor = "#333";
                  borderColor = "#e5e7eb";
                }

                return (
                  <div key={i} style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: isMine ? "flex-end" : "flex-start",
                    marginLeft: isMine ? "auto" : "0",
                    marginRight: isMine ? "0" : "auto",
                    maxWidth: "75%"
                  }}>
                    {isUnreadStart && (
                      <div style={{ textAlign: "center", margin: "12px 0", alignSelf: "center" }}>
                        <span style={{
                          padding: "4px 12px", fontSize: 12, borderRadius: 16,
                          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                          color: "#fff",
                          fontWeight: 600,
                          boxShadow: "0 2px 4px rgba(102, 126, 234, 0.3)"
                        }}>New Messages</span>
                      </div>
                    )}

                    {/* Display name */}
                    {displayName && (
                      <div style={{
                        fontSize: 12,
                        fontWeight: 600,
                        color: "#666",
                        marginBottom: 4,
                        paddingLeft: isMine ? 0 : 4,
                        paddingRight: isMine ? 4 : 0
                      }}>
                        {displayName}
                      </div>
                    )}

                    <div
                      ref={(el) => { msgRefs.current.set(i, el); }}
                      style={{
                        padding: "14px 16px",
                        borderRadius: 12,
                        background: bgColor,
                        color: textColor,
                        boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                        border: borderColor === "none" ? "none" : `1px solid ${borderColor}`,
                        width: "100%"
                      }}
                    >
                      <div style={{ whiteSpace: "pre-wrap" }}>{m.text}</div>

                      {/* Display sources for assistant messages as clickable citation bubbles */}
                      {(() => {
                        const hasSources = m.role === "assistant" && m.sources && m.sources.length > 0;
                        if (hasSources) {
                          console.log(`[RENDER] Message #${i} has ${m.sources?.length} sources:`, m.sources);
                        }
                        return hasSources;
                      })() && (
                        <div style={{ marginTop: 16, paddingTop: 12, borderTop: "1px solid #e5e7eb" }}>
                          <div style={{
                            fontSize: 12,
                            fontWeight: 600,
                            color: "#666",
                            marginBottom: 8
                          }}>
                            Sources ({m.sources!.length}):
                          </div>
                          <div style={{
                            display: "flex",
                            flexWrap: "wrap",
                            gap: 8
                          }}>
                            {m.sources!.map((src, idx) => {
                              // Use the new schema fields
                              const title = src.title;
                              // Add #page= fragment to jump to specific page in PDF viewer
                              const fileUrl = src.page
                                ? `${src.source_url}#page=${src.page}`
                                : src.source_url;

                              return (
                                <a
                                  key={idx}
                                  href={fileUrl}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  title={`${title}${src.page ? ` - Page ${src.page}` : ""}\n\n${src.snippet ? src.snippet.slice(0, 200) + "..." : "Click to view document"}`}
                                  style={{
                                    display: "inline-flex",
                                    alignItems: "center",
                                    gap: 6,
                                    padding: "8px 12px",
                                    background: "#f0f4ff",
                                    color: "#667eea",
                                    border: "1px solid #d0dcff",
                                    borderRadius: 8,
                                    fontSize: 13,
                                    fontWeight: 600,
                                    textDecoration: "none",
                                    transition: "all 0.2s ease",
                                    cursor: "pointer",
                                    boxShadow: "0 1px 3px rgba(0,0,0,0.08)"
                                  }}
                                  onMouseEnter={(e) => {
                                    e.currentTarget.style.background = "#667eea";
                                    e.currentTarget.style.color = "#fff";
                                    e.currentTarget.style.transform = "translateY(-2px)";
                                    e.currentTarget.style.boxShadow = "0 4px 8px rgba(102, 126, 234, 0.3)";
                                  }}
                                  onMouseLeave={(e) => {
                                    e.currentTarget.style.background = "#f0f4ff";
                                    e.currentTarget.style.color = "#667eea";
                                    e.currentTarget.style.transform = "translateY(0)";
                                    e.currentTarget.style.boxShadow = "0 1px 3px rgba(0,0,0,0.08)";
                                  }}
                                >
                                  <span style={{
                                    display: "inline-flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    width: 20,
                                    height: 20,
                                    borderRadius: 999,
                                    background: "currentColor",
                                    color: "#f0f4ff",
                                    fontSize: 11,
                                    fontWeight: 700,
                                    flexShrink: 0
                                  }}>
                                    {idx + 1}
                                  </span>
                                  <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 180 }}>
                                    {title}
                                  </span>
                                  {src.page && (
                                    <span style={{
                                      fontSize: 11,
                                      opacity: 0.8,
                                      flexShrink: 0
                                    }}>
                                      p.{src.page}
                                    </span>
                                  )}
                                  <span style={{ fontSize: 16, flexShrink: 0 }}>→</span>
                                </a>
                              );
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Composer */}
        <div style={{
          padding: 16,
          borderTop: "1px solid #e5e7eb",
          background: "#fff",
          boxShadow: "0 -2px 8px rgba(0,0,0,0.05)"
        }}>
          <div style={{ maxWidth: 900, margin: "0 auto" }}>
            <div style={{ display: "flex", gap: 10 }}>
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
                style={{
                  flex: 1,
                  padding: "12px 16px",
                  border: "2px solid #e5e7eb",
                  borderRadius: 8,
                  fontSize: 15,
                  outline: "none",
                  transition: "border-color 0.2s"
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = "#667eea"}
                onBlur={(e) => e.currentTarget.style.borderColor = "#e5e7eb"}
                disabled={selectedConv?.access_role === "viewer"}
              />
              <button
                onClick={() => { (async () => { await send(); })(); }}
                disabled={selectedConv?.access_role === "viewer"}
                style={{
                  minWidth: 100,
                  padding: "12px 24px",
                  background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  color: "#fff",
                  border: "none",
                  borderRadius: 12,
                  cursor: selectedConv?.access_role === "viewer" ? "not-allowed" : "pointer",
                  fontWeight: 600,
                  fontSize: 15,
                  boxShadow: "0 4px 14px rgba(102, 126, 234, 0.4)",
                  opacity: selectedConv?.access_role === "viewer" ? 0.5 : 1,
                  transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                }}
                onMouseEnter={(e) => {
                  if (selectedConv?.access_role !== "viewer") {
                    e.currentTarget.style.transform = "translateY(-3px) scale(1.05)";
                    e.currentTarget.style.boxShadow = "0 8px 24px rgba(102, 126, 234, 0.5)";
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0) scale(1)";
                  e.currentTarget.style.boxShadow = "0 4px 14px rgba(102, 126, 234, 0.4)";
                }}
                onMouseDown={(e) => {
                  if (selectedConv?.access_role !== "viewer") {
                    e.currentTarget.style.transform = "translateY(-1px) scale(0.98)";
                  }
                }}
                onMouseUp={(e) => {
                  if (selectedConv?.access_role !== "viewer") {
                    e.currentTarget.style.transform = "translateY(-3px) scale(1.05)";
                  }
                }}
              >
                {buttonLabel}
              </button>
            </div>
            {!!queuedInput && (
              <div style={{
                marginTop: 10,
                padding: "8px 12px",
                fontSize: 13,
                color: "#667eea",
                background: "#f0f4ff",
                borderRadius: 6,
                border: "1px solid #e0e7ff"
              }}>
                Queued: <span style={{ fontWeight: 600 }}>{queuedInput.slice(0, 80)}{queuedInput.length>80?"...":""}</span>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Share drawer - narrow screens overlay */}
      {mounted && isMobile && shareOpen && (
        <>
          <div onClick={() => setShareOpen(false)}
               style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.3)", zIndex: 20 }} />
          <aside role="dialog" aria-modal
            style={{
              position: "fixed", top: 0, right: 0, bottom: 0,
              width: "min(92vw, 280px)",
              background: "#fff", borderLeft: "1px solid #e5e7eb",
              boxShadow: "-8px 0 16px rgba(0,0,0,0.06)",
              zIndex: 21, display: "flex", flexDirection: "column", minHeight: 0
            }}
          >
            <SharePanel
              me={me}
              selectedConv={selectedConv}
              members={members}
              owner={ownerUser}
              shareBusy={shareBusy}
              shareError={shareError}
              shareEmail={shareEmail}
              newRole={newRole}
              setShareEmail={setShareEmail}
              setNewRole={setNewRole}
              addMember={addMember}
              changeRole={changeRole}
              removeMember={removeMember}
            />
          </aside>
        </>
      )}

      {/* Wide screens third column */}
      {mounted && !isMobile && shareOpen && (
        <aside
          style={{
            borderLeft: "1px solid #e5e7eb",
            background: "#fff",
            display: "flex",
            flexDirection: "column",
            minHeight: 0,
            overflow: "hidden",
          }}
        >
          <SharePanel
            me={me}
            selectedConv={selectedConv}
            members={members}
            owner={ownerUser}
            shareBusy={shareBusy}
            shareError={shareError}
            shareEmail={shareEmail}
            newRole={newRole}
            setShareEmail={setShareEmail}
            setNewRole={setNewRole}
            addMember={addMember}
            changeRole={changeRole}
            removeMember={removeMember}
          />
        </aside>
      )}
    </div>
  );
}

/** Share panel (Owner/Collaborator: show "Me" for self; self pinned to top with gray background) */
function SharePanel({
  me,
  selectedConv,
  members,
  owner,
  shareBusy,
  shareError,
  shareEmail,
  newRole,
  setShareEmail,
  setNewRole,
  addMember,
  changeRole,
  removeMember,
}: {
  me: Me | null;
  selectedConv: Conv | null;
  members: Member[];
  owner: UserBrief | null;
  shareBusy: boolean;
  shareError: string | null;
  shareEmail: string;
  newRole: "unassigned" | "editor" | "viewer";
  setShareEmail: (v: string) => void;
  setNewRole: (v: "unassigned" | "editor" | "viewer") => void;
  addMember: () => void;
  changeRole: (userId: number, role: "editor" | "viewer") => void;
  removeMember: (userId: number) => void;
}) {
  const myId = me?.id;
  const myEmail = (me?.email || "").toLowerCase();

  const isSelf = (u?: UserBrief | null) => {
    if (!u) return false;
    if (typeof myId === "number" && u.id === myId) return true;
    const ue = (u.email || "").toLowerCase();
    return !!ue && !!myEmail && ue === myEmail;
  };

  // Remove owner (owner displayed separately)
  const base = useMemo(() => members.filter(m => m.role !== "owner"), [members]);

  // In collaborators: place self on top; others sorted by name
  const editors = useMemo(() => {
    const arr = base.filter(m => m.role === "editor");
    return [...arr].sort((a, b) => {
      const aSelf = isSelf(a.user) ? 0 : 1;
      const bSelf = isSelf(b.user) ? 0 : 1;
      if (aSelf !== bSelf) return aSelf - bSelf;
      const an = displayName(a.user).toLowerCase();
      const bn = displayName(b.user).toLowerCase();
      return an.localeCompare(bn);
    });
  }, [base, myId, myEmail]);

  const viewers = useMemo(() => {
    const arr = base.filter(m => m.role === "viewer");
    return [...arr].sort((a, b) =>
      displayName(a.user).toLowerCase().localeCompare(displayName(b.user).toLowerCase())
    );
  }, [base]);

  const canAdd = !!shareEmail.trim() && isEmail(shareEmail.trim()) && newRole !== "unassigned" && !shareBusy && !!selectedConv;

  const emailTrim = shareEmail.trim();
  let inlineHint: string | null = null;
  if (!emailTrim) inlineHint = null;
  else if (!isEmail(emailTrim)) inlineHint = "Invalid email address.";
  else if (newRole === "unassigned") inlineHint = "Choose a role.";

  const heading: React.CSSProperties = { fontWeight: 700, flex: 1, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" };

  // Owner row: self => "Me"
  const ownerLine =
    selectedConv?.access_role === "owner" || isSelf(owner)
      ? `Me${me?.email ? ` - ${me.email}` : ""}`
      : (owner
          ? `${displayName(owner)}${owner.email ? ` - ${owner.email}` : ""}`
          : (selectedConv?.shared_by
              ? `${displayName(selectedConv.shared_by)}${selectedConv.shared_by.email ? ` - ${selectedConv.shared_by.email}` : ""}`
              : "Owner unknown"));

  const Row: React.FC<{ m: Member; onMake: "editor" | "viewer" }> = ({ m, onMake }) => {
    const self = isSelf(m.user);
    const bg = self ? "#f5f5f5" : "#fff";
    return (
      <div
        key={m.user.id}
        style={{
          padding: "5px 6px", border: "1px solid #e5e7eb", borderRadius: 4, background: bg,
          display: "flex", flexDirection: "column", gap: 3, marginBottom: 5
        }}
      >
        <div style={{ minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 4, minWidth: 0 }}>
            <div style={{ fontWeight: 600, fontSize: 12, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              {self ? "Me" : displayName(m.user)}
            </div>
            {/* Badge also says "Me" */}
            {self && (
              <span style={{
                fontSize: 9, padding: "0 4px", borderRadius: 999,
                border: "1px solid #ddd", background: "#eee", color: "#555", flexShrink: 0
              }}>
                Me
              </span>
            )}
          </div>
          <div style={{ fontSize: 10, color: "#666", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {emailOf(m.user)}
          </div>
        </div>
        <div style={{ display: "flex", gap: 3, alignItems: "center", opacity: self ? .6 : 1 }}>
          <button
            onClick={() => changeRole(m.user.id, onMake)}
            disabled={shareBusy || self}
            title={self ? "This is you" : undefined}
            style={{ padding: "2px 5px", fontSize: 10, flex: 1 }}
          >
            {onMake === "viewer" ? "→ Viewer" : "→ Editor"}
          </button>
          <button
            onClick={() => removeMember(m.user.id)}
            disabled={shareBusy || self}
            title={self ? "This is you" : undefined}
            style={{ padding: "2px 5px", fontSize: 10, flex: 1 }}
          >
            Remove
          </button>
        </div>
      </div>
    );
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: 0 }}>
      <div style={{
        display: "flex",
        gap: 6,
        padding: 10,
        borderBottom: "1px solid #e5e7eb",
        alignItems: "center",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
      }}>
        <div style={{ ...heading, color: "#fff", fontSize: 14 }}>Share</div>
        <div style={{ fontSize: 11, color: "rgba(255,255,255,0.8)" }}>{shareBusy ? "..." : ""}</div>
      </div>

      {/* Add new people */}
      <div style={{ padding: 8, borderBottom: "1px solid #e5e7eb", display: "grid", gap: 5 }}>
        <div style={{ fontWeight: 600, fontSize: 12 }}>Add people</div>
        <input
          value={shareEmail}
          onChange={(e) => setShareEmail(e.target.value)}
          placeholder="email"
          style={{ padding: "4px 6px", fontSize: 12, width: "100%", boxSizing: "border-box" }}
          disabled={shareBusy || !selectedConv}
        />
        <div style={{ display: "grid", gap: 3 }}>
          <label style={{ fontSize: 11, display: "flex", alignItems: "center", gap: 4 }}>
            <input
              type="radio"
              name="newRole"
              value="editor"
              checked={newRole === "editor"}
              onChange={() => setNewRole("editor")}
              disabled={shareBusy}
            />
            Collaborator
          </label>
          <label style={{ fontSize: 11, display: "flex", alignItems: "center", gap: 4 }}>
            <input
              type="radio"
              name="newRole"
              value="viewer"
              checked={newRole === "viewer"}
              onChange={() => setNewRole("viewer")}
              disabled={shareBusy}
            />
            Viewer
          </label>
        </div>
        <button
          onClick={addMember}
          disabled={!canAdd}
          style={{ padding: "4px 6px", fontSize: 12, width: "100%" }}
          title={
            !emailTrim ? "Enter an email address"
            : !isEmail(emailTrim) ? "Invalid email address"
            : newRole === "unassigned" ? "Choose a role"
            : "Add"
          }
        >
          Add
        </button>

        {shareError ? (
          <div style={{ color: "#b00020", fontSize: 10 }}>{shareError}</div>
        ) : (inlineHint && !canAdd) ? (
          <div style={{ color: "#666", fontSize: 10 }}>{inlineHint}</div>
        ) : null}
      </div>

      {/* Owner: plain text (self => Me) */}
      <div style={{ padding: 8, borderBottom: "1px solid #e5e7eb" }}>
        <div style={{ fontWeight: 600, marginBottom: 3, fontSize: 12 }}>Owner</div>
        <div style={{ fontSize: 11, wordBreak: "break-word" }}>{ownerLine}</div>
      </div>

      {/* Members */}
      <div style={{ flex: 1, minHeight: 0, overflow: "auto", display: "grid", gap: 8, padding: 8 }}>
        {/* Collaborators (self pinned + gray + "Me") */}
        <section>
          <div style={{ fontWeight: 600, marginBottom: 3, fontSize: 12 }}>Collaborators</div>
          {editors.length === 0 ? (
            <div style={{ padding: 3, fontSize: 11, opacity: .6 }}>No collaborators.</div>
          ) : editors.map((m) => <Row key={m.user.id} m={m} onMake="viewer" />)}
        </section>

        {/* Viewers (sorted by name) */}
        <section>
          <div style={{ fontWeight: 600, marginBottom: 3, fontSize: 12 }}>Viewers</div>
          {viewers.length === 0 ? (
            <div style={{ padding: 3, fontSize: 11, opacity: .6 }}>No viewers.</div>
          ) : viewers.map((m) => <Row key={m.user.id} m={m} onMake="editor" />)}
        </section>
      </div>
    </div>
  );
}
