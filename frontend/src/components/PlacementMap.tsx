import { useState } from "react";
import type { Placement, PlacementType, ValueScore, Verdict } from "../types";

const VERDICT_COLOR: Record<Verdict, string> = {
  undervalued: "#2f6b4f",
  fair: "#8a7f5c",
  overpriced: "#a4402f",
};

const VERDICT_LABEL: Record<Verdict, string> = {
  undervalued: "Undervalued",
  fair: "Fair",
  overpriced: "Overpriced",
};

type IconType = "gate" | "led" | "jumbotron" | "banner" | "jersey";

function iconTypeFor(t: PlacementType): IconType {
  switch (t) {
    case "gate_branding":
      return "gate";
    case "led_board":
      return "led";
    case "jumbotron":
      return "jumbotron";
    case "concourse_banner":
      return "banner";
    case "jersey_patch":
      return "jersey";
    case "naming_rights":
      return "banner";
  }
}

export function TypeIcon({ type, className = "" }: { type: PlacementType; className?: string }) {
  const iconType = iconTypeFor(type);
  const common = "stroke-current";
  switch (iconType) {
    case "gate":
      return (
        <svg viewBox="0 0 16 16" className={className} fill="none" strokeWidth="1.4">
          <path d="M3 13V6a5 5 0 0110 0v7" className={common} />
          <path d="M3 13h10" className={common} />
        </svg>
      );
    case "led":
      return (
        <svg viewBox="0 0 16 16" className={className} fill="none" strokeWidth="1.4">
          <rect x="2" y="6" width="12" height="4" className={common} />
          <path d="M5 12v1M11 12v1" className={common} />
        </svg>
      );
    case "jumbotron":
      return (
        <svg viewBox="0 0 16 16" className={className} fill="none" strokeWidth="1.4">
          <rect x="2.5" y="3.5" width="11" height="7" className={common} />
          <path d="M8 10.5V13M5 13h6" className={common} />
        </svg>
      );
    case "banner":
      return (
        <svg viewBox="0 0 16 16" className={className} fill="none" strokeWidth="1.4">
          <path d="M3 4h10l-2 3 2 3H3z" className={common} />
        </svg>
      );
    case "jersey":
      return (
        <svg viewBox="0 0 16 16" className={className} fill="none" strokeWidth="1.4">
          <path d="M4 3l2-1 2 1 2-1 2 1 2 2-2 2v6H4V7L2 5z" className={common} />
        </svg>
      );
  }
}

// Static numbered perimeter gates -- purely decorative wayfinding detail,
// not tied to real data (matches the reference stadium-map aesthetic).
const GATES = [
  { n: 1, x: 50, y: 96 },
  { n: 2, x: 22, y: 90 },
  { n: 3, x: 6, y: 66 },
  { n: 4, x: 22, y: 12 },
  { n: 5, x: 42, y: 6 },
  { n: 6, x: 58, y: 6 },
  { n: 7, x: 78, y: 12 },
  { n: 8, x: 92, y: 30 },
  { n: 9, x: 96, y: 50 },
  { n: 10, x: 92, y: 70 },
  { n: 11, x: 70, y: 94 },
];

const RINGS = [
  { rx: 46, ry: 38, fill: "#c98b6f" },
  { rx: 40, ry: 33, fill: "#d9a878" },
  { rx: 34, ry: 28, fill: "#dcc27a" },
  { rx: 28, ry: 23, fill: "#9db584" },
  { rx: 22, ry: 18, fill: "#8fb4c2" },
];

interface Props {
  placements: Placement[];
  scores: Record<string, ValueScore>;
}

