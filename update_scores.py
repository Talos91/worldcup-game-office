#!/usr/bin/env python3
"""Office World Cup league updater — 12 managers, 4 teams each, all 48 WC teams.

Resolves each manager's team names to football-data IDs, scores every manager
(+3 win / +1 draw / -1 loss per team), and writes data.json for the static page.
Pure Python standard library. Key from FOOTBALL_DATA_API_KEY env var or apikey.txt.
"""
import json
import os
import sys
import unicodedata
import urllib.request
import urllib.error
from datetime import datetime, timezone

COMPETITION = "WC"
API_BASE = "https://api.football-data.org/v4"
API_URL = f"{API_BASE}/competitions/{COMPETITION}/matches"
WIN, DRAW, LOSS = 3, 1, 0  # office rule: a loss counts 0 (not -1)
VERSION = "1.5"  # bump on every code push; shown in the page footer (via data.json)
COUNTED_STATUSES = ("FINISHED", "AWARDED")

# Each manager picked 4 teams (by name). Colours chosen to read on the dark theme.
PLAYERS = [
    {"name": "Daniele", "color": "#2ee06a", "teams": ["Brazil", "Curacao", "New Zealand", "Norway"]},
    {"name": "Herlyn",  "color": "#ff5d8f", "teams": ["Cape Verde", "Czechia", "Germany", "South Korea"]},
    {"name": "Htoo",    "color": "#3da5ff", "teams": ["Colombia", "DR Congo", "Portugal", "Saudi Arabia"]},
    {"name": "Jack",    "color": "#ff9f1c", "teams": ["Haiti", "Morocco", "Netherlands", "Switzerland"]},
    {"name": "Jeff",    "color": "#a06bff", "teams": ["Bosnia & Herzegovina", "England", "Ghana", "Tunisia"]},
    {"name": "Kate",    "color": "#ff6fc8", "teams": ["Belgium", "Egypt", "Iraq", "Uruguay"]},
    {"name": "Ken",     "color": "#ffd23b", "teams": ["Austria", "Canada", "Croatia", "Qatar"]},
    {"name": "Marco",   "color": "#18c6b8", "teams": ["Argentina", "Panama", "Paraguay", "Uzbekistan"]},
    {"name": "Max",     "color": "#6c8cff", "teams": ["Cote d'Ivoire", "Senegal", "Turkiye", "United States"]},
    {"name": "Nisha",   "color": "#ff7a3d", "teams": ["Australia", "Ecuador", "Japan", "Mexico"]},
    {"name": "Seth",    "color": "#b5e853", "teams": ["Algeria", "Scotland", "Spain", "Sweden"]},
    {"name": "Will",    "color": "#4fd0e1", "teams": ["France", "Iran", "Jordan", "South Africa"]},
]
# Spelling fixes where the manager's name differs from football-data's name.
ALIASES = {"turkiye": "turkey", "dr congo": "congo dr", "cote d ivoire": "ivory coast"}


def load_api_key():
    key = os.environ.get("FOOTBALL_DATA_API_KEY")
    if key and key.strip():
        return key.strip()
    here = os.path.dirname(os.path.abspath(__file__))
    keyfile = os.path.join(here, "apikey.txt")
    if os.path.exists(keyfile):
        with open(keyfile, "r", encoding="utf-8") as f:
            k = f.read().strip()
        if k:
            return k
    raise SystemExit("No API key. Set FOOTBALL_DATA_API_KEY or create apikey.txt.")


def _headers():
    return {"X-Auth-Token": load_api_key(),
            "User-Agent": "worldcup-office/1.0 (+https://github.com)",
            "Accept": "application/json"}


def _get(url):
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_matches():
    return _get(API_URL).get("matches", [])


# ---- team-name resolution ----
def _norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = "".join(c if (c.isalnum() or c.isspace()) else " " for c in s.lower())
    return " ".join(s.split())


def index_teams(matches):
    teams = {}
    for m in matches:
        for s in (m["homeTeam"], m["awayTeam"]):
            tid = s.get("id")
            if tid and tid not in teams:
                teams[tid] = {"name": s.get("name"), "tla": s.get("tla"), "crest": s.get("crest")}
    by_norm, by_tok = {}, {}
    for tid, t in teams.items():
        if t["name"]:
            by_norm[_norm(t["name"])] = tid
            by_tok[frozenset(_norm(t["name"]).split())] = tid
    return teams, by_norm, by_tok


