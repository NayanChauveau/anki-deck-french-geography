import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from shapely.geometry import LineString

from french_geography.build import map_field
from french_geography.cartography.display import derive
from french_geography.cartography.shared import maps
from french_geography.languages import localize
from french_geography.locales import load_locale
from french_geography.project import load

ROOT = Path(__file__).resolve().parents[1]
STREET = "street-boulevard-de-la-liberation"


def test_marseille_streets_are_asked_in_both_directions_and_languages():
    project = load(ROOT)
    cards = [c for c in project.cards if c.layer == "streets"]
    assert len(project.layers["streets"]) == 300 and len(cards) == 600
    assert {c.theme for c in cards} == {"Rues de Marseille"}
    assert {c.view for c in cards} == {"marseille"}
    for target in project.layers["streets"]:
        selected = {c.direction: c for c in cards if c.target == target}
        assert set(selected) == {"name-map", "map-name"}
        assert (selected["name-map"].front_map, selected["name-map"].back_map) == (
            "blank",
            "target",
        )
        assert (selected["map-name"].front_map, selected["map-name"].back_map) == (
            "target",
            "target",
        )
    # The first released street note keeps its identity.
    first = next(c for c in cards if c.target == STREET and c.direction == "name-map")
    assert first.id == f"fr-geo-marseille-rues-{STREET}-name-map"
    english = {c.id: c for c in localize(project, "en").cards}
    assert english[first.id + "-en"].question == (
        "Where is “Boulevard de la Libération” in Marseille?"
    )


def test_city_maps_use_their_own_zoomable_sprite(tmp_path):
    project = load(ROOT)
    project.cards = [c for c in project.cards if c.target in (STREET, "dep-33")]
    manifest = maps(project, tmp_path)
    street = next(c for c in project.cards if c.layer == "streets" and c.direction == "name-map")
    national = next(c for c in project.cards if c.layer == "departments" and c.back_map == "target")
    back = manifest[street.id]["back"]
    assert back["shared_svg"] != manifest[national.id]["back"]["shared_svg"]
    assert "streets" not in (tmp_path / manifest[national.id]["back"]["shared_svg"]).read_text()
    x, y, w, h = back["zoom"]["target_box"]
    assert back["zoom"]["max"] == 12 and 0 < x < x + w < 900 and 0 < y < y + h < 900
    sprite = ET.fromstring((tmp_path / back["shared_svg"]).read_bytes())
    nodes = {n.attrib["id"]: n for n in sprite.iter() if "id" in n.attrib}
    paths = [n for n in nodes[back["panes"][0]["background"]] if n.tag.endswith("path")]
    # Streets are merged per class; widths in em follow the zoom set by the reviewer.
    assert len([p for p in paths if p.get("fill") == "none"]) == 2
    assert all(p.get("stroke-width").endswith("em") for p in paths)
    assert all("vector-effect" not in n.attrib for n in sprite.iter())
    locale = load_locale(ROOT, "fr")
    for side in ("front", "back"):
        field = map_field(project, street, manifest[street.id][side], locale, side=side)
        svg = ET.fromstring(field.split("</svg>")[0] + "</svg>")
        assert "fg-zoomable" in svg.get("class")
        assert svg.get("data-max-zoom") == "12" and float(svg.get("font-size")) > 0
        assert svg.get("data-target-box") == " ".join(f"{v:g}" for v in (x, y, w, h))
        assert ("fg-highlight" in field) == (side == "back")
        assert all(
            u.get("stroke-width", "em").endswith("em")
            for u in svg.iter()
            if "fg-highlight" in u.get("class", "")
        )
    assert "OpenStreetMap" in field


def test_display_error_budget_scales_with_zoom():
    line = [LineString([(0, 0), (10, 0.045), (20, 0)])]
    setting = {"method": "preserve-topology", "tolerance_px": 0.05, "decimals": 2}
    assert derive(line, setting)
    with pytest.raises(ValueError, match="error budget"):
        derive(line, setting, max_error=0.5 / 12)
