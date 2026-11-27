"""Builds the framed section panels (assets/s-*.svg) in the personnel-file style.

Edit the data lists below and rerun. The daily workflow also reruns it so release
versions stay current. Env: GITHUB_TOKEN (optional, only for release lookups).
"""
import json
import os
import random
import urllib.request
from html import escape

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
RED = "#E8112D"

PRODUCTS = [  # key, code, category, name, description lines, tags, repo for latest release (or label)
    ("3bcad", "P-01", "cad // rust", "3BCAD",
     ["Open-source parametric 3D CAD in Rust, with assemblies", "and a built-in 3D-print studio."],
     "rust / open source / product hunt", "Three-Bugs-Studio/3bcad"),
    ("3binfra", "P-02", "notebook", "3B Infrastructure",
     ["A hand-drawn notebook on system architecture,", "databases and software engineering courses."],
     "system design / databases", "read"),
    ("pudo", "P-03", "ai workflow", "PUDO",
     ["Plan, Understand, Develop, Optimize. A four-step", "workflow for building software with AI agents."],
     "typescript / ai agents", "DongDuong2001/pudo-code-system"),
    ("3beditor", "P-04", "claude code plugin", "3beditor",
     ["Edits raw clips into TikTok, Reels and", "Shorts videos."],
     "python / video", "Three-Bugs-Studio/3beditor"),
    ("workspace", "P-05", "studio tools", "Workspace",
     ["An open-source workspace for software studios", "and their clients."],
     "typescript / open source", "source"),
]
WORK = [  # key, code, name, role, description lines, meta
    ("phitruong", "W-01", "random.phitruong", "full-stack",
     ["Shop and order site for a Vietnamese sukajan", "jacket studio: catalogue, cart, order requests."], "live // sukajan"),
    ("h1t", "W-02", "H1T MICRO", "solution architect, backend",
     ["Nutrition and micronutrient platform.", "Next.js + Go, Supabase, PayOS."], "2,500+ users"),
    ("luvcraft", "W-03", "Luvcraft", "technical lead",
     ["RMIT capstone with industry partner Project Pluto.", "AI fandom intelligence and brand-IP matching."], "rmit capstone"),
]
LOG = [("2026-11-17", "3BCAD v1.2.0 released"),
       ("2026-11-06", "H1T MICRO passes 2,500 users"),
       ("2026-09-22", "Luvcraft final report submitted (tech lead, Team Nightswatch)")]
STACK = [("daily", ["typescript", "rust", "go", "postgres", "supabase", "next.js", "docker", "linux"]),
         ("also", ["java", "python", "spring boot", "fastapi", "flutter", "github actions"])]
RULES = [("R-01", "Build the simple version before the scalable one."),
         ("R-02", "Design the API and the schema around how people actually use the thing."),
         ("R-03", "AI writes code with me, not instead of knowing how.")]

