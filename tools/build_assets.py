#!/usr/bin/env python3
"""Build the animated SVG assets of the profile README in a dark and a light version.

Run: python3 tools/build_assets.py  (writes assets/*.svg)
"""
import pathlib
import random
import re
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
LOGO_SRC = ROOT / "tools" / "bytefinch-icon.svg"

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', 'Courier New', monospace"

THEMES = {
    "dark": dict(
        bg0="#0b1120", bg1="#12203d", bg2="#1a2a4a",
        card="#0f1a30", card_stroke="#1e2d4f",
        text="#f1f5f9", muted="#94a3b8", faint="#64748b",
        blue="#3b82f6", blue_soft="#60a5fa", gold="#fbbf24",
        green="#4ade80", red="#f87171", purple="#a78bfa",
        logo="#f1f5f9", tint_op="0.16", pixel_op="0.55",
    ),
    "light": dict(
        bg0="#ffffff", bg1="#f1f5ff", bg2="#e3ecff",
        card="#ffffff", card_stroke="#e2e8f0",
        text="#1a2a4a", muted="#475569", faint="#64748b",
        blue="#2563eb", blue_soft="#3b82f6", gold="#f59e0b",
        green="#16a34a", red="#dc2626", purple="#7c3aed",
        logo="#1a2a4a", tint_op="0.10", pixel_op="0.45",
    ),
}


def logo_group():
    src = LOGO_SRC.read_text()
    m = re.search(r"<g[^>]*>(.*?)</g>", src, re.S)
    return m.group(1).strip()


LOGO_PATHS = logo_group()


def svg_open(w, h, title, extra_style=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(title)}">\n<title>{escape(title)}</title>\n'
        f"<style>\n"
        f"text{{font-family:{SANS};}}\n.mono{{font-family:{MONO};}}\n"
        "@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}\n"
        "@keyframes fadeIn{from{opacity:0}to{opacity:1}}\n"
        "@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}\n"
        "@keyframes twinkle{0%,100%{opacity:.12}50%{opacity:1}}\n"
        "@keyframes pulse{0%,100%{opacity:.35}50%{opacity:.9}}\n"
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}\n"
        ".fu{opacity:0;animation:fadeUp .9s cubic-bezier(.2,.7,.2,1) forwards;}\n"
        ".fi{opacity:0;animation:fadeIn .9s ease-out forwards;}\n"
        "@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}\n"
        ".grow{transform-box:fill-box;transform-origin:left center;transform:scaleX(0);"
        "animation:grow 1.1s cubic-bezier(.2,.7,.2,1) forwards;}\n"
        "@keyframes uncover{from{transform:scaleX(1)}to{transform:scaleX(0)}}\n"
        ".cover{transform-box:fill-box;transform-origin:right center;}\n"
        "@keyframes draw{to{stroke-dashoffset:0}}\n"
        f"{extra_style}</style>\n"
    )


def d(i, base=0.0, step=0.15):
    return f"animation-delay:{base + i * step:.2f}s"


def pill(x, y, label, color, T, size=16, filled=False, h=32):
    w = int(len(label) * size * 0.58 + 30)
    fill = color if filled else "none"
    txt = T["bg0"] if filled else color
    return (
        f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{fill}" '
        f'fill-opacity="{1 if filled else 0}" stroke="{color}" stroke-width="1.5"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{color}" fill-opacity="0.12"/>'
        f'<text x="{x + w/2}" y="{y + h/2 + size*0.36:.1f}" text-anchor="middle" font-size="{size}" '
        f'font-weight="600" fill="{txt}">{escape(label)}</text></g>',
        w,
    )


# ---------------------------------------------------------------- header

def header(T, mode):
    W, H = 1200, 400
    rnd = random.Random(7)
    s = svg_open(W, H, "Syed Umer Shah, Founder and CEO of ByteFinch Technologies")
    s += f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
 <stop offset="0" stop-color="{T['bg0']}"/><stop offset=".55" stop-color="{T['bg1']}"/><stop offset="1" stop-color="{T['bg2']}"/>
