import json
import re
import socket
import sqlite3
import zipfile
from collections import Counter
from dataclasses import replace
from pathlib import Path
from shutil import copytree

import pytest
import yaml

from french_geography.build import build_packages, image_html
from french_geography.languages import localize
from french_geography.project import load

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def source_project():
    return load(ROOT)


def test_default_build_emits_registered_offline_packages(tmp_path, monkeypatch, source_project):
    def offline(*args, **kwargs):
        raise AssertionError("Package build attempted network access")

    monkeypatch.setattr(socket, "socket", offline)
    # Full translation coverage is checked below; packaging uses a small real sample.
    project = replace(
        source_project,
        cards=[c for c in source_project.cards if c.target in {"loire", "dep-01", "city-75056"}],
    )
    paths = build_packages(project, tmp_path)
    from french_geography.distribution import load_registry

    registry = load_registry(ROOT)
    assert [path.name for path in paths] == [entry["filename"] for entry in registry.values()]
    identities, models, images_by_language = [], {}, {}
    for path, language in zip(paths, registry, strict=True):
        with zipfile.ZipFile(path) as package:
            database = tmp_path / f"{language}.anki2"
            database.write_bytes(package.read("collection.anki2"))
            media = set(json.loads(package.read("media")).values())
        with sqlite3.connect(database) as db:
            notes = db.execute("select guid,mid,flds from notes").fetchall()
            assert len(notes) == len(project.cards)
            identities.append({guid for guid, _mid, _fields in notes})
            models[language] = {mid for _guid, mid, _fields in notes}
            images_by_language[language] = {
                fields.split("\x1f")[0].removesuffix(registry[language]["note_suffix"]): re.findall(
                    r'src="([^" ]+)"', fields
                )
                for _guid, _mid, fields in notes
            }
            for _guid, _mid, fields in notes:
                assert set(re.findall(r'src="([^" ]+)"', fields)) <= media
            if language == "en":
                decks = json.loads(db.execute("select decks from col").fetchone()[0])
                expected_ids = set(registry[language]["deck_ids"].values())
                assert expected_ids <= {int(key) for key in decks}
                assert len({deck["id"] for deck in decks.values() if deck["id"] != 1}) == 9
                model = json.loads(db.execute("select models from col").fetchone()[0])
                assert "FRENCH GEOGRAPHY" in next(iter(model.values()))["tmpls"][0]["qfmt"]
                assert all(
                    "Cartographie" not in fields and "code départemental" not in fields
                    for _guid, _mid, fields in notes
                )
    assert images_by_language["en"] == images_by_language["fr"]
    assert len(set().union(*identities)) == sum(map(len, identities))
    assert all(models[code] == {entry["model_id"]} for code, entry in registry.items())


def test_complete_translation_preserves_source_notes_order_and_geometry(source_project):
    before = [card.model_dump() for card in source_project.cards]
    english = localize(source_project, "en")
    assert [card.model_dump() for card in source_project.cards] == before
    assert len(english.cards) == len(source_project.cards) == 1044
    assert Counter(c.theme for c in english.cards) == Counter(c.theme for c in source_project.cards)
    assert len({c.id for c in english.cards}) == len(english.cards)
    translated = {"id", "question", "answer", "explanation", "references"}
    for original, card in zip(source_project.cards, english.cards, strict=True):
        assert card.id == original.id + "-en"
        assert card.model_dump(exclude=translated) == original.model_dump(exclude=translated)
        assert [r for r in card.references if r.startswith("http")] == [
            r for r in original.references if r.startswith("http")
        ]
        if card.explanation:
            assert card.explanation != original.explanation
        if card.front_map == "target":
            assert card.answer.casefold() not in card.question.casefold()
        if card.direction in {
            "capital",
            "region",
            "department",
            "massif",
            "downstream",
            "ocean",
            "coast",
        }:
            assert card.answer.casefold() not in card.question.casefold()