def resolve_team(name, by_norm, by_tok):
    n = ALIASES.get(_norm(name), _norm(name))
    if n in by_norm:
        return by_norm[n]
    toks = frozenset(n.split())
    if toks in by_tok:
        return by_tok[toks]
    sub = [tid for nn, tid in by_norm.items()
           if toks <= set(nn.split()) or set(nn.split()) <= toks]
    return sub[0] if len(sub) == 1 else None


# ---- per-team record ----
def team_record(team_id, matches):
    records, pts = [], 0
    w = d = l = 0
    for m in matches:
        home, away = m["homeTeam"], m["awayTeam"]
        if team_id not in (home.get("id"), away.get("id")):
            continue
        is_home = home.get("id") == team_id
        opp = away if is_home else home
        ft = m.get("score", {}).get("fullTime", {})
        gf = ft.get("home") if is_home else ft.get("away")
        ga = ft.get("away") if is_home else ft.get("home")
        status = m.get("status")
        winner = m.get("score", {}).get("winner")
        result, mpts = None, 0
        counted = status in COUNTED_STATUSES and winner is not None
        if counted:
            if winner == "DRAW":
                result, mpts = "D", DRAW
                d += 1
            elif (winner == "HOME_TEAM") == is_home:
                result, mpts = "W", WIN
                w += 1
            else:
                result, mpts = "L", LOSS
                l += 1
            pts += mpts
        records.append({
            "opponent": opp.get("name"), "opponentTla": opp.get("tla"), "opponentCrest": opp.get("crest"),
            "utcDate": m.get("utcDate"), "status": status, "stage": m.get("stage"), "group": m.get("group"),
            "isHome": is_home, "goalsFor": gf, "goalsAgainst": ga,
            "result": result, "points": mpts, "counted": counted,
        })
    records.sort(key=lambda r: r["utcDate"] or "")
    return records, pts, w, d, l


# ---- extra endpoints ----
def fetch_standings():
    try:
        return _get(f"{API_BASE}/competitions/{COMPETITION}/standings").get("standings", [])
    except Exception:
        return []


def build_standings(tracked):
    by_team, groups = {}, []
    for tbl in fetch_standings():
        if tbl.get("type") not in (None, "TOTAL"):
            continue
        group = tbl.get("group") or tbl.get("stage")
        table_out, has_tracked = [], False
        for r in tbl.get("table", []) or []:
            team = r.get("team") or {}
            tid = team.get("id")
            info = tracked.get(tid)
            row = {
                "position": r.get("position"), "name": team.get("name"), "tla": team.get("tla"),
                "crest": team.get("crest"), "played": r.get("playedGames"), "won": r.get("won"),
                "draw": r.get("draw"), "lost": r.get("lost"), "gf": r.get("goalsFor"),
                "ga": r.get("goalsAgainst"), "gd": r.get("goalDifference"), "points": r.get("points"),
                "owner": info["player"] if info else None, "color": info["color"] if info else None,
            }
            table_out.append(row)
            if info:
                has_tracked = True
                by_team[tid] = {k: row[k] for k in
                                ("position", "played", "won", "draw", "lost", "gf", "ga", "gd", "points")}
                by_team[tid]["group"] = group
        groups.append({"group": group, "hasTracked": has_tracked, "table": table_out})
    return by_team, groups


def fetch_coaches(tracked):
    try:
        data = _get(f"{API_BASE}/competitions/{COMPETITION}/teams")
    except Exception:
        return {}
    out = {}
    for t in data.get("teams", []):
        if t.get("id") in tracked:
            coach = t.get("coach") or {}
            if coach.get("name"):
                out[t["id"]] = {"name": coach.get("name"), "nationality": coach.get("nationality")}
    return out


def fetch_scorers(tracked, limit=40):
    url = f"{API_BASE}/competitions/{COMPETITION}/scorers?limit={limit}"
    try:
        data = _get(url)
    except Exception:
        return []
    out = []
    for s in data.get("scorers", []):
        team = s.get("team") or {}
        player = s.get("player") or {}
        info = tracked.get(team.get("id"))
        out.append({
            "name": player.get("name"), "goals": s.get("goals") or 0,
            "team": team.get("name"), "teamTla": team.get("tla"), "teamCrest": team.get("crest"),
            "owner": info["player"] if info else None, "color": info["color"] if info else None,
        })
    return out


