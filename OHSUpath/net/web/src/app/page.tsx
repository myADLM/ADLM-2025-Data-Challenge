// net/web/src/app/page.tsx

"use client";
import Link from "next/link";

export default function Home() {
  return (
    <main style={{ maxWidth: 720, margin: "10vh auto", padding: 24 }}>
      <h1 style={{ marginBottom: 16 }}>Hello from OHSUpath</h1>
      <div style={{ display: "flex", gap: 12 }}>
        <Link href="/login" prefetch={false}>
          <span style={{ padding: "8px 14px", border: "1px solid #ddd", borderRadius: 8, cursor: "pointer" }}>
            /login
          </span>
        </Link>
        <Link href="/chat" prefetch={false}>
          <span style={{ padding: "8px 14px", border: "1px solid #ddd", borderRadius: 8, cursor: "pointer" }}>
            /chat
          </span>
        </Link>
      </div>
    </main>
  );
}