def test_department_codes_names_and_directions(source_project):
    english = localize(source_project, "en")
    selected = {
        "dep-01": ("Ain", "01"),
        "dep-21": ("Côte-d'Or", "21"),
        "dep-2A": ("Corse-du-Sud", "2A"),
        "dep-2B": ("Haute-Corse", "2B"),
        "dep-971": ("Guadeloupe", "971"),
        "dep-976": ("Mayotte", "976"),
    }
    cards = [c for c in english.cards if c.theme == "Départements"]
    assert len(cards) == 303
    for target, (name, code) in selected.items():
        group = [c for c in cards if c.target == target]
        assert {c.direction for c in group} == {"name-map", "map-name", "map-code"}
        for card in group:
            assert card.answer == (name if card.direction == "map-name" else f"{name} ({code})")
            assert card.explanation == f"{name} · department code {code}."
            if card.direction == "name-map":
                assert card.question == f"Where is the department of {name}?"
            else:
                assert name not in card.question and code not in card.question


def test_exonyms_qualifiers_and_relation_direction(source_project):
    cards = {c.id.removesuffix("-en"): c for c in localize(source_project, "en").cards}
    assert cards["fr-geo-hydrographie-identification-escaut"].answer == "The Scheldt"
    assert cards["fr-geo-hydrographie-lacs-lake-leman-map-name"].answer == "Lake Geneva"
    assert cards["fr-geo-regions-reg-53-map-name"].answer == "Brittany"
    saint_denis = cards["fr-geo-ville-departement-city-97411"]
    assert "Saint-Denis (Indian Ocean)" in saint_denis.question
    assert saint_denis.answer == "La Réunion"  # Official French department name is retained.
    assert "Saint-Denis (Île-de-France)" in cards["fr-geo-ville-departement-city-93066"].question
    assert cards["fr-geo-hydrographie-affluent-ain"].answer == "Rhône"
    assert cards["fr-geo-villes-portuaires-facade-city-76540"].answer == "English Channel coast"


def test_geographic_limitations_survive_translation(source_project):
    cards = {c.id.removesuffix("-en"): c for c in localize(source_project, "en").cards}
    assert (
        "does not show the entire international course"
        in cards["fr-geo-hydrographie-identification-rhin"].explanation
    )
    assert "available French section" in cards["fr-geo-hydrographie-affluent-oise"].explanation
    assert "schematic" in cards["fr-geo-relief-massifs-mountain-corse-map-name"].explanation
    assert (
        "neither an administrative zoning map nor a geological map"
        in cards["fr-geo-relief-massifs-mountain-armoricain-map-name"].explanation
    )
    assert "not a legal boundary" in cards["fr-geo-littoral-mers-sea-manche-map-name"].explanation
    for card in cards.values():
        if card.layer == "parks":
            assert "membership areas and adjacent marine areas are excluded" in card.explanation
            assert "do not use them to determine the regulations" in card.explanation


def translation_project(tmp_path, source_project):
    for folder in ("locales", "catalog", "cards"):
        copytree(ROOT / folder, tmp_path / folder)
    return replace(source_project, root=tmp_path)


@pytest.mark.parametrize(
    "kind, message",
    [
        ("missing-rule", "Rule translation coverage mismatch"),
        ("unknown-rule", "Rule translation coverage mismatch"),
        ("unknown-name", "Unknown localized feature IDs"),
        ("missing-direction", "Missing translation for rule/direction"),
        ("missing-explanation", "Explanation translation coverage mismatch"),
        ("missing-reference", "Missing reference translation"),
        ("missing-qualifier", "Qualifier translation coverage mismatch"),
        ("code-clue", "Map question contains a clue"),
        ("empty-explanation", "Empty translation"),
    ],
)
def test_incomplete_translation_fails_instead_of_falling_back(
    tmp_path, source_project, kind, message
):
    project = translation_project(tmp_path, source_project)
    path = tmp_path / "locales/en.yml"
    data = yaml.safe_load(path.read_text())
    if kind == "missing-rule":
        del data["rules"]["regions"]
    elif kind == "unknown-rule":
        data["rules"]["typo"] = data["rules"]["regions"]
    elif kind == "unknown-name":
        data["names"]["typo"] = "Unknown place"
    elif kind == "missing-direction":
        del data["rules"]["departements"]["questions"]["map-code"]
    elif kind == "missing-explanation":
        del data["explanations"][next(iter(data["explanations"]))]
    elif kind == "missing-reference":
        data["reference_labels"] = {}
    elif kind == "missing-qualifier":
        del data["qualifiers"]["location.indian_ocean"]
    elif kind == "code-clue":
        data["rules"]["departements"]["questions"]["map-code"] += " {code}"
    else:
        data["explanations"][next(iter(data["explanations"]))] = " "
    path.write_text(yaml.safe_dump(data, allow_unicode=True))
    with pytest.raises(ValueError, match=message):
        localize(project, "en")


