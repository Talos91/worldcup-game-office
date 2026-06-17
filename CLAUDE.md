# CLAUDE.md — AIP World Cup League 2026 (a.k.a. the office league)

Working notes for Claude sessions. This is the **office** spin-off of the
Nicha-vs-Daniele tracker (`C:\Users\itisf\worldcup-game`), generalised from 2
players to **12 managers**.

## What this is
12 managers, 4 teams each, **all 48 World Cup teams owned**. Scoring +3 win /
+1 draw / **0 loss** per team (office rule — a loss does NOT subtract), summed per manager. Because every team is owned,
**every match is a two-manager duel** (feeds always show both owners).

## Architecture
- `update_scores.py` — stdlib only. Manager rosters are in `PLAYERS` (teams by
  **name**). Team names are resolved to football-data IDs at runtime via
  `resolve_team()` (accent/punct-insensitive + token-set match + `ALIASES` for
  Türkiye→Turkey, DR Congo→Congo DR, Côte d'Ivoire→Ivory Coast, Cape Verde→Cape
  Verde Islands handled by subset match). Writes `data.json`; only rewrites on a
  real change (ignores the timestamp).
- `data.json` keys: `players` (each with `rank`, `agg`, and 4 `teams` with
  `group` + `coach`), `groups` (all 12, owner-coloured), `timeline` (per-point
  `totals` map name→cumulative pts → the lead chart), `recent`/`upcoming`
  (matches carry half-time, referee, duration, both `stakes`), `scorers`,
  `curiosities`.
- `index.html` — leaderboard hero, league table, manager cards, N-line lead
  chart, group tables, feeds, Golden Boot, curiosities; confetti for the leader,
  countdown, OG tags. All client-side from `data.json`.
- Endpoints (free tier): `/matches`, `/standings`, `/teams` (coaches), `/scorers`.
  NOT used here: `/head2head` (every match is a clash → too many calls). NOT on
  free plan: venue, attendance, odds, per-match goalscorers.

## Automation
- **GitHub Actions** `.github/workflows/update.yml`, cron `7 1,9,17 * * *` UTC =
  **3×/day ~08:00 / 16:00 / 00:00 Bangkok**. Commits `data.json` → Pages redeploys.
- Hosting: GitHub Pages, public repo **github.com/Talos91/worldcup-game-office**.
  Needs repo secret `FOOTBALL_DATA_API_KEY`.
- `og.png` via `gen_og.py` (Pillow, run once, score-agnostic).

## Conventions
- Never commit `apikey.txt`. Don't hand-edit `data.json`.
- To change rosters/colours, edit `PLAYERS` in `update_scores.py`.
- Daniele's colour is green (`#2ee06a`) by request; others are distinct hues.
