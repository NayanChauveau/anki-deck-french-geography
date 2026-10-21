import json
from collections import Counter
from pathlib import Path

import pytest
import yaml
from shapely.geometry import Point

from french_geography.build import maps, note_guid
from french_geography.project import load

ROOT = Path(__file__).resolve().parents[1]


def test_reviewed_river_explanations_have_fact_sources():
    data = yaml.safe_load((ROOT / "catalog/rivers.yml").read_text())["features"]
    assert len(data) == 32
    assert all(e["review"]["status"] == "verified" and e["references"] for e in data)
    assert all("naturalearthdata.com" not in url for e in data for url in e["references"])


def test_administrative_relations_match_cog_and_geographic_coverage():
    project = load(ROOT)
    reference = json.loads((ROOT / "data/administration/cog-2025.json").read_text())
    regions = {
        e["id"]: e for e in yaml.safe_load((ROOT / "catalog/regions.yml").read_text())["features"]
    }
    cities = {
        e["id"]: e for e in yaml.safe_load((ROOT / "catalog/cities.yml").read_text())["features"]
    }
    departments = {
        e["id"]: e
        for e in yaml.safe_load((ROOT / "catalog/departments.yml").read_text())["features"]
    }
    assert len(regions) == 18 and len(cities) == 113 and len(departments) == 101
    assert set(regions) == set(project.layers["regions"])
    assert set(cities) == set(project.layers["cities"])
    for row in reference["departments"]:
        dep = departments[f"dep-{row['DEP']}"]
        assert dep["region"] == f"reg-{row['REG']}"
        assert dep["capital"] == f"city-{row['CHEFLIEU']}"
        assert cities[dep["capital"]]["region"] == dep["region"]
    for row in reference["regions"]:
        region = regions[f"reg-{row['REG']}"]
        assert region["capital"] == f"city-{row['CHEFLIEU']}"
        assert cities[region["capital"]]["region"] == region["id"]
    assert regions["reg-28"]["capital"] == "city-76540"  # Rouen, not Caen
    assert regions["reg-27"]["capital"] == "city-21231"  # Dijon
    assert all(isinstance(g, Point) for g in project.layers["cities"].values())


def test_new_rules_do_not_change_existing_hydrographic_identities():
    project = load(ROOT)
    assert note_guid(next(c for c in project.cards if c.target == "loire").id) == note_guid(
        "fr-geo-hydrographie-identification-loire"
    )
    count = Counter(c.theme for c in project.cards)
    assert count["Fleuves"] == 38 and count["Départements"] == 303
    assert count["Régions"] == 148 and count["Villes"] == 427
    assert len({c.id for c in project.cards}) == len(project.cards)
    relations = [c for c in project.cards if c.direction in ("capital", "region", "department")]
    assert all(c.front_map == c.back_map == "none" for c in relations)
    for card in project.cards:
        if card.theme in ("Régions", "Villes") and card.direction != "name-map":
            assert card.answer not in card.question


def test_render_cache_reuses_identical_visuals(tmp_path, monkeypatch):
    from french_geography import cartography

    project = load(ROOT)
    project.cards = [c for c in project.cards if c.target == "loire"]
    # This test gets its own cache, independent of a developer's existing build.
    import copy
    from shutil import copytree

    project = copy.copy(project)
    project.root = tmp_path
    copytree(ROOT / "assets", tmp_path / "assets")
    first = maps(project, tmp_path / "first")
    original_png = cartography.render_png
    monkeypatch.setattr(
        cartography, "render_png", lambda *a, **kw: pytest.fail("Unexpected rerender")
    )
    assert maps(project, tmp_path / "second") == first
    assert all(
        (tmp_path / "second" / record["png"]).is_file()
        for entry in first.values()
        for record in entry.values()
    )

    # An unrelated view must not invalidate existing media.
    project.views = {**project.views, "unused-view": next(iter(project.views.values()))}
    assert maps(project, tmp_path / "third") == first
    monkeypatch.setattr(cartography, "render_png", original_png)
    name = next(record["png"] for entry in first.values() for record in entry.values() if record)
    cached = tmp_path / "build/media" / name
    expected = cached.read_bytes()
    cached.write_bytes(b"corrupted cached image")
    assert maps(project, tmp_path / "repaired") == first
    assert cached.read_bytes() == expected


def test_crowded_paris_capitals_share_a_local_view():
    project = load(ROOT)
    for target in ("city-75056", "city-92050", "city-93008", "city-94028"):
        cards = [card for card in project.cards if card.target == target]
        assert cards and all(card.view == "paris-region" for card in cards)
