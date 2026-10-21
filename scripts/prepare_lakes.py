"""Prepare lake polygons offline from local TOPAGE and Natural Earth inputs."""

import argparse
import hashlib
import json
from pathlib import Path

import yaml
from shapely import make_valid
from shapely.geometry import mapping, shape
from shapely.ops import unary_union


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_lakes(root, natural_earth):
    registry_path = root / "geo/sources.yml"
    registry = yaml.safe_load(registry_path.read_text())
    previous = next(s for s in registry["sources"] if s["id"] == "lakes")
    if digest(natural_earth) != previous["upstream_sha256"]:
        raise ValueError("Expected pinned Natural Earth lakes v5.1.2")
    raw = root / "data/lakes/topage2024-selection.geojson"
    selection = root / "data/lakes/selection.yml"
    entries = yaml.safe_load(selection.read_text())["features"]
    originals = json.loads(raw.read_text())["features"]
    by_code = {f["properties"]["CdOH"]: f for f in originals}
    codes = [code for entry in entries for code in entry["codes"]]
    if len(codes) != len(set(codes)) or set(codes) != set(by_code):
        raise ValueError("Lake selection must match unique pinned Sandre codes exactly")
    features = []
    catalog = yaml.safe_load((root / "catalog/lakes.yml").read_text())["features"]
    expected_ids = {entry["id"] for entry in entries} | {"lake-leman"}
    if {entry["id"] for entry in catalog} != expected_ids:
        raise ValueError("Lake geometry selection and editorial catalog must match")
    for entry in entries:
        geom = unary_union([make_valid(shape(by_code[c]["geometry"])) for c in entry["codes"]])
        if geom.is_empty or geom.geom_type not in ("Polygon", "MultiPolygon"):
            raise ValueError(f"Invalid lake polygon: {entry['id']}")
        features.append(
            {"type": "Feature", "properties": {"id": entry["id"]}, "geometry": mapping(geom)}
        )
    geneva = [
        f
        for f in json.loads(natural_earth.read_text())["features"]
        if f["properties"].get("name") == "Lake Geneva"
    ]
    if len(geneva) != 1:
        raise ValueError("Expected exactly one Lake Geneva polygon")
    features.append(
        {
            "type": "Feature",
            "properties": {"id": "lake-leman"},
            "geometry": mapping(make_valid(shape(geneva[0]["geometry"]))),
        }
    )
    output = root / "geo/features/lakes.geojson"
    output.write_text(
        json.dumps(
            {"type": "FeatureCollection", "features": features},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n"
    )
    previous.update(
        sha256=digest(output),
        modifications=(
            "TOPAGE waterbody polygons selected by explicit Sandre codes in "
            "data/lakes/selection.yml; Hourtin and Carcans united as one lake. "
            "Lake Geneva selected by NE name. WGS84 coordinates retained; properties "
            "reduced; make_valid applied. Snapshot water outlines are not current water levels."
        ),
        inputs=[
            {
                "file": str(raw.relative_to(root)),
                "sha256": digest(raw),
                "url": (root / "data/lakes/topage2024-query.txt").read_text(),
                "license": "Licence Ouverte 2.0",
                "license_url": "https://www.etalab.gouv.fr/licence-ouverte-open-licence/",
            },
            {
                "file": str(selection.relative_to(root)),
                "sha256": digest(selection),
                "url": "https://github.com/NayanChauveau/anki-deck-french-geography/blob/main/data/lakes/selection.yml",
            },
        ],
    )
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("natural_earth", type=Path, help="Pinned Natural Earth 10m lakes v5.1.2")
    args = parser.parse_args()
    prepare_lakes(Path(__file__).resolve().parents[1], args.natural_earth)
