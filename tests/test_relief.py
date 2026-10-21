from pathlib import Path
from shutil import copytree

import pytest
import yaml
from shapely.geometry import Point

from french_geography.project import load

ROOT = Path(__file__).resolve().parents[1]


def test_summit_cards_have_three_directions_and_fact_sources():
    project = load(ROOT)
    cards = [card for card in project.cards if card.layer == "peaks"]
    assert len(cards) == 12
    assert all(isinstance(point, Point) for point in project.layers["peaks"].values())
    expected = {
        "peak-monte-cinto": "Reliefs corses",
        "peak-mont-blanc": "Alpes",
        "peak-puy-de-sancy": "Massif central",
        "peak-cret-de-la-neige": "Jura",
    }
    for target, massif in expected.items():
        selected = [card for card in cards if card.target == target]
        assert {card.direction for card in selected} == {"name-map", "map-name", "massif"}
        relation = next(card for card in selected if card.direction == "massif")
        assert relation.answer == massif
        assert relation.front_map == relation.back_map == "none"
        assert any("larousse.fr" in reference for reference in relation.references)
        assert "Insee" not in relation.explanation
        assert massif not in relation.question


def test_unknown_summit_massif_is_rejected(tmp_path):
    for directory in ("geo", "cards", "catalog", "data", "locales"):
        copytree(ROOT / directory, tmp_path / directory)
    path = tmp_path / "catalog/peaks.yml"
    catalog = yaml.safe_load(path.read_text())
    catalog["features"][0]["massif"] = "mountain-unknown"
    path.write_text(yaml.safe_dump(catalog))
    with pytest.raises(ValueError, match="Unknown massif"):
        load(tmp_path)
