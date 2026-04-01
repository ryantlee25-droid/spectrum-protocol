"""
comparison_report.py — Generates COMPARISON-REPORT.md from scored results.

Produces:
  - Score tables (per-phase, per-dimension, both models side-by-side)
  - Cost/latency comparison
  - Per-scenario detail where models diverged
  - ## Recommendation section with binary pass/fail and overall conclusion
"""

from __future__ import annotations

import os
from typing import Any

from scoring.composite_scorer import within_tolerance, PHASE_THRESHOLDS, COMPOSITE_THRESHOLD


# ---------------------------------------------------------------------------
# Recommendation logic
# ---------------------------------------------------------------------------

def _determine_recommendation(
    sonnet_composite: dict,
    tolerance: dict,
) -> tuple[str, str]:
    """
    Evaluate Sonnet's per-phase pass/fail against scoring-guide.yaml rules.

    Returns (outcome_id, outcome_label).
    Conditions evaluated in priority order from scoring-guide.yaml.
    """
    phases = sonnet_composite["per_phase"]
    muster_passes = phases["muster"].get("passes") or False
    pax_passes = phases["pax"].get("passes") or False
    forge_passes = phases["forge"].get("passes") or False

    tol_phases = tolerance.get("phases", {})
    muster_in_tol = tol_phases.get("muster", {}).get("within_tolerance") or False
    pax_in_tol = tol_phases.get("pax", {}).get("within_tolerance") or False
    forge_in_tol = tol_phases.get("forge", {}).get("within_tolerance") or False
    composite_in_tol = tolerance.get("composite", {}).get("within_tolerance") or False
    composite_passes = sonnet_composite.get("composite_passes") or False

    muster_ok = muster_passes and muster_in_tol
    pax_ok = pax_passes and pax_in_tol
    forge_ok = forge_passes and forge_in_tol

    # 1. Full downgrade — all three phases pass absolute threshold AND tolerance
    if muster_ok and pax_ok and forge_ok and composite_passes and composite_in_tol:
        return ("full_sonnet_downgrade",
                "Sonnet meets threshold — full downgrade recommended")

    # 2. Muster + Forge pass, Pax fails
    if muster_ok and forge_ok and not pax_ok:
        return ("partial_downgrade_muster_forge",
                "Sonnet meets Muster and Forge but not Pax — partial downgrade (Muster + Forge)")

    # 3. Muster passes, at least one of Pax/Forge fails
    if muster_ok and (not pax_ok or not forge_ok):
        return ("partial_downgrade_muster_only",
                "Sonnet meets threshold for Muster only — partial downgrade (Muster)")

    # 4. Forge only passes
    if forge_ok and not muster_ok:
        return ("partial_downgrade_forge_only",
                "Sonnet meets threshold for Forge only — partial downgrade (Forge)")

    # 5. Keep Opus
    return ("keep_opus",
            "Sonnet does not meet threshold — keep Opus for all phases")


def _cost_savings_estimate(opus_results: list[dict], sonnet_results: list[dict]) -> str:
    """Compute rough cost difference from result JSON cost_usd fields."""
    def total_cost(results: list[dict]) -> float:
        return sum(r.get("cost_usd", 0.0) or 0.0 for r in results)

    opus_cost = total_cost(opus_results)
    sonnet_cost = total_cost(sonnet_results)

    if opus_cost == 0.0:
        return "N/A (no cost data in results)"

    savings_pct = ((opus_cost - sonnet_cost) / opus_cost) * 100.0 if opus_cost > 0 else 0.0
    return (
        f"Opus total: ${opus_cost:.4f}, Sonnet total: ${sonnet_cost:.4f} "
        f"({savings_pct:+.1f}% cost change per evaluation run)"
    )


# ---------------------------------------------------------------------------
# Table builders
# ---------------------------------------------------------------------------

def _fmt(val: float | None, digits: int = 4) -> str:
    if val is None:
        return "N/A"
    return f"{val:.{digits}f}"


def _pass_label(val: bool | None) -> str:
    if val is None:
        return "?"
    return "Yes" if val else "No"


