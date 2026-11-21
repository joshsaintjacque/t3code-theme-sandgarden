"""Generate index.html (palette is read from sandgarden.json so hexes always match)."""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
theme = json.load(open(os.path.join(ROOT, "sandgarden.json")))
C = theme["colors"]
SITE = "https://joshsaintjacque.github.io/t3code-theme-sandgarden/"
REPO = "https://github.com/joshsaintjacque/t3code-theme-sandgarden"

GROUPS = [
    ("Sand and stone", ["canvas", "chrome", "toolbar", "surface", "surfaceRaised", "surfaceOverlay", "sidebar", "sidebarRowSelected", "messageSurface", "codeBackground", "border"]),
    ("Ink", ["text", "textMuted", "placeholder", "sidebarForeground", "sidebarMutedForeground", "iconMuted"]),
    ("Moss", ["accent", "accentForeground", "focus", "messageActionHover", "accentSurface", "searchMatchBackground"]),
    ("Signals", ["error", "warning", "update", "errorSurface", "warningSurface", "updateSurface"]),
    ("Terminal", ["terminalBackground", "terminalForeground", "terminalCursor", "terminalSelection"]),
]
shown = set(k for _, ks in GROUPS for k in ks)
rest = [k for k in C if k not in shown]


def rows(keys):
    return "".join(
        f"<tr tabindex='0' role='button' data-hex='{C[k]}' title='Copy {C[k]}'><td><i style='background:{C[k]}'></i></td><td>{k}</td><td><code>{C[k]}</code></td></tr>"
        for k in keys)


pal = "".join(f"<h3>{g}</h3><table class='pal'>{rows(ks)}</table>" for g, ks in GROUPS)
pal += f"<details class='more'><summary>All {len(C)} roles</summary><table class='pal'>{rows(rest)}</table></details>"

MOTION = [
    ("At rest", "The furrows are set and the ripples sit still around each stone. Nothing moves.", "idle"),
    ("A turn is running", "Moss furrows are raked into each margin over about twenty seconds (about ten in the narrower 72px strips), bending round the stones and replacing the sand lines. Then the garden holds with a slow ring breath of 7%, so a long turn stays calm and nothing resets.", "[data-timeline-row-kind=&quot;working&quot;]"),
    ("Working row", "Three wavy furrows flow under the live Working line.", "working"),
    ("A background thread is busy", "The same wavy furrows run, slower, under that thread in the sidebar.", "aria-busy"),
    ("Composer focus", "Two soft ripples spread out from the composer's edge.", "focus-within"),
    ("Hover a thread", "Three tines are drawn under the row, each stopping a little short of the last.", ":hover"),
    ("Turn complete", "The moss fades into the sand over about a second and a half while each set of ripples spreads from its own stone. A turn that ends early fades only what was drawn. Then the sand goes still.", "done"),
    ("Narrow window", "When the margins are under about 220px (a small window, or the details panel open) a slim strip with one stone takes over, and turns moss while a turn runs. The header garden and the composer's furrows do the same.", "max-width"),
    ("Reduced motion", "Every animation stops. A running turn shows the finished moss garden as a still, and busy rows keep their wavy furrows so state is still visible.", "reduce"),
]
motion = "".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b, _ in MOTION)

page = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sandgarden · a calm light theme for T3 Code</title>
<meta name="description" content="Sandgarden is a light theme for T3 Code. Raked sand, quiet stones, moss ink. A rake draws furrows in the margins while the agent works and settles into ripples when it stops.">
<meta property="og:type" content="website">
<meta property="og:title" content="Sandgarden for T3 Code">
<meta property="og:description" content="A dry rock garden for your agent chat. The rake works while the agent works, then the sand goes still.">
<meta property="og:image" content="__SITE__assets/og.png">
<meta property="og:url" content="__SITE__">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Sandgarden for T3 Code">
<meta name="twitter:description" content="A dry rock garden for your agent chat. The rake works while the agent works, then the sand goes still.">
<meta name="twitter:image" content="__SITE__assets/og.png">
<meta name="theme-color" content="#f1e9d6">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23f1e9d6'/%3E%3Cellipse cx='16' cy='16' rx='11' ry='8' fill='none' stroke='%23a89868' stroke-width='1.4'/%3E%3Cellipse cx='16' cy='16' rx='6' ry='4.4' fill='%23686459'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..600;1,6..72,300..500&family=Figtree:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{--sand:#f1e9d6;--sand2:#e8dec6;--tray:#f7f1e2;--ink:#2b2822;--mute:#5b5546;--line:#cfc1a0;--rake:rgba(112,92,52,.34);--moss:#4a5e3e;--stone:#686459}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--sand);color:var(--ink);font:17px/1.65 Figtree,system-ui,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:hidden}
body:before{content:"";position:fixed;inset:0;z-index:-1;background:repeating-linear-gradient(90deg,rgba(112,92,52,.05) 0 1px,transparent 1px 11px)}
a{color:#3a6470;text-underline-offset:4px}
h1,h2,h3{font-family:Newsreader,"Iowan Old Style",Georgia,serif;font-weight:400;line-height:1.1;margin:0}
code,.mono{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:.86em}
.wrap{width:min(1120px,100% - 40px);margin:0 auto}
header.top{display:flex;justify-content:space-between;align-items:center;padding:22px 0}
header.top b{font:500 22px Newsreader,Georgia,serif;letter-spacing:.01em}
header.top nav{display:flex;gap:22px;font-size:14px}
header.top nav a{color:var(--mute);text-decoration:none}header.top nav a:hover{color:var(--ink)}
.hero{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:48px;align-items:center;padding:34px 0 120px}
.eyebrow{font:500 12px "JetBrains Mono",monospace;letter-spacing:.18em;text-transform:uppercase;color:var(--moss);margin-bottom:18px}
h1{font-size:clamp(46px,6vw,88px);font-weight:300;letter-spacing:-.02em}
h1 em{font-style:italic;color:var(--moss)}
.lede{font-size:19px;color:var(--mute);max-width:30em;margin:22px 0 30px}
.btns{display:flex;flex-wrap:wrap;gap:12px}
.btn{font:500 15px Figtree,sans-serif;padding:12px 20px;border-radius:999px;border:1px solid var(--moss);background:var(--moss);color:#f7f2e3;cursor:pointer;text-decoration:none;display:inline-block;transition:background .2s,transform .2s}
.btn:hover{background:#3a4c30}.btn.ghost{background:transparent;color:var(--moss)}.btn.ghost:hover{background:rgba(74,94,62,.1)}
.btn:focus-visible,tr:focus-visible,summary:focus-visible{outline:2px solid var(--moss);outline-offset:3px}
.tray{position:relative;border-radius:22px;padding:12px;background:var(--tray);border:1px solid var(--line);box-shadow:0 24px 60px -24px rgba(70,56,30,.35)}
.tray video,.tray img{display:block;width:100%;height:auto;border-radius:12px;background:var(--sand2)}
.tray:before,.tray:after{content:"";position:absolute;left:36px;right:36px;height:1px;background:var(--rake)}
.tray:before{bottom:-9px}.tray:after{bottom:-14px;left:70px;right:70px;opacity:.6}
.rakeline{display:block;width:100%;height:14px;margin:0}
.rakeline path{fill:none;stroke:var(--rake);stroke-width:1.2;stroke-dasharray:1;stroke-dashoffset:1;transition:stroke-dashoffset 2.4s cubic-bezier(.3,.6,.2,1)}
.rakeline.in path{stroke-dashoffset:0}.rakeline path:nth-child(2){transition-delay:.15s}.rakeline path:nth-child(3){transition-delay:.3s}
section{padding:72px 0}
section>.wrap>h2{font-size:clamp(34px,4.6vw,56px);font-weight:300;letter-spacing:-.01em;margin-bottom:12px}
section>.wrap>p.sub{color:var(--mute);max-width:36em;margin:0 0 36px}
.motion{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}
.motion li{background:var(--tray);border:1px solid var(--line);border-radius:16px;padding:18px 20px;display:grid;gap:6px;align-content:start}
.motion b{font:500 22px Newsreader,Georgia,serif;color:var(--moss)}.motion span{color:var(--mute);font-size:15.5px}
.stills{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:30px}
.stills figure{margin:0}.stills figcaption{font-size:14px;color:var(--mute);margin-top:8px}
.stills .tray{padding:8px}
.pal{width:100%;border-collapse:collapse;margin:6px 0 24px}
.pal tr{cursor:pointer;border-top:1px solid rgba(207,193,160,.7);transition:background .15s}
.pal tr:hover,.pal tr:focus-visible{background:rgba(74,94,62,.08)}
.pal td{padding:8px 10px;font-size:15px}.pal td:first-child{width:56px}.pal td:last-child{text-align:right;color:var(--mute)}
.pal i{display:block;width:36px;height:24px;border-radius:7px;border:1px solid rgba(70,56,30,.25)}
.pal tr.copied td:last-child:after{content:" · copied";color:var(--moss)}
.palwrap h3{font-size:24px;margin:26px 0 4px;font-weight:400;color:var(--moss)}
.palgrid{display:grid;grid-template-columns:1fr 1fr;gap:0 56px}
details.more{margin-top:14px}details.more summary{cursor:pointer;color:var(--moss);font-weight:500;padding:8px 0}
.install{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px}
.step{background:var(--tray);border:1px solid var(--line);border-radius:18px;padding:22px}
.step h3{font-size:26px;margin-bottom:8px}.step p{margin:0 0 14px;color:var(--mute);font-size:15.5px}
pre{margin:0;background:#e9e0c8;border:1px solid rgba(160,140,96,.4);border-left:3px solid var(--moss);border-radius:8px;padding:12px 14px;overflow-x:auto;font:13px/1.6 "JetBrains Mono",monospace;color:var(--ink);white-space:pre-wrap;word-break:break-all}
.status{min-height:1.4em;font-size:14px;color:var(--moss);margin-top:10px}
footer{padding:40px 0 70px;color:var(--mute);font-size:14px;border-top:1px solid var(--line)}
footer .wrap{display:flex;flex-wrap:wrap;justify-content:space-between;gap:12px}
/* hero stones */
.stones{position:absolute;right:6px;bottom:-124px;width:150px;height:110px;pointer-events:none}
.stones ellipse.ring{fill:none;stroke:var(--rake);stroke-width:1.2;transform-box:fill-box;transform-origin:center;animation:ripple 7.5s ease-out infinite}
.stones ellipse.ring:nth-of-type(2){animation-delay:2.5s}.stones ellipse.ring:nth-of-type(3){animation-delay:5s}
@keyframes ripple{0%{opacity:0;scale:.5}20%{opacity:1}100%{opacity:0;scale:1.25}}
@media (max-width:900px){.hero{grid-template-columns:1fr;gap:34px}.palgrid,.stills{grid-template-columns:1fr}.stones{display:none}header.top nav{display:none}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{animation:none!important;transition:none!important}.rakeline path{stroke-dashoffset:0}.stones ellipse.ring{opacity:.7;scale:1}.stones ellipse.ring:nth-of-type(1){scale:.55;opacity:.8}.stones ellipse.ring:nth-of-type(2){scale:.8;opacity:.55}.stones ellipse.ring:nth-of-type(3){scale:1.05;opacity:.32}}
</style>
</head>
<body>
<div class="wrap">
<header class="top"><b>Sandgarden</b><nav><a href="#moves">What moves</a><a href="#demo">Demo</a><a href="#palette">Palette</a><a href="#install">Install</a></nav></header>
<div class="hero">
<div>
<div class="eyebrow">A theme for T3 Code · light · calm</div>
<h1>Sand<em>garden</em></h1>
<p class="lede">A dry rock garden for your agent chat. Raked sand, quiet stones and moss ink. While the agent works, a rake draws furrows down the margins. When it stops, they settle into ripples and the sand goes still.</p>
<div class="btns"><a class="btn" href="#install">Install</a><a class="btn ghost" href="#demo">Watch the demo</a></div>
</div>
<div class="tray"><video id="hero" src="assets/hero.mp4" poster="assets/hero.jpg" autoplay muted loop playsinline preload="auto"></video>
<svg class="stones" viewBox="0 0 150 110" aria-hidden="true"><ellipse class="ring" cx="75" cy="55" rx="62" ry="40"/><ellipse class="ring" cx="75" cy="55" rx="62" ry="40"/><ellipse class="ring" cx="75" cy="55" rx="62" ry="40"/><ellipse cx="78" cy="58" rx="27" ry="19" fill="rgba(70,56,30,.22)"/><ellipse cx="75" cy="55" rx="26" ry="18" fill="#686459" transform="rotate(-14 75 55)"/><ellipse cx="68" cy="49" rx="13" ry="7" fill="rgba(255,252,240,.24)"/></svg></div>
</div>
</div>

<svg class="rakeline" viewBox="0 0 1200 14" preserveAspectRatio="none" aria-hidden="true"><path d="M0 2H1200"/><path d="M0 7H1200"/><path d="M0 12H1200"/></svg>

<section id="moves"><div class="wrap">
<h2>What moves, and why</h2>
<p class="sub">Nothing animates for its own sake. Every movement is a rake doing a job, and each one keys off something the app already knows.</p>
<ul class="motion">__MOTION__</ul>
<div class="stills">
<figure class="tray" style="grid-column:1/-1"><img src="assets/gutters.jpg" alt="The two margin gardens at rest and mid-turn, side by side at full size" loading="lazy" style="display:block;width:100%;max-width:800px;margin:0 auto"><figcaption style="text-align:center">Left margin and right margin, at rest then mid-turn, at 1:1: the moss rake replaces the sand furrows.</figcaption></figure>
</div>
</div></section>

<svg class="rakeline" viewBox="0 0 1200 14" preserveAspectRatio="none" aria-hidden="true"><path d="M0 2H1200"/><path d="M0 7H1200"/><path d="M0 12H1200"/></svg>

<section id="demo"><div class="wrap">
<h2>One turn, start to finish</h2>
<p class="sub">Idle, compose, a turn starts, a background thread goes busy, the answer lands, hover, and the narrow-window fallback.</p>
<div class="tray"><video src="assets/demo.mp4" poster="assets/demo.jpg" controls playsinline preload="none"></video></div>
</div></section>

<svg class="rakeline" viewBox="0 0 1200 14" preserveAspectRatio="none" aria-hidden="true"><path d="M0 2H1200"/><path d="M0 7H1200"/><path d="M0 12H1200"/></svg>

<section id="palette"><div class="wrap palwrap">
<h2>Palette</h2>
<p class="sub">Every colour role is set by hand in the theme file. Click a row to copy its hex.</p>
<div id="palette-body">__PALETTE__</div>
</div></section>

<svg class="rakeline" viewBox="0 0 1200 14" preserveAspectRatio="none" aria-hidden="true"><path d="M0 2H1200"/><path d="M0 7H1200"/><path d="M0 12H1200"/></svg>

<section id="install"><div class="wrap">
<h2>Install</h2>
<p class="sub">One JSON file. No fonts, images or extra files to download.</p>
<div class="install">
<div class="step"><h3>In the app</h3><p>Copy the theme, then open Settings › Appearance › Add theme and paste.</p>
<div class="btns"><button class="btn" id="copy">Copy theme JSON</button><a class="btn ghost" href="sandgarden.json" download="sandgarden.json">Download</a></div><div class="status" id="status" role="status"></div></div>
<div class="step"><h3>From the terminal</h3><p>Fetch the file and set it with the T3 CLI.</p>
<pre id="cli">curl -fsSL -o sandgarden.json __SITE__sandgarden.json
~/.t3/bin/t3 theme set sandgarden.json</pre><div class="btns" style="margin-top:12px"><button class="btn ghost" id="copycli">Copy commands</button></div></div>
</div>
<p class="sub" style="margin-top:28px">Light theme with margin art on windows 1460px wide and up; narrower layouts keep a slim one-stone strip in each margin. Source: <a href="__REPO__">GitHub</a> · MIT.</p>
</div></section>

<footer><div class="wrap"><span>Sandgarden is a community theme and is not affiliated with or endorsed by T3.</span><span>MIT © 2026 Josh Saint Jacque</span></div></footer>

<script>
const $=s=>document.querySelector(s);
async function copy(text){try{await navigator.clipboard.writeText(text);return true}catch(e){try{const t=document.createElement('textarea');t.value=text;t.style.position='fixed';t.style.opacity='0';document.body.appendChild(t);t.select();const ok=document.execCommand('copy');t.remove();return ok}catch(_){return false}}}
const themeP=fetch('sandgarden.json').then(r=>{if(!r.ok)throw 0;return r.text()});themeP.catch(()=>{});
$('#copy').onclick=async()=>{const s=$('#status');let ok=false;try{if(window.ClipboardItem&&navigator.clipboard&&navigator.clipboard.write){await navigator.clipboard.write([new ClipboardItem({'text/plain':themeP.then(t=>new Blob([t],{type:'text/plain'}))})]);ok=true}else ok=await copy(await themeP)}catch(e){try{ok=await copy(await themeP)}catch(_){ok=false}}s.textContent=ok?'Copied. Paste it into Settings › Appearance › Add theme.':'Could not copy here. Use Download instead.'};
$('#copycli').onclick=async()=>{const ok=await copy($('#cli').textContent);$('#copycli').textContent=ok?'Copied':'Copy failed'; setTimeout(()=>$('#copycli').textContent='Copy commands',1600)};
document.querySelectorAll('.pal tr').forEach(r=>{const go=async()=>{if(!await copy(r.dataset.hex))return;r.classList.add('copied');setTimeout(()=>r.classList.remove('copied'),1200)};r.onclick=go;r.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();go()}}});
const io='IntersectionObserver' in window?new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{threshold:.6}):null;
document.querySelectorAll('.rakeline').forEach(l=>io?io.observe(l):l.classList.add('in'));
if(matchMedia('(prefers-reduced-motion:reduce)').matches){const h=$('#hero');h.removeAttribute('autoplay');h.pause();const im=new Image();im.src='assets/working.jpg';im.alt='Sandgarden mid-turn, moss furrows drawn in both margins';im.style.cssText='display:block;width:100%';h.replaceWith(im)}
</script>
</body>
</html>
"""
page = page.replace("__MOTION__", motion).replace("__PALETTE__", pal).replace("__SITE__", SITE).replace("__REPO__", REPO)
open(os.path.join(ROOT, "index.html"), "w").write(page)
print("index.html", len(page))
