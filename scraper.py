import asyncio
import re
import os
from playwright.async_api import async_playwright
from datetime import datetime

# ── KONFIGURATION ─────────────────────────────────────────────────────────────
BASE_URL = "https://ZR-JT.github.io/basf-knowledge"

SOURCES = [
    {
        "id":    "warum-basf",
        "title": "Warum BASF – Arbeitgeber & Benefits",
        "url":   "https://www.basf.com/global/de/careers/why-join-basf",
        "desc":  "Unternehmenskultur, CORE-Werte, Benefits (you@BASF), Karrieremöglichkeiten, Work-Life-Balance, Mitarbeiterstimmen.",
        "tags":  ["Karriere", "Benefits", "Kultur", "Arbeitgeber"],
        "lang":  "de",
    },
    {
        "id":    "strategie",
        "title": "Strategie – Winning Ways",
        "url":   "https://www.basf.com/global/de/who-we-are/strategy",
        "desc":  "BASF Unternehmensstrategie: Winning Ways mit Focus, Accelerate, Transform, Win. Winning Culture, finanzielle Ziele.",
        "tags":  ["Strategie", "Unternehmen", "Winning Ways", "CEO"],
        "lang":  "de",
    },
    {
        "id":    "werte",
        "title": "Unsere Werte – CORE",
        "url":   "https://www.basf.com/global/de/who-we-are/about-us/our-values",
        "desc":  "Die vier CORE-Werte: Creative, Open, Responsible, Entrepreneurial. Standards, Verhaltenskodex, Compliance.",
        "tags":  ["Werte", "CORE", "Compliance", "Standards"],
        "lang":  "de",
    },
    {
        "id":    "diversity",
        "title": "Diversity, Equity & Inclusion",
        "url":   "https://www.basf.com/global/de/careers/why-join-basf/diversity",
        "desc":  "DE&I: Vielfalt, Geschlechterbalance, Netzwerke, UN Global Compact, WEPs, PROUT@work.",
        "tags":  ["Diversity", "Inklusion", "DE&I", "Chancengleichheit"],
        "lang":  "de",
    },
    {
        "id":    "faq-bewerbung",
        "title": "FAQ Bewerbungsprozess",
        "url":   "https://www.basf.com/global/de/careers/application/faq/questions-for-students",
        "desc":  "Bewerbungsablauf, Unterlagen, Interviews, Vergütungstabelle für Studierende, Datenschutz.",
        "tags":  ["Bewerbung", "FAQ", "Prozess", "Interviews"],
        "lang":  "de",
    },
    {
        "id":    "faq-studierende",
        "title": "FAQ Studierende & Praktika",
        "url":   "https://www.basf.com/global/de/careers/application/faq/questions-for-students",
        "desc":  "Praktikumsarten, Gap-Year, Auslandspraktikum Explore Together, Abschlussarbeiten, Deutschlandstipendium.",
        "tags":  ["Studierende", "Praktikum", "FAQ", "Explore Together"],
        "lang":  "de",
    },
    {
        "id":    "faq-berufseinsteiger",
        "title": "FAQ Berufseinsteiger & Absolventen",
        "url":   "https://www.basf.com/global/de/careers/application/faq/questions-for-graduates",
        "desc":  "Direkteinstieg, Traineeprogramme, Assessment Center, erste Stelle bei BASF.",
        "tags":  ["Absolventen", "Einstieg", "FAQ", "Direkteinstieg"],
        "lang":  "de",
    },
    {
        "id":    "faq-berufserfahrene",
        "title": "FAQ Berufserfahrene",
        "url":   "https://www.basf.com/global/de/careers/application/faq/questions-for-professionals",
        "desc":  "Bewerbungsprozess für Professionals, Quereinstieg, Senior-Level.",
        "tags":  ["Professionals", "Erfahrene", "FAQ", "Senior"],
        "lang":  "de",
    },
    {
        "id":    "faq-schueler",
        "title": "FAQ Schüler & Ausbildung",
        "url":   "https://www.basf.com/global/de/careers/for-pupils/FAQ_Onlinebewerbung",
        "desc":  "Ausbildungsberufe, duale Studiengänge, Bewerbung für Schüler.",
        "tags":  ["Schüler", "Ausbildung", "FAQ", "Duales Studium"],
        "lang":  "de",
    },
    {
        "id":    "faq-online-assessment",
        "title": "FAQ Online Assessment",
        "url":   "https://www.basf.com/global/de/careers/application/faq/questions-online-assessment",
        "desc":  "Online Assessment: Für welche Stellen, Vorbereitung, Ablauf, technische Anforderungen.",
        "tags":  ["Assessment", "Auswahl", "FAQ", "Online-Test"],
        "lang":  "de",
    },
    {
        "id":    "traineeprogramme",
        "title": "Traineeprogramme – START IN",
        "url":   "https://www.basf.com/global/de/careers/graduates/trainees",
        "desc":  "START IN Traineeprogramme: Engineering, Finance, IT, HR, Produktion. Struktur, Dauer, Voraussetzungen.",
        "tags":  ["Trainee", "START IN", "Einstieg", "Programme"],
        "lang":  "de",
    },
]
# ─────────────────────────────────────────────────────────────────────────────


