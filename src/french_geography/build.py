import hashlib
import html
import json
import shutil
from importlib.metadata import version
from pathlib import Path

import genanki

from french_geography.cartography import render
from french_geography.distribution import ROOT, THEME_KEYS, load_registry
from french_geography.locales import load_locale
from french_geography.project import Project

# Source-edition constants remain available to callers; identities live in one registry.
_SOURCE_EXPORT = load_registry()["fr"]
DECK_ID = _SOURCE_EXPORT["deck_ids"]["rivers"]
MODEL_ID = _SOURCE_EXPORT["model_id"]


def note_guid(card_id: str, language: str = "fr", *, definition=None) -> str:
    definition = definition or load_registry()[language]
    return genanki.guid_for(definition["namespace"], card_id)


def credits(card, locale=None):
    locale = locale or load_locale(ROOT, "fr")
    text = locale.text.ui
    label = html.escape(text["credits_label"]) + " "
    if card.layer == "parks":
        return (
            '<div class="credits">'
            + label
            + '<a href="https://www.data.gouv.fr/datasets/contours-des-11-parcs-nationaux-de-france">'
            + "Parcs nationaux de France / OFB · "
            + html.escape(text["parks_date"])
            + "</a> · "
            + '<a href="https://www.etalab.gouv.fr/licence-ouverte-open-licence/">'
            + "Licence Ouverte 2.0</a></div>"
        )
    if card.layer in ("rivers", "lakes"):
        return (
            '<div class="credits">'
            + label
            + "Natural Earth · "
            + html.escape(text["public_domain"])
            + " ; "
            + '<a href="https://www.data.gouv.fr/datasets/bd-topage-r-metropole-2024">'
            + "IGN / OFB / Sandre · BD TOPAGE 2024</a> · "
            + '<a href="https://www.etalab.gouv.fr/licence-ouverte-open-licence/">'
            + "Licence Ouverte 2.0</a></div>"
        )
    if card.layer not in ("departments", "regions", "cities", "overseas"):
        return ""
    return (
        '<div class="credits">'
        + label
        + '<a href="https://www.data.gouv.fr/datasets/contours-administratifs">'
        + "Etalab / IGN · 2025</a>"
        + ' · <a href="https://opendatacommons.org/licenses/odbl/1-0/">ODbL 1.0</a></div>'
    )


def references_html(references):
    return "<br>".join(
        f'<a href="{html.escape(ref, quote=True)}">{html.escape(ref)}</a>'
        if ref.startswith(("https://", "http://"))
        else html.escape(ref)
        for ref in references
    )