</linearGradient>
<radialGradient id="glow" cx=".5" cy=".5" r=".5">
 <stop offset="0" stop-color="{T['blue']}" stop-opacity=".55"/><stop offset=".6" stop-color="{T['blue']}" stop-opacity=".12"/><stop offset="1" stop-color="{T['blue']}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{T['blue']}"/><stop offset="1" stop-color="{T['gold']}"/></linearGradient>
<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".45" stop-color="#fff" stop-opacity=".25"/><stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient>
<mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
<clipPath id="round"><rect width="{W}" height="{H}" rx="28"/></clipPath>
</defs>
<g clip-path="url(#round)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
"""
    # pixel field (bytes), masked so that it fades out towards the text
    s += '<g mask="url(#m)">'
    for gx in range(560, 1190, 30):
        for gy in range(16, H - 10, 30):
            if rnd.random() < 0.38:
                col = T["gold"] if rnd.random() < 0.12 else T["blue"]
                size = rnd.choice([8, 10, 12])
                dur = rnd.uniform(2.4, 5.5)
                delay = rnd.uniform(0, 5)
                s += (f'<rect x="{gx}" y="{gy}" width="{size}" height="{size}" rx="2" fill="{col}" '
                      f'opacity="{T["pixel_op"]}" style="animation:twinkle {dur:.1f}s ease-in-out {delay:.1f}s infinite"/>')
    s += "</g>\n"

    # circuit traces with a travelling spark
    traces = [
        "M1200 70 H1080 V120 H990",
        "M1200 250 H1110 V200 H1020 V160",
        "M1200 330 H1060 V290 H960",
    ]
    for i, p in enumerate(traces):
        s += (f'<path d="{p}" fill="none" stroke="{T["blue"]}" stroke-opacity=".45" stroke-width="2"/>'
              f'<circle r="5" fill="{T["gold"]}"><animateMotion dur="{3.5 + i}s" repeatCount="indefinite" '
              f'path="{p}" keyPoints="0;1" keyTimes="0;1" calcMode="linear"/></circle>')
    # logo with glow and float
    s += f"""<circle cx="200" cy="200" r="175" fill="url(#glow)" style="animation:pulse 5s ease-in-out infinite"/>
<g style="animation:float 5s ease-in-out infinite">
 <svg x="60" y="60" width="280" height="280" viewBox="0 0 897 897">
  <g transform="translate(0,897) scale(0.1,-0.1)" fill="{T['logo']}">{LOGO_PATHS}</g>
 </svg>
</g>
"""
    # text block
    x = 372
    s += (f'<text x="{x}" y="118" font-size="18" font-weight="700" letter-spacing="5" fill="{T["blue"]}" '
          f'class="fu" style="{d(0, .1)}">HELLO, I AM</text>')
    s += (f'<text x="{x - 3}" y="190" font-size="70" font-weight="800" fill="{T["text"]}" '
          f'class="fu" style="{d(1, .1)}">Syed Umer Shah</text>')
    s += (f'<rect x="{x}" y="210" width="250" height="6" rx="3" fill="url(#bar)" class="grow" '
          f'style="animation-delay:.8s"/>')
    s += (f'<text x="{x}" y="262" font-size="29" font-weight="600" fill="{T["text"]}" class="fu" style="{d(3, .1)}">'
          f'Founder &amp; CEO, <tspan fill="{T["blue"]}" font-weight="700">ByteFinch Technologies</tspan></text>')
    cx = x
    chips = [("Full-stack engineer", T["blue"]), ("Node.js · TypeScript · React", T["blue"]),
             ("Lahore, Pakistan", T["gold"])]
    for i, (label, col) in enumerate(chips):
        g, w = pill(cx, 292, label, col, T, size=16)
        s += f'<g class="fu" style="{d(4 + i, .1, .12)}">{g}</g>'
        cx += w + 12
    s += (f'<text x="{x}" y="368" font-size="19" font-style="italic" font-weight="600" fill="{T["gold"]}" '
          f'class="fu" style="{d(8, .1, .12)}">Small bytes. Big builds.</text>')
    s += "</g></svg>\n"
    return s


# ---------------------------------------------------------------- section title

def section(T, title, sub):
    W, H = 1200, 96
    s = svg_open(W, H, title, extra_style="@keyframes run{0%{transform:translateX(0);opacity:0}10%{opacity:1}80%{opacity:1}100%{transform:translateX(1200px);opacity:0}}\n")
    s += f"""<defs><linearGradient id="ln" x1="0" x2="1">
