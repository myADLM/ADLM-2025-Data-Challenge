// net/web/src/app/page.tsx

"use client";
import Link from "next/link";

export default function Home() {
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
        maxWidth: 600,
        width: "100%",
        background: "#fff",
        borderRadius: "clamp(12px, 2vw, 16px)",
        padding: "clamp(24px, 5vw, 48px) clamp(20px, 4vw, 40px)",
        boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
        margin: "auto"
      }}>
        <div style={{ textAlign: "center", marginBottom: "clamp(24px, 5vw, 40px)" }}>
          <h1 style={{
            fontSize: "clamp(28px, 6vw, 42px)",
            fontWeight: 700,
            margin: 0,
            marginBottom: "clamp(8px, 2vw, 12px)",
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text"
          }}>
            OHSUpath Reader
          </h1>
          <p style={{
            fontSize: "clamp(13px, 2.5vw, 16px)",
            color: "#666",
            margin: 0,
            lineHeight: 1.6
          }}>
            Intelligent document search and analysis
          </p>
        </div>

        <div style={{ display: "grid", gap: "clamp(12px, 2vw, 16px)" }}>
          <Link href="/login" prefetch={false} style={{ textDecoration: "none" }}>
            <div style={{
              padding: "clamp(12px, 2vw, 16px) clamp(18px, 3vw, 24px)",
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              color: "#fff",
              borderRadius: "clamp(8px, 2vw, 12px)",
              cursor: "pointer",
              textAlign: "center",
              fontWeight: 600,
              fontSize: "clamp(14px, 2.5vw, 16px)",
              transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
              boxShadow: "0 4px 14px rgba(102, 126, 234, 0.4)",
              position: "relative",
              overflow: "hidden"
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-3px) scale(1.02)";
              e.currentTarget.style.boxShadow = "0 8px 24px rgba(102, 126, 234, 0.5)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0) scale(1)";
              e.currentTarget.style.boxShadow = "0 4px 14px rgba(102, 126, 234, 0.4)";
            }}
            onMouseDown={(e) => {
              e.currentTarget.style.transform = "translateY(-1px) scale(0.98)";
            }}
            onMouseUp={(e) => {
              e.currentTarget.style.transform = "translateY(-3px) scale(1.02)";
            }}>
              Sign In
            </div>
          </Link>

          <Link href="/chat" prefetch={false} style={{ textDecoration: "none" }}>
            <div style={{
              padding: "clamp(12px, 2vw, 16px) clamp(18px, 3vw, 24px)",
              background: "#fff",
              color: "#667eea",
              border: "2px solid #667eea",
              borderRadius: "clamp(8px, 2vw, 12px)",
              cursor: "pointer",
              textAlign: "center",
              fontWeight: 600,
              fontSize: "clamp(14px, 2.5vw, 16px)",
              transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
              boxShadow: "0 2px 8px rgba(102, 126, 234, 0.15)"
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
            onMouseDown={(e) => {
              e.currentTarget.style.transform = "translateY(-1px) scale(0.98)";
            }}
            onMouseUp={(e) => {
              e.currentTarget.style.transform = "translateY(-3px) scale(1.02)";
            }}>
              Go to Chat
            </div>
          </Link>
        </div>

        <div style={{
          marginTop: "clamp(20px, 4vw, 32px)",
          paddingTop: "clamp(16px, 3vw, 24px)",
          borderTop: "1px solid #eee",
          textAlign: "center"
        }}>
          <p style={{ fontSize: "clamp(11px, 2vw, 13px)", color: "#999", margin: 0 }}>
            Access documents with AI
          </p>
        </div>
      </div>
    </main>
  );
}