# ── SCHRITT 1: DYNAMISCHE INHALTE AUFKLAPPEN ──────────────────────────────────
async def expand_dynamic_content(page):
    """
    Öffnet alle versteckten/eingeklappten Inhalte:
    - <details>/<summary> Elemente
    - aria-expanded=false Buttons (Akkordeons)
    - Custom Toggle-Klassen
    Läuft mehrere Runden bis nichts mehr aufzuklappen ist.
    """
    total = 0

    for runde in range(4):
        opened_this_round = 0

        # 1. <details> ohne open-Attribut öffnen
        n = await page.evaluate("""
            () => {
                const els = document.querySelectorAll('details:not([open])');
                els.forEach(d => d.setAttribute('open', ''));
                return els.length;
            }
        """)
        opened_this_round += n

        # 2. Alle aria-expanded=false Buttons klicken
        # (Navigation und Cookie-Banner ausschließen)
        n = await page.evaluate("""
            () => {
                const SKIP = ['Menü','Menu','Navigation','Cookie','Suche','Search',
                              'Language','Sprache','Share','Teilen'];
                const btns = document.querySelectorAll(
                    '[aria-expanded="false"], ' +
                    '[data-collapsed="true"], ' +
                    '.accordion__button:not(.active), ' +
                    '.collapsible__trigger:not(.is-active)'
                );
                let count = 0;
                btns.forEach(btn => {
                    const text = (btn.innerText || btn.getAttribute('aria-label') || '').trim();
                    if (SKIP.some(s => text.includes(s))) return;
                    // Nicht in Navigation
                    if (btn.closest('nav') || btn.closest('header') || btn.closest('footer')) return;
                    try { btn.click(); count++; } catch(e) {}
                });
                return count;
            }
        """)
        opened_this_round += n

        # 3. summary-Elemente in geschlossenen details
        n = await page.evaluate("""
            () => {
                const els = document.querySelectorAll('details:not([open]) summary');
                els.forEach(s => s.click());
                return els.length;
            }
        """)
        opened_this_round += n

        total += opened_this_round

        if opened_this_round == 0:
            break

        await page.wait_for_timeout(700)

    print(f"    🔓 {total} dynamische Elemente geöffnet ({runde+1} Runden)")
    return total


