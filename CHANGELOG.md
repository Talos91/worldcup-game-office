# Changelog

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
