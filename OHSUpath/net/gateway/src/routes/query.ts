// net/gateway/src/routes/query.ts

import { Router } from "express";
import { config } from "../config.js";
import { requireAuth, AuthedRequest } from "../middleware/auth.js";

export const query = Router();

function upstreamHeaders(req: AuthedRequest) {
  return {
    "x-internal-key": config.internalKey,
    "x-user-id": String(req.user!.id),
    accept: "text/event-stream",
    "content-type": "application/json",
  } as Record<string, string>;
}

function apiUrl(path: string) {
  return `${config.apiBase}${path}`;
}

// POST /api/query/stream/:id -> POST /query/stream/:id
query.post("/query/stream/:id", requireAuth, async (req: AuthedRequest, res) => {
  try {
    const up = await fetch(apiUrl(`/query/stream/${encodeURIComponent(req.params.id)}`), {
      method: "POST",
      headers: upstreamHeaders(req),
      body: JSON.stringify(req.body ?? {}),
    });

    if (!up.ok || !up.body) {
      const ct = up.headers.get("content-type") || "text/plain";
      const text = await up.text().catch(() => "");
      res.status(up.status).type(ct).send(text || "stream upstream error");
      return;
    }

    // forward SSE headers
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("X-Accel-Buffering", "no");

    // Flush headers immediately
    if (typeof (res as any).flushHeaders === "function") {
      (res as any).flushHeaders();
    }

    // Handle premature client disconnect
    req.on("close", () => {
      console.log("[gw] SSE client disconnected");
      try { res.end(); } catch {}
    });

    // pipe the stream
    // @ts-ignore fetch WebReadableStream -> Node readable
    const reader = (up as any).body.getReader();
    async function pump() {
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        res.write(Buffer.from(value));
      }
      res.end();
    }
    pump().catch((e) => {
      console.error("[gw] SSE pump error:", e);
      try { res.end(); } catch {}
    });
  } catch (e) {
    console.error("[gw] POST /query/stream/:id error:", e);
    res.status(502).json({ error: "Bad gateway" });
  }
});

export default query;
