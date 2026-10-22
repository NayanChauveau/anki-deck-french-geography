# French Geography — Anki

Learn to place French rivers, departments, cities and landscapes on a map — and
remember them with Anki. **Over 1,000 cards**, available as complete English and
French editions, with maps included in every package.

**Designed to be installed and kept up to date with
[Deck Manager](https://github.com/NayanChauveau/anki-deck-manager)**, the Anki add-on that
tracks this deck’s releases and offers updates inside Anki. Install your preferred
edition once, then let Deck Manager check for new versions.

**[Get Deck Manager on AnkiWeb](https://ankiweb.net/shared/info/932198090)** ·
**[Browse deck releases](https://github.com/NayanChauveau/anki-deck-french-geography/releases/latest)**

## What you’ll learn

- **Departments:** locate a department from its name, or recall its name and code from a map.
- **Regions and cities:** place them on a map and learn their administrative relationships and capitals.
- **Rivers and lakes:** recognize their locations and learn selected tributary relationships.
- **Landscapes:** identify mountain areas and landmark peaks.
- **Coasts, overseas France and national parks:** build a broader picture of French geography.

The deck is split into nine themed subdecks, so you can start with one subject.
Map cards use highlighted features and uncluttered backgrounds; explanations and
sources appear below the images. Questions run in both directions where useful,
so you practise finding a place as well as naming it.

Choose the language you want to study in. Both editions cover the same geography;
they can also coexist in one Anki collection.

## Install with Deck Manager — recommended

You’ll need **Anki Desktop 26.09 or later** to use Deck Manager.

1. Open [Deck Manager on AnkiWeb](https://ankiweb.net/shared/info/932198090)
   and copy the add-on code: **`932198090`**. In Anki, choose
   **Tools → Add-ons → Get Add-ons**, paste the code, confirm, then restart Anki.
2. Open **Tools → Deck Manager**.
3. Paste the download link for your preferred edition and confirm the import.

These published links are ready to paste into Deck Manager:

**English edition**

```text
https://github.com/NayanChauveau/anki-deck-french-geography/releases/download/v0.1.3/french-geography-en.apkg
```

**Édition française**

```text
https://github.com/NayanChauveau/anki-deck-french-geography/releases/download/v0.1.3/french-geography-fr.apkg
```

These are working starting versions; Deck Manager will offer newer releases when
available. To start directly with the newest version, open the
[latest deck release](https://github.com/NayanChauveau/anki-deck-french-geography/releases/latest),
then copy the link address of the `.apkg` asset for your language.
Paste that **versioned file link** into Deck Manager, rather than the release page URL.

### Keeping your deck up to date

Deck Manager checks for new versions at Anki startup, at most once every 24 hours.
When an update is available, choose **Import update** or postpone it with **Later**.
You can also use **Check** in Deck Manager whenever you like.

Updates open Anki’s usual import dialog, so you stay in control of the import.
The deck keeps stable note identities so existing notes can be updated; your Anki
import settings determine how updates are applied. No GitHub account or token is
needed.

## Prefer a manual download?

Download `french-geography-en.apkg` or `french-geography-fr.apkg` from the
[latest release](https://github.com/NayanChauveau/anki-deck-french-geography/releases/latest),
then import it in Anki with **File → Import**. All map images are bundled.
With manual installation, you’ll need to check for new releases yourself.

## Sources and coverage

Maps use Natural Earth, IGN/OFB/Sandre BD TOPAGE and official French administrative
and national park data. Sources are linked on the cards; dataset versions,
licences and transformations are recorded in [the source registry](geo/sources.yml).
Schematic relief boundaries are identified in the explanations.

This is a growing learning deck, with a selection of geographic features rather
than an exhaustive atlas. Published packages reflect their release; the source
repository may already contain additions awaiting publication.

## Contribute

Found a misplaced feature, an unclear question or a translation to improve?
[Open an issue](https://github.com/NayanChauveau/anki-deck-french-geography/issues)
with the place, edition and correction you suggest. Factual corrections are most
useful with a source. Content, translation and code contributions are welcome.

To build locally, install Python 3.12+, [uv](https://docs.astral.sh/uv/) and Make:

```sh
uv sync --frozen --extra dev
make check
make build
make preview
```

`make build` creates both language packages in `dist/`.
`make preview` creates a French card gallery at `build/preview/index.html`.
Serve it with `python3 -m http.server 8000 --bind 127.0.0.1 --directory build/preview`
and open `http://127.0.0.1:8000/`; shared SVG maps require HTTP.
Packages use one shared SVG instead of individual PNG maps (under 2 MB per edition).
Normal builds use pinned local geographic inputs and need no geographic downloads.

Editorial content lives in `catalog/`, generation rules in `cards/`, translations
in `locales/`, and prepared geography in `geo/features/`. To learn how to extend
the deck, see [cartography](docs/CARTOGRAPHY.md),
[localization](docs/LOCALIZATION.md), [stable Anki IDs](docs/ANKI_IDS.md),
[distribution](docs/DECK_MANAGER.md) and the [roadmap](docs/ROADMAP.md).
Most detailed working documents are currently in French.
