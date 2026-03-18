import asyncio
import re
import os
from playwright.async_api import async_playwright
from datetime import datetime

# ── KONFIGURATION ─────────────────────────────────────────────────────────────
BASE_URL = "https://ZR-JT.github.io/basf-knowledge"

SOURCES = [
    {
        "id":       "warum-basf",
        "title":    "Warum BASF – Arbeitgeber & Benefits",
        "url":      "https://www.basf.com/global/de/careers/why-join-basf",
        "desc":     "Informationen darüber warum BASF ein attraktiver Arbeitgeber ist: Unternehmenskultur, CORE-Werte, Benefits, Karrieremöglichkeiten und Work-Life-Balance.",
        "tags":     ["Karriere", "Benefits", "Kultur", "Arbeitgeber"],
        "lang":     "de",
    },
    {
        "id":       "strategie",
        "title":    "Strategie – Winning Ways",
        "url":      "https://www.basf.com/global/de/who-we-are/strategy",
        "desc":     "Die Unternehmensstrategie von BASF: Winning Ways mit den vier Hebeln Focus, Accelerate, Transform und Win. Finanzielle Ziele und Winning Culture.",
        "tags":     ["Strategie", "Unternehmen", "Winning Ways", "CEO"],
        "lang":     "de",
    },
    {
        "id":       "werte",
        "title":    "Unsere Werte – CORE",
        "url":      "https://www.basf.com/global/de/who-we-are/about-us/our-values",
        "desc":     "Die vier CORE-Werte von BASF: Creative, Open, Responsible, Entrepreneurial. Internationale Standards, Verhaltenskodex und Compliance-Grundsätze.",
        "tags":     ["Werte", "CORE", "Compliance", "Standards"],
        "lang":     "de",
    },
    {
        "id":       "diversity",
        "title":    "Diversity, Equity & Inclusion",
        "url":      "https://www.basf.com/global/de/careers/why-join-basf/diversity",
        "desc":     "DE&I Strategie bei BASF: Vielfalt fördern, Geschlechterbalance, Beschäftigtennetzwerke, externes Engagement und globale Initiativen.",
        "tags":     ["Diversity", "Inklusion", "DE&I", "Chancengleichheit"],
        "lang":     "de",
    },
    {
        "id":       "faq-bewerbung",
        "title":    "FAQ Bewerbungsprozess",
        "url":      "https://www.basf.com/global/de/careers/application/faq/questions-for-students",
        "desc":     "Häufig gestellte Fragen zum Bewerbungsprozess bei BASF: Ablauf, Unterlagen, Interviews, Vergütungstabelle für Studierende, Datenschutz.",
        "tags":     ["Bewerbung", "FAQ", "Prozess", "Interviews"],
        "lang":     "de",
    },
    {
        "id":       "faq-studierende",
        "title":    "FAQ Studierende & Praktika",
        "url":      "https://www.basf.com/global/de/careers/application/faq/questions-for-students",
        "desc":     "FAQ für Studierende: Praktikumsarten, Gap-Year, Auslandspraktikum Explore Together, Abschlussarbeiten, Doktorarbeiten, Deutschlandstipendium.",
        "tags":     ["Studierende", "Praktikum", "FAQ", "Explore Together"],
        "lang":     "de",
    },
    {
        "id":       "faq-berufseinsteiger",
        "title":    "FAQ Berufseinsteiger & Absolventen",
        "url":      "https://www.basf.com/global/de/careers/application/faq/questions-for-graduates",
        "desc":     "FAQ für Absolventen und Berufseinsteiger: Direkteinstieg, Traineeprogramme, Assessment Center, erste Stelle bei BASF.",
        "tags":     ["Absolventen", "Einstieg", "FAQ", "Direkteinstieg"],
        "lang":     "de",
    },
    {
        "id":       "faq-berufserfahrene",
        "title":    "FAQ Berufserfahrene",
        "url":      "https://www.basf.com/global/de/careers/application/faq/questions-for-professionals",
        "desc":     "FAQ für erfahrene Fachkräfte: Bewerbungsprozess für Professionals, Quereinstieg, Senior-Level, internationale Möglichkeiten.",
        "tags":     ["Professionals", "Erfahrene", "FAQ", "Senior"],
        "lang":     "de",
    },
    {
        "id":       "faq-schueler",
        "title":    "FAQ Schüler & Ausbildung",
        "url":      "https://www.basf.com/global/de/careers/for-pupils/FAQ_Onlinebewerbung",
        "desc":     "FAQ für Schüler: Ausbildungsberufe, duale Studiengänge, Bewerbung, Online-Bewerbungsprozess, Voraussetzungen.",
        "tags":     ["Schüler", "Ausbildung", "FAQ", "Duales Studium"],
        "lang":     "de",
    },
    {
        "id":       "faq-online-assessment",
        "title":    "FAQ Online Assessment",
        "url":      "https://www.basf.com/global/de/careers/application/faq/questions-online-assessment",
        "desc":     "FAQ zum Online Assessment: Für welche Stellen es gilt, Vorbereitung, Ablauf und technische Anforderungen.",
        "tags":     ["Assessment", "Auswahl", "FAQ", "Online-Test"],
        "lang":     "de",
    },
    {
        "id":       "traineeprogramme",
        "title":    "Traineeprogramme – START IN",
        "url":      "https://www.basf.com/global/de/careers/graduates/trainees",
        "desc":     "BASF START IN Traineeprogramme: Engineering, Finance, IT, HR, Produktion. Programmstruktur, Dauer, Voraussetzungen und Bewerbungsweg.",
        "tags":     ["Trainee", "START IN", "Einstieg", "Programme"],
        "lang":     "de",
    },
]
# ─────────────────────────────────────────────────────────────────────────────