# ── SCHRITT 2: STRUKTURIERTEN CONTENT EXTRAHIEREN ────────────────────────────
async def extract_content(page):
    """
    Extrahiert den gesamten Seiten-Content als strukturierte Liste.
    Typen: heading, paragraph, list, table, accordion, quote
    """
    items = await page.evaluate("""
        () => {
            const SKIP_TEXT = [
                'Copyright © BASF','Follow us','Folge uns','BASF-Produktsuche',
                'Industrieauswahl','Presseinformationen','myBASFWorld',
                'Datenschutz-Präferenz','Impressum','Responsible Disclosure',
                'OBEN','Top Links','Empfohlene Links'
            ];

            const result = [];
            const seen   = new WeakSet();

            // Haupt-Content-Bereich
            const root = document.querySelector('main, [role="main"], .page-content, body');

            // Navigations-/Footer-Elemente ausschließen
            const excludeEls = new Set();
            root.querySelectorAll('nav, footer, header, [class*="footer"], [class*="header-nav"], .breadcrumb')
                .forEach(el => {
                    excludeEls.add(el);
                    el.querySelectorAll('*').forEach(c => excludeEls.add(c));
                });

            function isExcluded(el) {
                return excludeEls.has(el) || SKIP_TEXT.some(s => (el.textContent || '').trim().startsWith(s));
            }

            function processEl(el) {
                if (seen.has(el) || isExcluded(el)) return;
                seen.add(el);

                const tag  = el.tagName.toLowerCase();
                const text = (el.innerText || el.textContent || '').trim();
                if (!text || text.length < 3) return;

                // Headings
                if (/^h[1-5]$/.test(tag)) {
                    result.push({ type: 'heading', level: parseInt(tag[1]), text });
                    return;
                }

                // Paragraphs
                if (tag === 'p' && text.length > 8) {
                    result.push({ type: 'paragraph', text });
                    return;
                }

                // Listen
                if (tag === 'ul' || tag === 'ol') {
                    const items = Array.from(el.querySelectorAll(':scope > li'))
                        .map(li => li.innerText.trim())
                        .filter(t => t.length > 2);
                    if (items.length) {
                        result.push({ type: 'list', ordered: tag === 'ol', items });
                        el.querySelectorAll('*').forEach(c => seen.add(c));
                    }
                    return;
                }

                // Tabellen
                if (tag === 'table') {
                    const rows = [];
                    el.querySelectorAll('tr').forEach(tr => {
                        const isHeader = !!tr.querySelector('th');
                        const cells = Array.from(tr.querySelectorAll('th,td'))
                            .map(c => c.innerText.trim());
                        if (cells.some(c => c)) rows.push({ isHeader, cells });
                    });
                    if (rows.length) result.push({ type: 'table', rows });
                    el.querySelectorAll('*').forEach(c => seen.add(c));
                    return;
                }

                // <details>/<summary> Akkordeons (jetzt offen)
                if (tag === 'details') {
                    const summary = el.querySelector('summary');
                    const q = summary ? summary.innerText.trim() : '';
                    // Antwort = alles außer summary
                    const clone = el.cloneNode(true);
                    clone.querySelector('summary')?.remove();
                    const a = clone.innerText.trim();
                    if (q && a) result.push({ type: 'accordion', question: q, answer: a });
                    el.querySelectorAll('*').forEach(c => seen.add(c));
                    return;
                }

                // aria-controls Akkordeon (button + Panel)
                if (tag === 'button' && el.getAttribute('aria-controls')) {
                    const q = text;
                    const panelId = el.getAttribute('aria-controls');
                    const panel = document.getElementById(panelId);
                    const a = panel ? panel.innerText.trim() : '';
                    if (q && a && a.length > 5) {
                        result.push({ type: 'accordion', question: q, answer: a });
                        if (panel) panel.querySelectorAll('*').forEach(c => seen.add(c));
                    }
                    return;
                }

                // Blockquote
                if (tag === 'blockquote' && text.length > 10) {
                    result.push({ type: 'quote', text });
                    return;
                }

                // Generischer Container → Kinder verarbeiten
                if (['div','section','article','main','aside'].includes(tag)) {
                    Array.from(el.children).forEach(processEl);
                }
            }

            Array.from(root.children).forEach(processEl);
            return result;
        }
    """)

    return items or []


