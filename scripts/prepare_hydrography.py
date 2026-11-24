"""Extend Natural Earth rivers from pinned, explicitly selected BD TOPAGE 2024 objects."""

import argparse
import hashlib
import json
from pathlib import Path

import yaml
from pyproj import Transformer
from shapely import transform
from shapely.geometry import Polygon, box, mapping, shape
from shapely.ops import unary_union

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("natural_earth", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
raw = root / "data/hydrography/topage2024-selection.geojson"
# Later selections are queried by exact Sandre code; the estuary file holds PlanEau polygons.
pinned = [
    (raw, root / "data/hydrography/topage2024-query.txt"),
    (
        root / "data/hydrography/topage2024-selection-2.geojson",
        root / "data/hydrography/topage2024-selection-2-query.txt",
    ),
    (
        root / "data/hydrography/topage2024-estuaries.geojson",
        root / "data/hydrography/topage2024-estuaries-query.txt",
    ),
]
upstream = json.loads(raw.read_text())["features"]
by_code = {
    f["properties"]["CdOH"]: f
    for path, _ in pinned
    for f in json.loads(path.read_text())["features"]
}
extension = yaml.safe_load((root / "catalog/hydrography-extension.yml").read_text())
editorial = extension["features"]
selection = yaml.safe_load((root / "geo/selection.yml").read_text())["rivers"]
ne = json.loads(args.natural_earth.read_text())["features"]
features = {}
for key, aliases in selection.items():
    geom = unary_union([shape(f["geometry"]) for f in ne if f["properties"].get("name") in aliases])
    features[key] = geom.intersection(box(-7, 40, 12, 53))
forward = Transformer.from_crs(4326, 2154, always_xy=True).transform
inverse = Transformer.from_crs(2154, 4326, always_xy=True).transform


def geometry(codes):
    if not codes or not set(codes) <= by_code.keys():
        raise ValueError(f"Unknown TOPAGE selection: {codes}")
    geom = unary_union([shape(by_code[c]["geometry"]) for c in codes])
    if geom.geom_type == "Polygon":
        # Estuary islands are below one map pixel; keep the outer water outline only.
        geom = Polygon(geom.exterior)
    # 150 m generalisation in a metric CRS, rather than a tolerance in degrees.
    return transform(
        transform(geom, forward, interleaved=False).simplify(150), inverse, interleaved=False
    )


catalog_path = root / "catalog/rivers.yml"
catalog = yaml.safe_load(catalog_path.read_text())
old = {e["id"]: e for e in catalog["features"] if e["id"] in selection}
relations = []
used = {}
for e in editorial:
    codes = e["codes"] or [
        f["properties"]["CdOH"]
        for f in upstream
        if f["properties"]["TopoOH"] in ("Fleuve la Somme", "la Somme Canalisée")
    ]
    features[e["id"]] = geometry(codes)
    used[e["id"]] = codes
    old[e["id"]] = {
        "id": e["id"],
        "name": e["name"],
        "references": e["references"],
        "review": e.get("review", {"status": "verified", "checked_on": "2026-10-20"}),
        "explanation_key": e["explanation_key"],
    }
    if e["downstream"]:
        relations.append(
            {k: e[k] for k in ("id", "name", "downstream", "references", "explanation_key")}
        )
# Natural Earth courses replaced (Saône, Garonne down to the bec d'Ambès) or supplemented (Rhine).
corrections = {
    "saone": ("06C0000002000794279", "replace"),
    "rhin": ("02C0000002000786588", "supplement"),
    "garonne": ("05C0000002000894629", "replace"),
}
for key, (code, mode) in corrections.items():
    corrected = geometry([code])
    features[key] = corrected if mode == "replace" else unary_union([features[key], corrected])
    used[key] = [code]
    old[key]["explanation_key"] = f"river.{key}.summary"
    old[key]["references"] = list(
        dict.fromkeys(
            old[key]["references"]
            + ["https://www.data.gouv.fr/datasets/bd-topage-r-metropole-2024"]
        )
    )
# Relations between rivers already present (Natural Earth IDs), reusing their editorial text.
for relation in extension.get("natural_earth_relations", []):
    entry = old[relation["id"]]
    relations.append(
        {
            "id": entry["id"],
            "name": entry["name"],
            "downstream": relation["downstream"],
            "references": entry["references"],
            "explanation_key": entry["explanation_key"],
        }
    )
missing = {r["downstream"] for r in relations} - old.keys()
if missing:
    raise ValueError(f"Unknown downstream rivers: {sorted(missing)}")
output = root / "geo/features/rivers.geojson"
output.write_text(
    json.dumps(
        {
            "type": "FeatureCollection",
            "features": [
                {"type": "Feature", "properties": {"id": key}, "geometry": mapping(geom)}
                for key, geom in features.items()
            ],
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    + "\n"
)
catalog_path.write_text(
    yaml.safe_dump({"features": list(old.values())}, allow_unicode=True, sort_keys=False)
)
(root / "catalog/river-relations.yml").write_text(
    yaml.safe_dump({"features": relations}, allow_unicode=True, sort_keys=False)
)
(root / "catalog/river-destinations.yml").write_text(
    yaml.safe_dump(
        {
            "features": [
                {"id": key, "name": old[key]["name"]}
                for key in sorted({e["downstream"] for e in relations})
            ]
        },
        allow_unicode=True,
        sort_keys=False,
    )
)
(root / "data/hydrography/selected-codes.json").write_text(json.dumps(used, indent=2) + "\n")
registry_path = root / "geo/sources.yml"
registry = yaml.safe_load(registry_path.read_text())
source = next(s for s in registry["sources"] if s["id"] == "rivers")
source.update(
    source="Natural Earth + IGN / OFB / Sandre BD TOPAGE",
    version="NE v5.1.2 + TOPAGE 2024",
    license="Natural Earth: public domain; BD TOPAGE: Licence Ouverte 2.0",
    sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
    modifications=f"Original 18 NE IDs retained; {len(editorial)} rivers added by explicit Sandre "
    "codes, including the Gironde estuary as a TOPAGE PlanEau polygon without its "
    "island holes; Saone and Garonne "
    "replaced; Rhine supplemented (international course still incomplete). "
    "Somme includes 78 Fleuve la Somme records and the canalised course. "
    "TOPAGE geometries simplified at 150 m in EPSG:2154 and reprojected to WGS84.",
)
source["inputs"] = [
    {
        "source": "IGN / OFB / Sandre, BD TOPAGE 2024",
        "url": query.read_text().strip(),
        "file": str(path.relative_to(root)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "license": "Licence Ouverte 2.0",
        "license_url": "https://www.etalab.gouv.fr/licence-ouverte-open-licence/",
    }
    for path, query in pinned
]
registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