<stop offset="0" stop-color="{T['blue']}"/><stop offset=".35" stop-color="{T['gold']}"/><stop offset="1" stop-color="{T['blue']}" stop-opacity="0"/>
</linearGradient></defs>
<g class="fi">
 <rect x="2" y="22" width="12" height="12" rx="2" fill="{T['blue']}"/>
 <rect x="18" y="22" width="12" height="12" rx="2" fill="{T['blue']}" opacity=".55"/>
 <rect x="2" y="38" width="12" height="12" rx="2" fill="{T['gold']}"/>
 <rect x="18" y="38" width="12" height="12" rx="2" fill="{T['blue']}" opacity=".25"/>
</g>
<text x="48" y="50" font-size="34" font-weight="800" fill="{T['text']}" class="fu" style="animation-delay:.05s">{escape(title)}</text>
<text x="1198" y="50" text-anchor="end" font-size="17" font-weight="500" fill="{T['faint']}" class="mono fi" style="animation-delay:.3s">{escape(sub)}</text>
<rect x="0" y="76" width="1200" height="3" rx="1.5" fill="url(#ln)" opacity=".85"/>
<circle cx="0" cy="77.5" r="4.5" fill="{T['gold']}" style="animation:run 6s linear infinite"/>
</svg>
"""
    return s


# ---------------------------------------------------------------- terminal

def terminal(T, mode):
    W = 1200
    lines = [
        ("cmd", "whoami"),
        ("out", [("Syed Umer Shah", "text"), (" · founder of ", "muted"), ("ByteFinch Technologies", "blue"),
                 (" · Lahore, PK", "muted")]),
        ("cmd", "cat ./focus.txt"),
        ("out", [("Full-stack engineer. ", "text"), ("7 years", "gold"), (" of Node.js and TypeScript, ", "muted"),
                 ("6 years", "gold"), (" of React.", "muted")]),
        ("out", [("I design the system, write the code, and own it in production.", "muted")]),
        ("cmd", "ls ./building"),
        ("out", [("payroll-engine/", "blue"), ("   ", "muted"), ("secretveil/", "green"), ("   ", "muted"),
                 ("edge-saas-starter/", "blue"), ("   ", "muted"), ("ai-agents/", "purple")]),
        ("cmd", "echo $MOTTO"),
        ("out", [("Small bytes. Big builds.", "gold")]),
    ]
    top, lh = 96, 38
    H = top + lh * len(lines) + 44
    s = svg_open(W, H, "Terminal: whoami, focus, what I am building")
    code_bg = "#0d1526" if mode == "dark" else "#0f172a"
    s += f"""<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="20"/></clipPath></defs>