# ── SCHRITT 3: CONTENT → SEMANTIC HTML ───────────────────────────────────────
def to_html(items):
    """Wandelt strukturierte Item-Liste in sauberes Semantic HTML um."""
    parts          = []
    faq_buf        = []
    open_section   = False

    def flush_faq():
        if not faq_buf:
            return
        parts.append('<section class="faq-section">')
        for it in faq_buf:
            q = esc(it['question'])
            a = esc(it['answer']).replace('\n', '<br>')
            parts.append(
                f'<article class="faq-item">\n'
                f'  <h3 class="faq-question">{q}</h3>\n'
                f'  <div class="faq-answer"><p>{a}</p></div>\n'
                f'</article>'
            )
        parts.append('</section>')
        faq_buf.clear()

    def esc(t):
        return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    def slug(t):
        t = t.lower()
        for a, b in [('ä','ae'),('ö','oe'),('ü','ue'),('ß','ss')]:
            t = t.replace(a, b)
        return re.sub(r'[^a-z0-9]+', '-', t).strip('-')[:40]

    for it in items:
        tp = it.get('type')

        if tp == 'heading':
            flush_faq()
            lvl  = it['level']
            text = esc(it['text'])
            sid  = slug(it['text'])
            if lvl == 1:
                parts.append(f'<h1 id="{sid}">{text}</h1>')
            elif lvl == 2:
                if open_section:
                    parts.append('</section>')
                parts.append(f'<section id="{sid}">\n<h2>{text}</h2>')
                open_section = True
            else:
                parts.append(f'<h{lvl} id="{sid}">{text}</h{lvl}>')

        elif tp == 'paragraph':
            flush_faq()
            text = esc(it['text'])
            text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
            parts.append(f'<p>{text}</p>')

        elif tp == 'list':
            flush_faq()
            tag   = 'ol' if it.get('ordered') else 'ul'
            items_html = '\n'.join(f'  <li>{esc(li)}</li>' for li in it['items'])
            parts.append(f'<{tag}>\n{items_html}\n</{tag}>')

        elif tp == 'table':
            flush_faq()
            rows = it['rows']
            if not rows:
                continue
            tbl = ['<table>']
            header = [r for r in rows if r.get('isHeader')]
            body   = [r for r in rows if not r.get('isHeader')]
            if header:
                tbl.append('  <thead>')
                for r in header:
                    tbl.append('    <tr>' + ''.join(f'<th>{esc(c)}</th>' for c in r['cells']) + '</tr>')
                tbl.append('  </thead>')
            tbl.append('  <tbody>')
            for r in body:
                tbl.append('    <tr>' + ''.join(f'<td>{esc(c)}</td>' for c in r['cells']) + '</tr>')
            tbl.append('  </tbody>\n</table>')
            parts.append('\n'.join(tbl))

        elif tp == 'accordion':
            faq_buf.append(it)

        elif tp == 'quote':
            flush_faq()
            parts.append(f'<blockquote><p>{esc(it["text"])}</p></blockquote>')

    flush_faq()
    if open_section:
        parts.append('</section>')

    return '\n'.join(parts)


# ── SCHRITT 4: VOLLSTÄNDIGE KB-SEITE GENERIEREN ───────────────────────────────
def make_page(source, content_html, stats, timestamp):
    tags  = ''.join(f'<span class="tag">{t}</span>' for t in source['tags'])
    return f"""<!DOCTYPE html>
<html lang="{source['lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{source['desc']}">
<meta name="keywords" content="{', '.join(source['tags'])}">
<title>{source['title']} – BASF Knowledgebase</title>
<style>
  body         {{ font-family: Arial, sans-serif; max-width: 920px; margin: 40px auto; padding: 0 20px; color: #333; line-height: 1.8; }}
  h1           {{ color: #004a96; font-size: 1.7em; }}
  h2           {{ color: #004a96; border-bottom: 2px solid #004a96; padding-bottom: 5px; margin-top: 36px; }}
  h3           {{ color: #333; margin-top: 16px; }}
  nav a        {{ color: #004a96; text-decoration: none; font-size: 0.9em; }}
  .desc-box    {{ background: #f0f5ff; border-left: 4px solid #004a96; padding: 12px 16px; margin: 16px 0 28px; border-radius: 0 4px 4px 0; }}
  .desc-box p  {{ margin: 0 0 6px 0; font-size: 0.95em; color: #444; }}
  .tag         {{ display: inline-block; background: #e0ecff; color: #004a96; font-size: 0.78em; padding: 2px 8px; border-radius: 3px; margin-right: 4px; }}
  .source      {{ font-size: 0.8em; color: #888; margin-top: 4px; }}
  .source a    {{ color: #004a96; }}
  .stats       {{ background: #f5fff5; border: 1px solid #b0d8b0; border-radius: 4px; padding: 8px 16px; margin-bottom: 20px; font-size: 0.84em; color: #333; }}
  /* FAQ */
  .faq-section {{ margin: 12px 0 24px 0; }}
  .faq-item    {{ border: 1px solid #d8e8ff; border-radius: 6px; margin-bottom: 8px; overflow: hidden; }}
  .faq-question {{ background: #eef4ff; color: #004a96; margin: 0; padding: 12px 16px; font-size: 0.97em; font-weight: bold; border-bottom: 1px solid #d8e8ff; }}
  .faq-answer  {{ padding: 12px 16px; background: #fff; font-size: 0.92em; }}
  .faq-answer p {{ margin: 0; }}
  /* Tabellen */
  table        {{ border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 0.9em; }}
  th, td       {{ border: 1px solid #ddd; padding: 9px 13px; text-align: left; vertical-align: top; }}
  th           {{ background: #004a96; color: #fff; }}
  tr:nth-child(even) {{ background: #f6f9ff; }}
  /* Zitate */
  blockquote   {{ background: #f9f9f9; border-left: 4px solid #004a96; padding: 12px 18px; margin: 16px 0; font-style: italic; color: #555; border-radius: 0 4px 4px 0; }}
  ul, ol       {{ padding-left: 22px; }}
  li           {{ margin-bottom: 4px; }}
  footer       {{ font-size: 0.8em; color: #aaa; margin-top: 40px; border-top: 1px solid #eee; padding-top: 12px; }}
</style>
</head>
<body>

<nav id="breadcrumb">
  <a href="{BASE_URL}/index.html">← BASF Knowledgebase Übersicht</a>
</nav>

<main id="content">
  <header>
    <h1>{source['title']}</h1>
    <div class="desc-box">
      <p><strong>Was ist auf dieser Seite:</strong> {source['desc']}</p>
      <p style="margin-top:6px">{tags}</p>
      <p class="source">Quelle: <a href="{source['url']}" target="_blank">{source['url']}</a></p>
    </div>
    <p class="stats">
      Extrahiert: <strong>{stats.get('total',0)}</strong> Elemente |
      FAQ/Akkordeons: <strong>{stats.get('faq_items',0)}</strong> |
      Tabellen: <strong>{stats.get('tables',0)}</strong> |
      Dynamisch geöffnet: <strong>{stats.get('opened',0)}</strong>
    </p>
  </header>

  <article id="main-content">
    {content_html}
  </article>
</main>

<footer>
  <p>Zuletzt aktualisiert: {timestamp} | Quelle: <a href="{source['url']}">{source['url']}</a></p>
</footer>
</body>
</html>"""


