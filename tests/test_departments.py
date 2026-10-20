import json
import socket
import sqlite3
import zipfile
from collections import Counter
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from french_geography.build import build
from french_geography.cartography import scene_for
from french_geography.generate import generate_departments
from french_geography.project import load
from french_geography.schema import DepartmentCatalog, DepartmentEntry, DepartmentRule

ROOT = Path(__file__).resolve().parents[1]


def test_all_departments_have_three_directions_and_exactly_one_fact_to_recall():
    project = load(ROOT)
    cards = [card for card in project.cards if card.theme == "Départements"]
    assert len(cards) == 303
    assert len({card.id for card in cards}) == 303
    assert set(Counter(card.target for card in cards).values()) == {3}
    assert {card.direction for card in cards} == {"name-map", "map-name", "map-code"}
    catalog = DepartmentCatalog.model_validate(
        yaml.safe_load((ROOT / "catalog/departments.yml").read_text())
    )
    for entry in catalog.features:
        variants = {card.direction: card for card in cards if card.target == entry.id}
        assert variants["name-map"].front_map == "blank"
        assert entry.name in variants["name-map"].question
        assert variants["map-name"].answer == entry.name
        assert variants["map-code"].answer == entry.code
        assert entry.code not in variants["map-code"].question
        assert entry.name not in variants["map-name"].question
        assert not variants["map-name"].annotations
    assert {e.code for e in catalog.features} >= {
        "01",
        "2A",
        "2B",
        "971",
        "972",
        "973",
        "974",
        "976",
    }


def test_blank_front_hides_target_and_map_questions_share_the_same_image():
    project = load(ROOT)
    for key in ["01", "75", "2A", "971", "973", "976"]:
        variants = {c.direction: c for c in project.cards if c.target == f"dep-{key}"}
        blank = scene_for(project, variants["name-map"], False)[1]
        highlighted = scene_for(project, variants["name-map"], True)[1]
        assert not any(
            p.fill == project.style.target or p.stroke == project.style.target for p in blank
        )
        assert any(p.fill == project.style.target for p in highlighted)
        assert scene_for(project, variants["map-name"], False) == scene_for(
            project, variants["map-code"], False
        )
        assert all(key not in p.text for p in blank if p.kind == "text")


def test_all_six_directions_are_supported_but_only_three_are_enabled():
    project = load(ROOT)
    rule = DepartmentRule(
        id="test",
        references=["local snapshot"],
        directions=["name-map", "map-name", "map-code", "name-code", "code-name", "code-map"],
    )
    cards = generate_departments(ROOT, rule, project.layers["departments"])
    assert len(cards) == 606
    for card in cards:
        if card.direction in ("name-code", "code-name"):
            assert card.front_map == card.back_map == "none"


def test_code_stays_a_string_and_must_match_geometry_id():
    with pytest.raises(ValidationError):
        DepartmentEntry(id="dep-01", code=1, name="Ain")
    with pytest.raises(ValidationError):
        DepartmentEntry(id="dep-01", code="02", name="Ain")
    with pytest.raises(ValidationError):
        DepartmentEntry(id="dep-20", code="20", name="Corse")
    with pytest.raises(ValidationError):
        DepartmentRule(id="test", references=["source"], directions=["map-name", "map-name"])


def test_department_package_keeps_existing_river_identity_and_bundles_shared_media(
    tmp_path, monkeypatch
):
    def offline(*args, **kwargs):
        raise AssertionError("Network during build")

    monkeypatch.setattr(socket, "socket", offline)
    project = load(ROOT)
    project.cards = [
        c for c in project.cards if c.target in ("dep-01", "dep-75", "dep-971", "loire")
    ]
    output = build(project, tmp_path)
    with zipfile.ZipFile(output) as package:
        media = json.loads(package.read("media"))
        assert len(media) < 2 * len(project.cards)
        database = tmp_path / "collection.anki2"
        database.write_bytes(package.read("collection.anki2"))
    with sqlite3.connect(database) as db:
        assert db.execute("SELECT count(*) FROM cards WHERE did=1976423102").fetchone()[0] == 9
        assert db.execute("SELECT count(*) FROM cards WHERE did=1976423100").fetchone()[0] == 1
        for (fields,) in db.execute("SELECT flds FROM notes WHERE flds LIKE '%dep-01%'"):
            assert 'alt="Carte géographique"' in fields