<g clip-path="url(#c)">
<rect width="{W}" height="{H}" fill="{code_bg}"/>
<rect width="{W}" height="54" fill="#ffffff" fill-opacity=".05"/>
<circle cx="32" cy="27" r="8" fill="#ff5f57"/><circle cx="58" cy="27" r="8" fill="#febc2e"/><circle cx="84" cy="27" r="8" fill="#28c840"/>
<text x="600" y="33" text-anchor="middle" font-size="16" fill="#94a3b8" class="mono">umer@bytefinch: ~</text>
"""
    colors = dict(text="#f1f5f9", muted="#94a3b8", blue="#60a5fa", gold="#fbbf24", green="#4ade80",
                  purple="#c4b5fd")
    t = 0.4
    cw = 11.2  # char width of the mono font at 19px
    for i, (kind, content) in enumerate(lines):
        y = top + i * lh
        if kind == "cmd":
            n = len(content) + 2
            dur = max(0.35, 0.045 * n)
            s += (f'<text x="40" y="{y}" font-size="19" class="mono fi" style="animation-delay:{t - .3:.2f}s;animation-duration:.2s" xml:space="preserve">'
                  f'<tspan fill="#4ade80" font-weight="700">➜</tspan><tspan fill="#60a5fa" font-weight="700">  ~</tspan>'
                  f'<tspan fill="#f1f5f9"> {escape(content)}</tspan></text>')
            s += (f'<rect x="{40 + 4 * cw:.0f}" y="{y - 24}" width="{n * cw + 14:.0f}" height="34" fill="{code_bg}" '
                  f'class="cover" style="animation:uncover {dur:.2f}s steps({n}) {t:.2f}s forwards"/>')
            t += dur + 0.25
        else:
            body = "".join(f'<tspan fill="{colors[c]}">{escape(txt)}</tspan>' for txt, c in content)
            s += (f'<text x="40" y="{y}" font-size="19" class="mono fi" style="animation-delay:{t:.2f}s;'
                  f'animation-duration:.4s" xml:space="preserve">{body}</text>')
            t += 0.3
    y = top + len(lines) * lh
    s += (f'<text x="40" y="{y}" font-size="19" class="mono fi" style="animation-delay:{t:.2f}s">'
          f'<tspan fill="#4ade80" font-weight="700">➜</tspan><tspan fill="#60a5fa" font-weight="700">  ~</tspan></text>'
          f'<rect x="{40 + 5 * cw:.0f}" y="{y - 18}" width="11" height="22" fill="#f1f5f9" opacity="0" '
          f'style="animation:blink 1.1s step-end {t:.2f}s infinite"/>')
    s += "</g></svg>\n"
    return s


# ---------------------------------------------------------------- stats tiles

def stats(T, mode):
    W, H = 1200, 176
    tiles = [
        ("7", "yrs", "in production software", "full-stack, end to end"),
        ("7", "yrs", "Node.js and TypeScript", "plus 6 years of React"),
        ("3", "", "engineers I mentor", "on real product work"),
        ("3", "clouds", "AWS · Azure · GCP", "and Cloudflare at the edge"),
    ]
    s = svg_open(W, H, "7 years of production software, 7 years of Node.js and TypeScript, 3 engineers mentored, 3 clouds")
    s += f"""<defs><linearGradient id="num" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="{'#93c5fd' if mode == 'dark' else '#3b82f6'}"/><stop offset="1" stop-color="{'#3b82f6' if mode == 'dark' else '#1a2a4a'}"/></linearGradient>
