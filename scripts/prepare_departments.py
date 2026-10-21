"""Prepare an explicitly downloaded 2025 Etalab snapshot; never run during builds."""

import argparse
import hashlib
import json
import re
from pathlib import Path

import yaml
from shapely import make_valid
from shapely.geometry import mapping, shape
from shapely.ops import unary_union

parser = argparse.ArgumentParser()
parser.add_argument("input", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
original = args.input.read_bytes()
data = json.loads(original)
features, catalog = [], []
views = {
    "971": "world",
    "972": "world",
    "973": "world",
    "974": "world",
    "976": "world",
    **dict.fromkeys(["75", "92", "93", "94"], "paris-region"),
}
for feature in sorted(data["features"], key=lambda f: f["properties"]["code"]):
    code = feature["properties"]["code"]
    if not re.fullmatch(r"(?:0[1-9]|[1-8][0-9]|9[0-5]|2[AB]|97[12346])", code) or code == "20":
        continue
    key = f"dep-{code}"
    geom = make_valid(shape(feature["geometry"]))
    if geom.geom_type == "GeometryCollection":
        geom = unary_union([g for g in geom.geoms if g.geom_type in ("Polygon", "MultiPolygon")])
    if geom.is_empty or geom.geom_type not in ("Polygon", "MultiPolygon"):
        raise ValueError(f"Unexpected department geometry: {key}")
    features.append({"type": "Feature", "properties": {"id": key}, "geometry": mapping(geom)})
    catalog.append(
        {
            "id": key,
            "code": code,
            "name": feature["properties"]["nom"],
            **({"view": views[code]} if code in views else {}),
        }
    )
if len(features) != 101:
    raise ValueError(f"Expected 101 departments, got {len(features)}")
output = root / "geo/features/departments.geojson"
output.write_text(
    json.dumps(
        {"type": "FeatureCollection", "features": features},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    + "\n"
)
(root / "catalog/departments.yml").write_text(
    yaml.safe_dump({"features": catalog}, allow_unicode=True, sort_keys=False)
)
registry_path = root / "geo/sources.yml"
registry = yaml.safe_load(registry_path.read_text())
registry["sources"] = [s for s in registry["sources"] if s["id"] != "departments"]
registry["sources"].append(
    {
        "id": "departments",
        "source": "Etalab / data.gouv.fr, contours administratifs, IGN Admin Express",
        "version": "2025, 1000m; snapshot 2026-10-20",
        "url": "https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2025/geojson/departements-1000m.geojson",
        "license": "ODbL 1.0",
        "license_url": "https://opendatacommons.org/licenses/odbl/1-0/",
        "upstream_sha256": hashlib.sha256(original).hexdigest(),
        "file": "geo/features/departments.geojson",
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "modifications": (
            "WGS84; 101 departments selected by code, excluding COM; properties split into "
            "editorial catalog; IDs prefixed dep-; invalid polygons repaired with Shapely "
            "make_valid, discarding collapsed line remnants; "
            "no simplification beyond upstream 1000m."
        ),
    }
)
registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
