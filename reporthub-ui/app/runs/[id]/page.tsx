"use client";

import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

type TestStatus = "all" | "failed" | "passed" | "skipped";

type TestCase = {
  id: number;
  run_id: number;
  name: string;
  classname: string | null;
  status: "passed" | "failed" | "skipped";
  time_s: number | null;
  failure_message: string | null;
};

type RunSummary = {
  run_id: number;
  name: string;
  status: string;
  total: number;
  passed: number;
  failed: number;
  skipped: number;
  pass_rate: number | null;
  duration_s: number | null;
};

const API = process.env.NEXT_PUBLIC_API_BASE!;

export default function RunDetailPage() {
  const params = useParams();
  const id = (params?.id as string) ?? null;

  const [summary, setSummary] = useState<RunSummary | null>(null);
  const [tests, setTests] = useState<TestCase[]>([]);
  const [filter, setFilter] = useState<TestStatus>("failed"); // ✅ 기본은 failed
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testsUrl = useMemo(() => {
    if (!id) return null;
    if (filter === "all") return `${API}/runs/${id}/tests`;
    return `${API}/runs/${id}/tests?status=${filter}`;
  }, [id, filter]);

  // summary는 run id 바뀔 때만 가져오면 됨
  useEffect(() => {
    if (!id) return;

    (async () => {
      try {
        setError(null);
        const sRes = await fetch(`${API}/runs/${id}/summary`, { cache: "no-store" });
        if (!sRes.ok) throw new Error(`summary ${sRes.status}: ${await sRes.text()}`);
        setSummary(await sRes.json());
      } catch (e: any) {
        setError(e?.message ?? String(e));
      }
    })();
  }, [id]);

  // tests는 filter 바뀔 때마다 다시 fetch
  useEffect(() => {
    if (!testsUrl) return;

    (async () => {
      try {
        setLoading(true);
        setError(null);
        const tRes = await fetch(testsUrl, { cache: "no-store" });
        if (!tRes.ok) throw new Error(`tests ${tRes.status}: ${await tRes.text()}`);
        setTests(await tRes.json());
      } catch (e: any) {
        setError(e?.message ?? String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, [testsUrl]);

  if (!id) return <div style={{ padding: 16 }}>Invalid run id</div>;
  if (error) return <pre style={{ padding: 16, color: "crimson" }}>{error}</pre>;
  if (!summary) return <div style={{ padding: 16 }}>Loading summary...</div>;

  const filterButtons: { key: TestStatus; label: string }[] = [
    { key: "all", label: "All" },
    { key: "failed", label: "Failed" },
    { key: "passed", label: "Passed" },
    { key: "skipped", label: "Skipped" },
  ];

  return (
    <main style={{ maxWidth: 1100, margin: "40px auto", padding: 16 }}>
      <a href="/" style={{ textDecoration: "none", color: "#0070f3" }}>
        ← Back
      </a>

      <h1 style={{ fontSize: 24, fontWeight: 900, marginTop: 12 }}>
        Run #{id} · {summary.name}
      </h1>

      <div
        style={{
          marginTop: 16,
          padding: 16,
          border: "1px solid #ddd",
          borderRadius: 12,
          display: "flex",
          justifyContent: "space-between",
          gap: 16,
          flexWrap: "wrap",
        }}
      >
        <div>
          <div style={{ fontWeight: 800 }}>Status: {summary.status}</div>
          <div style={{ color: "#666", fontSize: 12 }}>
            Pass Rate: {summary.pass_rate ?? "-"}% · Duration: {summary.duration_s ?? "-"}s
          </div>
        </div>

        <div style={{ fontSize: 12, color: "#666" }}>
          total {summary.total} · ✅ {summary.passed} · ❌ {summary.failed} · ⏭ {summary.skipped}
        </div>
      </div>

      {/* ✅ Filter Buttons */}
      <div style={{ marginTop: 22, display: "flex", gap: 8, flexWrap: "wrap" }}>
        {filterButtons.map((b) => {
          const active = filter === b.key;
          return (
            <button
              key={b.key}
              onClick={() => setFilter(b.key)}
              style={{
                padding: "8px 12px",
                borderRadius: 999,
                border: active ? "1px solid #111" : "1px solid #ddd",
                background: active ? "#111" : "#fff",
                color: active ? "#fff" : "#111",
                cursor: "pointer",
                fontWeight: 700,
                fontSize: 12,
              }}
            >
              {b.label}
            </button>
          );
        })}
        {loading && <span style={{ color: "#666", fontSize: 12, alignSelf: "center" }}>Loading…</span>}
      </div>

      <h2 style={{ marginTop: 18, fontSize: 18, fontWeight: 900 }}>
        Tests ({filter.toUpperCase()})
      </h2>

      <div style={{ overflowX: "auto", marginTop: 8 }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ textAlign: "left", borderBottom: "1px solid #ddd" }}>
              <th style={{ padding: 8 }}>Status</th>
              <th style={{ padding: 8 }}>Name</th>
              <th style={{ padding: 8 }}>Classname</th>
              <th style={{ padding: 8 }}>Time(s)</th>
              <th style={{ padding: 8 }}>Message</th>
            </tr>
          </thead>
          <tbody>
            {tests.map((t) => (
              <tr key={t.id} style={{ borderBottom: "1px solid #eee" }}>
                <td style={{ padding: 8, fontWeight: 800 }}>
                  {t.status === "passed" ? "✅" : t.status === "failed" ? "❌" : "⏭"}
                </td>
                <td style={{ padding: 8, fontFamily: "monospace" }}>{t.name}</td>
                <td style={{ padding: 8, fontFamily: "monospace" }}>{t.classname ?? "-"}</td>
                <td style={{ padding: 8 }}>{t.time_s ?? "-"}</td>
                <td style={{ padding: 8, whiteSpace: "pre-wrap" }}>
                  {t.failure_message ?? (t.status === "failed" ? "(no message)" : "-")}
                </td>
              </tr>
            ))}

            {tests.length === 0 && !loading && (
              <tr>
                <td colSpan={5} style={{ padding: 12, color: "#666" }}>
                  표시할 테스트가 없습니다.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </main>
  );
}