<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{T['blue']}"/><stop offset="1" stop-color="{T['gold']}"/></linearGradient></defs>
"""
    tw, gap = 282, 24
    for i, (num, unit, l1, l2) in enumerate(tiles):
        x = i * (tw + gap)
        s += f'<g class="fu" style="{d(i, .1, .15)}">'
        s += (f'<rect x="{x + 1}" y="1" width="{tw - 2}" height="{H - 2}" rx="18" fill="{T["card"]}" '
              f'stroke="{T["card_stroke"]}" stroke-width="1.5"/>')
        s += (f'<text x="{x + 26}" y="82" font-size="64" font-weight="800" fill="url(#num)">{num}'
              f'<tspan font-size="26" font-weight="700" fill="{T["gold"]}" dx="8">{unit}</tspan></text>')
        s += f'<text x="{x + 26}" y="118" font-size="18" font-weight="600" fill="{T["text"]}">{escape(l1)}</text>'
        s += f'<text x="{x + 26}" y="142" font-size="16" fill="{T["muted"]}">{escape(l2)}</text>'
        s += (f'<rect x="{x + 26}" y="156" width="{tw - 52}" height="4" rx="2" fill="url(#bar)" class="grow" '
              f'style="animation-delay:{0.5 + i * 0.2:.1f}s"/>')
        s += "</g>"
    s += "</svg>\n"
    return s


# ---------------------------------------------------------------- building cards

ICONS = {
    "payroll": '<rect x="18" y="12" width="28" height="40" rx="4"/><path d="M24 22h16M24 30h16M24 38h9"/>'
               '<path d="M36 42l4 4 8-9" stroke-width="3.2"/>',
    "shield": '<path d="M32 10l18 7v13c0 12-8 20-18 24-10-4-18-12-18-24V17z"/><circle cx="32" cy="29" r="4"/>'
              '<path d="M32 33v8"/>',
    "bolt": '<path d="M35 8L17 36h14l-3 20 19-29H33z"/>',
    "bot": '<rect x="14" y="20" width="36" height="28" rx="8"/><circle cx="25" cy="34" r="3.5"/>'
           '<circle cx="39" cy="34" r="3.5"/><path d="M32 20v-8M28 12h8M9 30v8M55 30v8"/>',
}


def building(T, mode):
    W, H = 1200, 424
    cards = [
        ("payroll", "Payroll for UAE agencies",
         ["Salary runs, WPS SIF files and multi-tenant HR", "for staffing agencies, with golden-file tests."],
         "PRIVATE BUILD", T["gold"]),
        ("shield", "SecretVeil",
         ["Lets an AI coding agent work in your repo", "without reading your secrets."],
         "OPEN SOURCE", T["green"]),
        ("bolt", "Edge SaaS starter",
         ["Next.js 16 on Cloudflare Workers with D1, R2,", "Better Auth, Resend and Stripe."],
         "TEMPLATE", T["blue"]),
        ("bot", "AI agents and automation",
         ["LangGraph agents, MCP servers and n8n", "workflows, like an AI sales chatbot."],
         "ACTIVE", T["purple"]),
    ]
    s = svg_open(W, H, "What I am building: a payroll engine, SecretVeil, an edge SaaS starter and AI agents")
    cw, ch, gap = 588, 200, 24
    for i, (icon, title, desc, tag, col) in enumerate(cards):
        x = (i % 2) * (cw + gap)
        y = (i // 2) * (ch + gap)
        s += f'<g class="fu" style="{d(i, .1, .18)}">'
        s += (f'<rect x="{x + 1}" y="{y + 1}" width="{cw - 2}" height="{ch - 2}" rx="20" fill="{T["card"]}" '
              f'stroke="{T["card_stroke"]}" stroke-width="1.5"/>')
        s += f'<rect x="{x + 28}" y="{y + 1}" width="120" height="4" rx="2" fill="{col}"/>'
        s += (f'<rect x="{x + 28}" y="{y + 30}" width="64" height="64" rx="16" fill="{col}" fill-opacity="{T["tint_op"]}"/>'
              f'<rect x="{x + 28}" y="{y + 30}" width="64" height="64" rx="16" fill="none" stroke="{col}" '
              f'stroke-opacity=".6" style="animation:pulse 3s ease-in-out {i * .6:.1f}s infinite"/>')
        s += (f'<g transform="translate({x + 28},{y + 30})" fill="none" stroke="{col}" stroke-width="2.6" '
              f'stroke-linecap="round" stroke-linejoin="round">{ICONS[icon]}</g>')
        s += f'<text x="{x + 112}" y="{y + 70}" font-size="27" font-weight="800" fill="{T["text"]}">{escape(title)}</text>'
        for j, line in enumerate(desc):
            s += (f'<text x="{x + 28}" y="{y + 134 + j * 28}" font-size="19" fill="{T["muted"]}">'
                  f'{escape(line)}</text>')
        g, w = pill(x + cw - 28 - int(len(tag) * 13 * 0.58 + 30), y + ch - 56, tag, col, T, size=13, h=28)
        s += g
        s += "</g>"
    s += "</svg>\n"
    return s


# ---------------------------------------------------------------- secretveil feature

def secretveil(T, mode):
    W, H = 1200, 420
    s = svg_open(W, H, "SecretVeil: the .env file holds a handle, not a value", extra_style="""
