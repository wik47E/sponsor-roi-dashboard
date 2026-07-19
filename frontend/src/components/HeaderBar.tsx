interface Props {
  lastUpdated: string | null;
  loading: boolean;
}

export default function HeaderBar({ lastUpdated, loading }: Props) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-6">
      <div>
        <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-gold">
          Tournament Operations · Commercial
        </p>
        <h1 className="mt-1 font-display text-3xl font-semibold text-ink">
          Sponsorship &amp; Ad ROI Dashboard
        </h1>
        <p className="mt-1 max-w-xl font-body text-sm text-ink-dim">
          AI-analyzed footfall and broadcast exposure, translated into pricing
          recommendations for every sponsor placement.
        </p>
      </div>
      <div className="text-right font-mono text-xs text-ink-dim">
        <div className="flex items-center justify-end gap-1.5">
          <span
            className={`h-1.5 w-1.5 rounded-full ${loading ? "bg-gold animate-pulse" : "bg-verdict-under"}`}
            aria-hidden="true"
          />
          {loading ? "Refreshing analysis…" : "Up to date"}
        </div>
        {lastUpdated && <div className="mt-1">{new Date(lastUpdated).toLocaleTimeString()}</div>}
      </div>
    </header>
  );
}
