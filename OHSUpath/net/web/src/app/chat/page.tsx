"use client";
import { useEffect, useRef, useState } from "react";
import { startSSE } from "@/lib/sse";

export default function ChatPage() {
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState("");
  const esRef = useRef<{ close: () => void } | null>(null);

  const send = () => {
    if (!input.trim()) return;
    setMessages(m => [...m, `> ${input}`]);

    const base = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:3000";
    const url = `${base}/query/stream`;

    esRef.current?.close();
    esRef.current = startSSE(url, { q: input }, {
      onMessage: t => setMessages(m => [...m, t]),
      onClose: () => setMessages(m => [...m, "[stream closed]"]),
      onError: e => setMessages(m => [...m, `[error] ${String(e)}`])
    });
    setInput("");
  };

  useEffect(() => () => { esRef.current?.close(); }, []);

  return (
    <div style={{ maxWidth: 900, margin: "24px auto", padding: "0 16px" }}>
      <h1>Chat</h1>
      <div style={{ display: "flex", gap: 8 }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === "Enter") send(); }}
          placeholder="Type your question..."
          style={{ flex: 1, padding: "8px 12px" }}
        />
        <button onClick={send}>Send</button>
      </div>
      <pre style={{ whiteSpace: "pre-wrap", marginTop: 16, padding: 12, background: "#f7f7f7" }}>
        {messages.join("\n")}
      </pre>
    </div>
  );
}