@keyframes plain{0%,38%{opacity:1}44%,92%{opacity:0}98%,100%{opacity:1}}
@keyframes veiled{0%,38%{opacity:0}44%,92%{opacity:1}98%,100%{opacity:0}}
@keyframes sweep{0%,30%{transform:translateX(-700px)}46%{transform:translateX(700px)}100%{transform:translateX(700px)}}
@keyframes lbl1{0%,38%{opacity:1}44%,92%{opacity:0}98%,100%{opacity:1}}
.plain{animation:plain 9s ease-in-out infinite}
.veiled{animation:veiled 9s ease-in-out infinite}
.sweep{animation:sweep 9s ease-in-out infinite}
""")
    code_bg = "#0d1526" if mode == "dark" else "#0f172a"
    s += f"""<defs>
<clipPath id="ed"><rect x="28" y="28" width="640" height="{H - 56}" rx="16"/></clipPath>
<linearGradient id="veil" x1="0" x2="1">
 <stop offset="0" stop-color="#3b82f6" stop-opacity="0"/><stop offset=".5" stop-color="#93c5fd" stop-opacity=".55"/><stop offset="1" stop-color="#3b82f6" stop-opacity="0"/>
</linearGradient>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="{T['card']}" stroke="{T['card_stroke']}" stroke-width="1.5"/>
<g clip-path="url(#ed)">
<rect x="28" y="28" width="640" height="{H - 56}" fill="{code_bg}"/>
<rect x="28" y="28" width="640" height="46" fill="#ffffff" fill-opacity=".05"/>
<rect x="44" y="40" width="74" height="34" rx="6" fill="{code_bg}"/>
<text x="58" y="62" font-size="15" class="mono" fill="#e2e8f0">.env</text>
<circle cx="640" cy="51" r="6" fill="#fbbf24"><animate attributeName="opacity" values=".3;1;.3" dur="2s" repeatCount="indefinite"/></circle>
"""
    rows = [
        ("# what your AI agent reads", None, None, "#64748b"),
        ("API_KEY=", "sk-live-Q9xR2mVn7pLwT4aZ", "sv://api_key", None),
        ("DB_URL=postgres://app:", "s3cr3t-p4ss", "sv://db_url_password", "@db:5432/app"),
        ("STRIPE_SECRET=", "rk_live_51Hx9QaT2", "sv://stripe_secret", None),
        ("APP_ENV=production", None, None, "#94a3b8"),
    ]
    cw = 9.6
    for i, (key, plain, handle, col) in enumerate(rows):
        y = 124 + i * 44
        s += f'<text x="46" y="{y}" font-size="15" class="mono" fill="#475569">{i + 1}</text>'
        if plain is None:
            s += f'<text x="78" y="{y}" font-size="16" class="mono" fill="{col}">{escape(key)}</text>'
            continue
        s += f'<text x="78" y="{y}" font-size="16" class="mono" fill="#93c5fd">{escape(key)}</text>'
        vx = 78 + len(key) * cw
        tail = f'<tspan fill="#93c5fd">{escape(col)}</tspan>' if col else ""
        s += f'<text x="{vx:.0f}" y="{y}" font-size="16" class="mono plain" fill="#f87171">{escape(plain)}{tail}</text>'
        s += f'<text x="{vx:.0f}" y="{y}" font-size="16" class="mono veiled" fill="#4ade80">{escape(handle)}{tail}</text>'
    s += f'<rect class="sweep" x="28" y="74" width="260" height="{H - 102}" fill="url(#veil)"/>'
    # status bar
    s += (f'<rect x="28" y="{H - 72}" width="640" height="44" fill="#ffffff" fill-opacity=".04"/>'
          f'<g class="plain"><circle cx="54" cy="{H - 50}" r="6" fill="#f87171"/>'
          f'<text x="72" y="{H - 44}" font-size="15" class="mono" fill="#fca5a5">before: the agent can read every secret</text></g>'
          f'<g class="veiled"><circle cx="54" cy="{H - 50}" r="6" fill="#4ade80"/>'
          f'<text x="72" y="{H - 44}" font-size="15" class="mono" fill="#86efac">after: the agent reads handles, not values</text></g>')
    s += "</g>"
    # right side
    x = 712
    s += (f'<text x="{x}" y="86" font-size="42" font-weight="800" class="mono" fill="{T["text"]}">secretveil</text>'
          f'<text x="{x}" y="124" font-size="19" fill="{T["muted"]}">Let an AI coding agent work in your repository</text>'
          f'<text x="{x}" y="150" font-size="19" fill="{T["muted"]}">without letting it read your secrets.</text>')
    bullets = ["Nothing to integrate: no plugin, no proxy", "Filters secrets out of build output",
               "Reversible, byte for byte", "Local: no account, no network call"]
    for i, b in enumerate(bullets):
        y = 200 + i * 36
        s += (f'<g class="fu" style="{d(i, .3, .15)}"><circle cx="{x + 11}" cy="{y - 6}" r="11" fill="{T["green"]}" fill-opacity=".15"/>'
              f'<path d="M{x + 6} {y - 6}l4 4 7-8" fill="none" stroke="{T["green"]}" stroke-width="2.4" '
              f'stroke-linecap="round" stroke-linejoin="round"/>'
              f'<text x="{x + 32}" y="{y}" font-size="18" fill="{T["text"]}">{escape(b)}</text></g>')
    px = x
    for label, col in [("CLI", T["blue"]), ("npm", T["red"]), ("Apache-2.0", T["gold"])]:
        g, w = pill(px, 336, label, col, T, size=14, h=30)
        s += g
        px += w + 10
    s += (f'<text x="{x}" y="{H - 30}" font-size="15" class="mono" fill="{T["blue"]}">'
          f'github.com/ByteFinch-Technologies/secretveil →</text>')
    s += "</svg>\n"
    return s


# ---------------------------------------------------------------- journey

def journey(T, mode):
    W, H = 1200, 290
    nodes = [
        ("EDUCATION", "FAST-NUCES", "Computer Science"),
        ("2019", "Focusteck", "Software engineering"),
        ("2020", "Fiverr and Upwork", "Freelance clients"),
        ("2023", "Codefinity", "Director of Engineering"),
        ("2026", "ByteFinch", "Founder and CEO"),
    ]
    s = svg_open(W, H, "Journey: FAST-NUCES, Focusteck 2019, freelance 2020, Codefinity 2023, founded ByteFinch 2026")
    s += f"""<defs><linearGradient id="tl" x1="0" x2="1"><stop offset="0" stop-color="{T['blue']}"/><stop offset="1" stop-color="{T['gold']}"/></linearGradient></defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="{T['card']}" stroke="{T['card_stroke']}" stroke-width="1.5"/>