HEAD = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">
<defs>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#0e0e0e"/></pattern>
<style>
.m{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;letter-spacing:.14em;text-transform:uppercase}}
.s{{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif}}
</style>
</defs>
"""


def m(x, y, size, text, fill, extra=""):
    return f'<text x="{x}" y="{y}" class="m" font-size="{size}" fill="{fill}"{extra}>{escape(text)}</text>'


def s(x, y, size, text, fill, extra=""):
    return f'<text x="{x}" y="{y}" class="s" font-size="{size}" fill="{fill}"{extra}>{escape(text)}</text>'


def mono_w(text, size):  # rough width of .m text, for layout only
    return len(text) * size * 0.74


def frame(w, h, c=16):
    p = f"M{c} 0H{w}V{h-c}L{w-c} {h}H0V{c}Z"
    return (f'<clipPath id="c"><path d="{p}"/></clipPath><path d="{p}" fill="#050505"/>'
            f'<rect width="{w}" height="{h}" fill="url(#scan)" clip-path="url(#c)"/>'
            f'<path d="{p}" fill="none" stroke="#1c1c1c" stroke-width="2"/>'
            f'<path d="M{w-24} {h-6}H{w-6-c//2}M{w-6} {h-24}V{h-6-c//2}" stroke="{RED}" stroke-width="2"/>')


def barcode(x, y, w, h, seed):
    r, cx, out = random.Random(seed), x, []
    while cx < x + w:
        bw = r.choice([1, 1, 2, 3])
        out.append(f'<rect x="{cx}" y="{y}" width="{bw}" height="{h}"/>')
        cx += bw + r.choice([1, 2, 3])
    return '<g fill="#8a8a8a">' + "".join(out) + "</g>"


def tag(x, y, code):
    w = mono_w(code, 13) + 22
    return f'<path d="M{x+8} {y}H{x+w}V{y+26}H{x}V{y+8}Z" fill="{RED}"/>' + m(x + 11, y + 18, 13, code, "#050505", ' font-weight="800"'), w


def write(name, w, h, label, body):
    with open(os.path.join(OUT, f"{name}.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(HEAD.format(w=w, h=h, label=escape(label)) + body + "\n</svg>\n")


def latest(repo_or_label):
    if "/" not in repo_or_label:
        return repo_or_label
    req = urllib.request.Request(f"https://api.github.com/repos/{repo_or_label}/releases/latest",
                                 headers={"User-Agent": "profile-sections", "Accept": "application/vnd.github+json"})
    if os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)["tag_name"]
    except Exception:
        return "repo"  # no release yet or API down; still a sensible label


def part_drawing():
    """Isometric block with a bore and dimensions, a nod to 3BCAD."""
    return (f'<g fill="none"><path d="M960 52L1050 102L960 152L870 102Z M870 102V172L960 222L1050 172V102 M960 152V222" stroke="#cfcfcf" stroke-width="1.6"/>'
            f'<path d="M960 52V122L870 172M960 122L1050 172" stroke="#444" stroke-dasharray="4 4"/>'
            f'<ellipse cx="960" cy="102" rx="30" ry="17" stroke="{RED}" stroke-width="2"/>'
            f'<path d="M846 102V172M840 102H852M840 172H852M972 238L1062 188M968 232L976 244M1058 182L1066 194" stroke="{RED}" stroke-width="1.4"/></g>'
            + m(834, 142, 11, "40.00", RED, ' text-anchor="end"') + m(1074, 228, 11, "60.00", RED) + m(1066, 92, 11, "Ø24", RED))


def product(p, wide):
    key, code, cat, name, lines, tags, rel = p
    w, h = (1200, 260) if wide else (600, 250)
    t, tw = tag(28, 26, code)
    edge = 780 if wide else w - 28
    b = [frame(w, h), t, m(28 + tw + 14, 44, 13, cat, "#888"),
         barcode(edge - 64, 26, 64, 22, key),
         f'<path d="M28 68H{edge}" stroke="#2c2c2c"/><rect x="28" y="66" width="40" height="4" fill="{RED}"/>',
         s(26, 120, 36, name.upper(), "#f4f4f4", ' font-weight="800" letter-spacing=".5"')]
    b += [s(28, 158 + i * 25, 18, ln, "#9a9a9a") for i, ln in enumerate(lines)]
    b += [m(28, h - 28, 12, tags, "#6a6a6a"), m(edge, h - 28, 13, f"{latest(rel)} ->", RED, ' font-weight="700" text-anchor="end"')]
    if wide:
        b.append(part_drawing())
    write(f"s-p-{key}", w, h, f"{code} {name}: {' '.join(lines)}", "".join(b))


def work(wk):
    key, code, name, role, lines, meta = wk
    w, h = 1200, 150
    b = [frame(w, h),
         f'<path d="M16 0H104V150H0V16Z" fill="{RED}"/>',
         m(52, 70, 13, code[:1], "#050505", ' font-weight="800" text-anchor="middle"'),
         f'<text x="52" y="108" class="s" font-size="40" font-weight="800" fill="#050505" text-anchor="middle">{code[2:]}</text>',
         s(132, 70, 34, name.upper(), "#f4f4f4", ' font-weight="800"'),
         m(134, 106, 14, "role //", "#6a6a6a"), m(226, 106, 14, role, RED, ' font-weight="700"'),
         '<path d="M640 34V116" stroke="#2c2c2c"/>']
    b += [s(668, 62 + i * 26, 18, ln, "#bdbdbd") for i, ln in enumerate(lines)]
    b += [m(668, 120, 12, meta, "#777"), barcode(1100, 100, 60, 18, key)]
    write(f"s-w-{key}", w, h, f"{code} {name}, {role}: {' '.join(lines)}", "".join(b))


def log():
    w, h = 1200, 60 + len(LOG) * 50
    b = [frame(w, h), f'<path d="M222 40V{h-40}" stroke="#2c2c2c" stroke-width="2"/>']
    for i, (d, text) in enumerate(LOG):
        y = 60 + i * 50
        b += [m(48, y + 6, 14, d, RED if i == 0 else "#777", ' font-weight="700"'),
              f'<rect x="216" y="{y-6}" width="12" height="12" fill="{RED if i == 0 else "#050505"}" stroke="{RED}" stroke-width="2"/>',
              s(256, y + 7, 20, text, "#f4f4f4" if i == 0 else "#bdbdbd")]
    write("s-log", w, h, "Log: " + "; ".join(f"{d} {t}" for d, t in LOG), "".join(b))


def stack():
    w, h = 1200, 44 + len(STACK) * 58
    b = [frame(w, h)]
    for i, (label, items) in enumerate(STACK):
        y = 34 + i * 58
        b.append(m(48, y + 26, 12, label, RED if i == 0 else "#777", ' font-weight="700"'))
        x = 168
        for it in items:
            cw = mono_w(it, 14) + 26
            b += [f'<path d="M{x+6} {y}H{x+cw}V{y+38}H{x}V{y+6}Z" fill="#0c0c0c" stroke="{"#4a0710" if i == 0 else "#2a2a2a"}" stroke-width="1.5"/>',
                  m(x + 13, y + 24, 14, it, "#e6e6e6" if i == 0 else "#a8a8a8", ' font-weight="700"')]
            x += cw + 10
    write("s-stack", w, h, "Stack. " + ". ".join(f"{l}: {', '.join(it)}" for l, it in STACK), "".join(b))


def rules():
    w, h = 1200, 40 + len(RULES) * 64
    b = [frame(w, h)]
    for i, (code, text) in enumerate(RULES):
        y = 24 + i * 64
        t, _ = tag(40, y + 10, code)
        b += [t, s(150, y + 31, 22, text, "#f4f4f4")]
        if i < len(RULES) - 1:
            b.append(f'<path d="M40 {y+58}H1160" stroke="#1c1c1c"/>')
    write("s-rules", w, h, "Rules. " + " ".join(f"{c}: {t}" for c, t in RULES), "".join(b))


def listed():
    """Label strip above the Unikorn badge table (the badges themselves are external images)."""
    w, h = 1200, 56
    t, tw = tag(24, 15, "listed on")
    b = [frame(w, h, 12), t, m(24 + tw + 16, 33, 13, "unikorn.vn // vietnamese product directory", "#888"),
         f'<path d="M{24 + tw + 16 + mono_w("unikorn.vn // vietnamese product directory", 13):.0f} 28H1080" stroke="#2c2c2c"/>',
         barcode(1096, 18, 72, 20, "unikorn")]
    write("s-listed", w, h, "Listed on Unikorn.vn", "".join(b))


if __name__ == "__main__":
    for i, p in enumerate(PRODUCTS):
        product(p, wide=(i == 0))
    for wk in WORK:
        work(wk)
    log(), stack(), rules(), listed()
    print("sections written")