def image_html(card, name, language="fr", *, locale=None):
    locale = locale or load_locale(ROOT, language)
    return (
        f'<img src="{name}" alt="{html.escape(locale.text.ui["map_alt"], quote=True)}">'
        + credits(card, locale)
    )


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
    context = {}
    verified = {}
    copied = set()
    copy_media = out.resolve() != cache_dir.resolve()
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
                project.views[project.views[card.view].inset].model_dump()
                if project.views[card.view].inset
                else None,
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
                    if name not in verified:
                        verified[name] = (
                            path.is_file()
                            and name
                            == "geo-"
                            + hashlib.sha256(path.read_bytes()).hexdigest()
                            + "."
                            + extension
                        )
                    if not verified[name]:
                        valid = False
                        break
            if not valid:
                record = {
                    ext: path.name
                    for ext, path in render(project, card, back, cache_dir, context=context).items()
                }
                cache[key] = record
                verified.update(dict.fromkeys(record.values(), True))
            manifest[card.id][side] = record
            if copy_media:
                for name in record.values():
                    if name not in copied:
                        shutil.copyfile(cache_dir / name, out / name)
                        copied.add(name)
    index_path.write_text(json.dumps(cache, sort_keys=True) + "\n")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def preview(project: Project, out: Path, *, language="fr") -> Path:
    from french_geography.languages import localize

    locale = load_locale(project.root, language)
    project = localize(project, language)
    ui = locale.text.ui
    manifest = maps(project, out / "media")
    articles = []
    for card in project.cards:
        e = html.escape
        figures = "".join(
            f'<figure><figcaption>{label}</figcaption><img alt="{label}" '
            f'src="media/{manifest[card.id][side]["png"]}">{credits(card, locale)}</figure>'
            for side, label in [("front", ui["front"]), ("back", ui["back"])]
            if manifest[card.id][side]
        )
        articles.append(
            f"<article><h2>{e(card.answer)}</h2><p>{e(card.question)}</p>"
            f'<div class="pair">{figures}</div><p>{e(card.explanation)}</p>'
            f"<details><summary>{e(ui['sources'])}</summary>{references_html(card.references)}</details></article>"
        )
    css = (project.root / "templates/anki/style.css").read_text()
    document = (
        f'<!doctype html><html lang="{locale.code}"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{html.escape(ui['gallery_title'])}</title><style>"
        + css
        + "body{max-width:1200px;margin:24px auto;padding:16px}"
        ".pair{display:flex;gap:16px}figure{margin:0;flex:1;min-width:0}"
        "article{margin-bottom:48px}figcaption{margin-bottom:8px}"
        "@media(max-width:640px){.pair{display:block}}</style>"
        f"<h1>{html.escape(ui['title'])}</h1>"
        f"<p>{html.escape(ui['gallery_count'].format(count=len(project.cards)))}</p>"
        + "".join(articles)
        + "</html>"
    )
    out.mkdir(parents=True, exist_ok=True)
    path = out / "index.html"
    path.write_text(document)
    return path


def template_html(path: Path, locale):
    text = path.read_text()
    for key in ("heading", "sources"):
        text = text.replace("__" + key.upper() + "__", html.escape(locale.text.ui[key]))
    return text


def build(project: Project, out: Path, *, language: str = "fr") -> Path:
    from french_geography.languages import localize

    locale = load_locale(project.root, language)
    project = localize(project, language)
    ui = locale.text.ui
    media_dir = project.root / "build/media"
    manifest = maps(project, media_dir)
    templates = project.root / "templates/anki"
    model = genanki.Model(
        locale.export["model_id"],
        ui["model_name"],
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
                "name": ui["template_name"],
                "qfmt": template_html(templates / "front.html", locale),
                "afmt": template_html(templates / "back.html", locale),
            }
        ],
        css=(templates / "style.css").read_text(),
        sort_field_index=0,
    )
    decks = {
        theme: genanki.Deck(locale.export["deck_ids"][key], locale.text.themes[key].name)
        for theme, key in THEME_KEYS.items()
    }
    media_files = set()
    positions = dict.fromkeys(decks, 0)
    theme_tags = {theme: locale.text.themes[key].tag for theme, key in THEME_KEYS.items()}
    for card in project.cards:
        images = [manifest[card.id][side].get("png") for side in ["front", "back"]]
        media_files.update(str(media_dir / name) for name in images if name)
        image_fields = [image_html(card, name, locale=locale) if name else "" for name in images]
        refs = references_html(card.references)
        positions[card.theme] += 1
        decks[card.theme].add_note(
            genanki.Note(
                model=model,
                guid=note_guid(card.id, language, definition=locale.export),
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
                    f"language::{language}",
                    f"theme::{theme_tags[card.theme]}",
                    f"direction::{card.direction}",
                    f"id::{card.id}",
                ],
            )
        )
    package = genanki.Package(list(decks.values()))
    package.media_files = sorted(media_files)
    out.mkdir(parents=True, exist_ok=True)
    path = out / locale.export["filename"]
    package.write_to_file(str(path))
    return path


def build_packages(project: Project, out: Path, language: str = "all") -> list[Path]:
    languages = tuple(load_registry(project.root)) if language == "all" else (language,)
    return [build(project, out, language=item) for item in languages]
