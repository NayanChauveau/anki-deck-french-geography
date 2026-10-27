"""Prepare pinned Natural Earth regions and authored educational relief envelopes."""

import argparse
import hashlib
import json
from pathlib import Path

import yaml
from shapely import make_valid
from shapely.geometry import box, mapping, shape
from shapely.ops import unary_union

parser = argparse.ArgumentParser()
parser.add_argument("input", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
selection = {
    "ALPS": "alpes",
    "PYRENEES": "pyrenees",
    "Massif Central": "massif-central",
    "Jura": "jura",
    "Vosges": "vosges",
}
features = []
expected_hash = yaml.safe_load((root / "geo/sources.yml").read_text())["sources"]
expected_hash = next(s["upstream_sha256"] for s in expected_hash if s["id"] == "mountains")
if hashlib.sha256(args.input.read_bytes()).hexdigest() != expected_hash:
    raise ValueError("Unexpected Natural Earth input checksum")
for feature in json.loads(args.input.read_text())["features"]:
    name = feature["properties"]["NAME"]
    if name not in selection:
        continue
    key = "mountain-" + selection[name]
    geom = make_valid(shape(feature["geometry"])).intersection(box(-7, 40, 12, 53))
    features.append({"type": "Feature", "properties": {"id": key}, "geometry": mapping(geom)})
if len(features) != 5:
    raise ValueError("Incomplete relief pilot")
schematics = [
    root / "data/relief/schematic-zones.geojson",
    root / "data/relief/regional-schematic-zones.geojson",
]
country_path = root / "geo/features/countries.geojson"
france = unary_union(
    [
        shape(f["geometry"])
        for f in json.loads(country_path.read_text())["features"]
        if f["properties"]["france"]
    ]
)
for schematic in schematics:
    for feature in json.loads(schematic.read_text())["features"]:
        props = feature["properties"]
        geom = shape(feature["geometry"])
        if not geom.is_valid or geom.is_empty or geom.geom_type != "Polygon":
            raise ValueError(f"Invalid schematic: {props['id']}")
        geom = geom.intersection(france)
        if geom.is_empty:
            raise ValueError(f"Schematic outside France: {props['id']}")
        features.append(
            {"type": "Feature", "properties": {"id": props["id"]}, "geometry": mapping(geom)}
        )
ids = [feature["properties"]["id"] for feature in features]
if len(ids) != len(set(ids)):
    raise ValueError("Duplicate relief ID")
catalog = yaml.safe_load((root / "catalog/mountains.yml").read_text())
if set(ids) != {entry["id"] for entry in catalog["features"]}:
    raise ValueError("Relief catalogue/geometry mismatch")
output = root / "geo/features/mountains.geojson"
output.write_text(
    json.dumps(
        {"type": "FeatureCollection", "features": features},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    + "\n"
)
registry_path = root / "geo/sources.yml"
registry = yaml.safe_load(registry_path.read_text())
source_index = next(i for i, s in enumerate(registry["sources"]) if s["id"] == "mountains")
registry["sources"][source_index] = {
    "id": "mountains",
    "source": ("Natural Earth physical label polygons + independently authored relief schematics"),
    "version": "v5.1.2; schematics 2026-10-27",
    "url": "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_10m_geography_regions_polys.geojson",
    "license": "Public domain + CC0-1.0 schematics",
    "license_url": "https://www.naturalearthdata.com/about/terms-of-use/",
    "upstream_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
    "inputs": [
        *[
            {
                "file": str(schematic.relative_to(root)),
                "url": "local:" + str(schematic.relative_to(root)),
                "sha256": hashlib.sha256(schematic.read_bytes()).hexdigest(),
                "source": ("Independently authored educational schematics; references per feature"),
                "version": "2026-10-27" if "regional" in schematic.name else "2026-10-20",
                "license": "CC0-1.0",
                "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "modifications": (
                    "WGS84 educational envelopes; not digitized park or commune boundaries"
                ),
            }
            for schematic in schematics
        ],
        {
            "file": "geo/features/countries.geojson",
            "url": "local:geo/features/countries.geojson",
            "sha256": hashlib.sha256(country_path.read_bytes()).hexdigest(),
            "license": "Public domain",
        },
    ],
    "file": "geo/features/mountains.geojson",
    "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    "modifications": (
        "Five Natural Earth physical regions selected by NAME, clipped to [-7,40,12,53]; "
        "Two broad and 29 regional independently authored schematic zones added "
        "from data/relief/schematic-zones.geojson and regional-schematic-zones.geojson. "
        "properties reduced, IDs prefixed mountain-, make_valid applied. "
        "Label polygons describe approximate geographic extents, not administrative "
        "mountain-law zones. No island polygon substituted for Corsican relief. "
        "Schematic zones clipped to the pinned Natural Earth France outline "
        "to avoid marine fill."
    ),
}
registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
