# AIP World Cup League 2026 🏆

An auto-updating World Cup sweepstake for everyone at AIP. **12 managers** drafted
**4 teams each** — all 48 World Cup teams are owned, so every single match is a
duel between two managers.

**Scoring (per team):** win = **+3**, draw = **+1**, loss = **0**.

## Managers
Daniele · Herlyn · Htoo · Jack · Jeff · Kate · Ken · Marco · Max · Nisha · Seth · Will
(rosters live in `update_scores.py`).

## How it works
- **`update_scores.py`** — zero-dependency Python. Resolves each manager's team
  names to football-data.org IDs, scores everyone, builds the league table,
  group tables, feeds, top scorers and a lead-over-time timeline, and writes
  **`data.json`**.
- **`index.html`** — the static page: leaderboard, league table, manager cards,
  lead-tracker chart, all 12 group tables, results + upcoming feeds, Golden Boot
  and curiosities. Reads `data.json`, auto-refreshes every 5 min. No API key in
  the browser.
- A **GitHub Actions** workflow runs the updater **3× a day** (~08:00 / 16:00 /
  00:00 Bangkok) and commits `data.json`, so GitHub Pages republishes — fully
  hands-off, 24/7, laptop independent.

## API key
Read from the `FOOTBALL_DATA_API_KEY` env var, or git-ignored `apikey.txt`
locally. In GitHub it's the repo secret `FOOTBALL_DATA_API_KEY`. The public repo
never contains the key.

## Files
- `index.html` — the page
- `update_scores.py` — the updater
- `data.json` — generated standings
- `gen_og.py` / `og.png` — link-preview image (run once)
- `apikey.txt` — your key (git-ignored, local only)