def test_duplicate_yaml_keys_are_rejected(tmp_path, source_project):
    project = translation_project(tmp_path, source_project)
    path = tmp_path / "locales/en.yml"
    path.write_text(path.read_text() + "\nproper_names: retain_official_unless_translated\n")
    with pytest.raises(ValueError, match="Duplicate translation key"):
        localize(project, "en")


def test_english_park_credit_month_and_source_name(source_project):
    card = next(c for c in source_project.cards if c.layer == "parks")
    english = image_html(card, "map.png", "en")
    french = image_html(card, "map.png", "fr")
    assert "February 2026" in english and "février" not in english
    assert "février 2026" in french
    assert "Map data:" in english and "Parcs nationaux de France / OFB" in english


def test_locale_files_use_the_same_semantic_message_keys():
    from french_geography.locales import load_locale

    french = load_locale(ROOT, "fr").text
    english = load_locale(ROOT, "en").text
    for field in ("rules", "explanations", "qualifiers", "reference_labels", "themes", "ui"):
        assert getattr(french, field).keys() == getattr(english, field).keys()
    assert all(re.fullmatch(r"[a-z][a-z0-9_.-]+", key) for key in english.explanations)
    for rule in french.rules:
        assert french.rules[rule].questions.keys() == english.rules[rule].questions.keys()


def test_registering_a_third_locale_requires_no_language_specific_code(tmp_path, source_project):
    from french_geography.build import preview

    project = translation_project(tmp_path, source_project)
    for folder in ("assets", "templates"):
        copytree(ROOT / folder, tmp_path / folder)
    registry_path = tmp_path / "locales/languages.json"
    registry = json.loads(registry_path.read_text())
    third = dict(registry["en"])
    third.update(
        filename="french-geography-zz.apkg",
        label="Third locale fixture",
        namespace="test-third-locale",
        note_suffix="-zz",
        model_id=1976423401,
        deck_ids={key: identity + 200 for key, identity in registry["en"]["deck_ids"].items()},
    )
    registry["zz"] = third
    registry_path.write_text(json.dumps(registry))
    text = yaml.safe_load((tmp_path / "locales/en.yml").read_text())
    text["ui"]["heading"] = "THIRD LOCALE FIXTURE"
    text["ui"]["gallery_title"] = "Third locale gallery"
    text["rules"]["hydrographie-identification"]["answer"] = "Fixture {name}"
    (tmp_path / "locales/zz.yml").write_text(yaml.safe_dump(text))
    source_card = next(
        c for c in source_project.cards if c.layer == "rivers" and c.direction == "identification"
    )
    project = replace(project, cards=[source_card])
    packages = build_packages(project, tmp_path / "dist")
    assert [path.name for path in packages] == [
        "french-geography-en.apkg",
        "french-geography-fr.apkg",
        "french-geography-zz.apkg",
    ]
    with zipfile.ZipFile(packages[-1]) as archive:
        dbpath = tmp_path / "third.anki2"
        dbpath.write_bytes(archive.read("collection.anki2"))
    with sqlite3.connect(dbpath) as db:
        mid, fields = db.execute("select mid,flds from notes").fetchone()
        assert mid == 1976423401
        assert fields.split("\x1f")[0].endswith("-zz")
        assert fields.split("\x1f")[3].startswith("Fixture ")
        model = json.loads(db.execute("select models from col").fetchone()[0])
        assert "THIRD LOCALE FIXTURE" in next(iter(model.values()))["tmpls"][0]["qfmt"]
    gallery = preview(project, tmp_path / "preview", language="zz")
    assert 'lang="zz"' in gallery.read_text() and "Third locale gallery" in gallery.read_text()


def test_language_registry_rejects_anki_identity_collisions(tmp_path):
    from french_geography.distribution import load_registry

    (tmp_path / "locales").mkdir()
    registry = json.loads((ROOT / "locales/languages.json").read_text())
    registry["en"]["model_id"] = registry["fr"]["model_id"]
    (tmp_path / "locales/languages.json").write_text(json.dumps(registry))
    with pytest.raises(ValueError, match="duplicate Anki identity"):
        load_registry(tmp_path)