# ── MAIN ──────────────────────────────────────────────────────────────────────
async def main():
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs("kb", exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
            locale="de-DE",
        )
        page = await context.new_page()

        success = 0
        for source in SOURCES:
            print(f"\n📖 {source['title']}")
            print(f"   {source['url']}")

            # Seite laden
            try:
                await page.goto(source['url'], timeout=60000, wait_until="networkidle")
            except Exception:
                try:
                    await page.goto(source['url'], timeout=60000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(3000)
                except Exception as e:
                    print(f"  ❌ Ladefehler: {e}")
                    continue

            # Cookie-Banner wegklicken
            for txt in ['Alle akzeptieren', 'Accept all', 'Akzeptieren']:
                try:
                    btn = page.get_by_role("button", name=txt)
                    if await btn.is_visible():
                        await btn.click()
                        await page.wait_for_timeout(500)
                        break
                except Exception:
                    pass

            await page.wait_for_timeout(1500)

            # Dynamische Inhalte aufklappen
            print(f"  🔄 Klappe dynamischen Content auf...")
            opened = await expand_dynamic_content(page)

            # Nochmals warten
            await page.wait_for_timeout(1000)

            # Content extrahieren
            print(f"  📊 Extrahiere Content...")
            items = await extract_content(page)

            stats = {
                'opened':    opened,
                'faq_items': sum(1 for i in items if i.get('type') == 'accordion'),
                'tables':    sum(1 for i in items if i.get('type') == 'table'),
                'total':     len(items),
            }
            print(f"  ✅ {stats['total']} Elemente | {stats['faq_items']} FAQ | {stats['tables']} Tabellen")

            # HTML generieren
            content_html = to_html(items)
            page_html    = make_page(source, content_html, stats, timestamp)

            path = f"kb/{source['id']}.html"
            with open(path, "w", encoding="utf-8") as f:
                f.write(page_html)
            print(f"  💾 {path} gespeichert")
            success += 1

        await browser.close()

    # Index-Timestamp aktualisieren
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            idx = f.read()
        idx = idx.replace("siehe scrape.yml", timestamp)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(idx)
        print("✅ index.html aktualisiert")
    except Exception:
        pass

    print(f"\n✅ {success}/{len(SOURCES)} Seiten generiert!")


asyncio.run(main())
