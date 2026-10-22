# Cartography

## Build and preview

Local GeoJSON + editorial catalogues + generation rules + translations → projected
geometry → one shared SVG → Anki packages and HTML preview.

```sh
make check
make build
make preview
python3 -m http.server 8000 --bind 127.0.0.1 --directory build/preview
```

Open `http://127.0.0.1:8000/`. External SVG references require HTTP; opening the gallery
as a local file displays an explanation. `make push` builds the French edition,
imports it through AnkiConnect and requests synchronization. It does not push Git.

Each package bundles the SVG under its full SHA-256 filename, about 2.7 MB of media
and 5 MB total per language. Each map references its background and optional target
by SVG ID. A hidden image reference lets Anki's media scanner recognize the file.
There is no PNG renderer, target-selection JavaScript or browser-side positioning.
Questions, explanations, sources and credits are HTML outside the map.

## Files and responsibilities

| Location | Purpose |
| --- | --- |
| `geo/features/` and `geo/sources.yml` | Prepared geography and source provenance |
| `catalog/`, `cards/`, `locales/` | Editorial content, generation rules and translations |
| `geo/views.yml`, `geo/styles.yml` | Shared framing and appearance |
| `geo/display-svg.json` | Display-only simplification settings |
| `cartography/__init__.py` | Projection and geometry primitives |
| `cartography/display.py` | Simplification, topology and error checks |
| `cartography/svg.py` | SVG serialization |
| `cartography/shared.py` | Shared backgrounds, highlights, insets and markup |
| `cartography/shared_cache.py` | Content-addressed cache shared between languages |

Python modules above live under `src/french_geography/`. Builds verify pinned local
inputs and never download geographic data. Source geometry is never modified by
rendering. Names, text and note IDs do not determine geographic coordinates.
Released note/deck/model identities remain stable; see [ANKI_IDS.md](ANKI_IDS.md).

## Framing and geometry

Inputs use WGS84 longitude/latitude. Views project densified bounds and clip features
to a shared frame. Mainland maps use Lambert-93 and the whole of metropolitan France,
including Corsica. Overseas departments, regions, parks and location markers share
the Equal Earth world view. Sea zones use the European view. Paris-area cities use
a regional view with a national inset to distinguish nearby points. Five overseas
cities retain text relationships but have no location questions.

Points, lines, polygons, multipart geometries, holes and mixed collections are supported.
Neutral faces reference only the background; target faces add the requested feature.
Front and back retain the same frame. Sources and credits are added by the common
package/preview builder, not embedded in the SVG.

Simplification occurs in projected pixels. The retained settings preserve components,
holes, administrative coverage and existing river junctions, with a maximum geometric
error of 0.5 SVG pixels. Very small components retain sufficient decimal precision.
The European country context retains a known invalid projected Libya boundary without
simplification; it is not repaired or presented as authoritative source geography.

## Extending the deck

1. Prepare geography separately, recording source, version, licence, transformations
   and checksums in `geo/sources.yml`. Preparation scripts take pinned local inputs;
   they are never part of a normal build.
2. Add catalogue entries and localized text; reuse a generation rule where possible.
3. For a new layer/view, add a display setting. Start with `preserve-topology`, zero
   tolerance and eight decimals; optimize only after examining the resulting maps.
4. If geographic inputs, projection, views or style change, review the display profile
   and refresh its source fingerprint. The build deliberately rejects a stale profile.
5. Run `make check`, build and inspect the affected maps in the gallery and Anki.

To refresh the fingerprint after reviewing the profile:

```sh
uv run --frozen python - <<'PY'
import json
from pathlib import Path
from french_geography.project import load
from french_geography.cartography.display import fingerprint
path = Path('geo/display-svg.json')
data = json.loads(path.read_text())
data['source_fingerprint'] = fingerprint(load(Path.cwd()))
path.write_text(json.dumps(data, indent=2) + '\n')
PY
```

Preparation order matters: the original Natural Earth preparation precedes enriched
hydrography/world context; schematic relief depends on country outlines; overseas
markers depend on departments. `prepare_geography.py` alone does not recreate the
complete current dataset. Exact inputs and transformations are in the source registry.

## Geographic limitations

Natural Earth provides generalized context and some river/lake outlines. The initial
18-watercourse selection is extended to 32 with BD TOPAGE 2024; foreign segments absent
from the national dataset are not invented. The Rhine remains incomplete. The Rhône
includes Natural Earth's lake centerline through Lake Geneva. The Somme includes its
canalized course and a tiny detached source fragment, whose rasterization differs
slightly between SVG and the historical PNG reference.

The 20 lakes/reservoirs use exact selected Sandre codes, without small homonyms;
Hourtin-Carcans is combined. Lake boundaries do not describe current water levels.
Mountain areas are indicative; schematic Corsican/Armorican zones are recorded as
such. Five sea extents are conventional geographic areas, not legal boundaries.
National parks show official terrestrial/marine cores, excluding membership areas
and adjacent marine areas. These maps do not establish regulations for a parcel.
All dataset licences and modifications are recorded in `geo/sources.yml`.

## Cache and validation

The cache key includes geometry, views, style, display settings, renderer code and
library versions. The SVG bytes and cached visual metadata are hash-checked before
reuse. Both editions share one render; editorial changes do not rerender geography.
Old raster caches cannot enter packages. CI runs the same checks and build.

Tests cover offline packaging, stable identities, localization, references, highlights,
neutral/text-only faces, insets, geometry safety, cache reuse and corruption. Temporary
migration/browser/Anki-backend harnesses were removed after the switch. Their local
captures remain in ignored `build/review/`; they are not required for normal work.

The migration checked all ten layers in Chromium and a representative WebKit corpus.
Disposable Anki 25.9.5 backend imports preserved test history and scheduling, and
recognized the SVG as used media. Actual Android/AnkiWeb rendering and sync still need
user confirmation; iOS is not verified. The owner requested switching before those
checks were complete. See the short [migration status](SHARED_SVG_MIGRATION_PLAN.md).
