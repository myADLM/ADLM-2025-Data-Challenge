type SSEHandlers = {
  onOpen?: () => void;
  onMessage?: (t: string) => void;
  onEvent?: (e: { event?: string; data: string; id?: string }) => void;
  onError?: (e: any) => void;
  onClose?: () => void;
};

export function startSSE(url: string, body: any, handlers: SSEHandlers) {
  const ctrl = new AbortController();

  (async () => {
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
        },
        body: JSON.stringify(body),
        credentials: "include",
        signal: ctrl.signal,
      });

      if (!res.ok || !res.body) {
        let text = "";
        try { text = await res.text(); } catch {}
        throw new Error(`SSE HTTP ${res.status}${text ? `: ${text.slice(0,200)}` : ""}`);
      }

      const ct = res.headers.get("content-type") || "";
      if (!ct.includes("text/event-stream")) {
        let text = "";
        try { text = await res.text(); } catch {}
        throw new Error(`Unexpected content-type: ${ct}${text ? `; body: ${text.slice(0,200)}` : ""}`);
      }

      handlers.onOpen?.();

      const reader = res.body.getReader();
      const dec = new TextDecoder();
      let buf = "";
      const MAX_BUF = 1 << 20;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buf += dec.decode(value, { stream: true }).replace(/\r\n/g, "\n");

        let sep: number;
        while ((sep = buf.indexOf("\n\n")) !== -1) {
          const raw = buf.slice(0, sep);
          buf = buf.slice(sep + 2);

          // parse one SSE event frame
          let event: string | undefined;
          let id: string | undefined;
          const dataLines: string[] = [];

          for (const line of raw.split("\n")) {
            if (!line) continue;
            if (line.startsWith(":")) continue; // comment line
            const idx = line.indexOf(":");
            const field = idx === -1 ? line : line.slice(0, idx);
            let value = idx === -1 ? "" : line.slice(idx + 1);
            if (value.startsWith(" ")) value = value.slice(1);

            if (field === "event") event = value;
            else if (field === "data") dataLines.push(value);
            else if (field === "id") id = value;
            // ignore retry
          }

          const data = dataLines.join("\n");
          handlers.onEvent?.({ event, data, id });
          handlers.onMessage?.(data);
        }

        if (buf.length > MAX_BUF) buf = "";
      }
    } catch (e: any) {
      if (e?.name !== "AbortError") handlers.onError?.(e);
    } finally {
      handlers.onClose?.();
    }
  })();

  return { close() { ctrl.abort(); } };
}
