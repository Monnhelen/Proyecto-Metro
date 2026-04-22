# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a static data visualization project analyzing accessibility in the Mexico City Metro (Sistema de Transporte Colectivo Metro, CDMX). It has no build system — all files are plain HTML/CSS/JavaScript opened directly in a browser.

## Running the Project

Open any HTML file directly in a browser, or serve with any static file server:

```bash
python3 -m http.server 8080
# then open http://localhost:8080
```

No dependencies to install. No build step.

## File Structure and Architecture

### HTML Files (three standalone visualizations)

- **`index.html`** — Primary interactive map. The most complex file. Features:
  - D3.js v7.8.5 force-layout network graph of metro stations
  - Dark/light theme toggle (CSS custom properties on `:root` and `body.light`)
  - Sidebar with station search (autocomplete), route finder, and radial proximity analysis
  - Overlay modes: Accessibility, Ridership (`afluencia`), Radial analysis
  - Intro panel (editorial narrative mode) that hides the map and sidebar
  - Download menu (SVG/PNG export) and overlay options
  - All data is inlined in the JS — no fetch calls

- **`metro-accesibilidad.html`** — Long-form editorial/narrative article about metro accessibility. Uses a fixed light theme (same CSS variables as `index.html` light mode). Includes a scrolling progress bar and a dot-plot visualization (`#v3-svg`) built with D3.

- **`network_metro_cdmx.html`** — Standalone network graph with three view modes: Network (force layout), Radial, and Arch. Darker aesthetic than the other files.

### Data Files (`data/`)

- **`nodos.csv`** — Station nodes. Columns: `id, Linea, Orden, Tipo, Elevador, EE, Accesibilidad, Personas_Afectadas, lat, lng`
  - `Tipo`: Terminal / Transbordo (transfer) / Intermedia
  - `Elevador`: Si/No — elevator present
  - `EE`: Si/No — "Estación Especial" / accessible entrance
  - `Accesibilidad`: Si/No — overall accessibility rating
  - `Personas_Afectadas`: estimated daily ridership affected by inaccessibility

- **`aristas.csv`** — Edges. Columns: `source, target, Tipo, Linea, Accesible_PCD`
  - `Tipo`: Secuencial (sequential along a line) or Transbordo (transfer between lines)
  - `Accesible_PCD`: 1/0 — accessible for persons with disabilities

### Assets

- `Mapa_metro_2026-scaled.png` — Official metro map image (2026 version)
- `Visualización 1.png` — Tableau/BI visualization screenshot used in the article

## Design System

All three HTML files share the same CSS custom property naming convention:

```css
--bg, --panel, --card, --border          /* backgrounds */
--text, --text2, --text3                  /* text hierarchy */
--accent, --green, --orange, --red        /* semantic colors */
--mono, --sans, --serif                   /* font families */
```

`index.html` supports dark (default) and light themes via `body.light` class. `metro-accesibilidad.html` is always light. `network_metro_cdmx.html` is always dark.

Font stack: **DM Sans** (body/UI), **Space Mono** (labels/code/monospace), **Playfair Display** (editorial headlines).

## Key Conventions

- CSS is minified/compressed in `index.html` (single-line rules). `metro-accesibilidad.html` uses spaced-out CSS with section comments.
- Station IDs in `nodos.csv` use underscores with line suffixes for transfer stations (e.g., `Tacubaya_1`, `Tacubaya_2`) since the same physical station appears on multiple lines.
- Line colors for CDMX metro lines are hardcoded in JS objects (not in CSS). Line 1 = pink, Line 2 = blue, etc., following official STC colors.
- `index.html` inlines all station/edge data in JavaScript rather than fetching the CSV files at runtime.