# ---- feeds ----
def build_feeds(matches, tracked):
    recent, upcoming = [], []
    for m in matches:
        home, away = m["homeTeam"], m["awayTeam"]
        hid, aid = home.get("id"), away.get("id")
        if hid not in tracked and aid not in tracked:
            continue
        ft = m.get("score", {}).get("fullTime", {})
        gh, ga = ft.get("home"), ft.get("away")
        winner = m.get("score", {}).get("winner")
        status = m.get("status")
        counted = status in COUNTED_STATUSES and winner is not None
        sc = m.get("score", {})
        ht = sc.get("halfTime") or {}
        pen = sc.get("penalties") or {}
        ref = None
        for rr in (m.get("referees") or []):
            if rr.get("type") == "REFEREE":
                ref = {"name": rr.get("name"), "nationality": rr.get("nationality")}
                break
        stakes = []
        for tid, is_home in ((hid, True), (aid, False)):
            info = tracked.get(tid)
            if info:
                result, mpts = None, 0
                if counted:
                    if winner == "DRAW":
                        result, mpts = "D", DRAW
                    elif (winner == "HOME_TEAM") == is_home:
                        result, mpts = "W", WIN
                    else:
                        result, mpts = "L", LOSS
                stakes.append({"player": info["player"], "color": info["color"],
                               "team": info["team"], "isHome": is_home, "result": result, "points": mpts})
        entry = {
            "id": m.get("id"), "utcDate": m.get("utcDate"), "status": status,
            "stage": m.get("stage"), "group": m.get("group"),
            "home": {"name": home.get("name"), "tla": home.get("tla"), "crest": home.get("crest")},
            "away": {"name": away.get("name"), "tla": away.get("tla"), "crest": away.get("crest")},
            "scoreHome": gh, "scoreAway": ga,
            "htHome": ht.get("home"), "htAway": ht.get("away"),
            "duration": sc.get("duration"), "penHome": pen.get("home"), "penAway": pen.get("away"),
            "referee": ref, "stakes": stakes,
        }
        if counted or status in ("IN_PLAY", "PAUSED"):
            recent.append(entry)
        elif status in ("SCHEDULED", "TIMED"):
            upcoming.append(entry)
    recent.sort(key=lambda e: e["utcDate"] or "", reverse=True)
    upcoming.sort(key=lambda e: e["utcDate"] or "")
    return recent, upcoming


def build_timeline(matches, tracked):
    events = []
    for m in matches:
        winner = m.get("score", {}).get("winner")
        if m.get("status") not in COUNTED_STATUSES or winner is None:
            continue
        deltas = {}
        for team, is_home in ((m["homeTeam"], True), (m["awayTeam"], False)):
            info = tracked.get(team.get("id"))
            if not info:
                continue
            pts = DRAW if winner == "DRAW" else (WIN if (winner == "HOME_TEAM") == is_home else LOSS)
            deltas[info["player"]] = deltas.get(info["player"], 0) + pts
        if deltas:
            events.append((m.get("utcDate") or "", deltas))
    events.sort(key=lambda e: e[0])
    totals = {p["name"]: 0 for p in PLAYERS}
    tl = [{"date": None, "totals": dict(totals)}]
    for date, deltas in events:
        for n, v in deltas.items():
            totals[n] += v
        tl.append({"date": date, "totals": dict(totals)})
    return tl


def _ft(m):
    s = m.get("score", {}).get("fullTime", {})
    return s.get("home"), s.get("away")


