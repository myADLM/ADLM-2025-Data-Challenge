import React, { useEffect, useRef } from "react";

/**
 * props:
 * - messages: array<{ id: string|number, role: "user"|"assistant"|"system"|"other", text: string }>
 */
export default function ChatMessages({ messages = [] }) {
    const scrollRef = useRef(null);

    // auto-scroll to bottom when messages change
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    return (
        <div
            ref={scrollRef}
            className="flex-grow-1 overflow-auto px-3 py-3"
            style={{ minHeight: 0 }}
            role="log"
            aria-live="polite"
        >
            {messages.length === 0 && (
                <div className="text-center text-muted py-5">
                    <small>No messages yet — start the conversation below.</small>
                </div>
            )}

            <ul className="list-unstyled mb-0">
                {messages.map((m) => {
                    const isUser = m.role === "user";
                    return (
                        <li key={m.id} className={`d-flex mb-3 ${isUser ? "justify-content-end" : "justify-content-start"}`}>
                            <div
                                className={`px-3 py-2 rounded-3 ${isUser ? "bg-primary text-white" : "bg-body-secondary"
                                    }`}
                                style={{ maxWidth: "75%" }}
                            >
                                <div className="small text-capitalize mb-1 opacity-75">
                                    {m.role === "assistant" ? "Assistant" : m.role}
                                </div>
                                <div>{m.text}</div>
                            </div>
                        </li>
                    );
                })}
            </ul>
        </div>
    );
}