def clean_text(text):
    """Bereinigt extrahierten Text."""
    if not text:
        return ""
    # Mehrfache Leerzeichen/Zeilenumbrüche reduzieren
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    # Navigation/Footer entfernen (typische Muster)
    lines = text.split('\n')
    clean_lines = []
    skip_patterns = [
        'Copyright © BASF',
        'Follow us', 'Folge uns',
        'BASF-Produktsuche', 'Industrieauswahl',
        'Presseinformationen', 'myBASFWorld',
        'Datenschutz-Präferenz', 'Impressum',
        'Responsible Disclosure',
        'OBEN',
    ]
    for line in lines:
        if any(p in line for p in skip_patterns):
            break
        clean_lines.append(line)
    return '\n'.join(clean_lines).strip()


def text_to_semantic_html(text, source):
    """
    Wandelt bereinigten Text in semantisches HTML um.
    Optimiert für AI-Agent Lesbarkeit.
    """
    lines = text.split('\n')
    html_parts = []
    in_faq = False
    faq_items = []
    current_question = None
    current_answer_lines = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        # H1 → wird zum Seiten-Titel (bereits im Header)
        if line.startswith('# ') and not line.startswith('## '):
            i += 1
            continue

        # H2 → section
        elif line.startswith('## '):
            heading = line[3:].strip()
            if heading.startswith('**') and heading.endswith('**'):
                heading = heading[2:-2]
            html_parts.append(f'</section>\n<section id="section-{_slug(heading)}">\n<h2>{heading}</h2>')
            i += 1
            continue

        # H3 → h3 (FAQ-Fragen)
        elif line.startswith('### '):
            question = line[4:].strip()
            # Sammle Antwort-Zeilen
            answer_lines = []
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if next_line.startswith('### ') or next_line.startswith('## '):
                    break
                if next_line:
                    answer_lines.append(next_line)
                i += 1
            answer = ' '.join(answer_lines)
            # Markdown-Links bereinigen
            answer = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', answer)
            answer = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', answer)
            html_parts.append(
                f'<article class="faq-item">\n'
                f'  <h3>{question}</h3>\n'
                f'  <p>{answer}</p>\n'
                f'</article>'
            )
            continue

        # Tabellen (Markdown) → HTML table
        elif line.startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1
            if len(table_lines) >= 2:
                html_parts.append(_md_table_to_html(table_lines))
            continue

        # Blockquote → aside
        elif line.startswith('>'):
            quote = line[1:].strip()
            quote = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', quote)
            html_parts.append(f'<aside class="quote"><p>{quote}</p></aside>')
            i += 1
            continue

        # Bullet-Liste
        elif line.startswith('* ') or line.startswith('- ') or line.startswith('1. '):
            list_lines = []
            while i < len(lines):
                l = lines[i].strip()
                if l.startswith('* ') or l.startswith('- ') or re.match(r'^\d+\. ', l):
                    item = re.sub(r'^[\*\-\d\.]+\s*', '', l)
                    item = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', item)
                    item = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', item)
                    list_lines.append(f'  <li>{item}</li>')
                    i += 1
                else:
                    break
            if list_lines:
                html_parts.append('<ul>\n' + '\n'.join(list_lines) + '\n</ul>')
            continue

        # Bold-Paragraphen
        else:
            para = line
            para = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', para)
            para = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', para)
            if para:
                html_parts.append(f'<p>{para}</p>')
            i += 1
            continue

    return '\n'.join(html_parts)


