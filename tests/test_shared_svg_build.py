"""Integration gates for production shared SVG, packages, gallery and cache."""

import copy
import hashlib
import html
import json
import re
import shutil
import socket
import sqlite3
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pytest
from shapely.geometry import Point

from french_geography.build import build_packages, map_field, maps, note_guid, preview
from french_geography.cartography import Projection, shared
from french_geography.languages import localize
from french_geography.locales import load_locale
from french_geography.project import load

ROOT = Path(__file__).resolve().parents[1]
CASES = {
    ("dep-33", "name-map"),
    ("dep-971", "map-name"),
    ("city-92050", "map-name"),  # Nanterre: local map plus national inset.
    ("city-97411", "department"),  # Text-only overseas relationship.
    ("rhone", "identification"),
}


@pytest.fixture
def project(tmp_path):
    project = load(ROOT)
    project.cards = [c for c in project.cards if (c.target, c.direction) in CASES]
    assert len(project.cards) == len(CASES)
    for folder in ("assets", "templates", "locales", "cards", "catalog"):
        shutil.copytree(ROOT / folder, tmp_path / folder)
    (tmp_path / "geo").mkdir()
    shutil.copyfile(ROOT / "geo/display-svg.json", tmp_path / "geo/display-svg.json")
    project.root = tmp_path
    return project


def package_contents(path, tmp_path):
    with zipfile.ZipFile(path) as package:
        media = {name: package.read(key) for key, name in json.loads(package.read("media")).items()}
        database = tmp_path / (path.parent.name + "-" + path.stem + ".sqlite")
        database.write_bytes(package.read("collection.anki2"))
    with sqlite3.connect(database) as db:
        rows = db.execute("SELECT guid,mid,flds,tags FROM notes").fetchall()
        notes = {row[2].split("\x1f")[0]: row for row in rows}
        cards = db.execute(
            "SELECT n.guid,c.did,c.ord,c.due FROM cards c JOIN notes n ON c.nid=n.id"
        ).fetchall()
        models = json.loads(db.execute("SELECT models FROM col").fetchone()[0])
    return media, notes, sorted(cards), models


def test_bilingual_packages_keep_released_identities_and_share_one_offline_sprite(
    project, tmp_path, monkeypatch
):
    monkeypatch.setattr(socket, "socket", lambda *a, **kw: pytest.fail("Unexpected network"))
    original_sprite = shared.sprite
    calls = []

    def count(*args):
        calls.append(True)
        return original_sprite(*args)

    monkeypatch.setattr(shared, "sprite", count)
    outputs = build_packages(project, tmp_path / "svg")
    assert len(calls) == 1
    # Both locales must have used one cached geographic render, also reusable by preview.
    monkeypatch.setattr(shared, "sprite", lambda *a: pytest.fail("Unexpected second SVG render"))
    manifest = maps(project, tmp_path / "gallery-media")
    sprite_hashes = set()
    for path in outputs:
        lang = path.stem.rsplit("-", 1)[1]
        media, notes, cards, models = package_contents(path, tmp_path)
        manifest = maps(localize(project, lang), tmp_path / "gallery-media")
        assert len(media) == 1
        for name, data in media.items():
            assert name == "geo-" + hashlib.sha256(data).hexdigest() + ".svg"
            sprite_hashes.add(hashlib.sha256(data).hexdigest())
        assert len(notes) == len(project.cards)
        assert len(cards) == len(project.cards)
        assert set(models) == {str(load_locale(project.root, lang).export["model_id"])}
        localized = {c.id: c for c in localize(project, lang).cards}
        for note_id, (guid, mid, fields, tags) in notes.items():
            card = localized[note_id]
            assert guid == note_guid(
                card.id, lang, definition=load_locale(project.root, lang).export
            )
            assert mid == load_locale(project.root, lang).export["model_id"]
            assert "french-geography" in tags
            parts = fields.split("\x1f")
            assert parts[0] == card.id
            assert parts[1] == html.escape(card.question)
            assert parts[3] == html.escape(card.answer)
            assert parts[5] == html.escape(card.explanation)
            for side, index in (("front", 2), ("back", 4)):
                record = manifest[note_id][side]
                assert bool(parts[index]) == bool(record)
                assert set(re.findall(r'<img src="([^"]+)"', parts[index])) <= set(media)
                if record:
                    assert parts[index].count('class="fg-highlight"') == sum(
                        pane["target"] is not None for pane in record["panes"]
                    )
    assert len(sprite_hashes) == 1
    monkeypatch.setattr(shared, "sprite", original_sprite)


def test_inset_uses_existing_projection_and_keeps_correct_paint_order(project, tmp_path):
    manifest = maps(project, tmp_path / "media")
    card = next(c for c in project.cards if c.target == "city-92050")
    back = manifest[card.id]["back"]
    assert len(back["panes"]) == 2
    root = ET.parse(tmp_path / "media" / back["shared_svg"]).getroot()
    ids = {n.attrib["id"]: n for n in root.iter() if "id" in n.attrib}
    assert len(ids) == sum("id" in n.attrib for n in root.iter())
    assert all(n.attrib["href"][1:] in ids for n in root.iter() if "href" in n.attrib)
    main, inset = back["panes"]
    rectangle = (900 - 235, 900 - 245, 205, 180)
    point = Projection(project.views["metropolitan"], rectangle).geometry(
        project.layers["cities"][card.target]
    )
    circle = next(iter(ids[inset["target"]]))
    assert abs(float(circle.attrib["cx"]) - point.x) < 1e-7
    assert abs(float(circle.attrib["cy"]) - point.y) < 1e-7
    assert float(circle.attrib["r"]) == project.style.target_marker_radius
    main_group = ids[main["background"]]
    # Department context in the main map must remain present below city markers.
    assert any(n.tag.endswith("path") for n in main_group)
    markup = shared.markup(project, back, alt="Map")
    positions = [
        markup.index("#" + v)
        for v in (main["background"], main["target"], inset["background"], inset["target"])
    ]
    assert positions == sorted(positions)


