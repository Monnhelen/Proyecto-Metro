# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Static data visualization project analyzing accessibility in the Mexico City Metro (STC Metro, CDMX). No build system — all files are plain HTML/CSS/JavaScript opened directly in a browser.

## Running the Project

```bash
python3 -m http.server 8080
# then open http://localhost:8080
```

No dependencies to install. No build step. The font files in `Tipografías/` must be served over HTTP (not `file://`) for `@font-face` to load correctly.

## Site Architecture and Navigation

The four active pages link to each other via a shared top-nav:

| File | Role | Theme |
|---|---|---|
| `intro.html` | Editorial narrative ("Reportaje") — entry point | Always light |
| `index.html` | Interactive force-layout network map | Dark (default) / Light toggle |
| `Radial.html` | Standalone radial + arch view of the network | Dark (default) / Light toggle |
| `mapa-accesibilidad.html` | Geographic map with accessibility/ridership overlays | Always light |

Additional files not part of the main navigation:
- `intro2.html` — alternate/in-progress version of the intro page; do not treat as canonical
- `metro-accesibilidad.html` — older long-form article with D3 dot-plot (`#v3-svg`)
- `network_metro_cdmx.html` — older standalone network graph (Network / Radial / Arch views)

`Versiones anteriores/` and `Corregir/` contain archived/reference material — do not edit these.

## Key Files and Their Roles

### `intro.html`
The main editorial page. Uses **Leaflet 1.9.4** for geographic rendering (not D3 SVG), loaded on top of `basemap_data.js`. Also embeds the D3 dot-plot visualization (`#v3-svg`) and editorial hero section with `Foto/imglargaaaa.jpg`. Uses the custom `tipo_metro_cdmx` typeface for display headings (referenced as `var(--metro)`).

### `index.html`
The most complex file. D3.js v7.8.5 force-layout network graph. **All station and edge data is inlined in the JS** — no fetch calls, no dependency on `data/*.csv` at runtime. Features: dark/light theme toggle, sidebar with station search + route finder + radial proximity analysis, overlay modes (Accessibility / Ridership / Radial), SVG/PNG export.

### `Radial.html`
Standalone radial visualization. Shares similar CSS variable system with `index.html` and supports the same dark/light toggle. Uses Satoshi (via fontshare.com CDN) as the primary sans-serif.

### `mapa-accesibilidad.html`
SVG-based geographic map (D3, no Leaflet). Sidebar shows per-line accessibility stats. Three view modes: Accesibilidad / Afluencia / Solo red. Does **not** use `basemap_data.js`.

### `basemap_data.js`
Auto-generated file (~18 MB). Contains two JS constants:
- `BASEMAP_MANZANAS` — GeoJSON FeatureCollection of CDMX city blocks (manzanas)
- `BASEMAP_MUN15` — GeoJSON FeatureCollection of Estado de México municipalities

**Do not edit by hand** and is excluded from git via `.gitignore`. Regenerate using `convert_shapefiles.py` if the source shapefiles change:
```bash
pip install pyshp
python3 convert_shapefiles.py
```
The script reads shapefiles from `Mapa/` (absolute paths hardcoded in the script) and overwrites `basemap_data.js`.

## Data Files (`data/`)

- **`nodos.csv`** — Station nodes: `id, Linea, Orden, Tipo, Elevador, EE, Accesibilidad, Personas_Afectadas, lat, lng`
  - `Tipo`: Terminal / Transbordo / Intermedia
  - `Elevador` / `EE` / `Accesibilidad`: Si/No
  - Transfer stations appear multiple times with line suffixes (e.g., `Tacubaya_1`, `Tacubaya_2`)

- **`aristas.csv`** — Edges: `source, target, Tipo, Linea, Accesible_PCD`
  - `Tipo`: Secuencial (along a line) or Transbordo (between lines)
  - `Accesible_PCD`: 1/0

`index.html` inlines this data directly in JS rather than fetching at runtime. If you update the CSVs, you must also update the inlined data in `index.html`.

## Design System

All HTML files share the same CSS custom property names:

```css
--bg, --panel, --card, --border     /* backgrounds */
--text, --text2, --text3            /* text hierarchy */
--accent, --green, --orange, --red  /* semantic colors */
--mono, --sans, --serif             /* font families */
--metro                             /* tipo_metro_cdmx (intro.html only) */
```

Light/dark theming is done via `body.light` class on the `<body>` element. Files with a fixed theme just don't include the `body.light` override block.

**Font stack:**
- `DM Sans` — primary UI/body (Google Fonts)
- `Space Mono` — labels, stats, monospace values (Google Fonts)
- `Playfair Display` — editorial headlines (Google Fonts, used in `metro-accesibilidad.html`)
- `Satoshi` — primary sans in `Radial.html` (fontshare.com CDN)
- `tipo_metro_cdmx` — official STC Metro typeface, used for display headings in `intro.html`. Served from `Tipografías/Metro/Web Fonts/tipometrocdmx_regular_macroman/` (woff2 + woff). Four weights available: Regular, Bold, Light, and their italics.

**Line colors** are hardcoded in JS objects (not CSS). Line 1 = pink (`#E4538F`), Line 2 = blue (`#0069A7`), etc., following official STC colors.

## Static Assets

- `cargando/` — PNG images for individual Metro stations (one per station, named by station slug). Used as thumbnails or loading visuals in `intro.html`.
- `Foto/` — Hero/editorial photography.
- `SVG/` — Vector icons and line-symbol assets.
- `Iconografía/` — Accessibility and UI iconography.
- `Número de línea de Metro/` — Official Metro line-number badge assets.

## CSS Conventions

- `index.html`: CSS is minified to single-line rules (compressed style).
- `metro-accesibilidad.html`: Spaced-out CSS with `/* ═══ section ═══ */` section comments.
- `intro.html` and `Radial.html`: Compressed CSS with occasional section comments.
- Font sizes throughout use `rem` with very small values (e.g., `.72rem`, `.52rem`) — this is intentional for the dense UI aesthetic.