def _slug(text):
    text = text.lower()
    text = re.sub(r'[äÄ]', 'ae', text)
    text = re.sub(r'[öÖ]', 'oe', text)
    text = re.sub(r'[üÜ]', 'ue', text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')[:40]


def _md_table_to_html(lines):
    rows = []
    for line in lines:
        if re.match(r'^\|[\s\-\|]+\|$', line):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        rows.append(cells)

    if not rows:
        return ''

    html = '<table>\n'
    # Erste Zeile als Header
    html += '  <thead><tr>'
    for cell in rows[0]:
        html += f'<th>{cell}</th>'
    html += '</tr></thead>\n  <tbody>\n'
    for row in rows[1:]:
        html += '  <tr>'
        for cell in row:
            html += f'<td>{cell}</td>'
        html += '</tr>\n'
    html += '  </tbody>\n</table>'
    return html


def generate_kb_page(source, content_text, timestamp):
    """Generiert eine vollständige KB-Seite als Semantic HTML."""

    tags_html = ''.join(f'<span class="tag">{t}</span>' for t in source['tags'])

    # Content in semantisches HTML umwandeln
    body_html = text_to_semantic_html(content_text, source)

    html = f"""<!DOCTYPE html>
<html lang="{source['lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{source['desc']}">
<meta name="keywords" content="{', '.join(source['tags'])}">
<title>{source['title']} – BASF Knowledgebase</title>
<style>
  body       {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; color: #333; line-height: 1.7; }}
  h1         {{ color: #004a96; font-size: 1.7em; }}
  h2         {{ color: #004a96; border-bottom: 1px solid #cde; padding-bottom: 5px; margin-top: 32px; }}
  h3         {{ color: #333; margin-top: 20px; }}
  nav a      {{ color: #004a96; text-decoration: none; font-size: 0.9em; }}
  .desc-box  {{ background: #f0f5ff; border-left: 4px solid #004a96; padding: 12px 16px; margin: 16px 0 24px 0; border-radius: 0 4px 4px 0; }}
  .desc-box p {{ margin: 0; font-size: 0.95em; color: #444; }}
  .tag       {{ display: inline-block; background: #e0ecff; color: #004a96; font-size: 0.78em; padding: 2px 8px; border-radius: 3px; margin-right: 4px; }}
  .source    {{ font-size: 0.8em; color: #888; margin-top: 4px; }}
  .source a  {{ color: #004a96; }}
  .faq-item  {{ border-bottom: 1px solid #eee; padding: 14px 0; }}
  .faq-item h3 {{ margin: 0 0 8px 0; color: #004a96; font-size: 1em; }}
  .faq-item p  {{ margin: 0; font-size: 0.93em; }}
  .quote     {{ background: #f9f9f9; border-left: 4px solid #004a96; padding: 10px 16px; margin: 16px 0; font-style: italic; color: #555; }}
  table      {{ border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 0.9em; }}
  th, td     {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
  th         {{ background: #004a96; color: #fff; }}
  tr:nth-child(even) {{ background: #f8f8f8; }}
  ul         {{ padding-left: 20px; }}
  li         {{ margin-bottom: 4px; }}
  aside.quote {{ border-radius: 0 4px 4px 0; }}
  footer     {{ font-size: 0.8em; color: #aaa; margin-top: 40px; border-top: 1px solid #eee; padding-top: 12px; }}
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
      <p style="margin-top:6px">{tags_html}</p>
      <p class="source">Quelle: <a href="{source['url']}" target="_blank">{source['url']}</a></p>
    </div>
  </header>

  <section id="main-content">
    {body_html}
  </section>

</main>

<footer>
  <p>Zuletzt aktualisiert: {timestamp} | Quelle: <a href="{source['url']}">{source['url']}</a></p>
</footer>

</body>
</html>"""

    return html


def generate_index(sources, timestamp):
    """Aktualisiert den Timestamp in der index.html."""
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace(
        'siehe scrape.yml',
        timestamp
    )
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ index.html Timestamp aktualisiert")


async def scrape_page(page, url):
    """Scrapt eine Seite und gibt den bereinigten Text zurück."""
    try:
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        # Versuche zuerst den Haupt-Content-Bereich
        content = None
        for selector in ['main', 'article', '#content', '.content', 'body']:
            try:
                el = await page.query_selector(selector)
                if el:
                    content = await el.inner_text()
                    if len(content) > 200:
                        break
            except Exception:
                continue

        if not content:
            content = await page.inner_text('body')

        return clean_text(content)

    except Exception as e:
        print(f"  ❌ Fehler beim Laden von {url}: {e}")
        return ""


async def main():
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    os.makedirs("kb", exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900},
        )
        page = await context.new_page()

        for source in SOURCES:
            print(f"\n📖 Scrape: {source['title']}")
            print(f"   URL: {source['url']}")

            text = await scrape_page(page, source['url'])

            if not text:
                print(f"  ⚠ Kein Inhalt gefunden — überspringe")
                continue

            print(f"  ✅ {len(text)} Zeichen extrahiert")

            # KB-Seite generieren
            html = generate_kb_page(source, text, timestamp)
            filepath = f"kb/{source['id']}.html"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"  💾 {filepath} gespeichert")

        await browser.close()

    # Index aktualisieren
    generate_index(SOURCES, timestamp)

    print(f"\n✅ Alle {len(SOURCES)} Knowledgebase-Seiten generiert!")


asyncio.run(main())
