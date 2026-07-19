import type { ValueScore } from "../types";

const VERDICT_STYLE: Record<string, string> = {
  undervalued: "text-verdict-under border-verdict-under/40",
  fair: "text-verdict-fair border-verdict-fair/40",
  overpriced: "text-verdict-over border-verdict-over/40",
};

interface Props {
  scores: ValueScore[];
  topRecommendation: string;
}

const currency = (n: number) =>
  n.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });

export default function Leaderboard({ scores, topRecommendation }: Props) {
  return (
    <div className="rounded-sm border border-line bg-panel p-5 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="font-display text-lg font-semibold text-ink">Value Leaderboard</h2>
        <span className="font-mono text-[11px] text-gold">AI-ranked</span>
      </div>

      {topRecommendation && (
        <p className="mb-4 rounded-sm border border-gold/30 bg-gold/5 px-3 py-2 font-body text-sm text-ink-soft">
          <span className="font-semibold text-gold">Top signal: </span>
          {topRecommendation}
        </p>
      )}

      <ol className="space-y-2" aria-label="Sponsor placements ranked by exposure value">
        {scores.map((s, i) => (
          <li
            key={s.placement_id}
            className={`rounded-sm border bg-white/40 px-3 py-3 ${VERDICT_STYLE[s.verdict]}`}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="flex items-baseline gap-2">
                  <span className="font-mono text-xs text-ink-dim">#{i + 1}</span>
                  <span className="font-display text-base font-medium text-ink">{s.placement_name}</span>
                </div>
                <div className="mt-0.5 font-mono text-[11px] text-ink-dim">{s.zone_name}</div>
              </div>
              <span className="whitespace-nowrap font-mono text-xs font-semibold capitalize">
                {s.verdict}
              </span>
            </div>

            <p className="mt-2 font-body text-sm leading-snug text-ink-soft">{s.rationale}</p>

            <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 font-mono text-[11px] text-ink-dim">
              <span>Exposure {s.exposure_score}/100</span>
              <span>{s.estimated_monthly_impressions.toLocaleString()} impressions/mo</span>
              <span>CPM ${s.cost_per_thousand_impressions}</span>
              <span>
                Suggested: <strong className="text-ink">{currency(s.recommended_monthly_value)}</strong>/mo
              </span>
            </div>
          </li>
        ))}
        {scores.length === 0 && (
          <li className="rounded-sm border border-line/60 px-3 py-6 text-center font-mono text-xs text-ink-dim">
            No placement data yet.
          </li>
        )}
      </ol>
    </div>
  );
}