def build_curiosities(matches, players_out):
    fin = [m for m in matches
           if m.get("status") in COUNTED_STATUSES and _ft(m)[0] is not None]
    cur = []
    played = len(fin)
    if played:
        goals = sum((_ft(m)[0] or 0) + (_ft(m)[1] or 0) for m in fin)
        cur.append({"icon": "⚽", "label": "Goals so far", "value": f"{goals} in {played} games"})
        cur.append({"icon": "\U0001F4CA", "label": "Goals per game", "value": f"{goals / played:.1f}"})

        def margin(m):
            h, a = _ft(m)
            return abs((h or 0) - (a or 0))

        bw = max(fin, key=margin)
        h, a = _ft(bw)
        if (h or 0) >= (a or 0):
            val = f'{bw["homeTeam"]["tla"]} {h}–{a} {bw["awayTeam"]["tla"]}'
        else:
            val = f'{bw["awayTeam"]["tla"]} {a}–{h} {bw["homeTeam"]["tla"]}'
        cur.append({"icon": "\U0001F4A5", "label": "Biggest win", "value": val})

        wg = max(fin, key=lambda m: (_ft(m)[0] or 0) + (_ft(m)[1] or 0))
        h, a = _ft(wg)
        cur.append({"icon": "\U0001F525", "label": "Wildest game",
                    "value": f'{wg["homeTeam"]["tla"]} {h}–{a} {wg["awayTeam"]["tla"]}'})

        draws = sum(1 for m in fin if m.get("score", {}).get("winner") == "DRAW")
        cur.append({"icon": "\U0001F91D", "label": "Draws so far", "value": str(draws)})

    if players_out:
        leader = min(players_out, key=lambda p: p["rank"])
        cur.append({"icon": "\U0001F451", "label": "Leading manager",
                    "value": f'{leader["name"]} ({leader["total"]:+d})'})
        top_scorer_mgr = max(players_out, key=lambda p: p["agg"]["gf"])
        cur.append({"icon": "\U0001F3AF", "label": "Most goals (manager)",
                    "value": f'{top_scorer_mgr["name"]} · {top_scorer_mgr["agg"]["gf"]}'})

        best = None
        for p in players_out:
            for t in p["teams"]:
                gd = sum((r["goalsFor"] or 0) - (r["goalsAgainst"] or 0) for r in t["matches"] if r["counted"])
                k = (t["points"], gd)
                if best is None or k > best[0]:
                    best = (k, t, p)
        if best:
            _, t, p = best
            cur.append({"icon": "⭐", "label": "Top team",
                        "value": f'{t["name"]} ({p["name"]}, {t["points"]:+d})'})
    return cur


KNOCKOUT_STAGES = {"LAST_32", "LAST_16", "ROUND_OF_16", "QUARTER_FINALS",
                   "SEMI_FINALS", "THIRD_PLACE", "FINAL"}


def team_status(team, knockout_started):
    """'champion' | 'out' (eliminated) | 'in' (still alive). Inferred from
    fixtures + group standings, erring toward 'in' to avoid false eliminations."""
    recs = team.get("matches", [])
    has_upcoming = any(r["status"] in ("SCHEDULED", "TIMED", "IN_PLAY", "PAUSED") for r in recs)
    finished = [r for r in recs if r["counted"]]
    if any(r.get("stage") == "FINAL" and r.get("result") == "W" for r in finished):
        return "champion"
    if has_upcoming or not finished:
        return "in"
    last = finished[-1]                       # most recent finished match
    if last.get("stage") in KNOCKOUT_STAGES:
        return "out"                          # knockout run ended, no next fixture
    g = team.get("group") or {}
    if g.get("position") and g.get("played", 0) >= 3 and g["position"] >= 4:
        return "out"                          # bottom of a completed group
    if knockout_started:
        return "out"                          # group team not in the started knockouts
    return "in"


def build_knockout(matches, tracked):
    """All knockout matches (R32 -> final) with owner tags + scores. Teams are
    empty until the draw is made; the page shows a provisional R32 field from the
    group tables until then, then this real bracket."""
    order = {"LAST_32": 1, "LAST_16": 2, "ROUND_OF_16": 2, "QUARTER_FINALS": 3,
             "SEMI_FINALS": 4, "THIRD_PLACE": 5, "FINAL": 6}
    out = []
    for m in matches:
        st = m.get("stage")
        if st not in KNOCKOUT_STAGES:
            continue
        sc = m.get("score", {})
        ft = sc.get("fullTime", {})
        pen = sc.get("penalties") or {}
        winner = sc.get("winner")
        counted = m.get("status") in COUNTED_STATUSES and winner is not None

        def side(team, is_home):
            info = tracked.get(team.get("id"))
            res = None
            if counted:
                res = "D" if winner == "DRAW" else ("W" if (winner == "HOME_TEAM") == is_home else "L")
            return {"name": team.get("name"), "tla": team.get("tla"), "crest": team.get("crest"),
                    "owner": info["player"] if info else None,
                    "color": info["color"] if info else None, "result": res}

        out.append({
            "stage": st, "order": order.get(st, 9), "utcDate": m.get("utcDate"),
            "status": m.get("status"), "home": side(m["homeTeam"], True), "away": side(m["awayTeam"], False),
            "scoreHome": ft.get("home"), "scoreAway": ft.get("away"),
            "penHome": pen.get("home"), "penAway": pen.get("away"),
        })
    out.sort(key=lambda e: (e["order"], e["utcDate"] or ""))
    return out


