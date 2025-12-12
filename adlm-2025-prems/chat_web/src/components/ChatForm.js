import React, { useState } from "react";

export default function ChatForm({ placeholder = "Type your message…", onSubmit, disabled = false }) {
    const [value, setValue] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();
        const trimmed = value.trim();
        if (!trimmed || disabled) return;
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
                    disabled={disabled}
                />
                <button className="btn btn-primary" type="submit" disabled={disabled}>
                    Send
                </button>
            </div>
        </form>
    );
}
