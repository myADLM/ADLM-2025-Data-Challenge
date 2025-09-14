// net/web/src/app/login/LoginClient.tsx

"use client";
import { useState } from "react";

type Props = {
  currentUser: { id: string; email?: string; name?: string } | null;
  next: string;
  force?: boolean;
};

export default function LoginClient({ currentUser, next, force }: Props) {
  const [u, setU] = useState("");
  const [p, setP] = useState("");
  const [err, setErr] = useState<string>();

  const submit = async () => {
    setErr(undefined);
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "content-type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ username: u, password: p }),
      });
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      window.location.href = next || "/chat";
    } catch (e: any) {
      setErr(String(e.message || e));
    }
  };

  const continueAs = () => {
    window.location.href = next || "/chat";
  };

  const switchAccount = async () => {
    await fetch("/api/auth/logout", { method: "POST", credentials: "include" }).catch(() => {});
    const url = new URL(window.location.href);
    url.searchParams.set("force", "1");
    window.location.href = url.toString();
  };

  const isLoggedIn = !!currentUser && !force;

  return (
    <div style={{ maxWidth: 460, margin: "10vh auto", padding: 24, border: "1px solid #eee", borderRadius: 12 }}>
      <h1>Login</h1>
      {isLoggedIn ? (
        <div style={{ display: "grid", gap: 12 }}>
          <div style={{ padding: 12, background: "#f6f8fa", border: "1px solid #e5e7eb", borderRadius: 8 }}>
            Already signed in as <strong>{currentUser?.name || currentUser?.email || currentUser?.id}</strong>
          </div>
          <button onClick={continueAs}>Continue</button>
          <button onClick={switchAccount}>Logout and switch account</button>
        </div>
      ) : (
        <div style={{ display: "grid", gap: 12 }}>
          <input placeholder="Email address" value={u} onChange={(e) => setU(e.target.value)} />
          <input placeholder="Password" type="password" value={p} onChange={(e) => setP(e.target.value)} />
          <button onClick={submit}>Sign in</button>
          {err && <div style={{ color: "crimson" }}>{err}</div>}
        </div>
      )}
    </div>
  );
}
