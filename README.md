# French Geography — Anki

An English-first project for learning French geography, with separate English and
French Anki packages. The English edition is deliberately starting small: **one Loire
card**. The French edition currently contains **1,014 cards**. Full translation is
outside the current scope.

## Build

Requires Python 3.12+, [uv](https://docs.astral.sh/uv/) and Make.

```sh
uv sync --frozen --extra dev
make check
make build
```

The default build produces both packages, English first:

| Stable filename | Current content |
| --- | --- |
| `dist/french-geography-en.apkg` | English starter: one Loire card |
| `dist/french-geography-fr.apkg` | French edition: 1,014 cards |

These filenames are fixed for future releases. The French notes retain their
existing identifiers; English notes have separate identities and model/deck IDs.
Both packages can coexist in the same Anki collection.

To build one language only:

```sh
uv run --frozen french-geography build --lang en
uv run --frozen french-geography build --lang fr
```

`make preview` generates the existing French gallery at `build/preview/index.html`.
`make push` keeps its existing behaviour: build and import the **French** package
through AnkiConnect, then request a sync. It does not push Git commits or import the
English starter automatically.

## Releases and Deckdock

As in the neighbouring WSET 3 project, each successful push to `main` publishes the
next stable patch release. Pull requests run checks without publishing. Both language
packages are attached to the same release; their filenames remain constant.

[Releases](https://github.com/NayanChauveau/anki-deck-french-geography/releases)
contain packages for manual import or [Deckdock](https://github.com/NayanChauveau/anki-deckdock).
Use a versioned asset URL with Deckdock, not a repository page or `latest-main` link.
The initial single-file release `v0.1.0` predates the final bilingual filenames.
See [distribution notes](docs/DECKDOCK.md).

## Project structure

- `geo/features/`: pinned, prepared geographic inputs.
- `geo/sources.yml`: provenance, versions, licences, transformations and checksums.
- `catalog/`: editorial content and relationships.
- `cards/`: shared generation rules, rather than one handwritten entry per note.
- `locales/en.yml`: the explicitly selected English pilot translations.
- `templates/anki/`: Anki presentation; map images contain no text.
- `src/french_geography/`: validation, generation, rendering and packaging.
- `scripts/`: preparation and release tools, separate from normal offline builds.

Normal builds never download geographic data. SVG/PNG media are content-addressed;
all referenced PNGs are embedded in the APKG. Geographic sources include Natural
Earth, INSEE COG/Etalab 2025, BD TOPAGE 2024 and the February 2026 national park dataset.
Approximate and schematic relief boundaries are identified as such.

The French catalog contains rivers, departments, regions, cities, relief, lakes,
maritime areas, overseas landmarks and national park cores. Content expansion is
paused while the existing architecture is consolidated.

Detailed working documents are currently in French:
[cartography](docs/CARTOGRAPHY.md), [administration](docs/ADMINISTRATION.md),
[stable Anki IDs](docs/ANKI_IDS.md), [roadmap](docs/ROADMAP.md), and
[architecture review](docs/reviews/ARCHITECTURE_2026-10-21.md).
