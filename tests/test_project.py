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
from PIL import Image
from pydantic import ValidationError
from shapely.geometry import LineString, Point, Polygon

from french_geography.build import DECK_ID, MODEL_ID, build, note_guid, preview
from french_geography.cartography import Projection, render, scene_for
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
        media = json.loads(package.read("media"))
        assert len(media) == len(project.cards)
        for key, name in media.items():
            data = package.read(key)
            assert name == "geo-" + hashlib.sha256(data).hexdigest() + ".png"
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


@pytest.mark.parametrize("index", range(18))
def test_render_is_deterministic_and_front_does_not_reveal_answer(project, tmp_path, index):
    card = project.cards[index]
    label = card.annotations[0].text
    first = render(project, card, False, tmp_path / "one")
    second = render(project, card, False, tmp_path / "two")
    assert {k: p.name for k, p in first.items()} == {k: p.name for k, p in second.items()}
    assert label not in first["svg"].read_text()
    back_image = render(project, card, True, tmp_path / "back")
    assert label not in back_image["svg"].read_text()
    assert "<text" not in first["svg"].read_text()
    assert "<text" not in back_image["svg"].read_text()
    assert first["png"].read_bytes() == back_image["png"].read_bytes()
    with Image.open(first["png"]) as image:
        assert image.size == (900, 900)
        assert len(image.getcolors(900 * 900)) > 100
    front = scene_for(project, card, False)[1]
    back = scene_for(project, card, True)[1]
    assert [p for p in front if p.kind != "text"] == [p for p in back if p.kind != "text"]


def test_point_polygon_holes_and_inset(project, tmp_path):
    project.views["regional"] = View(
        projection="EPSG:2154", bounds=(-3, 44, 5, 50), inset="metropolitan"
    )
    card = project.cards[0].model_copy(update={"view": "regional"})
    targets = [
        Point(2, 47),
        LineString([(1, 46), (2, 48)]),
        Polygon([(0, 45), (4, 45), (4, 49), (0, 49)], holes=[[(1, 46), (2, 46), (2, 47), (1, 47)]]),
    ]
    for i, geom in enumerate(targets):
        project.features[card.target] = geom
        result = render(project, card, True, tmp_path / str(i))
        assert result["png"].exists()
        assert 'fill-rule="evenodd"' in result["svg"].read_text()


def test_projection_uses_longitude_latitude():
    p = Projection(View(projection="EPSG:2154", bounds=(-6, 41, 10, 52)))
    west, north = p.point(-4, 50)
    east, south = p.point(8, 43)
    assert west < east and north < south


def test_reject_outside_target(project, tmp_path):
    project.features[project.cards[0].target] = Point(150, -20)
    with pytest.raises(ValueError, match="outside"):
        render(project, project.cards[0], False, tmp_path)


def copied_project(tmp_path):
    for directory in ("geo", "cards", "catalog", "data"):
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
    catalog["features"].append({"id": "example", "name": "Exemple", "article": "l’"})
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
    path = root / "cards/identification.yml"
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
    assert len(json.loads((tmp_path / "media/manifest.json").read_text())) == len(project.cards)


def test_ankiconnect_errors_are_reported(monkeypatch):
    import io

    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *a, **kw: io.BytesIO(b'{"result":null,"error":"Anki unavailable"}'),
    )
    with pytest.raises(RuntimeError, match="Anki unavailable"):
        anki("version")
