// src/apiClient.js
const BASE_URL = process.env.REACT_APP_API_BASE_URL ?? "http://localhost:8000";

export async function* streamChat(message) {
    const res = await fetch(`${BASE_URL}/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            // no auth headers needed
        },
        body: JSON.stringify({ message }),
    });

    if (!res.ok || !res.body) {
        const text = await res.text().catch(() => "");
        throw new Error(`HTTP ${res.status}: ${text || res.statusText}`);
    }

    // Stream parsing: the server yields newline-delimited lines
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        // Process complete lines
        let nl;
        while ((nl = buffer.indexOf("\n")) >= 0) {
            const line = buffer.slice(0, nl).trim();
            buffer = buffer.slice(nl + 1);

            if (!line) continue;

            // line format: "<type>: <payload>"
            const sep = line.indexOf(":");
            if (sep === -1) {
                yield { type: "unknown", raw: line };
                continue;
            }

            const type = line.slice(0, sep).trim();
            const rawPayload = line.slice(sep + 1).trim();

            // Some events carry JSON; reply payload is JSON-encoded string
            let payload = rawPayload;
            try {
                payload = JSON.parse(rawPayload);
            } catch {
                // keep as raw string if not valid JSON
            }

            yield { type, payload };
        }
    }
}

export async function health() {
    const r = await fetch(`${BASE_URL}/health`);
    if (!r.ok) throw new Error(`Health check failed: ${r.status}`);
    return r.json();
}
