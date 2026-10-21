"""Select physical label polygons, with explicit approximate limits, from Natural Earth."""

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
    "ALPS": ("alpes", "Alpes"),
    "PYRENEES": ("pyrenees", "Pyrénées"),
    "Massif Central": ("massif-central", "Massif central"),
    "Jura": ("jura", "Jura"),
    "Vosges": ("vosges", "Vosges"),
}
features, entries = [], []
for feature in json.loads(args.input.read_text())["features"]:
    name = feature["properties"]["NAME"]
    if name not in selection:
        continue
    key, french = selection[name]
    key = "mountain-" + key
    geom = make_valid(shape(feature["geometry"])).intersection(box(-7, 40, 12, 53))
    features.append({"type": "Feature", "properties": {"id": key}, "geometry": mapping(geom)})
    entries.append(
        {
            "id": key,
            "name": french,
            "view": "metropolitan",
            "explanation_key": ("landforms.approximate_notice"),
        }
    )
if len(features) != 5:
    raise ValueError("Incomplete relief pilot")
schematic = root / "data/relief/schematic-zones.geojson"
country_path = root / "geo/features/countries.geojson"
france = unary_union(
    [
        shape(f["geometry"])
        for f in json.loads(country_path.read_text())["features"]
        if f["properties"]["france"]
    ]
)
for feature in json.loads(schematic.read_text())["features"]:
    props = feature["properties"]
    geom = make_valid(shape(feature["geometry"])).intersection(france)
    features.append(
        {"type": "Feature", "properties": {"id": props["id"]}, "geometry": mapping(geom)}
    )
    entries.append(
        {
            "id": props["id"],
            "name": props["name"],
            "view": "metropolitan",
            "explanation_key": "landforms.schematic_notice",
            "references": props["references"],
        }
    )
output = root / "geo/features/mountains.geojson"
output.write_text(
    json.dumps(
        {"type": "FeatureCollection", "features": features},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    + "\n"
)
(root / "catalog/mountains.yml").write_text(
    yaml.safe_dump({"features": entries}, allow_unicode=True, sort_keys=False)
)
registry_path = root / "geo/sources.yml"
registry = yaml.safe_load(registry_path.read_text())
registry["sources"] = [s for s in registry["sources"] if s["id"] != "mountains"]
registry["sources"].append(
    {
        "id": "mountains",
        "source": "Natural Earth, physical label polygons",
        "version": "v5.1.2",
        "url": "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_10m_geography_regions_polys.geojson",
        "license": "Public domain",
        "license_url": "https://www.naturalearthdata.com/about/terms-of-use/",
        "upstream_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "inputs": [
            {
                "url": "local:data/relief/schematic-zones.geojson",
                "file": "data/relief/schematic-zones.geojson",
                "sha256": hashlib.sha256(schematic.read_bytes()).hexdigest(),
                "source": "Independently authored educational schematics, 2026-10-20",
                "license": "CC0-1.0",
                "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            },
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
            "Two independently authored schematic zones added "
            "from data/relief/schematic-zones.geojson. "
            "properties reduced, IDs prefixed mountain-, make_valid applied. "
            "Label polygons describe approximate geographic extents, not administrative "
            "mountain-law zones. No island polygon substituted for Corsican relief. "
            "Schematic zones clipped to the pinned Natural Earth France outline "
            "to avoid marine fill."
        ),
    }
)
registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
