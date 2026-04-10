"use client";

export default function GlobalError({ reset }: { reset: () => void }) {
  return (
    <html>
      <body style={{ fontFamily: "system-ui, sans-serif", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: "100vh", gap: "16px" }}>
        <p style={{ fontSize: "18px", fontWeight: 600 }}>Something went wrong</p>
        <button onClick={reset} style={{ padding: "8px 20px", borderRadius: "10px", background: "#2563eb", color: "#fff", border: "none", cursor: "pointer" }}>
          Try again
        </button>
      </body>
    </html>
  );
}
