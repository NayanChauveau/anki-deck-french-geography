import hashlib
import json
import re
import shutil
import socket
import sqlite3
import zipfile
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError
from shapely.geometry import LineString, Point, Polygon, box

from french_geography.build import DECK_ID, MODEL_ID, build, maps, note_guid, preview
from french_geography.cartography import Projection
from french_geography.cartography.svg import glyph
from french_geography.cli import anki
from french_geography.project import load
from french_geography.schema import CatalogFile, RuleFile, View

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def project():
    project = load(ROOT)
    project.cards = [
        card
        for card in project.cards
        if card.theme == "Fleuves" and card.direction == "identification"
    ]
    return project


def test_offline_package_contains_all_notes_and_media(project, tmp_path, monkeypatch):
    def offline(*args, **kwargs):
        raise AssertionError("Build attempted network access")

    monkeypatch.setattr(socket, "socket", offline)
    output = build(project, tmp_path)
    with zipfile.ZipFile(output) as package:
        assert all(i.compress_type == zipfile.ZIP_DEFLATED for i in package.infolist())
        media = json.loads(package.read("media"))
        assert len(media) == 1
        for key, name in media.items():
            data = package.read(key)
            assert name == "geo-" + hashlib.sha256(data).hexdigest() + ".svg"
        database = tmp_path / "collection.anki2"
        database.write_bytes(package.read("collection.anki2"))
    with sqlite3.connect(database) as db:
        notes = db.execute("SELECT guid,mid,flds FROM notes").fetchall()
        assert len(notes) == len(project.cards)
        assert {n[0] for n in notes} == {note_guid(c.id) for c in project.cards}
        assert {n[1] for n in notes} == {MODEL_ID}
        assert db.execute("SELECT count(*) FROM cards WHERE did=?", (DECK_ID,)).fetchone()[
            0
        ] == len(project.cards)
        for _, _, fields in notes:
            images = re.findall(r'src="([^" ]+)"', fields)
            assert len(images) == 2
            assert set(images) <= set(media.values())


def test_identity_does_not_depend_on_editorial_changes(project):
    before = note_guid(project.cards[0].id)
    project.cards[0].answer = "Nouveau libellé"
    assert note_guid(project.cards[0].id) == before
    assert before != note_guid(project.cards[1].id)
    assert DECK_ID == 1976423100
    assert MODEL_ID == 1976423101
    assert project.cards[0].id == "fr-geo-hydrographie-identification-loire"


# Exercise representative river geometries; full catalog coverage is in the package build.
@pytest.mark.parametrize("target", ["loire", "rhone", "rhin", "saone"])
def test_render_is_deterministic_and_front_does_not_reveal_answer(project, tmp_path, target):
    card = next(c for c in project.cards if c.target == target)
    label = card.annotations[0].text
    project.cards = [card]
    first = maps(project, tmp_path / "one")
    second = maps(project, tmp_path / "two")
    assert first == second
    front = first[card.id]["front"]
    back = first[card.id]["back"]
    assert front == back
    data = (tmp_path / "one" / front["shared_svg"]).read_text()
    assert label not in data and "<text" not in data
    assert all(p["target"] is not None for p in front["panes"])


def test_point_polygon_holes_and_lines():
    view = View(projection="EPSG:2154", bounds=(-3, 44, 5, 50))
    polygon = Polygon([(0, 0), (4, 0), (4, 4), (0, 4)], holes=[[(1, 1), (2, 1), (2, 2), (1, 2)]])
    assert glyph(view, polygon, "test")[0].get("d").count("Z") == 2
    assert glyph(view, Point(2, 2), "test")[0].tag.endswith("circle")
    assert glyph(view, LineString([(1, 1), (2, 2)]), "test")[0].get("fill") == "none"


def test_projection_uses_longitude_latitude():
    p = Projection(View(projection="EPSG:2154", bounds=(-6, 41, 10, 52)))
    west, north = p.point(-4, 50)
    east, south = p.point(8, 43)
    assert west < east and north < south


def test_reject_outside_target(project, tmp_path):
    project.layers["rivers"][project.cards[0].target] = Point(150, -20)
    with pytest.raises(ValueError, match="outside"):
        maps(project, tmp_path)


def copied_project(tmp_path):
    for directory in ("geo", "cards", "catalog", "data", "locales"):
        shutil.copytree(ROOT / directory, tmp_path / directory)
    return tmp_path


def test_reject_tampered_geography(tmp_path):
    root = copied_project(tmp_path)
    with (root / "geo/features/rivers.geojson").open("a") as stream:
        stream.write(" ")
    with pytest.raises(ValueError, match="checksum"):
        load(root)


