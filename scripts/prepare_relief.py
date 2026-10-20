"""Select physical label polygons, with explicit approximate limits, from Natural Earth."""

import argparse
import hashlib
import json
from pathlib import Path

import yaml
from shapely import make_valid
from shapely.geometry import box, mapping, shape

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
            "explanation": (
                "Zone indicative de relief : les limites Natural Earth sont approximatives, "
                "sans valeur administrative."
            ),
        }
    )
if len(features) != 5:
    raise ValueError("Incomplete relief pilot")
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
        "file": "geo/features/mountains.geojson",
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "modifications": (
            "Five physical regions selected by NAME, clipped to [-7,40,12,53], "
            "properties reduced, IDs prefixed mountain-, make_valid applied. "
            "Label polygons describe approximate geographic extents, not administrative "
            "mountain-law zones. No island polygon substituted for Corsican relief."
        ),
    }
)
registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
