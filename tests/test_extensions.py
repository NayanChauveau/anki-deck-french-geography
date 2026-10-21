import hashlib
from pathlib import Path

import yaml
from shapely.geometry import Point, shape

from french_geography.project import load

ROOT = Path(__file__).resolve().parents[1]


def test_topage_selection_excludes_homonymous_small_rivers():
    project = load(ROOT)
    # Orne in Normandy, not the Moselle tributary; Somme in Picardy, not Burgundy.
    assert project.features["orne"].bounds[2] < 1
    assert project.features["somme"].bounds[1] > 49
    assert project.features["allier"].bounds[1] > 44
    assert project.features["vilaine"].bounds[2] < 0
    assert project.features["saone"].bounds[3] > 48  # Former NE fragment lacked upper course.
    relations = {
        card.target: card.answer for card in project.cards if card.direction == "downstream"
    }
    assert relations == {
        "allier": "Loire",
        "cher": "Loire",
        "oise": "Seine",
        "lot": "Garonne",
        "isere": "Rhône",
        "ain": "Rhône",
    }


def test_schematic_corsican_relief_is_not_the_island_outline():
    project = load(ROOT)
    mountain = project.features["mountain-corse"]
    island = project.features["dep-2A"].union(project.features["dep-2B"])
    assert mountain.area < island.area * 0.6
    card = next(c for c in project.cards if c.target == "mountain-corse")
    assert "schématique" in card.explanation
    assert card.view == "metropolitan"


def test_homonymous_saint_denis_questions_remain_useful():
    project = load(ROOT)
    for target, qualifier in (("city-93066", "Île-de-France"), ("city-97411", "océan Indien")):
        cards = [c for c in project.cards if c.target == target]
        assert {c.direction for c in cards} == {"name-map", "map-name", "department"}
        assert qualifier in next(c.question for c in cards if c.direction == "name-map")
        relation = next(c for c in cards if c.direction == "department")
        assert relation.answer.casefold() not in relation.question.casefold()


def test_overseas_points_and_world_map_keep_actual_geography():
    project = load(ROOT)
    for code in ("971", "972", "973", "974", "976"):
        point = project.features["overseas-" + code]
        assert isinstance(point, Point)
        assert project.features["dep-" + code].covers(point)
        card = next(c for c in project.cards if c.target == "overseas-" + code)
        assert card.view == "world"
        assert project.views[card.view].inset is None
    countries = project.countries
    assert any(
        Point(135, -25).intersects(shape(f["geometry"])) for f in countries
    )  # Background actually covers Australia, not just Europe.


def test_composite_dataset_inputs_are_pinned():
    registry = yaml.safe_load((ROOT / "geo/sources.yml").read_text())["sources"]
    for source in registry:
        for item in source.get("inputs", []):
            if "file" in item:
                assert (
                    hashlib.sha256((ROOT / item["file"]).read_bytes()).hexdigest() == item["sha256"]
                )


def test_national_park_cores_cover_eleven_parks_including_overseas():
    project = load(ROOT)
    assert len(project.layers["parks"]) == 11
    cards = [c for c in project.cards if c.layer == "parks"]
    assert len(cards) == 22
    assert {c.direction for c in cards} == {"name-map", "map-name"}
    for slug, view in (("guadeloupe", "guadeloupe"), ("reunion", "reunion"), ("guyane", "guyane")):
        assert {c.view for c in cards if c.target == "park-" + slug} == {view}
    assert all("sans aire d’adhésion" in c.explanation for c in cards)


def test_port_relations_reuse_existing_city_positions():
    project = load(ROOT)
    cards = [c for c in project.cards if c.direction == "coast"]
    assert len(cards) == 5
    assert all(c.front_map == c.back_map == "none" for c in cards)
    assert all(c.target in project.layers["cities"] for c in cards)
    assert next(c.answer for c in cards if c.target == "city-76540") == "Manche"


def test_major_lakes_cover_twenty_places_on_one_france_view():
    project = load(ROOT)
    cards = [c for c in project.cards if c.layer == "lakes"]
    assert len(project.layers["lakes"]) == 20
    assert len(cards) == 40
    assert {c.direction for c in cards} == {"name-map", "map-name"}
    assert {c.view for c in cards} == {"metropolitan"}
    assert project.views["metropolitan"].inset is None
    # Hourtin and Carcans are two source objects for one lake, not just its northern half.
    hourtin = project.features["lake-hourtin"]
    assert hourtin.bounds[1] < 45.08 and hourtin.bounds[3] > 45.20
    # Exclude tiny homonyms south-west of the actual Vassivière reservoir.
    assert project.features["lake-vassiviere"].bounds[0] > 1.8
    assert project.features["lake-grand-lieu"].bounds[2] < -1.5
    assert project.features["lake-der-chantecoq"].bounds[1] > 48.5
    assert all(project.features[c.target].is_valid for c in cards)
