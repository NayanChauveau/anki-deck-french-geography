import html
import json
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
    if card.layer != "departments":
        return ""
    return (
        '<div class="credits">Contours : '
        '<a href="https://www.data.gouv.fr/datasets/contours-administratifs">'
        "Etalab / IGN · 2025</a>"
        ' · <a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a></div>'
    )


def image_html(card, name):
    return f'<img src="{name}" alt="Carte géographique">' + credits(card)


def maps(project: Project, out: Path):
    manifest = {}
    cache = {}
    out.mkdir(parents=True, exist_ok=True)
    for card in project.cards:
        manifest[card.id] = {}
        for side, back in [("front", False), ("back", True)]:
            mode = card.back_map if back else card.front_map
            if mode == "none":
                manifest[card.id][side] = {}
                continue
            key = (card.layer, card.view, mode, card.target if mode == "target" else None)
            if key not in cache:
                cache[key] = {
                    ext: path.name for ext, path in render(project, card, back, out).items()
                }
            manifest[card.id][side] = cache[key]
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
            f'<div class="pair">{figures}</div><p>{e(card.explanation)}</p></article>'
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
    }
    media_files = set()
    for card in project.cards:
        images = [manifest[card.id][side].get("png") for side in ["front", "back"]]
        media_files.update(str(media_dir / name) for name in images if name)
        image_fields = [image_html(card, name) if name else "" for name in images]
        refs = " · ".join(html.escape(ref) for ref in card.references)
        decks[card.theme].add_note(
            genanki.Note(
                model=model,
                guid=note_guid(card.id),
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
