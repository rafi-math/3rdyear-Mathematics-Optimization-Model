import type { Plan, SolveResponse, ParsedPlan, ModelType } from "./types";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function readError(res: Response, fallback: string): Promise<string> {
  const data = await res.json().catch(() => null);
  if (data && typeof data.detail === "string") return data.detail;
  if (data && Array.isArray(data.detail)) return data.detail.map((d: any) => d.msg || JSON.stringify(d)).join("; ");
  return fallback;
}

export async function fetchHealth(): Promise<{ status: string }> {
  try {
    const res = await fetch(`${API_BASE}/health`, { cache: "no-store" });
    if (!res.ok) return { status: "offline" };
    return await res.json();
  } catch {
    return { status: "offline" };
  }
}

export async function fetchCaseStudy(): Promise<any> {
  const res = await fetch(`${API_BASE}/case-study`, { cache: "no-store" });
  if (!res.ok) throw new Error(await readError(res, "Failed to load case study fixture"));
  return await res.json();
}

export async function solvePlan(plan: Plan, models: ModelType[] = ["A", "B", "C"]): Promise<SolveResponse> {
  const res = await fetch(`${API_BASE}/solve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ plan, models }),
  });
  if (!res.ok) {
    throw new Error(await readError(res, "Solver request failed"));
  }
  return await res.json();
}

export async function parseMultimodal(text?: string, files?: File[]): Promise<ParsedPlan> {
  const formData = new FormData();
  if (text && text.trim()) {
    formData.append("text", text);
  }
  if (files && files.length > 0) {
    for (const f of files) {
      formData.append("files", f);
    }
  }

  const res = await fetch(`${API_BASE}/parse`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error(await readError(res, "Parser failed to process the input."));
  }
  return await res.json();
}

export async function downloadExport(type: "csv" | "pdf" | "ics", payload: any): Promise<void> {
  const res = await fetch(`${API_BASE}/export/${type}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(await readError(res, `Failed to export ${type.toUpperCase()}`));
  }

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `study-budget.${type}`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}
