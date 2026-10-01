#!/usr/bin/env python3
"""Build the GitHub activity card (dark and light) from the GitHub GraphQL API.

Usage: GH_TOKEN=... python3 tools/build_activity.py <out_dir> [login]
The profile workflow runs this every day and publishes the files to the `output` branch.
"""
import datetime as dt
import json
import os
import pathlib
import sys
import urllib.request
from xml.sax.saxutils import escape

LOGIN = sys.argv[2] if len(sys.argv) > 2 else "umer-bytefinch"
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
MAX_WEEKS = 26

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, sans-serif"

QUERY = """query($login: String!) { user(login: $login) { contributionsCollection {
  totalCommitContributions totalPullRequestContributions totalPullRequestReviewContributions
  totalIssueContributions
  contributionCalendar { totalContributions weeks { firstDay contributionDays { contributionCount } } }
} } }"""

THEMES = {
    "dark": dict(card="#0f1a30", stroke="#1e2d4f", text="#f1f5f9", muted="#94a3b8", faint="#64748b",
                 grid="#1e2d4f", bar="#3b82f6", accent="#fbbf24"),
    "light": dict(card="#ffffff", stroke="#e2e8f0", text="#1a2a4a", muted="#475569", faint="#64748b",
                  grid="#e2e8f0", bar="#2563eb", accent="#f59e0b"),
}


def fetch():
    token = os.environ["GH_TOKEN"]
    body = json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body,
                                 headers={"Authorization": f"bearer {token}", "User-Agent": LOGIN})
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    return data["data"]["user"]["contributionsCollection"]


def weekly(cc):
    weeks = [(w["firstDay"], sum(d["contributionCount"] for d in w["contributionDays"]))
             for w in cc["contributionCalendar"]["weeks"]]
    first = next((i for i, (_, n) in enumerate(weeks) if n > 0), len(weeks) - 1)
    weeks = weeks[first:]
    return weeks[-MAX_WEEKS:]


def nice_max(v):
    for step in (5, 10, 20, 25, 50, 100, 200, 250, 500, 1000):
        if v <= step * 4:
            return step * 4, step
    return v, v // 4


def card(T, cc, weeks):
    W, H = 1200, 420
    kpis = [
        (cc["contributionCalendar"]["totalContributions"], "contributions", "in the last year"),
        (cc["totalCommitContributions"], "commits", "pushed"),
        (cc["totalPullRequestContributions"], "pull requests", "opened"),
        (cc["totalPullRequestReviewContributions"], "code reviews", "given"),
    ]
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="GitHub activity: {kpis[0][0]} contributions, {kpis[1][0]} commits, {kpis[2][0]} pull requests, '
         f'{kpis[3][0]} code reviews in the last year">\n<title>GitHub activity</title>\n<style>\n'
         f"text{{font-family:{SANS};}}\n"
         "@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}\n"
         ".fu{opacity:0;animation:fadeUp .8s cubic-bezier(.2,.7,.2,1) forwards;}\n"
         "@keyframes rise{from{transform:scaleY(0)}to{transform:scaleY(1)}}\n"
         ".bar{transform-box:fill-box;transform-origin:center bottom;transform:scaleY(0);"
         "animation:rise .9s cubic-bezier(.2,.7,.2,1) forwards;}\n</style>\n")
    s += (f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="{T["card"]}" '
          f'stroke="{T["stroke"]}" stroke-width="1.5"/>\n')
    # KPI row
    for i, (num, label, sub) in enumerate(kpis):
        x = 40 + i * 290
        s += (f'<g class="fu" style="animation-delay:{i * .12:.2f}s">'
              f'<text x="{x}" y="78" font-size="46" font-weight="800" fill="{T["text"]}">{num:,}</text>'
              f'<text x="{x}" y="106" font-size="18" font-weight="600" fill="{T["muted"]}">{label} '
              f'<tspan fill="{T["faint"]}" font-weight="400">{sub}</tspan></text></g>')
        if i:
            s += f'<rect x="{x - 24}" y="44" width="1.5" height="66" fill="{T["grid"]}"/>'
    # chart
    left, right, top, base = 88, W - 40, 170, H - 70
    top_v, step = nice_max(max(n for _, n in weeks) or 1)
    s += (f'<text x="40" y="146" font-size="16" font-weight="700" fill="{T["text"]}">Contributions per week'
          f'<tspan fill="{T["faint"]}" font-weight="400">  ·  since {weeks[0][0]}</tspan></text>')
    for k in range(0, 5):
        v = step * k
        y = base - (base - top) * v / top_v
        s += (f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="{T["grid"]}" '
              f'stroke-width="{1.5 if k == 0 else 1}"{"" if k == 0 else " stroke-dasharray=\"3 5\""}/>'
              f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-size="13" fill="{T["faint"]}">{v}</text>')
    n = len(weeks)
    slot = (right - left) / n
    bw = min(44, slot * 0.62)
    peak = max(range(n), key=lambda i: weeks[i][1])
    for i, (day, v) in enumerate(weeks):
        cx = left + slot * (i + 0.5)
        h = (base - top) * v / top_v
        if v:
            h = max(h, 4)
            r = min(4, bw / 2, h / 2)
            x0, y0 = cx - bw / 2, base - h
            path = (f"M{x0:.1f} {base}V{y0 + r:.1f}Q{x0:.1f} {y0:.1f} {x0 + r:.1f} {y0:.1f}"
                    f"H{x0 + bw - r:.1f}Q{x0 + bw:.1f} {y0:.1f} {x0 + bw:.1f} {y0 + r:.1f}V{base}Z")
            s += (f'<path d="{path}" fill="{T["bar"]}" class="bar" style="animation-delay:{.3 + i * .06:.2f}s">'
                  f'<title>Week of {day}: {v} contributions</title></path>')
        if i == peak and v:
            s += (f'<g class="fu" style="animation-delay:{.9 + n * .06:.2f}s">'
                  f'<text x="{cx:.1f}" y="{base - h - 12:.1f}" text-anchor="middle" font-size="16" '
                  f'font-weight="700" fill="{T["text"]}">{v}</text></g>')
        d = dt.date.fromisoformat(day)
        if i % max(1, n // 7) == 0 or i == n - 1:
            s += (f'<text x="{cx:.1f}" y="{base + 24}" text-anchor="middle" font-size="13" fill="{T["faint"]}">'
                  f'{d.strftime("%b")} {d.day}</text>')
    today = dt.date.today().isoformat()
    s += (f'<text x="{right}" y="{H - 18}" text-anchor="end" font-size="12" fill="{T["faint"]}">'
          f'updated {today} · built by a GitHub Action from the GraphQL API</text>')
    s += "</svg>\n"
    return s


def main():
    cc = fetch()
    weeks = weekly(cc)
    OUT.mkdir(parents=True, exist_ok=True)
    for mode, T in THEMES.items():
        (OUT / f"activity-{mode}.svg").write_text(card(T, cc, weeks))
    print("wrote activity cards to", OUT)


if __name__ == "__main__":
    main()
