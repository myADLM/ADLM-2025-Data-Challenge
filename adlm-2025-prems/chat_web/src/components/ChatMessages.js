import React, { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";

/**
 * Props:
 * - messages: Array<{ id: string|number, role: "user"|"assistant"|"system"|"other", text: string }>
 */
export default function ChatMessages({ messages = [] }) {
    const scrollRef = useRef(null);

    // Auto-scroll to bottom when messages change
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
                    const citedDocuments = m.citedDocuments || [];
                    
                    // Extract document name from path
                    const getDocumentName = (path) => {
                        if (!path) return "Unknown Document";
                        // Handle both document_path and documnet_path (typo)
                        const filePath = path.split('/').pop() || path;
                        return filePath.replace(/\.[^/.]+$/, ""); // Remove extension
                    };
                    
                    // Filter out duplicates based on document_id and page_index
                    const uniqueCitedDocuments = citedDocuments.filter((citation, index, self) => {
                        const documentId = citation.document_id;
                        const pageIndex = citation.page_index;
                        return index === self.findIndex((c) => 
                            c.document_id === documentId && c.page_index === pageIndex
                        );
                    });
                    
                    return (
                        <li key={m.id} className={`d-flex flex-column mb-3 ${isUser ? "align-items-end" : "align-items-start"}`}>
                            <div
                                className={`px-3 py-2 rounded-3 ${isUser ? "bg-primary text-white" : "bg-body-secondary"
                                    }`}
                                style={{ maxWidth: "75%" }}
                            >
                                <div className="small text-capitalize mb-1 opacity-75">
                                    {m.role === "assistant" ? "Assistant" : m.role}
                                </div>
                                <div>
                                    {m.role === "assistant" ? (
                                        <ReactMarkdown>{m.text}</ReactMarkdown>
                                    ) : (
                                        m.text
                                    )}
                                </div>
                            </div>
                            {uniqueCitedDocuments.length > 0 && m.role === "assistant" && (
                                <div className="d-flex flex-wrap gap-2 mt-2" style={{ maxWidth: "75%" }}>
                                    {uniqueCitedDocuments.map((citation, idx) => {
                                        const documentId = citation.document_id;
                                        const documentPath = citation.document_path || citation.documnet_path; // Handle typo
                                        const pageIndex = citation.page_index;
                                        const documentName = getDocumentName(documentPath);
                                        const documentUrl = `http://mlagnuriai01d.aruplab.net:8000/documents/${documentId}/`;
                                        
                                        return (
                                            <a
                                                key={`${documentId}-${pageIndex}-${idx}`}
                                                href={documentUrl}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-decoration-none"
                                            >
                                                <div className="bg-light border rounded px-2 py-1 small d-flex align-items-center gap-1" style={{ cursor: "pointer" }}>
                                                    <span className="text-dark">{documentName}</span>
                                                    <span className="text-muted">•</span>
                                                    <span className="text-muted">Page {pageIndex !== undefined ? pageIndex + 1 : 'N/A'}</span>
                                                </div>
                                            </a>
                                        );
                                    })}
                                </div>
                            )}
                        </li>
                    );
                })}
            </ul>
        </div>
    );
}