def _phase_summary_table(opus_comp: dict, sonnet_comp: dict, tolerance: dict) -> str:
    thresholds = {
        "Muster": PHASE_THRESHOLDS["muster"],
        "Pax": PHASE_THRESHOLDS["pax"],
        "Forge": PHASE_THRESHOLDS["forge"],
        "Composite": COMPOSITE_THRESHOLD,
    }

    rows = []
    for display_name, phase_key in [("Muster", "muster"), ("Pax", "pax"), ("Forge", "forge")]:
        opus_score = opus_comp["per_phase"][phase_key]["score"]
        sonnet_score = sonnet_comp["per_phase"][phase_key]["score"]
        delta = tolerance["phases"].get(phase_key, {}).get("delta")
        threshold = thresholds[display_name]
        sonnet_passes = sonnet_comp["per_phase"][phase_key].get("passes")
        rows.append(
            f"| {display_name:<7} | {_fmt(opus_score, 2):<9} | {_fmt(sonnet_score, 2):<12} "
            f"| {('+' if delta and delta >= 0 else '') + _fmt(delta, 2):<6} "
            f"| {threshold:<9} | {_pass_label(sonnet_passes):<12} |"
        )

    opus_comp_score = opus_comp.get("composite_score")
    sonnet_comp_score = sonnet_comp.get("composite_score")
    comp_delta = tolerance.get("composite", {}).get("delta")
    comp_passes = sonnet_comp.get("composite_passes")
    rows.append(
        f"| {'Composite':<7} | {_fmt(opus_comp_score, 2):<9} | {_fmt(sonnet_comp_score, 2):<12} "
        f"| {('+' if comp_delta and comp_delta >= 0 else '') + _fmt(comp_delta, 2):<6} "
        f"| {COMPOSITE_THRESHOLD:<9} | {_pass_label(comp_passes):<12} |"
    )

    header = (
        "| Phase   | Opus Score | Sonnet Score | Delta  | Threshold | Sonnet Pass? |\n"
        "|---------|-----------|--------------|--------|-----------|--------------|"
    )
    return header + "\n" + "\n".join(rows)


def _dimension_table(opus_scored: list[dict], sonnet_scored: list[dict], phase: str) -> str:
    """Build a per-dimension comparison table for a given phase."""
    # Collect all item ids from either model
    opus_items: dict[str, dict] = {}
    for r in opus_scored:
        if r.get("phase") == phase:
            for item in r.get("items", []):
                iid = item.get("id", "")
                if iid not in opus_items:
                    opus_items[iid] = {"name": item.get("name", iid), "scores": []}
                s = item.get("score")
                if s is not None:
                    opus_items[iid]["scores"].append(s)

    sonnet_items: dict[str, dict] = {}
    for r in sonnet_scored:
        if r.get("phase") == phase:
            for item in r.get("items", []):
                iid = item.get("id", "")
                if iid not in sonnet_items:
                    sonnet_items[iid] = {"name": item.get("name", iid), "scores": []}
                s = item.get("score")
                if s is not None:
                    sonnet_items[iid]["scores"].append(s)

    all_ids = sorted(set(opus_items) | set(sonnet_items))
    if not all_ids:
        return f"_No scored items for {phase}._"

    lines = [
        f"| Dimension | Opus Avg | Sonnet Avg | Delta |",
        f"|-----------|----------|------------|-------|",
    ]
    for iid in all_ids:
        name = (opus_items.get(iid) or sonnet_items.get(iid) or {}).get("name", iid)
        o_scores = opus_items.get(iid, {}).get("scores", [])
        s_scores = sonnet_items.get(iid, {}).get("scores", [])
        o_avg = sum(o_scores) / len(o_scores) if o_scores else None
        s_avg = sum(s_scores) / len(s_scores) if s_scores else None
        delta = round(s_avg - o_avg, 4) if (o_avg is not None and s_avg is not None) else None
        delta_str = (("+" if delta >= 0 else "") + f"{delta:.4f}") if delta is not None else "N/A"
        lines.append(
            f"| {name[:40]:<40} | {_fmt(o_avg, 4):<8} | {_fmt(s_avg, 4):<10} | {delta_str:<5} |"
        )
    return "\n".join(lines)


def _cost_latency_table(opus_results: list[dict], sonnet_results: list[dict]) -> str:
    def stats(results: list[dict]) -> dict:
        costs = [r.get("cost_usd") or 0.0 for r in results]
        latencies = [r.get("latency_ms") or 0 for r in results]
        input_tokens = [r.get("tokens_used", {}).get("input", 0) or 0 for r in results]
        output_tokens = [r.get("tokens_used", {}).get("output", 0) or 0 for r in results]
        n = len(results)
        return {
            "n": n,
            "total_cost": sum(costs),
            "avg_cost": sum(costs) / n if n else 0.0,
            "total_latency_ms": sum(latencies),
            "avg_latency_ms": sum(latencies) / n if n else 0.0,
            "total_input_tokens": sum(input_tokens),
            "total_output_tokens": sum(output_tokens),
        }

    o = stats(opus_results)
    s = stats(sonnet_results)

    cost_delta_pct = ((s["avg_cost"] - o["avg_cost"]) / o["avg_cost"] * 100) if o["avg_cost"] > 0 else 0.0
    lat_delta_pct = ((s["avg_latency_ms"] - o["avg_latency_ms"]) / o["avg_latency_ms"] * 100) if o["avg_latency_ms"] > 0 else 0.0

    lines = [
        "| Metric | Opus | Sonnet | Delta |",
        "|--------|------|--------|-------|",
        f"| Scenarios run | {o['n']} | {s['n']} | — |",
        f"| Total cost (USD) | ${o['total_cost']:.4f} | ${s['total_cost']:.4f} | {cost_delta_pct:+.1f}% |",
        f"| Avg cost/scenario (USD) | ${o['avg_cost']:.4f} | ${s['avg_cost']:.4f} | {cost_delta_pct:+.1f}% |",
        f"| Avg latency (ms) | {o['avg_latency_ms']:.0f} | {s['avg_latency_ms']:.0f} | {lat_delta_pct:+.1f}% |",
        f"| Total input tokens | {o['total_input_tokens']:,} | {s['total_input_tokens']:,} | — |",
        f"| Total output tokens | {o['total_output_tokens']:,} | {s['total_output_tokens']:,} | — |",
    ]
    return "\n".join(lines)


