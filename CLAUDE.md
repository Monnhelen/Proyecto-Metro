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

Contains the **scrollytelling route stories** (see architecture section below).

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

`basemap_data_simple.js` and `basemap_data_v2.js` are lighter variants produced by `simplify_basemap.py` (rounds coordinates to 4 decimal places and applies Douglas-Peucker simplification, reducing file size from ~68 MB to ~5-10 MB). Unlike `basemap_data.js`, these lighter variants **are** tracked in git.

A third geographic constant, `BASEMAP_GEO`, is inlined directly in `intro.html` (~line 2699) as a compact GeoJSON FeatureCollection of the 16 CDMX alcaldías (borough boundaries). It is not in `basemap_data.js` and must be edited by hand if boundaries change.

## Scrollytelling Architecture (`intro.html`)

The three route stories in `intro.html` use a shared scroll-lock pattern driven by a `makeRoute()` factory function.

### DOM structure
Each route story follows this pattern:
```html
<section id="rs-story-N" class="rs-story">
  <div class="rs-sticky">          <!-- sticky map panel -->
    <div id="rs-map-N">...</div>   <!-- Leaflet map -->
    <div id="rs-overlay-N" class="rs-overlay">
      <!-- .rs-note-card elements (phases-based routes only) -->
      <!-- .rs-cap-card elements (non-phases routes) -->
    </div>
  </div>
  <div class="rs-spacer">          <!-- scroll space; one .rs-step per scroll step -->
    <div class="rs-step" data-step="0"></div>
    ...
  </div>
</section>
```

An IIFE at script-end reorders stories into `#rs-stage` as `[rs-story-3, rs-story-2, rs-story-1]` and hides stories 2 and 1 via `translateX(100%)`. A slide transition controller (another IIFE) watches `panel.style.overflowY` for the `'hidden'→''` transition (route completion signal) and animates a horizontal slide to the next story.

### `makeRoute(o)` factory
Called once per route with an options object. Key parameters:
- `stations` — array of station objects `{id, lat, lng, line, accessible, elevator, ee}`
- `caps` — array of caption strings (indexed by step, non-phases routes)
- `phases` — array of phase control objects (route 3 only; absent → legacy per-station scroll behavior)
- `phaseData` — array of caption/note data loaded from CSV (route 3 only; `o.phases` and `o.phaseData` are separate concerns)
- `offSystem` — `{from, to}` objects for off-system origin/destination markers
- `fitToStations`, `fitPadding` — map bounds behavior

Inside `makeRoute`, `go(step)` renders station markers up to `step`, drawing the route polyline and animating dots. The scroll listener calls `go()` directly (non-phases) or `runPhase(idx)` (phases).

### Phases system (route 3 only)
When `o.phases` is present, `runPhase(idx)` controls:
- Which `.rs-note-card` is visible (`ph.note` index, or `-1` for none)
- Visibility of off-system from/to markers (`ph.showOffFrom`, `ph.showOffTo`)
- Whether to call `go(ph.goStep)` directly or fire a burst animation (`ph.burst: {from, to, interval}`)

`o.phaseData[idx]` (populated from `captions.csv` story=3 rows) provides the caption/note text for each phase; `_showPhaseCap()` applies it. The two arrays are kept separate so phase geometry (inline) and phase text (CSV) can be edited independently.

Route completion for phases routes: `pi >= o.phases.length - 1`.
Route completion for non-phases routes: `Math.floor(spacer/100) >= N - 2` (where N = station count).

### Caption data
All three routes read caption text from **`data/captions.csv`** at startup via `fetch`. Schema:
```
story, index, caption_text, caption_bg, caption_opacity, note_text, note_bg, note_opacity, note_x, note_y
```
`story` matches the route number (1, 2, or 3). Routes 1 and 2 use `caption_text`/`note_text` to drive the `.rs-cap-card` display. Route 3 rows feed into `phaseData` (assigned to `_phaseData3` after parse); the note cards for route 3 are also backed by inline `rs-note-card` HTML but their text is overridden at runtime by `phaseData`.

A parse fallback (`catch`) calls `_initRoutes()` with empty arrays so the page still works if CSV fetch fails.

### Debug overlay
`intro.html` injects a fixed debug panel at startup (hidden by default). Press **D** to toggle it; **Shift+X** to clear the log. It displays current phase/step state and a copy-able event log — useful when diagnosing scroll or phase-transition issues without adding `console.log` statements.

## Data Files (`data/`)

- **`nodos.csv`** — Station nodes: `id, Linea, Orden, Tipo, Elevador, EE, Accesibilidad, Personas_Afectadas, lat, lng`
  - `Tipo`: Terminal / Transbordo / Intermedia
  - `Elevador` / `EE` / `Accesibilidad`: Si/No
  - Transfer stations appear multiple times with line suffixes (e.g., `Tacubaya_1`, `Tacubaya_2`)

- **`aristas.csv`** — Edges: `source, target, Tipo, Linea, Accesible_PCD`
  - `Tipo`: Secuencial (along a line) or Transbordo (between lines)
  - `Accesible_PCD`: 1/0

- **`captions.csv`** — Caption text for route stories 1 and 2 (fetched at runtime by `intro.html`). Schema described above.

`index.html` inlines `nodos.csv` and `aristas.csv` data directly in JS rather than fetching at runtime. If you update the CSVs, you must also update the inlined data in `index.html`.

## Utility Scripts

- **`compress_images.js`** — Compresses images in `cargando/` to WebP using `sharp`. Run `npm install` first (installs `sharp`), then `node compress_images.js`. Backs up originals with `.orig` extension.

- **`simplify_basemap.py`** — Reads `basemap_data.js`, rounds coordinates to 4 decimal places, applies Douglas-Peucker simplification (tolerance `0.0002`), and writes a smaller variant. Run standalone: `python3 simplify_basemap.py`.

- **`convert_shapefiles.py`** — Generates `basemap_data.js` from source shapefiles in `Mapa/`. Paths are hardcoded; run only when shapefiles change.

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
