// net/gateway/src/server.ts

import express from "express";
import cors from "cors";
import cookieParser from "cookie-parser";
import morgan from "morgan";
import helmet from "helmet";
import compression from "compression";
import rateLimit from "express-rate-limit";
import { config } from "./config.js";

import { auth } from "./routes/auth.js";
import conversations from "./routes/conversations.js";
import query from "./routes/query.js";
import { files } from "./routes/files.js";

const app = express();

// Base middleware
app.use(helmet());

// Disable compression for SSE and file downloads to avoid chunking/flush issues
const noCompress = (req: any, res: any) => {
  const path = req?.path || "";
  if (path.startsWith("/api/query/stream")) return true;
  if (path.startsWith("/api/files/") && path.includes("/download")) return true;
  const accept = req.headers?.accept || "";
  if (accept.includes("text/event-stream")) return true;
  return false;
};

app.use(compression({
  filter: (req, res) => {
    if (noCompress(req, res)) return false;
    return compression.filter(req, res);
  }
}));

app.use(cors({ origin: config.corsOrigin, credentials: true }));
app.use(express.json({ limit: "1mb" }));
app.use(cookieParser());
app.use(morgan("dev"));

/** -- Rate limit: relaxed or can be disabled in dev -- */
const isProd = process.env.NODE_ENV === "production";
const disableDevRateLimit = process.env.RATE_LIMIT_DISABLE === "1";

if (!disableDevRateLimit) {
  app.use(
    rateLimit({
      windowMs: config.rateLimit?.windowMs ?? 15 * 60 * 1000,
      max: config.rateLimit?.max ?? (isProd ? 600 : 100000), // very high locally
      standardHeaders: true,
      legacyHeaders: false,
    })
  );
}

// Routes (mounted under /api prefix)
app.use("/api", auth);
app.use("/api", conversations);
app.use("/api", query); // proxy /api/query/stream
app.use("/api", files); // proxy /api/files/document/*

app.listen(config.port, () => {
  console.log(
    `[gw] listening on :${config.port} | apiBase=${config.apiBase} | cors=${config.corsOrigin}`
  );
});