def _divergence_section(
    opus_scored: list[dict],
    sonnet_scored: list[dict],
    divergence_threshold: float = 0.15,
) -> str:
    """List scenarios where models diverged by more than divergence_threshold."""
    opus_by_id = {r["scenario_id"]: r for r in opus_scored if r.get("scenario_id")}
    sonnet_by_id = {r["scenario_id"]: r for r in sonnet_scored if r.get("scenario_id")}

    shared_ids = sorted(set(opus_by_id) & set(sonnet_by_id))
    divergent = []

    for sid in shared_ids:
        o_score = opus_by_id[sid].get("phase_score")
        s_score = sonnet_by_id[sid].get("phase_score")
        if o_score is not None and s_score is not None:
            diff = abs(o_score - s_score)
            if diff >= divergence_threshold:
                divergent.append({
                    "scenario_id": sid,
                    "phase": opus_by_id[sid].get("phase", ""),
                    "opus_score": o_score,
                    "sonnet_score": s_score,
                    "delta": round(s_score - o_score, 4),
                })

    if not divergent:
        return "_No scenarios diverged by more than {:.0%}._".format(divergence_threshold)

    lines = [
        "| Scenario | Phase | Opus | Sonnet | Delta |",
        "|----------|-------|------|--------|-------|",
    ]
    for d in sorted(divergent, key=lambda x: abs(x["delta"]), reverse=True):
        lines.append(
            f"| {d['scenario_id']} | {d['phase']} | {_fmt(d['opus_score'], 4)} "
            f"| {_fmt(d['sonnet_score'], 4)} | {'+' if d['delta'] >= 0 else ''}{d['delta']:.4f} |"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_report(
    opus_scores: dict,
    sonnet_scores: dict,
    output_path: str,
) -> None:
    """
    Generate COMPARISON-REPORT.md.

    Args:
        opus_scores:   Dict with keys 'muster', 'pax', 'forge' (lists of scored result dicts)
                       and 'composite' (output of compute_composite()),
                       and 'raw_results' (original result JSONs for cost/latency).
        sonnet_scores: Same structure for Sonnet model.
        output_path:   Absolute path to write the markdown file.
    """
    opus_muster = opus_scores.get("muster", [])
    opus_pax = opus_scores.get("pax", [])
    opus_forge = opus_scores.get("forge", [])
    opus_all = opus_muster + opus_pax + opus_forge

    sonnet_muster = sonnet_scores.get("muster", [])
    sonnet_pax = sonnet_scores.get("pax", [])
    sonnet_forge = sonnet_scores.get("forge", [])
    sonnet_all = sonnet_muster + sonnet_pax + sonnet_forge

    opus_comp = opus_scores.get("composite", {})
    sonnet_comp = sonnet_scores.get("composite", {})

    tolerance = within_tolerance(opus_comp, sonnet_comp)
    outcome_id, outcome_label = _determine_recommendation(sonnet_comp, tolerance)

    # Cost savings for full downgrade recommendation
    opus_raw = opus_scores.get("raw_results", opus_all)
    sonnet_raw = sonnet_scores.get("raw_results", sonnet_all)
    cost_estimate = _cost_savings_estimate(opus_raw, sonnet_raw)

    lines: list[str] = []

    # Header
    lines.append("# Gold Agent Evaluation — Comparison Report")
    lines.append("")
    lines.append(
        "This report compares Opus vs Sonnet performance on the Gold agent evaluation "
        "harness across Muster, Pax, and Forge phases."
    )
    lines.append("")

    # Phase summary
    lines.append("## Phase Summary")
    lines.append("")
    lines.append(_phase_summary_table(opus_comp, sonnet_comp, tolerance))
    lines.append("")

    # Per-phase dimension tables
    for phase_display, phase_key, scored_list_pair in [
        ("Muster", "muster", (opus_muster, sonnet_muster)),
        ("Pax", "pax", (opus_pax, sonnet_pax)),
        ("Forge", "forge", (opus_forge, sonnet_forge)),
    ]:
        opus_list, sonnet_list = scored_list_pair
        lines.append(f"## {phase_display} Phase — Per-Dimension Scores")
        lines.append("")
        lines.append(_dimension_table(opus_list, sonnet_list, phase_key))
        lines.append("")

    # Cost and latency
    lines.append("## Cost and Latency Comparison")
    lines.append("")
    lines.append(_cost_latency_table(opus_raw, sonnet_raw))
    lines.append("")

    # Divergence detail
    lines.append("## Per-Scenario Divergence (|delta| >= 0.15)")
    lines.append("")
    lines.append(_divergence_section(opus_all, sonnet_all))
    lines.append("")

    # Human review queue
    lines.append("## Items Pending Human Review")
    lines.append("")
    all_human_items: list[dict] = []
    for r in sonnet_all:
        for hr in r.get("needs_human_review", []):
            all_human_items.append({"scenario_id": r.get("scenario_id"), "phase": r.get("phase"), **hr})

    if not all_human_items:
        lines.append("_No items pending human review._")
    else:
        for hr in all_human_items:
            lines.append(
                f"- **{hr.get('item_id', '')}** "
                f"(scenario: {hr.get('scenario_id', 'N/A')}, phase: {hr.get('phase', 'N/A')}): "
                f"{hr.get('auto_human_split', '')}"
            )
    lines.append("")

    # Recommendation
    lines.append("## Recommendation")
    lines.append("")
    lines.append(_phase_summary_table(opus_comp, sonnet_comp, tolerance))
    lines.append("")

    # Per-phase pass/fail sentences
    phases_info = {
        "Muster": ("muster", PHASE_THRESHOLDS["muster"]),
        "Pax": ("pax", PHASE_THRESHOLDS["pax"]),
        "Forge": ("forge", PHASE_THRESHOLDS["forge"]),
    }
    for phase_display, (phase_key, threshold) in phases_info.items():
        score = sonnet_comp["per_phase"][phase_key]["score"]
        passes = sonnet_comp["per_phase"][phase_key].get("passes")
        tol_data = tolerance["phases"].get(phase_key, {})
        in_tol = tol_data.get("within_tolerance")
        delta = tol_data.get("delta")
        lines.append(
            f"**{phase_display}**: Sonnet score {_fmt(score, 4)} vs threshold {threshold} — "
            f"{'PASS' if passes else 'FAIL'}. "
            f"Delta from Opus: {('+' if delta and delta >= 0 else '') + _fmt(delta, 4)} "
            f"(tolerance band ±0.05 — {'within' if in_tol else 'outside'})."
        )
    lines.append("")

    composite_score = sonnet_comp.get("composite_score")
    composite_passes = sonnet_comp.get("composite_passes")
    comp_delta = tolerance.get("composite", {}).get("delta")
    comp_in_tol = tolerance.get("composite", {}).get("within_tolerance")
    lines.append(
        f"**Composite**: Sonnet score {_fmt(composite_score, 4)} vs threshold {COMPOSITE_THRESHOLD} — "
        f"{'PASS' if composite_passes else 'FAIL'}. "
        f"Delta from Opus: {('+' if comp_delta and comp_delta >= 0 else '') + _fmt(comp_delta, 4)} "
        f"(tolerance band ±0.03 — {'within' if comp_in_tol else 'outside'})."
    )
    lines.append("")

    # Conclusion
    lines.append(
        f"Sonnet {'meets' if outcome_id != 'keep_opus' else 'does not meet'} threshold. "
        f"**Recommendation: {outcome_label}.**"
    )
    lines.append("")

    if outcome_id == "full_sonnet_downgrade":
        lines.append(f"**Cost savings estimate**: {cost_estimate}")
        lines.append("")
        lines.append(
            "Flag for re-evaluation after any major protocol change or model update."
        )
    elif outcome_id == "partial_downgrade_muster_only":
        lines.append(
            "Use Sonnet for Muster phase only; keep Opus for Pax and Forge."
        )
    elif outcome_id == "partial_downgrade_forge_only":
        lines.append(
            "Use Sonnet for Forge phase only; keep Opus for Muster and Pax. "
            "Forge activates only when Howlers fail; cost savings are scenario-dependent."
        )
    elif outcome_id == "partial_downgrade_muster_forge":
        lines.append(
            "Use Sonnet for Muster and Forge; keep Opus for Pax. "
            "This is the predicted outcome based on PLAN.md Section 7 analysis. "
            "Pax's 'green but wrong' detection is the highest-risk Sonnet downgrade scenario."
        )
    else:
        lines.append(
            "Keep Opus as Gold for all phases. "
            "Re-evaluate after 90 days or after a significant model update."
        )
    lines.append("")

    # Write file
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
