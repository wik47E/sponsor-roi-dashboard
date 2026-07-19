import type { PlacementSnapshot, ROIReport } from "./types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8001";
const API_KEY = import.meta.env.VITE_API_KEY ?? "demo-key-change-me";

async function request<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "X-API-Key": API_KEY },
  });
  if (!res.ok) {
    throw new Error(`Request to ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function fetchSnapshot(): Promise<PlacementSnapshot> {
  return request<PlacementSnapshot>("/api/snapshot");
}

export function fetchROIReport(): Promise<ROIReport> {
  return request<ROIReport>("/api/roi-report");
}
