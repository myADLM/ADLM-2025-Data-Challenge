// net/web/src/app/login/LoginClient.tsx

"use client";
import { useState } from "react";
import Link from "next/link";

type Props = {
  currentUser: { id: string; email?: string; name?: string } | null;
  next: string;
  force?: boolean;
};

export default function LoginClient({ currentUser, next, force }: Props) {
  const [u, setU] = useState("");
  const [p, setP] = useState("");
  const [err, setErr] = useState<string>();

  const submit = async () => {
    setErr(undefined);
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "content-type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ username: u, password: p }),
      });
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      window.location.href = next || "/chat";
    } catch (e: any) {
      setErr(String(e.message || e));
    }
  };

  const continueAs = () => {
    window.location.href = next || "/chat";
  };

  const switchAccount = async () => {
    await fetch("/api/auth/logout", { method: "POST", credentials: "include" }).catch(() => {});
    const url = new URL(window.location.href);
    url.searchParams.set("force", "1");
    window.location.href = url.toString();
  };

  const isLoggedIn = !!currentUser && !force;

  return (
    <main style={{
      minHeight: "100vh",
      height: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      padding: "clamp(12px, 3vw, 24px)",
      overflow: "auto"
    }}>
      <div style={{
        maxWidth: 480,
        width: "100%",
        background: "#fff",
        borderRadius: "clamp(12px, 2vw, 16px)",
        padding: "clamp(24px, 5vw, 40px)",
        boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
        margin: "auto"
      }}>
        <div style={{ textAlign: "center", marginBottom: "clamp(20px, 4vw, 32px)" }}>
          <h1 style={{
            fontSize: "clamp(24px, 5vw, 32px)",
            fontWeight: 700,
            margin: 0,
            marginBottom: "clamp(6px, 1.5vw, 8px)",
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text"
          }}>
            {isLoggedIn ? "Welcome Back" : "Sign In"}
          </h1>
          <p style={{ fontSize: "clamp(12px, 2.5vw, 14px)", color: "#666", margin: 0 }}>
            OHSUpath Reader
          </p>
        </div>

        {isLoggedIn ? (
          <div style={{ display: "grid", gap: "clamp(12px, 2vw, 16px)" }}>
            <div style={{
              padding: "clamp(12px, 2vw, 16px)",
              background: "linear-gradient(135deg, #f0f4ff 0%, #f5f0ff 100%)",
              border: "1px solid #e0e7ff",
              borderRadius: "clamp(6px, 1.5vw, 8px)",
              textAlign: "center"
            }}>
              <div style={{ fontSize: "clamp(11px, 2vw, 13px)", color: "#666", marginBottom: 4 }}>Signed in as</div>
              <strong style={{ fontSize: "clamp(13px, 2.5vw, 15px)", color: "#333", wordBreak: "break-word" }}>
                {currentUser?.name || currentUser?.email || currentUser?.id}
              </strong>
            </div>

            <button onClick={continueAs} style={{
              padding: "clamp(12px, 2vw, 14px) clamp(18px, 3vw, 24px)",
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              color: "#fff",
              border: "none",
              borderRadius: "clamp(8px, 2vw, 12px)",
              cursor: "pointer",
              fontWeight: 600,
              fontSize: "clamp(13px, 2.5vw, 15px)",
              boxShadow: "0 4px 14px rgba(102, 126, 234, 0.4)",
              transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-3px) scale(1.02)";
              e.currentTarget.style.boxShadow = "0 8px 24px rgba(102, 126, 234, 0.5)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0) scale(1)";
              e.currentTarget.style.boxShadow = "0 4px 14px rgba(102, 126, 234, 0.4)";
            }}
            onMouseDown={(e) => e.currentTarget.style.transform = "translateY(-1px) scale(0.98)"}
            onMouseUp={(e) => e.currentTarget.style.transform = "translateY(-3px) scale(1.02)"}>
              Continue to Chat
            </button>

            <button onClick={switchAccount} style={{
              padding: "clamp(12px, 2vw, 14px) clamp(18px, 3vw, 24px)",
              background: "#fff",
              color: "#667eea",
              border: "2px solid #667eea",
              borderRadius: "clamp(8px, 2vw, 12px)",
              cursor: "pointer",
              fontWeight: 600,
              fontSize: "clamp(13px, 2.5vw, 15px)",
              boxShadow: "0 2px 8px rgba(102, 126, 234, 0.15)",
              transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "#f0f4ff";
              e.currentTarget.style.transform = "translateY(-3px) scale(1.02)";
              e.currentTarget.style.boxShadow = "0 6px 16px rgba(102, 126, 234, 0.25)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "#fff";
              e.currentTarget.style.transform = "translateY(0) scale(1)";
              e.currentTarget.style.boxShadow = "0 2px 8px rgba(102, 126, 234, 0.15)";
            }}
            onMouseDown={(e) => e.currentTarget.style.transform = "translateY(-1px) scale(0.98)"}
            onMouseUp={(e) => e.currentTarget.style.transform = "translateY(-3px) scale(1.02)"}>
              Switch Account
            </button>
          </div>
        ) : (
          <div style={{ display: "grid", gap: "clamp(12px, 2vw, 16px)" }}>
            <div>
              <label style={{ display: "block", fontSize: "clamp(11px, 2vw, 13px)", fontWeight: 600, color: "#555", marginBottom: "clamp(4px, 1vw, 6px)" }}>
                Email Address
              </label>
              <input
                placeholder="Enter your email"
                value={u}
                onChange={(e) => setU(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && submit()}
                style={{
                  width: "100%",
                  padding: "clamp(10px, 2vw, 12px) clamp(12px, 2vw, 14px)",
                  border: "2px solid #e5e7eb",
                  borderRadius: "clamp(6px, 1.5vw, 8px)",
                  fontSize: "clamp(13px, 2.5vw, 15px)",
                  outline: "none",
                  transition: "border-color 0.2s",
                  boxSizing: "border-box"
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = "#667eea"}
                onBlur={(e) => e.currentTarget.style.borderColor = "#e5e7eb"}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "clamp(11px, 2vw, 13px)", fontWeight: 600, color: "#555", marginBottom: "clamp(4px, 1vw, 6px)" }}>
                Password
              </label>
              <input
                placeholder="Enter your password"
                type="password"
                value={p}
                onChange={(e) => setP(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && submit()}
                style={{
                  width: "100%",
                  padding: "clamp(10px, 2vw, 12px) clamp(12px, 2vw, 14px)",
                  border: "2px solid #e5e7eb",
                  borderRadius: "clamp(6px, 1.5vw, 8px)",
                  fontSize: "clamp(13px, 2.5vw, 15px)",
                  outline: "none",
                  transition: "border-color 0.2s",
                  boxSizing: "border-box"
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = "#667eea"}
                onBlur={(e) => e.currentTarget.style.borderColor = "#e5e7eb"}
              />
            </div>

            <button onClick={submit} style={{
              padding: "clamp(12px, 2vw, 14px) clamp(18px, 3vw, 24px)",
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              color: "#fff",
              border: "none",
              borderRadius: "clamp(8px, 2vw, 12px)",
              cursor: "pointer",
              fontWeight: 600,
              fontSize: "clamp(13px, 2.5vw, 15px)",
              marginTop: "clamp(6px, 1.5vw, 8px)",
              boxShadow: "0 4px 14px rgba(102, 126, 234, 0.4)",
              transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-3px) scale(1.02)";
              e.currentTarget.style.boxShadow = "0 8px 24px rgba(102, 126, 234, 0.5)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0) scale(1)";
              e.currentTarget.style.boxShadow = "0 4px 14px rgba(102, 126, 234, 0.4)";
            }}
            onMouseDown={(e) => e.currentTarget.style.transform = "translateY(-1px) scale(0.98)"}
            onMouseUp={(e) => e.currentTarget.style.transform = "translateY(-3px) scale(1.02)"}>
              Sign In
            </button>

            {err && (
              <div style={{
                padding: "clamp(10px, 2vw, 12px) clamp(12px, 2vw, 14px)",
                background: "#fef2f2",
                border: "1px solid #fecaca",
                borderRadius: "clamp(6px, 1.5vw, 8px)",
                color: "#dc2626",
                fontSize: "clamp(12px, 2.5vw, 14px)"
              }}>
                {err}
              </div>
            )}
          </div>
        )}

        <div style={{ marginTop: "clamp(16px, 3vw, 24px)", textAlign: "center" }}>
          <Link href="/" style={{ color: "#667eea", fontSize: "clamp(12px, 2.5vw, 14px)", textDecoration: "none" }}>
            Back to Home
          </Link>
        </div>
      </div>
    </main>
  );
}
