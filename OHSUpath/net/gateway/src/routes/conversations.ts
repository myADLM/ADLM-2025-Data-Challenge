// net/gateway/src/routes/conversations.ts

import { Router } from "express";
import { requireAuth, AuthedRequest } from "../middleware/auth.js";
import { config } from "../config.js";

const conversations = Router();

// -- Helper: unify upstream request headers
function upstreamHeaders(req: AuthedRequest) {
  return {
    "x-internal-key": config.internalKey,
    "x-user-id": String(req.user!.id),
    accept: "application/json",
    "content-type": "application/json",
  } as Record<string, string>;
}

// -- Helper: proxy fetch response with a safe fallback
async function proxyJson(up: Response, res: any) {
  const ct = up.headers.get("content-type") ?? "application/json";
  const text = await up.text().catch(() => "");
  res.status(up.status).type(ct).send(text);
}

function apiUrl(path: string) {
  // Do not add /api prefix here; FastAPI mounts endpoints directly at /conversations
  return `${config.apiBase}${path}`;
}

// List
conversations.get("/conversations", requireAuth, async (req: AuthedRequest, res) => {
  try {
    const up = await fetch(apiUrl("/conversations"), { headers: upstreamHeaders(req), cache: "no-store" as any });
    console.log("[gw] proxy GET /conversations ->", up.status);
    await proxyJson(up, res);
  } catch (e) {
    console.error("[gw] /conversations error:", e);
    res.status(502).json({ error: "Bad gateway" });
  }
});

// Create
conversations.post("/conversations", requireAuth, async (req: AuthedRequest, res) => {
  try {
    const up = await fetch(apiUrl("/conversations"), { method: "POST", headers: upstreamHeaders(req), body: JSON.stringify({}) });
    console.log("[gw] proxy POST /conversations ->", up.status);
    await proxyJson(up, res);
  } catch (e) {
    console.error("[gw] POST /conversations error:", e);
    res.status(502).json({ error: "Bad gateway" });
  }
});

// Detail
conversations.get("/conversations/:id", requireAuth, async (req: AuthedRequest, res) => {
  try {
    const up = await fetch(apiUrl(`/conversations/${encodeURIComponent(req.params.id)}`), {
      headers: upstreamHeaders(req),
      cache: "no-store" as any,
    });
    console.log("[gw] proxy GET /conversations/%s -> %d", req.params.id, up.status);
    await proxyJson(up, res);
  } catch (e) {
    console.error("[gw] GET /conversations/:id error:", e);
    res.status(502).json({ error: "Bad gateway" });
  }
});

// Rename
conversations.patch("/conversations/:id", requireAuth, async (req: AuthedRequest, res) => {
  try {
    const up = await fetch(apiUrl(`/conversations/${encodeURIComponent(req.params.id)}`), {
      method: "PATCH",
      headers: upstreamHeaders(req),
      body: JSON.stringify(req.body ?? {}),
    });
    console.log("[gw] proxy PATCH /conversations/%s -> %d", req.params.id, up.status);
    await proxyJson(up, res);
  } catch (e) {
    console.error("[gw] PATCH /conversations/:id error:", e);
    res.status(502).json({ error: "Bad gateway" });
  }
});

// Delete
conversations.delete("/conversations/:id", requireAuth, async (req: AuthedRequest, res) => {
  try {
    const up = await fetch(apiUrl(`/conversations/${encodeURIComponent(req.params.id)}`), {
      method: "DELETE",
      headers: upstreamHeaders(req),
    });
    console.log("[gw] proxy DELETE /conversations/%s -> %d", req.params.id, up.status);
    res.status(up.status).send();
  } catch (e) {
    console.error("[gw] DELETE /conversations/:id error:", e);
    res.status(502).json({ error: "Bad gateway" });
  }
});

