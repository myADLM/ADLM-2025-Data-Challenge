// net/gateway/src/routes/query.ts

import { Router } from "express";
import { config } from "../config.js";
import { requireAuth, AuthedRequest } from "../middleware/auth.js";
import { Readable } from "node:stream";

const query = Router();

function upstreamHeaders(req: AuthedRequest) {
  return {
    "x-internal-key": config.internalKey,
    "x-user-id": String(req.user!.id),
    accept: "text/event-stream",
    "content-type": "application/json",
  } as Record<string, string>;
}

function normalizePayload(raw: any) {
  // Allow multiple input shapes; normalize to { content, ...rest }
  if (raw == null) return {};
  if (typeof raw === "string") return { content: raw };
  if (typeof raw === "object") {
    if (typeof raw.content === "string" && raw.content.trim() !== "") return raw;
    const candidates = ["q", "message", "text", "input", "prompt"];
    for (const k of candidates) {
      const v = (raw as any)[k];
      if (typeof v === "string" && v.trim() !== "") {
        const { [k]: _, ...rest } = raw as any;
        return { content: v, ...rest };
      }
    }
  }
  return raw;
}

function extractPublicId(req: AuthedRequest, payload: any): string | undefined {
  // 0) Path params first: /query/stream/:id
  const p = (req.params?.id || req.params?.public_id) as string | undefined;
  if (p && p.trim()) return p.trim();

  // 1) Body
  const body = payload ?? {};
  const bodyKeys = ["public_id", "publicId", "id", "public_chat_id", "conversation_id"];
  for (const k of bodyKeys) {
    const v = (body as any)[k];
    if (typeof v === "string" && v.trim()) return v.trim();
  }

  // 2) Query string
  const q = req.query as Record<string, any>;
  const qKeys = ["public_id", "publicId", "id", "public_chat_id", "conversation_id"];
  for (const k of qKeys) {
    const v = q?.[k];
    if (typeof v === "string" && v.trim()) return v.trim();
  }

  // 3) Headers
  const h = req.headers as Record<string, any>;
  const hKeys = ["x-public-id", "x-conversation-id", "x-chat-id"];
  for (const k of hKeys) {
    const v = h?.[k];
    if (typeof v === "string" && v.trim()) return v.trim();
  }

  // 4) Referer: often only origin is sent across origins; try a best-effort fallback
  const ref = (h["referer"] || h["referrer"]) as string | undefined;
  if (ref && typeof ref === "string") {
    try {
      const u = new URL(ref);
      const parts = u.pathname.split("/").filter(Boolean); // e.g. ["chat", "<id>"]
      const idx = parts.findIndex((s) => s === "chat");
      const cand = idx >= 0 ? parts[idx + 1] : undefined;
      if (cand && cand !== "[public_chat_id]") return cand;
    } catch {}
  }
  return undefined;
}

async function pipeUpstream(upstream: Response, res: any) {
  res.status(upstream.status);
  const ct = upstream.headers.get("content-type") || "text/event-stream";
  res.setHeader("Content-Type", ct);
  res.setHeader("Cache-Control", "no-cache, no-transform");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");
  if (!upstream.body) return res.end();

  // @ts-ignore Node 18: convert WebReadableStream to Node Readable
  const nodeStream = Readable.fromWeb(upstream.body as any);
  nodeStream.on("error", (e) => {
    console.error("[gw] stream error:", e);
    try { res.end(); } catch {}
  });
  res.flushHeaders?.();
  nodeStream.pipe(res);
}

// ---------- POST /api/query/stream ----------
query.post("/query/stream", requireAuth, async (req: AuthedRequest, res) => {
  try {
    const payload = normalizePayload(req.body ?? {});
    if (!payload || typeof payload.content !== "string" || payload.content.trim() === "") {
      return res.status(400).json({ error: "content is required" });
    }
    const pubId = extractPublicId(req, payload);
    if (pubId) (payload as any).public_id = pubId;

    const up = await fetch(`${config.apiBase}/query/stream`, {
      method: "POST",
      headers: upstreamHeaders(req),
      body: JSON.stringify(payload),
    });
    console.log("[gw] proxy POST /query/stream ->", up.status);
    await pipeUpstream(up, res);
  } catch (e) {
    console.error("[gw] POST /query/stream error:", e);
    res.status(502).json({ error: "Bad gateway" });
  }
});

// ---------- POST /api/query/stream/:id ----------
query.post("/query/stream/:id", requireAuth, async (req: AuthedRequest, res) => {
  try {
    const payload = normalizePayload(req.body ?? {});
    if (!payload || typeof payload.content !== "string" || payload.content.trim() === "") {
      return res.status(400).json({ error: "content is required" });
    }
    const pubId = extractPublicId(req, payload);
    if (pubId) (payload as any).public_id = pubId;

    const up = await fetch(`${config.apiBase}/query/stream`, {
      method: "POST",
      headers: upstreamHeaders(req),
      body: JSON.stringify(payload),
    });
    console.log("[gw] proxy POST /query/stream/:id ->", up.status);
    await pipeUpstream(up, res);
  } catch (e) {
    console.error("[gw] POST /query/stream/:id error:", e);
    res.status(502).json({ error: "Bad gateway" });
  }
});

// ---------- GET compatibility (normalize GET to POST upstream) ----------
query.get("/query/stream", requireAuth, async (req: AuthedRequest, res) => {
  try {
    const raw = Object.fromEntries(Object.entries(req.query).map(([k, v]) => [k, Array.isArray(v) ? v[0] : v]));
    const payload = normalizePayload(raw);
    if (!payload || typeof payload.content !== "string" || payload.content.trim() === "") {
      return res.status(400).json({ error: "content is required" });
    }
    const pubId = extractPublicId(req, payload);
    if (pubId) (payload as any).public_id = pubId;

    const up = await fetch(`${config.apiBase}/query/stream`, {
      method: "POST",
      headers: upstreamHeaders(req),
      body: JSON.stringify(payload),
    });
    console.log("[gw] proxy GET->POST /query/stream ->", up.status);
    await pipeUpstream(up, res);
  } catch (e) {
    console.error("[gw] GET /query/stream error:", e);
    res.status(502).json({ error: "Bad gateway" });
  }
});

query.get("/query/stream/:id", requireAuth, async (req: AuthedRequest, res) => {
  try {
    // Allow ?q= / ?content= directly in the query string
    const raw = Object.fromEntries(Object.entries(req.query).map(([k, v]) => [k, Array.isArray(v) ? v[0] : v]));
    const payload = normalizePayload(raw);
    if (!payload || typeof payload.content !== "string" || payload.content.trim() === "") {
      return res.status(400).json({ error: "content is required" });
    }
    const pubId = extractPublicId(req, payload);
    if (pubId) (payload as any).public_id = pubId;

    const up = await fetch(`${config.apiBase}/query/stream`, {
      method: "POST",
      headers: upstreamHeaders(req),
      body: JSON.stringify(payload),
    });
    console.log("[gw] proxy GET->POST /query/stream/:id ->", up.status);
    await pipeUpstream(up, res);
  } catch (e) {
    console.error("[gw] GET /query/stream/:id error:", e);
    res.status(502).json({ error: "Bad gateway" });
  }
});

export { query };
export default query;
