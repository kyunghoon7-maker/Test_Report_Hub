type RunSummary = {
  total: number;
  passed: number;
  failed: number;
  skipped: number;
  pass_rate: number | null;
};

type RunItem = {
  id: number;
  name: string;
  status: string;
  started_at: string;
  finished_at: string | null;
  duration_s: number | null;
  summary: RunSummary;
};

const API = process.env.NEXT_PUBLIC_API_BASE!;

async function getRuns(): Promise<RunItem[]> {
  const res = await fetch(`${API}/runs?limit=20&offset=0`, { cache: "no-store" });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to fetch runs: ${res.status} ${text}`);
  }
  return res.json();
}

export default async function HomePage() {
  const runs = await getRuns();

  return (
    <main style={{ maxWidth: 900, margin: "40px auto", padding: 16 }}>
      <h1 style={{ fontSize: 28, fontWeight: 800 }}>Test Report Hub</h1>
      <p style={{ color: "#666" }}>최근 실행(Runs) 목록</p>

      <div style={{ display: "grid", gap: 12, marginTop: 20 }}>
        {runs.map((r) => (
          <a
            key={r.id}
            href={`/runs/${r.id}`}
            style={{
              border: "1px solid #ddd",
              borderRadius: 12,
              padding: 16,
              textDecoration: "none",
              color: "inherit",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
              <div>
                <div style={{ fontWeight: 800 }}>{r.name}</div>
                <div style={{ fontSize: 12, color: "#666" }}>
                  id={r.id} · status={r.status} · started_at={new Date(r.started_at).toLocaleString()}
                </div>
              </div>

              <div style={{ textAlign: "right" }}>
                <div style={{ fontWeight: 800 }}>
                  Pass Rate: {r.summary.pass_rate === null ? "-" : `${r.summary.pass_rate}%`}
                </div>
                <div style={{ fontSize: 12, color: "#666" }}>
                  total {r.summary.total} · ✅ {r.summary.passed} · ❌ {r.summary.failed} · ⏭ {r.summary.skipped}
                </div>
              </div>
            </div>
          </a>
        ))}

        {runs.length === 0 && (
          <div style={{ color: "#666" }}>아직 run이 없습니다. 먼저 백엔드에서 run 생성/업로드 해주세요.</div>
        )}
      </div>
    </main>
  );
}
