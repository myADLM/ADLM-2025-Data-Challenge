import React, { useState, startTransition } from "react";
import ChatForm from "./components/ChatForm";
import ChatMessages from "./components/ChatMessages";
import { streamChat } from "./ApiClient";
import "bootstrap/dist/css/bootstrap.min.css";

export default function App() {
  const [messages, setMessages] = useState([
    // optional seed
    { id: "w1", role: "assistant", text: "Hi! I’m ready." },
  ]);
  const [err, setErr] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);

  const generateRandomId = (length = 8) => {
    return Math.random().toString(36).substring(2, length + 2);
  };

  const startChat = async (userText) => {
    setErr("");

    // Prepare conversation history from previous messages (last 6 messages)
    // Format: [{ role: "user", content: "..." }, { role: "assistant", content: "..." }]
    // Do this BEFORE adding new messages so we don't include the current user message
    const conversationHistory = messages
      .slice(-6) // Get last 6 messages
      .filter(m => m.role === "user" || m.role === "assistant")
      .filter(m => m.text && m.text.trim() !== "") // Only include messages with actual content
      .map(m => ({
        role: m.role,
        content: m.text || ""
      }));

    // push user message immediately
    const userMsg = { id: generateRandomId(), role: "user", text: userText };
    setMessages((prev) => [...prev, userMsg]);

    // create a placeholder assistant message we'll append to
    const asstId = generateRandomId();
    let draft = "";
    let citedDocuments = [];
    setMessages((prev) => [...prev, { id: asstId, role: "assistant", text: "", citedDocuments: [] }]);

    setIsStreaming(true);
    try {
      for await (const event of streamChat(userText, conversationHistory)) {
        switch (event.type) {
          case "reply": {
            // payload is a small string chunk
            draft += typeof event.payload === "string" ? event.payload : String(event.payload);
            // Use startTransition for non-urgent updates to prevent blocking token rendering
            startTransition(() => {
              setMessages((prev) =>
                prev.map((m) => (m.id === asstId ? { ...m, text: draft, citedDocuments } : m))
              );
            });
            break;
          }
          case "cited_document": {
            // payload is a JSON object with {document_id, document_path (or documnet_path), page_index, bbox}
            const citation = typeof event.payload === "object" ? event.payload : JSON.parse(event.payload);
            // Check for duplicates based on document_id and page_index
            const isDuplicate = citedDocuments.some(
              (c) => c.document_id === citation.document_id && c.page_index === citation.page_index
            );
            if (!isDuplicate) {
              citedDocuments = [...citedDocuments, citation];
              startTransition(() => {
                setMessages((prev) =>
                  prev.map((m) => (m.id === asstId ? { ...m, citedDocuments } : m))
                );
              });
            }
            break;
          }
          case "tool_call_started": {
            // optional: show tool activity in the transcript
            const info =
              typeof event.payload === "object"
                ? `Calling tool "${event.payload.function}"…`
                : "Calling tool…";
            const toolMsg = { id: generateRandomId(), role: "system", text: info };
            startTransition(() => {
              setMessages((prev) => [...prev, toolMsg]);
            });
            break;
          }
          case "tool_call_response": {
            const val =
              typeof event.payload === "object" && "value" in event.payload
                ? JSON.stringify(event.payload.value)
                : JSON.stringify(event.payload);
            const toolMsg = { id: crypto.randomUUID(), role: "system", text: `Tool result: ${val}` };
            startTransition(() => {
              setMessages((prev) => [...prev, toolMsg]);
            });
            break;
          }
          case "error": {
            setErr(typeof event.payload === "string" ? event.payload : JSON.stringify(event.payload));
            break;
          }
          default: {
            // ignore unknown lines, or log them
            // console.debug("unhandled event", event);
          }
        }
      }
    } catch (e) {
      setErr(e.message);
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div className="container min-vh-100 d-flex flex-column py-3">
      <header className="mb-3">
        <h1 className="h4 mb-0">Chat UI</h1>
        <small className="text-muted">Streaming from Django/Ninja</small>
      </header>

      <div className="card shadow-sm flex-grow-1 d-flex">
        <div className="card-body p-0 d-flex flex-column" style={{ minHeight: 0 }}>
          <ChatMessages messages={messages} />

          {err && (
            <div className="alert alert-danger m-3 mb-0" role="alert">
              {err}
            </div>
          )}

          <div className="border-top p-3">
            <ChatForm
              placeholder={isStreaming ? "Receiving reply…" : "Send a message…"}
              onSubmit={startChat}
              disabled={isStreaming} // optional: prevent overlapping requests
            />
          </div>
        </div>
      </div>
    </div>
  );
}
