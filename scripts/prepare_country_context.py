"""Prepare detailed European context from a pinned local Natural Earth 10m input."""

import argparse
import hashlib
import json
from pathlib import Path

from pyproj import Transformer
from shapely import coverage_simplify, make_valid, transform
from shapely.geometry import box, mapping, shape

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("input", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
raw = args.input.read_bytes()
registry_path = root / "geo/sources.yml"
registry = json.loads(registry_path.read_text())
old = next((s for s in registry["sources"] if s["id"] == "country-context"), None)
if old and old["upstream_sha256"] != hashlib.sha256(raw).hexdigest():
    raise ValueError("Input differs from pinned Natural Earth source")
window = box(-60, -10, 100, 85)  # Well outside all European card frames.
selected = []
for feature in json.loads(raw)["features"]:
    geometry = make_valid(shape(feature["geometry"])).intersection(window)
    if not geometry.is_empty:
        selected.append((feature["properties"]["ADM0_A3"], geometry))
forward = Transformer.from_crs(4326, 3035, always_xy=True).transform
backward = Transformer.from_crs(3035, 4326, always_xy=True).transform
projected = [transform(g, forward, interleaved=False) for _, g in selected]
# Shared borders are simplified together; no independent per-country drift.
simplified = coverage_simplify(projected, 250)
features = [
    {
        "type": "Feature",
        "properties": {"id": key, "france": key == "FRA", "detail": True},
        "geometry": mapping(transform(geometry, backward, interleaved=False)),
    }
    for (key, _), geometry in zip(selected, simplified, strict=True)
]
output = root / "geo/features/country-context.geojson"
output.write_text(
    json.dumps({"type": "FeatureCollection", "features": features}, separators=(",", ":")) + "\n"
)
entry = {
    "id": "country-context",
    "kind": "reference",
    "source": "Natural Earth",
    "version": "v5.1.2, 10m",
    "url": "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_10m_admin_0_countries.geojson",
    "license": "Public domain",
    "license_url": "https://www.naturalearthdata.com/about/terms-of-use/",
    "upstream_sha256": hashlib.sha256(raw).hexdigest(),
    "file": str(output.relative_to(root)),
    "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    "modifications": (
        "European context clipped to [-60,-10,100,85], outside card frames; make_valid; "
        "joint coverage simplification at 250 m in EPSG:3035; reprojected to WGS84; "
        "properties reduced. Global cards retain the separate pinned 50m background."
    ),
}
registry["sources"] = [s for s in registry["sources"] if s["id"] != entry["id"]] + [entry]
registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
print(output)