def test_corrupt_media_and_contract_are_rebuilt_and_editorial_changes_reuse_cache(
    project, tmp_path, monkeypatch
):
    first = maps(project, tmp_path / "one")
    original = shared.sprite
    calls = []

    def count(*args):
        calls.append(True)
        return original(*args)

    monkeypatch.setattr(shared, "sprite", count)
    project.cards[0].answer = "Editorial change only"
    assert maps(project, tmp_path / "two") == first
    assert not calls
    record = next(s for c in first.values() for s in c.values() if s)
    cache = project.root / "build/media"
    (cache / record["shared_svg"]).write_text("corrupt")
    assert maps(project, tmp_path / "three") == first
    assert len(calls) == 1
    index = cache / ".shared-svg-cache.json"
    damaged = json.loads(index.read_text())
    damaged["visuals"] = {}
    index.write_text(json.dumps(damaged))
    assert maps(project, tmp_path / "four") == first
    assert len(calls) == 2
    # A real geometry change invalidates the cache even with unchanged source registry IDs.
    city = project.layers["cities"]["city-92050"]
    project.layers = copy.deepcopy(project.layers)
    project.layers["cities"]["city-92050"] = Point(city.x + 0.001, city.y)
    maps(project, tmp_path / "five")
    assert len(calls) == 3


@pytest.mark.parametrize("failure", ["missing-target", "outside-view", "stale-settings"])
def test_invalid_target_or_stale_profile_fails_instead_of_showing_empty_map(
    project, tmp_path, failure
):
    card = next(c for c in project.cards if c.target == "dep-33")
    project.cards = [card]
    if failure == "missing-target":
        card.target = "missing"
    elif failure == "outside-view":
        project.layers = copy.deepcopy(project.layers)
        project.layers["departments"][card.target] = Point(150, -40)
    else:
        project.style.target = "#123456"
    with pytest.raises(ValueError, match="Missing SVG|outside view|stale"):
        maps(project, tmp_path / "media")


def test_gallery_reuses_package_map_markup_and_explains_http_requirement(project, tmp_path):
    page = preview(project, tmp_path / "gallery")
    document = page.read_text()
    manifest = json.loads((page.parent / "media/manifest.json").read_text())["cards"]
    locale = load_locale(project.root, "fr")
    for card in project.cards:
        for side in ("front", "back"):
            field = map_field(project, card, manifest[card.id][side], locale, prefix="media/")
            assert field in document
    assert 'location.protocol==="file:"' in document
    assert "Shared SVG preview requires HTTP" in document
    assert "python3 -m http.server" in document
    assert "svg.fg-map" in document


def test_cli_build_and_push_use_the_same_production_renderer(tmp_path, monkeypatch):
    from french_geography import cli

    selected, actions = [], []
    monkeypatch.setattr("sys.argv", ["french-geography", "build", "--root", str(tmp_path)])
    monkeypatch.setattr(cli, "load", lambda root: object())

    def capture(project, out, language):
        selected.append((out, language))
        return []

    monkeypatch.setattr(cli, "build_packages", capture)
    cli.main()
    assert selected == [(tmp_path / "dist", "all")]
    package = tmp_path / "dist/french-geography-fr.apkg"
    monkeypatch.setattr("sys.argv", ["french-geography", "push", "--root", str(tmp_path)])
    monkeypatch.setattr(cli, "build", lambda project, out: package)
    monkeypatch.setattr(cli, "anki", lambda action, **params: actions.append((action, params)))
    cli.main()
    assert actions == [("version", {}), ("importPackage", {"path": str(package)}), ("sync", {})]


def test_relief_back_can_switch_to_department_borders(tmp_path):
    project = load(ROOT)
    project.cards = [
        c for c in project.cards if c.target == "mountain-vercors" or c.target == "dep-33"
    ]
    manifest = maps(project, tmp_path)
    relief = next(c for c in project.cards if c.layer == "mountains")
    data = ET.fromstring((tmp_path / manifest[relief.id]["back"]["shared_svg"]).read_bytes())
    nodes = {n.attrib["id"]: n for n in data.iter() if "id" in n.attrib}
    locale = load_locale(ROOT, "fr")
    for card in project.cards:
        back = manifest[card.id]["back"]
        if card.layer != "mountains":
            assert "alternate" not in back
            continue
        (pane,) = back["alternate"]
        assert pane["background"] == "fg-map-departments-metropolitan"
        assert pane["target"] == back["panes"][0]["target"]
        outline = nodes[pane["outline"]]
        assert outline.get("fill") == "none"
        assert len(outline) == sum(
            1 for i in nodes if i.startswith("fg-shape-departments-metropolitan-")
        )
        front = map_field(project, card, manifest[card.id]["front"], locale, side="front")
        assert "fg-alternate" not in front
        field = map_field(project, card, back, locale, side="back")
        svg = ET.fromstring(field.split("</svg>")[0] + "</svg>")
        assert "fg-has-alternate" in svg.get("class")
        alternate = svg[-1]
        assert alternate.get("class") == "fg-alternate"
        assert [u.get("href").split("#")[1] for u in alternate] == [
            pane["background"],
            pane["target"],
            pane["outline"],
        ]
