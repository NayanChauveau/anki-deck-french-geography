"""Prepare pinned COG tables, regional polygons and selected city centres, offline."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import yaml
from shapely import make_valid
from shapely.geometry import mapping, shape
from shapely.ops import unary_union

parser = argparse.ArgumentParser()
parser.add_argument("regions", type=Path)
parser.add_argument("cog_regions", type=Path)
parser.add_argument("cog_departments", type=Path)
parser.add_argument("cog_communes", type=Path)
parser.add_argument("centres", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]


def rows(path):
    return list(csv.DictReader(path.open(encoding="utf-8-sig")))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n")


regions = rows(args.cog_regions)
departments = rows(args.cog_departments)
capitals = {row["CHEFLIEU"] for row in regions + departments}
selection = yaml.safe_load((root / "catalog/additional-cities.yml").read_text())
needed = capitals | set(selection["communes"])
communes = {
    row["COM"]: row
    for row in rows(args.cog_communes)
    if row["TYPECOM"] == "COM" and row["COM"] in needed
}
centres = {
    f["properties"]["commune"]: f
    for f in json.loads(args.centres.read_text())["features"]
    if f["properties"]["commune"] in needed
}
if (
    len(regions) != 18
    or len(departments) != 101
    or set(communes) != needed
    or set(centres) != needed
):
    raise ValueError("Incomplete administrative reference")
region_views = {
    "01": "world",
    "02": "world",
    "03": "world",
    "04": "world",
    "06": "world",
}
region_data = {row["REG"]: row for row in regions}
polygons = []
for f in json.loads(args.regions.read_text())["features"]:
    code = f["properties"]["code"]
    if code not in region_data:
        continue
    geom = make_valid(shape(f["geometry"]))
    if geom.geom_type == "GeometryCollection":
        geom = unary_union([g for g in geom.geoms if g.geom_type in ("Polygon", "MultiPolygon")])
    if geom.is_empty or not geom.is_valid:
        raise ValueError(code)
    polygons.append(
        {"type": "Feature", "properties": {"id": f"reg-{code}"}, "geometry": mapping(geom)}
    )
if len(polygons) != 18:
    raise ValueError("Regional geometry coverage")
write_json(
    root / "geo/features/regions.geojson", {"type": "FeatureCollection", "features": polygons}
)
region_catalog = {
    "features": [
        {
            "id": f"reg-{r['REG']}",
            "code": r["REG"],
            "name": r["LIBELLE"],
            "capital": f"city-{r['CHEFLIEU']}",
            "view": region_views.get(r["REG"], "metropolitan"),
        }
        for r in regions
    ]
}
(root / "catalog/regions.yml").write_text(
    yaml.safe_dump(region_catalog, allow_unicode=True, sort_keys=False)
)
dep_by_code = {r["DEP"]: r for r in departments}
dep_path = root / "catalog/departments.yml"
dep_catalog = yaml.safe_load(dep_path.read_text())
for entry in dep_catalog["features"]:
    row = dep_by_code[entry["code"]]
    entry.update(region=f"reg-{row['REG']}", capital=f"city-{row['CHEFLIEU']}")
dep_path.write_text(yaml.safe_dump(dep_catalog, allow_unicode=True, sort_keys=False))
cities = []
city_features = []
for code, row in sorted(communes.items()):
    point = centres[code]["geometry"]
    region = row["REG"]
    cities.append(
        {
            "id": f"city-{code}",
            "code": code,
            "name": row["LIBELLE"],
            "qualifier_key": "location.ile_de_france"
            if code == "93066"
            else "location.indian_ocean"
            if code == "97411"
            else None,
            "department": f"dep-{row['DEP']}",
            "region": f"reg-{region}",
            "view": (
                "paris-region"
                if code in {"75056", "92050", "93008", "94028", "93066"}
                else region_views.get(region, "metropolitan")
            ),
        }
    )
    city_features.append(
        {"type": "Feature", "properties": {"id": f"city-{code}"}, "geometry": point}
    )
(root / "catalog/cities.yml").write_text(
    yaml.safe_dump({"features": cities}, allow_unicode=True, sort_keys=False)
)
write_json(
    root / "geo/features/cities.geojson", {"type": "FeatureCollection", "features": city_features}
)
(root / "data/administration").mkdir(parents=True, exist_ok=True)
reference = root / "data/administration/cog-2025.json"
write_json(
    reference, {"regions": regions, "departments": departments, "communes": list(communes.values())}
)
registry_path = root / "geo/sources.yml"
registry = yaml.safe_load(registry_path.read_text())
registry["sources"] = [
    s for s in registry["sources"] if s["id"] not in ("regions", "cities", "administration")
]
base = {
    "version": "2025; local preparation 2026-10-20",
    "license": "ODbL 1.0",
    "license_url": "https://opendatacommons.org/licenses/odbl/1-0/",
}
for key, path, input_path, source, url, modifications in [
    (
        "regions",
        "geo/features/regions.geojson",
        args.regions,
        "Etalab / IGN, contours administratifs",
        "https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2025/geojson/regions-1000m.geojson",
        (
            "WGS84; 18 COG regions selected, COM excluded; IDs prefixed reg-; make_valid"
            " repairs; collapsed non-polygon remnants discarded; upstream 1000m generali"
            "sation retained."
        ),
    ),
    (
        "cities",
        "geo/features/cities.geojson",
        args.centres,
        "Etalab / IGN, positions des mairies",
        "https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2025/geojson/mairies.geojson",
        (
            "WGS84; town halls for COG 2025 capitals and editorial city selection; nam"
            "e/relations from COG; codes prefixed city-; one town-hall point per selecte"
            "d commune."
        ),
    ),
]:
    registry["sources"].append(
        {
            **base,
            "id": key,
            "source": source,
            "url": url,
            "version": base["version"] if key == "regions" else "2025; snapshot 2026-10-20",
            "upstream_sha256": digest(input_path),
            "file": path,
            "sha256": digest(root / path),
            "modifications": modifications,
        }
    )
registry["sources"].append(
    {
        "id": "administration",
        "kind": "reference",
        "source": "INSEE, COG au 1er janvier 2025",
        "version": "2025",
        "url": "https://www.insee.fr/fr/information/8377162",
        "license": "Licence Ouverte 2.0",
        "license_url": "https://www.insee.fr/fr/information/2008466?page=copyright.htm",
        "file": str(reference.relative_to(root)),
        "sha256": digest(reference),
        "upstream_sha256": digest(args.cog_regions),
        "inputs": [
            {
                "url": f"https://www.insee.fr/fr/statistiques/fichier/8377162/v_{kind}_2025.csv",
                "sha256": digest(path),
            }
            for kind, path in [
                ("region", args.cog_regions),
                ("departement", args.cog_departments),
                ("commune", args.cog_communes),
            ]
        ],
        "modifications": (
            "COG regions and departments retained; communes restricted to capitals "
            "and the editorial city selection"
            "; UTF-8 CSV converted to JSON without changing codes, names or relationship"
            "s."
        ),
    }
)
registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
print(
    len(region_catalog["features"]),
    "regions;",
    len(cities),
    "reusable cities;",
    len(departments),
    "department links",
)