def test_reject_duplicate_catalog_entries_and_unknown_targets(tmp_path):
    root = copied_project(tmp_path)
    path = root / "catalog/rivers.yml"
    original = path.read_text()
    path.write_text(original.replace("id: seine", "id: loire"))
    with pytest.raises(ValueError, match="Duplicate catalog"):
        load(root)
    path.write_text(original.replace("id: seine", "id: absent"))
    with pytest.raises(ValueError, match="Catalog/layer mismatch"):
        load(root)


def test_schema_forbids_unknown_editorial_fields():
    with pytest.raises(ValidationError):
        CatalogFile.model_validate(
            {
                "features": [
                    {"id": "test", "name": "Test", "article": "le", "question": "Duplicated prompt"}
                ]
            }
        )
    with pytest.raises(ValidationError):
        RuleFile.model_validate({"rules": [{"question": "Missing settings"}]})


def test_new_catalog_entry_and_geometry_generate_a_note_without_a_card_file(tmp_path):
    root = copied_project(tmp_path)
    catalog_path = root / "catalog/rivers.yml"
    catalog = yaml.safe_load(catalog_path.read_text())
    catalog["features"].append({"id": "example", "name": "Exemple"})
    catalog_path.write_text(yaml.safe_dump(catalog))
    geometry_path = root / "geo/features/rivers.geojson"
    data = json.loads(geometry_path.read_text())
    data["features"].append(
        {
            "type": "Feature",
            "properties": {"id": "example"},
            "geometry": {"type": "LineString", "coordinates": [[1, 46], [2, 47]]},
        }
    )
    geometry_path.write_text(json.dumps(data))
    source_path = root / "geo/sources.yml"
    sources = yaml.safe_load(source_path.read_text())
    sources["sources"][0]["sha256"] = hashlib.sha256(geometry_path.read_bytes()).hexdigest()
    source_path.write_text(yaml.safe_dump(sources))
    locale_path = root / "locales/fr.yml"
    locale = yaml.safe_load(locale_path.read_text())
    locale["forms"]["example"] = {"identification": "L’Exemple"}
    locale_path.write_text(yaml.safe_dump(locale, allow_unicode=True))
    project = load(root)
    card = next(c for c in project.cards if c.target == "example")
    assert (
        len([c for c in project.cards if c.theme == "Fleuves" and c.direction == "identification"])
        == 33
    )
    assert card.target == "example"
    assert card.answer == "L’Exemple"
    assert card.explanation == ""
    assert card.annotations[0].text == "Exemple"
    first_river = next(
        c for c in project.cards if c.theme == "Fleuves" and c.direction == "identification"
    )
    assert card.question == first_river.question
    assert set(card.references) <= set(first_river.references)


def test_common_rule_applies_to_all_notes(tmp_path):
    root = copied_project(tmp_path)
    path = root / "locales/fr.yml"
    path.write_text(
        path.read_text().replace(
            "Quel cours d’eau est surligné sur la carte ?", "Identifiez le tracé."
        )
    )
    assert {
        card.question
        for card in load(root).cards
        if card.theme == "Fleuves" and card.direction == "identification"
    } == {"Identifiez le tracé."}


def test_catalog_requires_every_geographic_feature(tmp_path):
    root = copied_project(tmp_path)
    path = root / "catalog/rivers.yml"
    data = yaml.safe_load(path.read_text())
    removed = data["features"].pop()["id"]
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(ValueError, match=f"missing=.*{removed}"):
        load(root)


def test_preview_images_exist(project, tmp_path):
    page = preview(project, tmp_path)
    for src in re.findall(r'src="([^" ]+)"', page.read_text()):
        assert (page.parent / src).is_file()
    assert len(json.loads((tmp_path / "media/manifest.json").read_text())["cards"]) == len(
        project.cards
    )


def test_ankiconnect_errors_are_reported(monkeypatch):
    import io

    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *a, **kw: io.BytesIO(b'{"result":null,"error":"Anki unavailable"}'),
    )
    with pytest.raises(RuntimeError, match="Anki unavailable"):
        anki("version")


def test_projection_crops_in_pixel_space_without_interior_cut_edges():
    projection = Projection(View(projection="EPSG:2154", bounds=(-6, 41, 10, 52)))
    land = projection.geometry(box(-20, 30, 30, 65))
    assert land.equals(box(0, 0, 900, 900))
    point = projection.geometry(Point(2, 47))
    assert point.distance(Point(*projection.point(2, 47))) < 1e-9