export default function PlacementMap({ placements, scores }: Props) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const hoveredPlacement = placements.find((p) => p.id === hoveredId) ?? null;
  const hoveredScore = hoveredId ? scores[hoveredId] : undefined;

  return (
    <div className="rounded-sm border border-line bg-panel">
      <div className="border-b border-line px-6 py-5">
        <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-gold">Figure 01</p>
        <h2 className="mt-1 font-display text-2xl font-semibold text-ink">Exposure Map</h2>
        <p className="mt-1 text-sm text-ink-soft">
          Placements plotted at anatomical stadium positions. Pin size scales with exposure;
          color signals valuation verdict.
        </p>
      </div>

      <div className="relative p-4 md:p-6">
        <svg viewBox="0 0 100 100" className="h-auto w-full" preserveAspectRatio="xMidYMid meet">
          <defs>
            <pattern id="dots" width="4" height="4" patternUnits="userSpaceOnUse">
              <circle cx="0.5" cy="0.5" r="0.3" fill="#d9d1bd" />
            </pattern>
          </defs>
          <rect width="100" height="100" fill="url(#dots)" opacity="0.3" />

          {RINGS.map((r, i) => (
            <ellipse
              key={i}
              cx="50"
              cy="50"
              rx={r.rx}
              ry={r.ry}
              fill={r.fill}
              stroke="#fffdf7"
              strokeWidth="0.5"
              opacity="0.72"
            />
          ))}

          {Array.from({ length: 16 }).map((_, i) => {
            const a = (i / 16) * Math.PI * 2 - Math.PI / 2;
            const x1 = 50 + Math.cos(a) * 22;
            const y1 = 50 + Math.sin(a) * 18;
            const x2 = 50 + Math.cos(a) * 46;
            const y2 = 50 + Math.sin(a) * 38;
            return (
              <line
                key={i}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke="#fffdf7"
                strokeWidth="0.35"
                opacity="0.65"
              />
            );
          })}

          <rect x="32" y="40" width="36" height="20" fill="#c9d6b0" stroke="#7a8f5c" strokeWidth="0.3" />
          <line x1="50" y1="40" x2="50" y2="60" stroke="#7a8f5c" strokeWidth="0.2" />
          <circle cx="50" cy="50" r="2" fill="none" stroke="#7a8f5c" strokeWidth="0.2" />
          <text x="50" y="51.2" textAnchor="middle" fontSize="1.8" fontFamily="IBM Plex Mono" fill="#4d5c3a" letterSpacing="0.3">
            PITCH
          </text>

          {[
            { l: "N", x: 50, y: 3 },
            { l: "S", x: 50, y: 99 },
            { l: "E", x: 99, y: 51 },
            { l: "W", x: 1, y: 51 },
          ].map((c) => (
            <text
              key={c.l}
              x={c.x}
              y={c.y}
              textAnchor={c.l === "E" ? "end" : c.l === "W" ? "start" : "middle"}
              fontSize="2"
              fontFamily="IBM Plex Mono"
              fill="#7a7791"
              letterSpacing="0.4"
            >
              {c.l}
            </text>
          ))}

          {GATES.map((g) => (
            <g key={g.n}>
              <circle cx={g.x} cy={g.y} r="2.4" fill="#1c1b29" />
              <text
                x={g.x}
                y={g.y + 0.9}
                textAnchor="middle"
                fontSize="2.2"
                fontFamily="IBM Plex Mono"
                fontWeight="600"
                fill="#f6f2e9"
              >
                {g.n}
              </text>
            </g>
          ))}

          {placements.map((p) => {
            const score = scores[p.id];
            const verdict: Verdict = score?.verdict ?? "fair";
            const exposure = score?.exposure_score ?? 20;
            const r = 1.5 + (exposure / 100) * 2.2;
            const isHover = hoveredId === p.id;
            const label = `${p.name}, ${VERDICT_LABEL[verdict]}, exposure ${exposure} out of 100${
              score ? `, CPM $${score.cost_per_thousand_impressions}` : ""
            }`;
            return (
              <g
                key={p.id}
                transform={`translate(${p.x * 100} ${p.y * 100})`}
                onMouseEnter={() => setHoveredId(p.id)}
                onMouseLeave={() => setHoveredId(null)}
                onFocus={() => setHoveredId(p.id)}
                onBlur={() => setHoveredId(null)}
                tabIndex={0}
                role="button"
                aria-label={label}
                style={{ cursor: "pointer", outline: "none" }}
              >
                <circle r={r + 1.4} fill={VERDICT_COLOR[verdict]} opacity={isHover ? 0.3 : 0.15} />
                <circle
                  r={r}
                  fill={VERDICT_COLOR[verdict]}
                  stroke="#fffdf7"
                  strokeWidth={isHover ? "1" : "0.4"}
                />
              </g>
            );
          })}
        </svg>

        <div
          className={`mt-3 border border-line bg-paper px-4 py-3 transition-opacity ${
            hoveredPlacement ? "opacity-100" : "opacity-60"
          }`}
          aria-live="polite"
        >
          {hoveredPlacement ? (
            <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4">
              <div className="min-w-0">
                <div className="truncate font-display text-base text-ink">{hoveredPlacement.name}</div>
                <div className="mt-0.5 font-mono text-[11px] text-ink-dim">
                  {hoveredScore?.zone_name ?? ""}
                </div>
              </div>
              <div className="flex items-center gap-4 font-mono text-xs tabular-nums text-ink-dim">
                {hoveredScore && (
                  <>
                    <span style={{ color: VERDICT_COLOR[hoveredScore.verdict] }}>
                      {VERDICT_LABEL[hoveredScore.verdict]}
                    </span>
                    <span>EXP {hoveredScore.exposure_score}</span>
                    <span>CPM ${hoveredScore.cost_per_thousand_impressions}</span>
                  </>
                )}
              </div>
            </div>
          ) : (
            <div className="font-mono text-[11px] uppercase tracking-[0.12em] text-ink-dim">
              Hover a placement to inspect
            </div>
          )}
        </div>
      </div>

      <div className="space-y-3 border-t border-line px-6 py-4">
        <div className="font-mono text-[11px] uppercase tracking-[0.12em] text-ink-dim">Legend</div>
        <div className="flex flex-wrap gap-x-6 gap-y-2">
          {(["undervalued", "fair", "overpriced"] as Verdict[]).map((v) => (
            <div key={v} className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full" style={{ background: VERDICT_COLOR[v] }} />
              <span className="font-mono text-xs uppercase tracking-[0.12em] text-ink-dim">
                {VERDICT_LABEL[v]}
              </span>
            </div>
          ))}
        </div>
        <div className="flex flex-wrap gap-x-6 gap-y-2 pt-1">
          {(
            [
              ["gate_branding", "Gate"],
              ["led_board", "LED Board"],
              ["jumbotron", "Jumbotron"],
              ["concourse_banner", "Banner"],
              ["jersey_patch", "Jersey Patch"],
            ] as [PlacementType, string][]
          ).map(([t, label]) => (
            <div key={t} className="flex items-center gap-2 text-ink-dim">
              <TypeIcon type={t} className="h-3.5 w-3.5" />
              <span className="font-mono text-xs uppercase tracking-[0.12em]">{label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
