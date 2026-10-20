import hashlib
import html
import json
import shutil
from importlib.metadata import version
from pathlib import Path

import genanki

from french_geography.cartography import render
from french_geography.project import Project

# Permanent IDs and namespace. Never derive these from mutable editorial text.
DECK_ID = 1976423100
MODEL_ID = 1976423101
NAMESPACE = "ultimate-french-geography-v1"
DECK_NAME = "Géographie française::Fleuves"


def note_guid(card_id: str) -> str:
    return genanki.guid_for(NAMESPACE, card_id)


def credits(card):
    if card.layer not in ("departments", "regions", "cities"):
        return ""
    return (
        '<div class="credits">Cartographie : '
        '<a href="https://www.data.gouv.fr/datasets/contours-administratifs">'
        "Etalab / IGN · 2025</a>"
        ' · <a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a></div>'
    )


def references_html(references):
    return "<br>".join(
        f'<a href="{html.escape(ref, quote=True)}">{html.escape(ref)}</a>'
        if ref.startswith(("https://", "http://"))
        else html.escape(ref)
        for ref in references
    )


def image_html(card, name):
    return f'<img src="{name}" alt="Carte géographique">' + credits(card)


def maps(project: Project, out: Path):
    manifest = {}
    cache_dir = project.root / "build/media"
    cache_dir.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    index_path = cache_dir / ".render-cache.json"
    try:
        cache = json.loads(index_path.read_text())
    except (OSError, ValueError):
        cache = {}
    renderer = hashlib.sha256(Path(render.__code__.co_filename).read_bytes()).hexdigest()
    sources = {source["id"]: source["sha256"] for source in project.sources}
    environment = [version(package) for package in ("Pillow", "pyproj", "shapely")]
    font = hashlib.sha256(
        (project.root / "assets/fonts/NotoSans-Regular.ttf").read_bytes()
    ).hexdigest()
    for card in project.cards:
        manifest[card.id] = {}
        for side, back in [("front", False), ("back", True)]:
            mode = card.back_map if back else card.front_map
            if mode == "none":
                manifest[card.id][side] = {}
                continue
            inputs = [
                card.layer,
                card.view,
                mode,
                card.target if mode == "target" else None,
                project.views[card.view].model_dump(),
                {name: value.model_dump() for name, value in project.views.items()},
                project.style.model_dump(),
                sources[card.layer],
                sources["countries"],
                sources.get("departments")
                if card.layer == "cities" and card.view == "paris-region"
                else None,
                renderer,
                environment,
                font,
            ]
            key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
            record = cache.get(key, {})
            valid = set(record) == {"svg", "png"}
            if valid:
                for extension, name in record.items():
                    path = cache_dir / name
                    if (
                        not path.is_file()
                        or name
                        != "geo-" + hashlib.sha256(path.read_bytes()).hexdigest() + "." + extension
                    ):
                        valid = False
                        break
            if not valid:
                record = {
                    ext: path.name for ext, path in render(project, card, back, cache_dir).items()
                }
                cache[key] = record
            manifest[card.id][side] = record
            if out.resolve() != cache_dir.resolve():
                for name in record.values():
                    shutil.copyfile(cache_dir / name, out / name)
    index_path.write_text(json.dumps(cache, sort_keys=True) + "\n")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def preview(project: Project, out: Path) -> Path:
    manifest = maps(project, out / "media")
    articles = []
    for card in project.cards:
        e = html.escape
        figures = "".join(
            f'<figure><figcaption>{label}</figcaption><img alt="{label}" '
            f'src="media/{manifest[card.id][side]["png"]}">{credits(card)}</figure>'
            for side, label in [("front", "Recto"), ("back", "Verso")]
            if manifest[card.id][side]
        )
        articles.append(
            f"<article><h2>{e(card.answer)}</h2><p>{e(card.question)}</p>"
            f'<div class="pair">{figures}</div><p>{e(card.explanation)}</p>'
            f"<details><summary>Sources</summary>{references_html(card.references)}</details></article>"
        )
    css = (project.root / "templates/anki/style.css").read_text()
    document = (
        '<!doctype html><html lang="fr"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>Géographie française — galerie</title><style>"
        + css
        + "body{max-width:1200px;margin:24px auto;padding:16px}"
        ".pair{display:flex;gap:16px}figure{margin:0;flex:1;min-width:0}"
        "article{margin-bottom:48px}figcaption{margin-bottom:8px}"
        "@media(max-width:640px){.pair{display:block}}</style>"
        f"<h1>Géographie française</h1><p>{len(project.cards)} cartes · recto et verso</p>"
        + "".join(articles)
        + "</html>"
    )
    out.mkdir(parents=True, exist_ok=True)
    path = out / "index.html"
    path.write_text(document)
    return path


def build(project: Project, out: Path) -> Path:
    media_dir = project.root / "build/media"
    manifest = maps(project, media_dir)
    templates = project.root / "templates/anki"
    model = genanki.Model(
        MODEL_ID,
        "Géographie française — carte physique",
        fields=[
            {"name": name}
            for name in [
                "NoteId",
                "Question",
                "MapFront",
                "Answer",
                "MapBack",
                "Explanation",
                "Sources",
            ]
        ],
        templates=[
            {
                "name": "Identifier",
                "qfmt": (templates / "front.html").read_text(),
                "afmt": (templates / "back.html").read_text(),
            }
        ],
        css=(templates / "style.css").read_text(),
        sort_field_index=0,
    )
    decks = {
        "Fleuves": genanki.Deck(DECK_ID, DECK_NAME),
        "Départements": genanki.Deck(1976423102, "Géographie française::Départements"),
        "Régions": genanki.Deck(1976423103, "Géographie française::Régions"),
        "Villes": genanki.Deck(1976423104, "Géographie française::Villes"),
        "Relief": genanki.Deck(1976423105, "Géographie française::Relief"),
    }
    media_files = set()
    positions = dict.fromkeys(decks, 0)
    for card in project.cards:
        images = [manifest[card.id][side].get("png") for side in ["front", "back"]]
        media_files.update(str(media_dir / name) for name in images if name)
        image_fields = [image_html(card, name) if name else "" for name in images]
        refs = references_html(card.references)
        positions[card.theme] += 1
        decks[card.theme].add_note(
            genanki.Note(
                model=model,
                guid=note_guid(card.id),
                due=positions[card.theme],
                fields=[
                    card.id,
                    html.escape(card.question),
                    image_fields[0],
                    html.escape(card.answer),
                    image_fields[1],
                    html.escape(card.explanation),
                    refs,
                ],
                tags=[
                    "french-geography",
                    f"theme::{card.theme.lower()}",
                    f"direction::{card.direction}",
                    f"id::{card.id}",
                ],
            )
        )
    package = genanki.Package(list(decks.values()))
    package.media_files = sorted(media_files)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "french-geography.apkg"
    package.write_to_file(str(path))
    return path