<line x1="120" y1="140" x2="1080" y2="140" stroke="{T['card_stroke']}" stroke-width="6" stroke-linecap="round"/>
<line x1="120" y1="140" x2="1080" y2="140" stroke="url(#tl)" stroke-width="6" stroke-linecap="round" stroke-dasharray="962" stroke-dashoffset="962" style="animation:draw 2.4s cubic-bezier(.4,0,.2,1) .2s forwards"/>
"""
    for i, (top, org, role) in enumerate(nodes):
        x = 120 + i * 240
        last = i == len(nodes) - 1
        col = T["gold"] if last else T["blue"]
        delay = 0.2 + i * 0.55
        s += f'<g class="fu" style="animation-delay:{delay:.2f}s">'
        if last:
            s += (f'<circle cx="{x}" cy="140" r="16" fill="none" stroke="{col}" stroke-width="2">'
                  f'<animate attributeName="r" values="14;30" dur="1.8s" repeatCount="indefinite"/>'
                  f'<animate attributeName="opacity" values=".9;0" dur="1.8s" repeatCount="indefinite"/></circle>')
        s += (f'<circle cx="{x}" cy="140" r="15" fill="{T["card"]}" stroke="{col}" stroke-width="4"/>'
              f'<circle cx="{x}" cy="140" r="6" fill="{col}"/>')
        tsize = 16 if top == "EDUCATION" else 26
        tcol = T["faint"] if top == "EDUCATION" else col
        s += (f'<text x="{x}" y="100" text-anchor="middle" font-size="{tsize}" font-weight="800" '
              f'letter-spacing="{2 if tsize == 16 else 0}" fill="{tcol}">{top}</text>')
        s += f'<text x="{x}" y="200" text-anchor="middle" font-size="20" font-weight="700" fill="{T["text"]}">{escape(org)}</text>'
        s += f'<text x="{x}" y="228" text-anchor="middle" font-size="16" fill="{T["muted"]}">{escape(role)}</text>'
        s += "</g>"
    s += "</svg>\n"
    return s


# ---------------------------------------------------------------- footer

def footer(T, mode):
    W, H = 1200, 200

    def wave(amp, y0, length=300):
        pts = f"M0 {y0}"
        for k in range(0, 2400 // length):
            pts += f" q{length / 4} {-amp} {length / 2} 0 t{length / 2} 0"
        return pts + f" V{H} H0 Z"

    s = svg_open(W, H, "Small bytes. Big builds. bytefinch.dev", extra_style="""
