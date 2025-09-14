// net/gateway/src/config.ts

import "dotenv/config";

export const config = {
  port: Number(process.env.PORT ?? 3000),
  cookieName: process.env.COOKIE_NAME ?? "sid",
  jwtSecret: process.env.JWT_SECRET ?? "dev-jwt-secret",
  apiBase: process.env.API_BASE ?? "http://localhost:8000", // FastAPI
  internalKey: process.env.INTERNAL_SHARED_KEY ?? "dev-internal-key",
  corsOrigin: process.env.CORS_ORIGIN ?? "http://localhost:4000",
  rateLimit: { windowMs: 60_000, max: 120 },
};