// mark read (latest)
conversations.post("/conversations/:id/read", requireAuth, async (req: AuthedRequest, res) => {
  try {
    const up = await fetch(apiUrl(`/conversations/${encodeURIComponent(req.params.id)}/read`), {
      method: "POST",
      headers: upstreamHeaders(req),
    });
    console.log("[gw] proxy POST /conversations/%s/read -> %d", req.params.id, up.status);
    res.status(up.status).send();
  } catch (e) {
    console.error("[gw] POST /conversations/:id/read error:", e);
    res.status(502).json({ error: "Bad gateway" });
  }
});

// NEW: mark read-to timestamp
conversations.post("/conversations/:id/read_to", requireAuth, async (req: AuthedRequest, res) => {
  try {
    const up = await fetch(apiUrl(`/conversations/${encodeURIComponent(req.params.id)}/read_to`), {
      method: "POST",
      headers: upstreamHeaders(req),
      body: JSON.stringify(req.body ?? {}),
    });
    console.log("[gw] proxy POST /conversations/%s/read_to -> %d", req.params.id, up.status);
    res.status(up.status).send();
  } catch (e) {
    console.error("[gw] POST /conversations/:id/read_to error:", e);
    res.status(502).json({ error: "Bad gateway" });
  }
});

// shares (unchanged)
conversations.get("/conversations/:id/shares", requireAuth, async (req: AuthedRequest, res) => {
  try {
    const up = await fetch(apiUrl(`/conversations/${encodeURIComponent(req.params.id)}/shares`), {
      headers: upstreamHeaders(req),
      cache: "no-store" as any,
    });
    console.log("[gw] proxy GET /conversations/%s/shares -> %d", req.params.id, up.status);
    await proxyJson(up, res);
  } catch (e) {
    console.error("[gw] GET /conversations/:id/shares error:", e);
    res.status(502).json({ error: "Bad gateway" });
  }
});

// Add or update member
conversations.post("/conversations/:id/shares", requireAuth, async (req: AuthedRequest, res) => {
  try {
    const up = await fetch(apiUrl(`/conversations/${encodeURIComponent(req.params.id)}/shares`), {
      method: "POST",
      headers: upstreamHeaders(req),
      body: JSON.stringify(req.body ?? {}),
    });
    console.log("[gw] proxy POST /conversations/%s/shares -> %d", req.params.id, up.status);
    res.status(up.status).send();
  } catch (e) {
    console.error("[gw] POST /conversations/:id/shares error:", e);
    res.status(502).json({ error: "Bad gateway" });
  }
});

// Change role
conversations.patch("/conversations/:id/shares/:userId", requireAuth, async (req: AuthedRequest, res) => {
  try {
    const up = await fetch(apiUrl(`/conversations/${encodeURIComponent(req.params.id)}/shares/${encodeURIComponent(req.params.userId)}`), {
      method: "PATCH",
      headers: upstreamHeaders(req),
      body: JSON.stringify(req.body ?? {}),
    }
  );
    console.log("[gw] proxy PATCH /conversations/%s/shares/%s -> %d", req.params.id, req.params.userId, up.status);
    res.status(up.status).send();
  } catch (e) {
    console.error("[gw] PATCH /conversations/:id/shares/:userId error:", e);
    res.status(502).json({ error: "Bad gateway" });
  }
});

// Remove member
conversations.delete("/conversations/:id/shares/:userId", requireAuth, async (req: AuthedRequest, res) => {
  try {
    const up = await fetch(apiUrl(`/conversations/${encodeURIComponent(req.params.id)}/shares/${encodeURIComponent(req.params.userId)}`), {
      method: "DELETE",
      headers: upstreamHeaders(req),
    }
  );
    console.log("[gw] proxy DELETE /conversations/%s/shares/%s -> %d", req.params.id, req.params.userId, up.status);
    res.status(up.status).send();
  } catch (e) {
    console.error("[gw] DELETE /conversations/:id/shares/:userId error:", e);
    res.status(502).json({ error: "Bad gateway" });
  }
});

export { conversations };
export default conversations;
