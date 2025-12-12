// net/gateway/src/routes/auth.ts

import { Router } from "express";
import jwt from "jsonwebtoken";
import { config } from "../config.js";
import type { AuthedRequest } from "../middleware/auth.js";
import { parseAuth, requireAuth } from "../middleware/auth.js";

export const auth = Router();
auth.use(parseAuth);

auth.post("/auth/login", async (req, res) => {
  const { username, email, password } = (req.body ?? {}) as any;
  const body = { username: (username ?? email ?? "").toString(), password: String(password ?? "") };

  if (!body.username || !body.password) {
    return res.status(400).json({ error: "username/password required" });
  }

  try {
    const upstream = await fetch(`${config.apiBase}/auth/login`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-internal-key": config.internalKey, // required internal key
      } as any,
      body: JSON.stringify(body),
    });

    const ct = upstream.headers.get("content-type") || "";
    const isJson = ct.includes("application/json");
    const upData = isJson ? await upstream.json().catch(() => null) : await upstream.text().catch(() => "");

    if (!upstream.ok) {
      // pass through upstream status for easier debugging
      return res.status(upstream.status).type(ct || "text/plain").send(upData || "login failed");
    }

    // API returns a user object -> gateway signs a JWT
    const u = (isJson && upData && typeof upData === "object") ? (upData as any) : null;
    const payload = { id: String(u?.id), email: u?.email, name: u?.name ?? u?.username };
    if (!payload.id) return res.status(502).json({ error: "bad upstream response" });

    const token = jwt.sign(payload, config.jwtSecret, { expiresIn: "7d" });

    res.cookie(config.cookieName, token, {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 7 * 24 * 3600 * 1000,
    });

    // compatible with existing LoginClient: 204 with no body
    res.status(204).end();
  } catch (err) {
    console.error("[gw] /auth/login error:", err);
    return res.status(502).json({ error: "API unavailable" });
  }
});

auth.post("/auth/logout", (_req, res) => {
  // use clearCookie with the same attributes to ensure deletion in the browser
  res.clearCookie(config.cookieName, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
  });
  res.status(204).end();
});

auth.get("/auth/me", requireAuth, (req: AuthedRequest, res) => res.json(req.user));
