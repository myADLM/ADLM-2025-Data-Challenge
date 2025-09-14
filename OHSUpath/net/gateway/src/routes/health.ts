// net/gateway/src/routes/health.ts

import { Router } from "express";
export const health = Router();
health.get("/health", (_req, res) => res.json({ ok: true, ts: Date.now() }));
