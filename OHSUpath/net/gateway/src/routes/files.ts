// net/gateway/src/routes/files.ts

import { Router } from "express";
import { requireAuth, AuthedRequest } from "../middleware/auth.js";
import { config } from "../config.js";
import { Readable } from "node:stream";

export const files = Router();

files.get("/files/document/*", requireAuth, async (req: AuthedRequest, res) => {
  // Extract the file path from the URL (everything after /files/document/)
  const filePath = req.params[0];
  const upstream = await fetch(`${config.apiBase}/files/document/${encodeURIComponent(filePath)}`, {
    headers: { "x-internal-key": config.internalKey, "x-user-id": String(req.user!.id) } as any,
  });
  res.status(upstream.status);
  upstream.headers.forEach((v, k) => res.setHeader(k, v));
  if (!upstream.body) return res.end();
  // @ts-ignore
  const nodeStream = (Readable as any).fromWeb ? (Readable as any).fromWeb(upstream.body) : Readable.from(upstream.body as any);
  nodeStream.pipe(res);
});