def build():
    matches = fetch_matches()
    teams, by_norm, by_tok = index_teams(matches)

    tracked = {}
    players_out = []
    for p in PLAYERS:
        teams_out = []
        total = 0
        for tname in p["teams"]:
            tid = resolve_team(tname, by_norm, by_tok)
            tinfo = teams.get(tid, {})
            disp = tinfo.get("name") or tname
            if tid:
                tracked[tid] = {"player": p["name"], "color": p["color"], "team": disp}
                recs, pts, w, d, l = team_record(tid, matches)
            else:
                recs, pts, w, d, l = [], 0, 0, 0, 0
                print(f"WARN: unresolved team '{tname}' ({p['name']})", file=sys.stderr)
            teams_out.append({"id": tid, "name": disp, "tla": tinfo.get("tla"), "crest": tinfo.get("crest"),
                              "points": pts, "w": w, "d": d, "l": l,
                              "group": None, "coach": None, "matches": recs})
            total += pts
        agg = {"played": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0}
        for t in teams_out:
            agg["w"] += t["w"]
            agg["d"] += t["d"]
            agg["l"] += t["l"]
            for r in t["matches"]:
                if r["counted"]:
                    agg["played"] += 1
                    agg["gf"] += r["goalsFor"] or 0
                    agg["ga"] += r["goalsAgainst"] or 0
        players_out.append({"name": p["name"], "color": p["color"], "total": total,
                            "agg": agg, "teams": teams_out})

    standings_by_team, groups = build_standings(tracked)
    coaches = fetch_coaches(tracked)
    for p in players_out:
        for t in p["teams"]:
            t["group"] = standings_by_team.get(t["id"])
            t["coach"] = coaches.get(t["id"])

    knockout_started = any(m.get("stage") in KNOCKOUT_STAGES and m.get("status") in COUNTED_STATUSES for m in matches)
    for p in players_out:
        for t in p["teams"]:
            t["status"] = team_status(t, knockout_started)
        p["alive"] = sum(1 for t in p["teams"] if t["status"] != "out")

    ranked = sorted(players_out, key=lambda x: (-x["total"], -x["agg"]["gf"], x["agg"]["ga"], x["name"]))
    for i, p in enumerate(ranked):
        p["rank"] = i + 1

    recent, upcoming = build_feeds(matches, tracked)
    scorers = fetch_scorers(tracked)
    timeline = build_timeline(matches, tracked)
    knockout = build_knockout(matches, tracked)
    curiosities = build_curiosities(matches, players_out)

    return {
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "version": VERSION,
        "competition": "FIFA World Cup 2026",
        "rules": {"win": WIN, "draw": DRAW, "loss": LOSS},
        "players": players_out,
        "groups": groups,
        "timeline": timeline,
        "knockout": knockout,
        "recent": recent,
        "upcoming": upcoming,
        "scorers": scorers,
        "curiosities": curiosities,
    }


def main():
    try:
        out = build()
    except urllib.error.HTTPError as e:
        print(f"HTTP error {e.code}: {e.read().decode('utf-8', 'ignore')}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "data.json")
    new_cmp = {k: v for k, v in out.items() if k != "updatedAt"}
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                old_cmp = {k: v for k, v in json.load(f).items() if k != "updatedAt"}
            if old_cmp == new_cmp:
                lead = min(out["players"], key=lambda p: p["rank"])
                print(f"No changes. Leader: {lead['name']} ({lead['total']:+d})")
                return
        except Exception:
            pass

    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    for p in sorted(out["players"], key=lambda x: x["rank"]):
        print(f"{p['rank']:>2}. {p['name']:<9} {p['total']:+d}")
    print(f"Wrote {path} at {out['updatedAt']}")


if __name__ == "__main__":
    main()
