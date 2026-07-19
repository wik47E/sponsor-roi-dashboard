export type PlacementType =
  | "led_board"
  | "jumbotron"
  | "concourse_banner"
  | "jersey_patch"
  | "gate_branding"
  | "naming_rights";

export interface Placement {
  id: string;
  name: string;
  type: PlacementType;
  zone_id: string;
  x: number;
  y: number;
  broadcast_visibility: number;
  monthly_cost: number;
}

export interface FootfallZone {
  id: string;
  name: string;
  foot_traffic: number;
  avg_dwell_seconds: number;
}

export interface PlacementSnapshot {
  timestamp: string;
  placements: Placement[];
  zones: FootfallZone[];
}

export type Verdict = "undervalued" | "fair" | "overpriced";

export interface ValueScore {
  placement_id: string;
  placement_name: string;
  zone_name: string;
  exposure_score: number;
  estimated_monthly_impressions: number;
  cost_per_thousand_impressions: number;
  verdict: Verdict;
  rationale: string;
  recommended_monthly_value: number;
}

export interface ROIReport {
  id: string;
  timestamp: string;
  scores: ValueScore[];
  top_recommendation: string;
}
