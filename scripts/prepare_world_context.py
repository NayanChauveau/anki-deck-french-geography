"""Prepare the global country background from a local NE 50m v5.1.2 input."""

import argparse
import hashlib
import json
from pathlib import Path

from shapely import make_valid
from shapely.geometry import mapping, shape

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("input", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
p = args.input
raw = json.loads(p.read_text())
features = []
for f in raw["features"]:
    features.append(
        {
            "type": "Feature",
            "properties": {
                "id": f["properties"]["ADM0_A3"],
                "france": f["properties"]["ADM0_A3"] == "FRA",
            },
            "geometry": mapping(make_valid(shape(f["geometry"]))),
        }
    )
out = root / "geo/features/countries.geojson"
out.write_text(
    json.dumps({"type": "FeatureCollection", "features": features}, separators=(",", ":")) + "\n"
)
s = root / "geo/sources.yml"
reg = json.loads(s.read_text())
entry = next(x for x in reg["sources"] if x["id"] == "countries")
entry.update(
    sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
    modifications=(
        "Global Natural Earth 50m countries retained without geographic "
        "clipping; properties reduced; make_valid applied. World/ocean context "
        "for overseas views; historical IDs and source version retained."
    ),
)
s.write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n")
