"""Builds assets/activity.svg: contributions, grade and committers.top rank, in the personnel-file style.

Runs daily from .github/workflows/activity.yml. Stdlib only.
Env: GITHUB_TOKEN (required), GH_USER (default DongDuong2001).
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request
from html import escape

USER = os.environ.get("GH_USER", "DongDuong2001")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "activity.svg")
RED = "#E8112D"
HEAT = ["#141414", "#4a0710", "#7a0b18", "#b00e22", RED]

QUERY = """query($login:String!){user(login:$login){
  followers{totalCount} pullRequests{totalCount} issues{totalCount}
  repositories(ownerAffiliations:OWNER,privacy:PUBLIC,isFork:false,first:100){nodes{stargazerCount}}
  contributionsCollection{totalCommitContributions totalPullRequestReviewContributions
    contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


def graphql():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "User-Agent": "profile-activity"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors") or not body.get("data", {}).get("user"):
        sys.exit(f"GraphQL error: {body.get('errors')}")  # keep yesterday's SVG rather than write a broken one
    return body["data"]["user"]


def vn_rank():
    """Rank in committers.top Vietnam (all contributions), or None while unranked or unreachable."""
    try:
        req = urllib.request.Request(f"https://user-badge.committers.top/vietnam_private/{USER}.svg",
                                     headers={"User-Agent": "profile-activity"})
        with urllib.request.urlopen(req, timeout=20) as r:
            title = re.search(r"<title>(.*?)</title>", r.read().decode("utf-8", "replace"))
    except Exception:
        return None
    m = title and re.search(r"#\s*(\d+)", title.group(1))
    return int(m.group(1)) if m else None


def grade(commits, prs, issues, reviews, stars, followers):
    """Same weights and medians as github-readme-stats calculateRank (last-year commits)."""
    exp = lambda x: 1 - 2 ** -x
    logn = lambda x: x / (1 + x)
    parts = [(2, exp(commits / 250)), (3, exp(prs / 50)), (1, exp(issues / 25)),
             (1, exp(reviews / 2)), (4, logn(stars / 50)), (1, logn(followers / 10))]
    pct = (1 - sum(w * v for w, v in parts) / sum(w for w, _ in parts)) * 100
    for t, lvl in zip([1, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100], ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C"]):
        if pct <= t:
            return lvl, pct
    return "C", pct


def streaks(days):
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    i = len(counts) - 1
    if counts and counts[i] == 0:  # today may simply not have started yet
        i -= 1
    current = 0
    while i >= 0 and counts[i]:
        current, i = current + 1, i - 1
    return current, longest


def heat_level(c, q):
    if not c:
        return 0
    return 1 + sum(c > x for x in q)


def build(u, rank, today):
    cc = u["contributionsCollection"]
    cal = cc["contributionCalendar"]
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    commits = cc["totalCommitContributions"]
    reviews = cc["totalPullRequestReviewContributions"]
    prs, issues = u["pullRequests"]["totalCount"], u["issues"]["totalCount"]
    stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
    followers = u["followers"]["totalCount"]
    lvl, pct = grade(commits, prs, issues, reviews, stars, followers)
    cur, longest = streaks(days)
    nz = sorted(d["contributionCount"] for d in days if d["contributionCount"])
    q = [nz[len(nz) * k // 4] for k in (1, 2, 3)] if nz else [0, 0, 0]

    m = lambda x, y, s, t, fill, extra="": f'<text x="{x}" y="{y}" class="m" font-size="{s}" fill="{fill}"{extra}>{t}</text>'
    b = [f'<path d="M18 0H1200V392L1182 410H0V18Z" fill="#050505"/><rect width="1200" height="410" fill="url(#scan)"/>',
         f'<rect x="24" y="22" width="236" height="28" fill="{RED}"/>',
         m(38, 41, 13, "activity // rank", "#050505", ' font-weight="700"'),
         m(1176, 41, 12, f"file 3B-000 &#160;//&#160; updated {today} utc", "#777", ' text-anchor="end"'),
         f'<path d="M24 50H1176" stroke="{RED}"/>',
         # headline
         m(56, 98, 12, "contributions // 12 mo", RED),
         f'<text x="52" y="162" class="s" font-size="64" font-weight="800" fill="#f4f4f4">{cal["totalContributions"]:,}</text>',
         m(56, 190, 11, "public + private, from the profile graph", "#5a5a5a")]
    for i, (k, v) in enumerate([("commits", commits), ("pull reqs", prs), ("issues", issues), ("reviews", reviews)]):
        x = 430 + i * 118
        b += [m(x, 98, 11, k, "#5a5a5a"), m(x, 128, 22, f"{v:,}", "#dcdcdc", ' font-weight="700"')]
    for i, (k, v) in enumerate([("streak", f"{cur} d"), ("longest", f"{longest} d")]):
        x = 430 + i * 118
        b += [m(x, 166, 11, k, "#5a5a5a"), m(x, 196, 22, v, "#dcdcdc", ' font-weight="700"')]
    if cur:  # live marker right after the current-streak value
        b.append(f'<rect x="{430 + len(f"{cur} d") * 16.4 + 10:.0f}" y="179" width="10" height="10" fill="{RED}" class="blink"/>')
    # grade + rank box, corner brackets like the banner
    b += [f'<g stroke="{RED}" stroke-width="2" fill="none"><path d="M904 86V72H930M1150 72H1176V86M1176 196V210H1150M930 210H904V196"/></g>',
          m(926, 102, 11, "grade", "#555"),
          f'<text x="922" y="172" class="s gl" font-size="64" font-weight="800" fill="{RED}">{escape(lvl)}</text>',
          f'<text x="922" y="172" class="s" font-size="64" font-weight="800" fill="#f4f4f4">{escape(lvl)}</text>',
          m(926, 196, 11, f"top {pct:.0f}%", RED),
          f'<path d="M1040 90V192" stroke="#2c2c2c"/>',
          m(1058, 102, 11, "vn rank", "#555"),
          m(1056, 150, 30 if rank else 26, f"#{rank}" if rank else "—", "#f4f4f4" if rank else "#5a5a5a", ' font-weight="800"'),
          m(1058, 176, 10, "committers.top", "#666"),
          m(1058, 196, 10, "all contribs" if rank else "at 48 followers", RED if rank else "#666")]
    # heatmap: last 53 weeks
    cells = []
    for wi, w in enumerate(weeks[-53:]):
        for d in w["contributionDays"]:
            wd = dt.date.fromisoformat(d["date"]).isoweekday() % 7
            cells.append(f'<rect x="{56 + wi * 16}" y="{238 + wd * 16}" width="13" height="13" '
                         f'fill="{HEAT[heat_level(d["contributionCount"], q)]}"/>')
    b += [m(56, 226, 11, "52 weeks", "#5a5a5a"), "".join(cells)]
    lx = 934
    b += [m(lx, 252, 11, "less", "#5a5a5a")] + [f'<rect x="{lx + 46 + i * 16}" y="242" width="13" height="13" fill="{c}"/>' for i, c in enumerate(HEAT)]
    b += [m(lx + 132, 252, 11, "more", "#5a5a5a"),
          m(lx, 296, 11, "best day", "#5a5a5a"),
          m(lx, 322, 18, f"{max((d['contributionCount'] for d in days), default=0):,}", "#dcdcdc", ' font-weight="700"'),
          m(lx + 120, 296, 11, "active", "#5a5a5a"),
          m(lx + 120, 322, 18, f"{sum(1 for d in days if d['contributionCount'])} d", "#dcdcdc", ' font-weight="700"')]
    b += [f'<rect x="24" y="378" width="300" height="10" fill="url(#haz)"/>',
          m(340, 387, 11, "grade: github-readme-stats formula &#160;//&#160; regenerated daily", "#666"),
          f'<g fill="{RED}"><rect x="1120" y="378" width="8" height="10"/><rect x="1134" y="378" width="8" height="10"/>'
          f'<rect x="1148" y="378" width="8" height="10"/><rect x="1162" y="378" width="14" height="10"/></g>']

    head = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 410" width="1200" height="410" role="img" aria-label="GitHub activity: {cal['totalContributions']:,} contributions in 12 months, grade {escape(lvl)}">
<defs>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#0e0e0e"/></pattern>
<pattern id="haz" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="8" height="16" fill="{RED}"/></pattern>
<style>
.m{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;letter-spacing:.14em;text-transform:uppercase}}
.s{{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif}}
.blink{{animation:bl 1.2s steps(1) infinite}}@keyframes bl{{50%{{opacity:0}}}}
.gl{{opacity:0;animation:gl 6s steps(1) infinite}}
@keyframes gl{{0%{{opacity:0}}91%{{opacity:.85;transform:translateX(-5px)}}92%{{opacity:0}}95%{{opacity:.7;transform:translateX(6px)}}96%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
</defs>
"""
    return head + "\n".join(x for x in b if x) + "\n</svg>\n"


if __name__ == "__main__":
    assert grade(0, 0, 0, 0, 0, 0)[0] == "C" and grade(10**5, 10**4, 10**4, 10**4, 10**6, 10**6)[0] == "S"
    assert streaks([{"contributionCount": c} for c in [1, 1, 0, 1, 1, 1, 0]]) == (3, 3)
    svg = build(graphql(), vn_rank(), dt.datetime.now(dt.timezone.utc).date().isoformat())
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print("wrote", os.path.normpath(OUT))
