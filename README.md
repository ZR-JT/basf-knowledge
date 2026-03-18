# basf-knowledge

Automatische BASF Knowledgebase für AI-Agenten. Scrapt wöchentlich offizielle BASF-Seiten und speichert die Inhalte als strukturiertes Semantic HTML auf GitHub Pages.

---

## Live URLs

```
https://ZR-JT.github.io/basf-knowledge/index.html              ← Übersicht
https://ZR-JT.github.io/basf-knowledge/kb/warum-basf.html
https://ZR-JT.github.io/basf-knowledge/kb/strategie.html
https://ZR-JT.github.io/basf-knowledge/kb/werte.html
https://ZR-JT.github.io/basf-knowledge/kb/diversity.html
https://ZR-JT.github.io/basf-knowledge/kb/faq-bewerbung.html
https://ZR-JT.github.io/basf-knowledge/kb/faq-studierende.html
https://ZR-JT.github.io/basf-knowledge/kb/faq-berufseinsteiger.html
https://ZR-JT.github.io/basf-knowledge/kb/faq-berufserfahrene.html
https://ZR-JT.github.io/basf-knowledge/kb/faq-schueler.html
https://ZR-JT.github.io/basf-knowledge/kb/faq-online-assessment.html
https://ZR-JT.github.io/basf-knowledge/kb/traineeprogramme.html
```

---

## Knowledgebases

| Seite | Inhalt | Tags |
|---|---|---|
| warum-basf | Arbeitgeber, Benefits, Kultur | Karriere, Benefits |
| strategie | Winning Ways, 4 Hebel, Finanzziele | Strategie, CEO |
| werte | CORE-Werte, Compliance, Standards | Werte, CORE |
| diversity | DE&I, Netzwerke, Initiativen | Diversity, Inklusion |
| faq-bewerbung | Ablauf, Unterlagen, Vergütung | Bewerbung, FAQ |
| faq-studierende | Praktika, Gap-Year, Ausland, Stipendium | Studierende, FAQ |
| faq-berufseinsteiger | Direkteinstieg, Trainee, Assessment | Absolventen, FAQ |
| faq-berufserfahrene | Professionals, Senior, Quereinstieg | Erfahrene, FAQ |
| faq-schueler | Ausbildung, Duales Studium | Schüler, FAQ |
| faq-online-assessment | Assessment-Ablauf, Vorbereitung | Assessment, FAQ |
| traineeprogramme | START IN Programme, Voraussetzungen | Trainee, START IN |

---

## Wie es funktioniert

```
Jeden Montag:
  Playwright öffnet jede BASF-Quellenseite
  → Text wird extrahiert und bereinigt
  → Semantic HTML wird generiert (main, article, section, dl)
  → GitHub Actions committed alle kb/*.html Dateien
  → GitHub Pages stellt sie bereit
  → AI-Agent liest die strukturierten Seiten
```

---

## Für den AI-Agenten

```
Einstieg: https://ZR-JT.github.io/basf-knowledge/index.html
→ Übersicht zeigt alle verfügbaren Knowledgebases mit Beschreibung
→ Passende Seite direkt per URL abrufen
→ Jede Seite erklärt am Anfang was sie enthält (desc-box)
```

---

## GitHub Pages einrichten

1. Repo → Settings → Pages
2. Branch: `main` | Folder: `/ (root)`
3. Save
