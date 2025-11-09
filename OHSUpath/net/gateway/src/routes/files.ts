// net/gateway/src/routes/files.ts

import { Router } from "express";
import { requireAuth, AuthedRequest } from "../middleware/auth.js";
import { config } from "../config.js";
import { Readable } from "node:stream";

export const files = Router();

// File viewing endpoint: proxy to FastAPI /files/{file_path}/download
// Displays inline in browser tab using browser's native PDF viewer
// Use wildcard to support nested paths like "subfolder/document.pdf"
files.get("/files/*/download", requireAuth, async (req: AuthedRequest, res) => {
  try {
    // Extract file path from wildcard (everything between /files/ and /download)
    const filePath = req.params[0];

    // No query params needed - backend always serves inline
    const upstreamUrl = `${config.apiBase}/files/${filePath}/download`;
    console.log(`[gw] proxy GET /files/${filePath}/download -> ${upstreamUrl}`);

    const upstream = await fetch(upstreamUrl, {
      headers: {
        "x-internal-key": config.internalKey,
        "x-user-id": String(req.user!.id),
      } as any,
    });

    // Forward status and all headers (especially Content-Disposition)
    res.status(upstream.status);
    upstream.headers.forEach((v, k) => {
      res.setHeader(k, v);
    });

    if (!upstream.body) {
      return res.end();
    }

    // Stream the file response
    // @ts-ignore
    const nodeStream = (Readable as any).fromWeb
      ? (Readable as any).fromWeb(upstream.body)
      : Readable.from(upstream.body as any);
    nodeStream.pipe(res);
  } catch (e) {
    console.error("[gw] GET /files/*/download error:", e);
    res.status(502).json({ error: "Download proxy error" });
  }
});
