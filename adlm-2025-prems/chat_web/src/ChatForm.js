import React, { useState } from "react";

/**
 * props:
 * - placeholder?: string
 * - onSubmit?: (value: string) => void
 */
export default function ChatForm({ placeholder = "Type your message…", onSubmit }) {
    const [value, setValue] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();
        const trimmed = value.trim();
        if (!trimmed) return;
        onSubmit && onSubmit(trimmed);
        setValue("");
    };

    return (
        <form onSubmit={handleSubmit}>
            <div className="input-group">
                <input
                    type="text"
                    className="form-control"
                    placeholder={placeholder}
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    aria-label="Message"
                />
                <button className="btn btn-primary" type="submit">
                    Send
                </button>
            </div>
        </form>
    );
}
