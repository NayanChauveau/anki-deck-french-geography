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


def maps(project: Project, out: Path):
    manifest = {}
    for card in project.cards:
        manifest[card.id] = {
            side: {ext: path.name for ext, path in render(project, card, back, out).items()}
            for side, back in [("front", False), ("back", True)]
        }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def preview(project: Project, out: Path) -> Path:
    manifest = maps(project, out / "media")
    articles = []
    for card in project.cards:
        e = html.escape
        figures = "".join(
            f'<figure><figcaption>{label}</figcaption><img alt="{label}" '
            f'src="media/{manifest[card.id][side]["png"]}"></figure>'
            for side, label in [("front", "Recto"), ("back", "Verso")]
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
        f"<h1>Géographie française</h1><p>{len(project.cards)} cours d’eau · recto et verso</p>"
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
    deck = genanki.Deck(DECK_ID, DECK_NAME)
    media_files = set()
    for card in project.cards:
        images = [manifest[card.id][side]["png"] for side in ["front", "back"]]
        media_files.update(str(media_dir / name) for name in images)
        refs = " · ".join(html.escape(ref) for ref in card.references)
        deck.add_note(
            genanki.Note(
                model=model,
                guid=note_guid(card.id),
                fields=[
                    card.id,
                    html.escape(card.question),
                    f'<img src="{images[0]}" alt="Cours d’eau à identifier">',
                    html.escape(card.answer),
                    f'<img src="{images[1]}" alt="{html.escape(card.answer)}">',
                    html.escape(card.explanation),
                    refs,
                ],
                tags=["french-geography", "theme::fleuves", f"id::{card.id}"],
            )
        )
    package = genanki.Package(deck)
    package.media_files = sorted(media_files)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "french-geography.apkg"
    package.write_to_file(str(path))
    return path
