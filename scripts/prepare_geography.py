"""Explicit acquisition preparation: accepts downloaded files, never used by builds."""

import argparse
import hashlib
import json
from pathlib import Path

import yaml
from shapely.geometry import box, mapping, shape
from shapely.ops import unary_union

parser = argparse.ArgumentParser()
parser.add_argument("rivers", type=Path)
parser.add_argument("countries", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
window = box(-7, 40, 12, 53)
sources = []
for name, path, layer in [
    ("rivers", args.rivers, "ne_10m_rivers_lake_centerlines"),
    ("countries", args.countries, "ne_50m_admin_0_countries"),
]:
    original = path.read_bytes()
    data = json.loads(original)
    features = []
    if name == "rivers":
        selection = yaml.safe_load((root / "geo/selection.yml").read_text())["rivers"]
        for river, names in selection.items():
            parts = [
                shape(f["geometry"])
                for f in data["features"]
                if f["properties"].get("name") in names and f["geometry"]["coordinates"]
            ]
            geom = unary_union(parts).intersection(window)
            if geom.is_empty:
                raise ValueError(f"Empty selected river: {river}")
            features.append(
                {"type": "Feature", "properties": {"id": river}, "geometry": mapping(geom)}
            )
    else:
        for feature in data["features"]:
            geom = shape(feature["geometry"])
            if geom.intersects(window):
                features.append(
                    {
                        "type": "Feature",
                        "properties": {
                            "id": feature["properties"]["ADM0_A3"],
                            "france": feature["properties"]["ADM0_A3"] == "FRA",
                        },
                        "geometry": mapping(geom.intersection(window)),
                    }
                )
    output = root / "geo" / "features" / f"{name}.geojson"
    output.write_text(
        json.dumps(
            {"type": "FeatureCollection", "features": features},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n"
    )
    sources.append(
        {
            "id": name,
            "source": "Natural Earth",
            "version": "v5.1.2",
            "url": f"https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/{layer}.geojson",
            "license": "Public domain",
            "license_url": "https://www.naturalearthdata.com/about/terms-of-use/",
            "upstream_sha256": hashlib.sha256(original).hexdigest(),
            "file": str(output.relative_to(root)),
            "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "modifications": (
                "WGS84; clipped to [-7,40,12,53]; properties reduced; "
                "rivers selected by aliases in geo/selection.yml and unioned; "
                "Rhône includes Rhne lake centerline; "
                "no added geometry."
                if name == "rivers"
                else (
                    "WGS84; countries clipped to [-7,40,12,53]; "
                    "properties reduced; no added geometry."
                )
            ),
        }
    )
registry_path = root / "geo/sources.yml"
if registry_path.exists():
    previous = yaml.safe_load(registry_path.read_text())["sources"]
    sources.extend(source for source in previous if source["id"] not in ("rivers", "countries"))
registry_path.write_text(json.dumps({"sources": sources}, indent=2) + "\n")
