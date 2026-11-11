"""Prepare Marseille streets and context from pinned local OpenStreetMap extracts."""

import hashlib
import json
from pathlib import Path

import shapely
import yaml
from shapely.geometry import LineString, MultiLineString, mapping
from shapely.ops import polygonize, unary_union

root = Path(__file__).resolve().parents[1]
data = root / "data/marseille"
MARSEILLE = 76469
# Drawn thicker than the rest of the network.
MAJOR = {
    "motorway",
    "motorway_link",
    "trunk",
    "trunk_link",
    "primary",
    "primary_link",
    "secondary",
    "secondary_link",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def line(geometry):
    return LineString([(p["lon"], p["lat"]) for p in geometry])


def compact(geometry):
    # About 0.1 m: far below the deck's maximum zoom resolution.
    return shapely.set_precision(geometry, 1e-6)


def polygon(relation):
    def rings(role):
        lines = [line(m["geometry"]) for m in relation["members"] if m.get("role") == role]
        return unary_union(list(polygonize(lines)))

    result = rings("outer").difference(rings("inner"))
    if result.is_empty or not result.is_valid:
        raise ValueError(f"Invalid commune boundary: {relation['tags']['name']}")
    return result


streets = json.loads((data / "osm-streets.json").read_text())["elements"]
communes = json.loads((data / "osm-communes.json").read_text())["elements"]
selection = yaml.safe_load((data / "street-selection.yml").read_text())["streets"]

major = [line(w["geometry"]) for w in streets if w["tags"]["highway"] in MAJOR]
minor = [line(w["geometry"]) for w in streets if w["tags"]["highway"] not in MAJOR]
marseille = next(polygon(r) for r in communes if r["id"] == MARSEILLE)
neighbours = unary_union([polygon(r) for r in communes if r["id"] != MARSEILLE])
context = {
    "marseille-neighbours": neighbours.difference(marseille),
    "marseille-land": marseille,
    "marseille-major-streets": shapely.line_merge(MultiLineString(major)),
    "marseille-minor-streets": shapely.line_merge(MultiLineString(minor)),
}
by_id = {w["id"]: w for w in streets}
targets = {}
for street in selection:
    # Way IDs, not names: homonymous streets elsewhere in the city stay out.
    ways = [by_id[i] for i in street["ways"] if i in by_id]
    if len(ways) != len(street["ways"]) or any(
        w["tags"].get("name") != street["osm_name"] for w in ways
    ):
        raise ValueError(f"Street ways missing or renamed: {street['id']}")
    targets[street["id"]] = shapely.line_merge(MultiLineString([line(w["geometry"]) for w in ways]))


def write(name, items):
    path = root / "geo/features" / name
    features = [
        {"type": "Feature", "properties": {"id": key}, "geometry": mapping(compact(geom))}
        for key, geom in items.items()
    ]
    path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}, separators=(",", ":"))
        + "\n"
    )
    return path


context_path = write("marseille-context.geojson", context)
streets_path = write("streets.geojson", targets)
query = "https://overpass-api.de/api/interpreter"
inputs = [
    {
        "source": "OpenStreetMap contributors, Overpass API",
        "url": query,
        "query": f"local:data/marseille/{name}-query.overpassql",
        "file": f"data/marseille/osm-{name}.json",
        "sha256": sha256(data / f"osm-{name}.json"),
        "license": "ODbL 1.0",
        "license_url": "https://www.openstreetmap.org/copyright",
    }
    for name in ("streets", "communes")
]
ranking_input = {
    "file": "data/marseille/street-ranking.yml",
    "url": "local:data/marseille/street-ranking.yml",
    "sha256": sha256(data / "street-ranking.yml"),
}
selection_input = {
    "file": "data/marseille/street-selection.yml",
    "url": "local:data/marseille/street-selection.yml",
    "sha256": sha256(data / "street-selection.yml"),
}
version = "OpenStreetMap snapshot " + json.loads((data / "osm-streets.json").read_text())["osm3s"][
    "timestamp_osm_base"
].removesuffix("Z")
common = {
    "source": "OpenStreetMap contributors",
    "version": version,
    "url": query,
    "license": "ODbL 1.0",
    "license_url": "https://www.openstreetmap.org/copyright",
    "upstream_sha256": inputs[0]["sha256"],
}
registry_path = root / "geo/sources.yml"
registry = yaml.safe_load(registry_path.read_text())
registry["sources"] = [
    s for s in registry["sources"] if s["id"] not in ("marseille-context", "streets")
]
registry["sources"] += [
    {
        "id": "marseille-context",
        **common,
        "file": "geo/features/marseille-context.geojson",
        "sha256": sha256(context_path),
        "modifications": (
            "Commune boundaries assembled from OSM relations (Marseille, relation 76469, and "
            "neighbours); neighbours merged into one area. Road ways (motorway to pedestrian, "
            "excluding service roads and paths) merged into major (motorway to secondary) and "
            "minor networks. Names and other tags dropped; coordinates rounded to 1e-6 degree."
        ),
        "inputs": inputs,
    },
    {
        "id": "streets",
        **common,
        "file": "geo/features/streets.geojson",
        "sha256": sha256(streets_path),
        "modifications": (
            "Streets ranked by scripts/select_marseille_streets.py (rules in "
            "data/marseille/street-ranking.yml); ways listed by OSM ID in "
            "data/marseille/street-selection.yml merged per street; tags dropped; "
            "coordinates rounded to 1e-6 degree."
        ),
        "inputs": [inputs[0], selection_input, ranking_input],
    },
]
registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
