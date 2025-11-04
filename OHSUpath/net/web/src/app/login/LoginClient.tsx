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
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      padding: 24
    }}>
      <div style={{
        maxWidth: 480,
        width: "100%",
        background: "#fff",
        borderRadius: 16,
        padding: "40px",
        boxShadow: "0 20px 60px rgba(0,0,0,0.3)"
      }}>
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <h1 style={{
            fontSize: 32,
            fontWeight: 700,
            margin: 0,
            marginBottom: 8,
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text"
          }}>
            {isLoggedIn ? "Welcome Back" : "Sign In"}
          </h1>
          <p style={{ fontSize: 14, color: "#666", margin: 0 }}>
            OHSUpath Reader
          </p>
        </div>

        {isLoggedIn ? (
          <div style={{ display: "grid", gap: 16 }}>
            <div style={{
              padding: 16,
              background: "linear-gradient(135deg, #f0f4ff 0%, #f5f0ff 100%)",
              border: "1px solid #e0e7ff",
              borderRadius: 8,
              textAlign: "center"
            }}>
              <div style={{ fontSize: 13, color: "#666", marginBottom: 4 }}>Signed in as</div>
              <strong style={{ fontSize: 15, color: "#333" }}>
                {currentUser?.name || currentUser?.email || currentUser?.id}
              </strong>
            </div>

            <button onClick={continueAs} style={{
              padding: "14px 24px",
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              color: "#fff",
              border: "none",
              borderRadius: 12,
              cursor: "pointer",
              fontWeight: 600,
              fontSize: 15,
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
              padding: "14px 24px",
              background: "#fff",
              color: "#667eea",
              border: "2px solid #667eea",
              borderRadius: 12,
              cursor: "pointer",
              fontWeight: 600,
              fontSize: 15,
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
          <div style={{ display: "grid", gap: 16 }}>
            <div>
              <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "#555", marginBottom: 6 }}>
                Email Address
              </label>
              <input
                placeholder="Enter your email"
                value={u}
                onChange={(e) => setU(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && submit()}
                style={{
                  width: "100%",
                  padding: "12px 14px",
                  border: "2px solid #e5e7eb",
                  borderRadius: 8,
                  fontSize: 15,
                  outline: "none",
                  transition: "border-color 0.2s",
                  boxSizing: "border-box"
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = "#667eea"}
                onBlur={(e) => e.currentTarget.style.borderColor = "#e5e7eb"}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "#555", marginBottom: 6 }}>
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
                  padding: "12px 14px",
                  border: "2px solid #e5e7eb",
                  borderRadius: 8,
                  fontSize: 15,
                  outline: "none",
                  transition: "border-color 0.2s",
                  boxSizing: "border-box"
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = "#667eea"}
                onBlur={(e) => e.currentTarget.style.borderColor = "#e5e7eb"}
              />
            </div>

            <button onClick={submit} style={{
              padding: "14px 24px",
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              color: "#fff",
              border: "none",
              borderRadius: 12,
              cursor: "pointer",
              fontWeight: 600,
              fontSize: 15,
              marginTop: 8,
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
                padding: "12px 14px",
                background: "#fef2f2",
                border: "1px solid #fecaca",
                borderRadius: 8,
                color: "#dc2626",
                fontSize: 14
              }}>
                {err}
              </div>
            )}
          </div>
        )}

        <div style={{ marginTop: 24, textAlign: "center" }}>
          <Link href="/" style={{ color: "#667eea", fontSize: 14, textDecoration: "none" }}>
            Back to Home
          </Link>
        </div>
      </div>
    </main>
  );
}
