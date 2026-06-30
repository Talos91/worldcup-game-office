# Changelog

## 2026-06-30 — v2.0
- **Fixed: knockout winners no longer flash "out".** A team that *won* its last
  knockout match (e.g. Brazil after its R32 win) now stays **alive** while the
  API assigns its next-round fixture — it was briefly mis-flagged as eliminated,
  which also wrongly listed it under "Knocked out" in The office report.
- **Group stage tidied away once the knockouts begin.** Group tables and the
  "Round of 32 — as it stands" predictor now disappear the moment a knockout
  match is played (or the full draw is set), leaving just the live bracket.
- Group tables also gained dimmed rows + an "out" tag for eliminated teams (for
  the brief window they're still shown during the group stage).

## 2026-06-26 — v1.8
- New **"The office report"** at the top: an auto-generated, fun commentary on
  the league (leader, standout results with manager names highlighted in their
  colours, who's been knocked out, who's bottom) — refreshed on every update.
- Slightly wider page (max-width 1180) + narrower bracket columns so the bracket
  fits without a horizontal scrollbar on desktop.

## 2026-06-25 — v1.7
- Confirmed qualifiers carry a **✓** in the "as it stands" board; the bracket
  fills progressively as the API assigns R32 slots, and only switches to the
  bracket-only view once the full draw is set (all 16 ties).

## 2026-06-25 — v1.5
- Knockout section now shows **both** during the group stage: the "Round of 32 —
  as it stands" qualifier board **and** the bracket tree (R32 → final, with
  dates). The bracket fills in real teams once the draw lands.

## 2026-06-25 — v1.4
- New **Knockout board**: provisional "Round of 32 — as it stands" (group
  winners, runners-up, and the live race for the 8 best 3rd-placed spots, all
  manager-coloured), auto-swapping to the live bracket (R32 → final) once the
  draw lands; group tables step aside then.

## 2026-06-18 — v1.3
- **Elimination visuals:** knocked-out teams dim out with an **OUT** tag, the
  champion gets a 🏆, and each manager card shows **teams alive** once any of
  theirs is out. Status inferred from fixtures + group tables (eliminated teams'
  points just freeze — no penalty).

## 2026-06-18 — v1.2
- Auto-update cron switched from 3×/day to **every 2 hours** (`7 */2 * * *`) so
  scores stay fresh despite GitHub's irregular scheduled-job timing.

## 2026-06-17 — v1.1
- Expanded "Did you know?" to **101 facts** (100 World Cup + one league fact).
- **Live version number** in the footer — stamped into data.json and shown as
  "v1.1 · Updated …" (never cache-stale). Bump `VERSION` in update_scores.py
  each code push.

## 2026-06-17 — v1.0 corrections
- Office scoring: a **loss now counts 0** (not −1). Win +3 / Draw +1 / Loss 0.
- Standings / manager cards show the **W-L-D record** (won-lost-drawn); actual
  scorelines stay in the Recent results feed.
- Added **legends** (P / W / D / L / GD / Pts, and the W-L-D record) and a
  **version number** (v1.0) in the footer.
- Renamed **Office League → AIP World Cup League** (title, header, link preview).

## 2026-06-17 — initial build (office league)
- Adapted the Nicha-vs-Daniele tracker to a **12-manager office league** (all 48
  World Cup teams owned).
- Manager team names resolved to football-data IDs dynamically (handles
  Türkiye/Turkey, DR Congo/Congo DR, Côte d'Ivoire/Ivory Coast, Cape Verde/Cape
  Verde Islands).
- New presentation for N managers: ranked **leaderboard** with bars, full
  **league table**, **manager cards** (4 teams each, colour-coded scorelines),
  **12-line lead-tracker** chart.
- Carried over: all 12 group tables (owner-coloured), results + upcoming feeds
  (every match shows both managers), Golden Boot (owner-coloured), curiosities,
  confetti for the leader, next-match countdown, Open Graph link preview.
- Colours: Daniele green (#2ee06a) by request; distinct hues for the rest.
- Auto-updates 3×/day (~08:00 / 16:00 / 00:00 Bangkok) via GitHub Actions.
