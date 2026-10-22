"""SVG geometry and selection contracts for the production renderer."""

import xml.etree.ElementTree as ET
from types import SimpleNamespace

import pytest
from shapely.geometry import LineString, Point, Polygon, box, mapping

from french_geography.cartography.shared import markup, sprite
from french_geography.cartography.shared_cache import visual_key
from french_geography.cartography.svg import glyph, technical_id
from french_geography.schema import Card, Style, View


def fixture_project():
    return SimpleNamespace(
        views={"test": View(projection="EPSG:2154", bounds=(-1, 44, 1, 46), width=400, height=400)},
        style=Style(),
        countries=[{"geometry": mapping(box(-1, 44, 1, 46)), "properties": {"france": True}}],
        layers={"cities": {"city-2A004": Point(0, 45), "city-neighbor": Point(0.2, 45.2)}},
    )


def city_card():
    return Card(
        id="fr-geo-test-city",
        target="city-2A004",
        view="test",
        layer="cities",
        question="Example?",
        answer="Example",
        references=["https://example.org"],
    )


def test_shared_geometry_resolves_every_reference_and_keeps_both_markers():
    project = fixture_project()
    card = city_card()
    project.cards = [card]
    setting = {"method": "preserve-topology", "tolerance_px": 0, "decimals": 2}
    data, visuals = sprite(project, {("countries", "test"): setting, ("cities", "test"): setting})
    root = ET.fromstring(data)
    ids = [n.attrib["id"] for n in root.iter() if "id" in n.attrib]
    assert len(ids) == len(set(ids))
    assert all(n.attrib["href"][1:] in ids for n in root.iter() if "href" in n.attrib)
    radii = [float(n.attrib["r"]) for n in root.iter() if n.tag.endswith("circle")]
    assert sorted(radii) == [2.5, 2.5, 7.0, 7.0]
    assert all(n.attrib["stroke"] == "none" for n in root.iter() if n.tag.endswith("circle"))
    record = {**visuals[visual_key(card, "target")], "shared_svg": "asset.svg"}
    target = ET.fromstring(markup(project, record, alt="Map").split("</svg>")[0] + "</svg>")
    assert len(target) == 2
    assert target[1].attrib["href"] == "asset.svg#" + record["panes"][0]["target"]
    blank_record = {**record, "panes": [{**p, "target": None} for p in record["panes"]]}
    blank = ET.fromstring(markup(project, blank_record, alt="Map").split("</svg>")[0] + "</svg>")
    assert len(blank) == 1
    assert markup(project, {}, alt="Map") == ""


def test_polygon_holes_and_unfilled_lines_survive_glyph_generation():
    view = fixture_project().views["test"]
    polygon = Polygon(
        [(10, 10), (100, 10), (100, 100), (10, 100)],
        holes=[[(30, 30), (60, 30), (60, 60), (30, 60)]],
    )
    shape = glyph(view, polygon, "polygon")
    assert shape[0].attrib["fill-rule"] == "evenodd"
    assert shape[0].attrib["d"].count("Z") == 2
    line = glyph(view, LineString([(10, 10), (100, 100)]), "line")
    assert line[0].attrib["fill"] == "none"
    assert line[0].attrib["stroke-linecap"] == "butt"
    assert "stroke" not in line[0].attrib  # Style inherited from the selecting <use>.


def test_technical_ids_preserve_corsican_codes_and_reject_markup():
    assert technical_id("cities", "city-2A004") == "fg-cities-city-2A004"
    with pytest.raises(ValueError, match="Unsafe SVG ID"):
        technical_id("cities", 'name" onload="bad')
