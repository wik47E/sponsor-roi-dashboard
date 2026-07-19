import { useEffect, useState } from "react";
import HeaderBar from "./components/HeaderBar";
import PlacementMap from "./components/PlacementMap";
import Leaderboard from "./components/Leaderboard";
import { fetchROIReport, fetchSnapshot } from "./api";
import type { Placement, ROIReport, ValueScore } from "./types";

const REFRESH_MS = 8000;

export default function App() {
  const [placements, setPlacements] = useState<Placement[]>([]);
  const [report, setReport] = useState<ROIReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      try {
        const [snap, roi] = await Promise.all([fetchSnapshot(), fetchROIReport()]);
        if (cancelled) return;
        setPlacements(snap.placements);
        setReport(roi);
        setError(null);
      } catch (e) {
        if (!cancelled) setError("Could not reach the ROI analysis service.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    load();
    const interval = setInterval(load, REFRESH_MS);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const scoreMap: Record<string, ValueScore> = {};
  report?.scores.forEach((s) => {
    scoreMap[s.placement_id] = s;
  });

  return (
    <div className="min-h-screen font-body">
      <main className="mx-auto max-w-6xl px-6 py-8">
        <HeaderBar lastUpdated={report?.timestamp ?? null} loading={loading} />

        {error && (
          <div className="mt-4 rounded-sm border border-verdict-over/40 bg-verdict-over/5 px-3 py-2 font-mono text-xs text-verdict-over">
            {error}
          </div>
        )}

        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-[1fr_1.2fr]">
          <PlacementMap placements={placements} scores={scoreMap} />
          <Leaderboard scores={report?.scores ?? []} topRecommendation={report?.top_recommendation ?? ""} />
        </div>

        <footer className="mt-10 border-t border-line pt-4 font-mono text-[11px] text-ink-dim">
          Personal project · Sponsorship &amp; Ad ROI analysis for tournament venues
        </footer>
      </main>
    </div>
  );
}
