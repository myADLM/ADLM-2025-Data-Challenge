// net/gateway/src/middleware/auth.ts

import type { Request, Response, NextFunction } from "express";
import jwt from "jsonwebtoken";
import { config } from "../config.js";

export type AuthUser = { id: string; email?: string; name?: string };
export interface AuthedRequest extends Request { user?: AuthUser }

export function parseAuth(req: AuthedRequest, res: Response, next: NextFunction) {
  const raw = req.cookies?.[config.cookieName];
  if (!raw) return next();
  try {
    req.user = jwt.verify(raw, config.jwtSecret) as AuthUser;
  } catch {
    // Token invalid/expired (e.g., after rotating JWT_SECRET): clear old cookie
    res.cookie(config.cookieName, "", {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      expires: new Date(0),
    });
  }
  next();
}

export function requireAuth(req: AuthedRequest, res: Response, next: NextFunction) {
  if (!req.user) return res.status(401).json({ error: "Unauthorized" });
  next();
}