@keyframes slide{from{transform:translateX(0)}to{transform:translateX(-600px)}}
@keyframes slide2{from{transform:translateX(-600px)}to{transform:translateX(0)}}
""")
    s += f"""<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="24"/></clipPath>
<linearGradient id="bg" x1="0" x2="1"><stop offset="0" stop-color="{T['bg0']}"/><stop offset="1" stop-color="{T['bg2']}"/></linearGradient></defs>
<g clip-path="url(#c)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<path d="{wave(18, 150)}" fill="{T['blue']}" fill-opacity=".22" style="animation:slide 9s linear infinite"/>
<path d="{wave(14, 165, 300)}" fill="{T['blue']}" fill-opacity=".35" style="animation:slide2 12s linear infinite"/>
<path d="{wave(10, 182, 300)}" fill="{T['bg2']}" style="animation:slide 7s linear infinite"/>
<path d="{wave(10, 182, 300).split(' V')[0]}" fill="none" stroke="{T['gold']}" stroke-width="2.5" stroke-opacity=".8" style="animation:slide 7s linear infinite"/>
<text x="600" y="78" text-anchor="middle" font-size="36" font-weight="800" fill="{T['text']}" class="fu">Small bytes. <tspan fill="{T['blue']}">Big builds.</tspan></text>
<text x="600" y="114" text-anchor="middle" font-size="18" class="mono fu" style="animation-delay:.3s" fill="{T['muted']}">bytefinch.dev · Lahore, Pakistan</text>
</g></svg>
"""
    return s


SECTIONS = {
    "about": ("About me", "~/whoami"),
    "building": ("What I am building", "~/building"),
    "featured": ("Featured open source", "~/secretveil"),
    "stack": ("Tech stack", "~/stack"),
    "journey": ("Journey", "~/career.log"),
    "activity": ("GitHub activity", "~/contributions"),
    "connect": ("Let's connect", "~/contact"),
}


def main():
    OUT.mkdir(exist_ok=True)
    for mode, T in THEMES.items():
        files = {
            f"header-{mode}.svg": header(T, mode),
            f"terminal-{mode}.svg": terminal(T, mode),
            f"stats-{mode}.svg": stats(T, mode),
            f"building-{mode}.svg": building(T, mode),
            f"secretveil-{mode}.svg": secretveil(T, mode),
            f"journey-{mode}.svg": journey(T, mode),
            f"footer-{mode}.svg": footer(T, mode),
        }
        for key, (title, sub) in SECTIONS.items():
            files[f"section-{key}-{mode}.svg"] = section(T, title, sub)
        for name, body in files.items():
            (OUT / name).write_text(body)
    print("wrote", len(list(OUT.glob("*.svg"))), "svg files to", OUT)


if __name__ == "__main__":
    main()
