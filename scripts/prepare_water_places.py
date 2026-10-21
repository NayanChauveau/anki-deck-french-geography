"""Prepare first lakes, marine zones and overseas landmarks from local pinned inputs."""

import argparse
import hashlib
import json
from pathlib import Path

import yaml
from shapely import make_valid
from shapely.geometry import mapping, shape

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("lakes", type=Path, help="Natural Earth 10m lakes v5.1.2")
parser.add_argument("marine", type=Path, help="Natural Earth 10m marine polygons v5.1.2")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
registry_path = root / "geo/sources.yml"
registry = yaml.safe_load(registry_path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(layer, features, catalog, source):
    output = root / f"geo/features/{layer}.geojson"
    output.write_text(
        json.dumps(
            {"type": "FeatureCollection", "features": features},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n"
    )
    (root / f"catalog/{layer}.yml").write_text(
        yaml.safe_dump({"features": catalog}, allow_unicode=True, sort_keys=False)
    )
    registry["sources"][:] = [s for s in registry["sources"] if s["id"] != layer]
    registry["sources"].append(
        {"id": layer, "file": str(output.relative_to(root)), "sha256": digest(output), **source}
    )


def feature(key, geom):
    return {"type": "Feature", "properties": {"id": key}, "geometry": mapping(make_valid(geom))}


def natural_earth(path, filename):
    return {
        "source": "Natural Earth",
        "version": "v5.1.2",
        "upstream_sha256": digest(path),
        "url": f"https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/{filename}.geojson",
        "license": "Public domain",
        "license_url": "https://www.naturalearthdata.com/about/terms-of-use/",
    }


# Lakes: original national TOPAGE polygons, plus the transboundary Lake Geneva polygon.
raw = root / "data/lakes/topage2024-selection.geojson"
names = {
    "06P0000002000777191": ("bourget", "Bourget", "lake-savoie", "lakes.natural"),
    "06P0000002000776973": ("annecy", "Annecy", "lake-savoie", "lakes.natural"),
    "06P0000002000777258": (
        "serre-poncon",
        "Serre-Ponçon",
        "lake-south",
        "lakes.durance_reservoir",
    ),
    "06P0000002000777286": (
        "sainte-croix",
        "Sainte-Croix",
        "lake-south",
        "lakes.verdon_reservoir",
    ),
}
features, entries = [], []
for f in json.loads(raw.read_text())["features"]:
    key, name, view, explanation_key = names[f["properties"]["CdOH"]]
    key = "lake-" + key
    features.append(feature(key, shape(f["geometry"])))
    entries.append(
        {
            "id": key,
            "name": name,
            "view": view,
            "explanation_key": explanation_key,
            "references": [
                "https://www.data.gouv.fr/datasets/bd-topage-r-metropole-2024",
                "https://www.larousse.fr/encyclopedie/riviere-lac/la_Durance/117449",
            ],
        }
    )
for f in json.loads(args.lakes.read_text())["features"]:
    if f["properties"].get("name") == "Lake Geneva":
        features.append(feature("lake-leman", shape(f["geometry"])))
        entries.append(
            {
                "id": "lake-leman",
                "name": "Léman",
                "view": "lake-savoie",
                "explanation_key": "lakes.shared_france_switzerland",
                "references": [
                    "https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-lakes/"
                ],
            }
        )
if len(features) != 5:
    raise ValueError("Incomplete lake selection")
source = natural_earth(args.lakes, "ne_10m_lakes")
source.update(
    source="Natural Earth + IGN / OFB / Sandre BD TOPAGE",
    version="NE v5.1.2 + TOPAGE 2024",
    license="Natural Earth: public domain; TOPAGE: Licence Ouverte 2.0",
    modifications=(
        "Four TOPAGE waterbody polygons selected by Sandre code; Lake Geneva "
        "selected by NE name. WGS84 unchanged; properties reduced; make_valid "
        "applied."
    ),
    inputs=[
        {
            "file": str(raw.relative_to(root)),
            "sha256": digest(raw),
            "url": (root / "data/lakes/topage2024-query.txt").read_text(),
            "license": "Licence Ouverte 2.0",
            "license_url": "https://www.etalab.gouv.fr/licence-ouverte-open-licence/",
        }
    ],
)
save("lakes", features, entries, source)

# Marine areas: broad conventional extents, not territorial waters.
selection = {
    "English Channel": ("manche", "Manche"),
    "North Sea": ("mer-du-nord", "Mer du Nord"),
    "Bay of Biscay": ("gascogne", "Golfe de Gascogne"),
    "Golfe du Lion": ("lion", "Golfe du Lion"),
    "Mediterranean Sea": ("mediterranee", "Mer Méditerranée"),
}
features, entries = [], []
for f in json.loads(args.marine.read_text())["features"]:
    name = f["properties"].get("name")
    if name in selection:
        key, name = selection[name]
        key = "sea-" + key
        features.append(feature(key, shape(f["geometry"])))
        entries.append(
            {
                "id": key,
                "name": name,
                "view": "europe-seas",
                "explanation_key": ("seas.boundary_notice"),
            }
        )
if len(features) != 5:
    raise ValueError("Incomplete marine selection")
save(
    "seas",
    features,
    entries,
    {
        **natural_earth(args.marine, "ne_10m_geography_marine_polys"),
        "modifications": (
            "Five named marine polygons selected; properties reduced; make_valid "
            "applied; broad geographic extents without legal significance."
        ),
    },
)

# Overseas location points lie inside their department, without moving the geography.
departments = {
    f["properties"]["id"]: f
    for f in json.loads((root / "geo/features/departments.geojson").read_text())["features"]
}
selection = {
    "971": ("Guadeloupe", "caribbean", "atlantic"),
    "972": ("Martinique", "caribbean", "atlantic"),
    "973": ("Guyane", "caribbean", "atlantic"),
    "974": ("La Réunion", "indian-ocean", "indian"),
    "976": ("Mayotte", "indian-ocean", "indian"),
}
features, entries = [], []
for code, (name, view, ocean) in selection.items():
    key = "overseas-" + code
    features.append(
        feature(key, shape(departments["dep-" + code]["geometry"]).representative_point())
    )
    entries.append(
        {
            "id": key,
            "name": name,
            "view": view,
            "ocean": "ocean-" + ocean,
            "explanation_key": ("overseas.position_notice"),
            "references": [
                "https://geoconfluences.ens-lyon.fr/images/glossaire/img-france/monde-outre-mer-francais-2025.pdf/download"
            ],
        }
    )
dep_source = next(s for s in registry["sources"] if s["id"] == "departments")
save(
    "overseas",
    features,
    entries,
    {
        **{
            k: dep_source[k]
            for k in ("source", "version", "url", "license", "license_url", "upstream_sha256")
        },
        "modifications": (
            "Representative interior point computed from each of the five pinned "
            "overseas department polygons; WGS84, no displaced geometry."
        ),
        "inputs": [
            {"file": dep_source["file"], "sha256": dep_source["sha256"], "url": dep_source["url"]}
        ],
    },
)
(root / "catalog/oceans.yml").write_text(
    yaml.safe_dump(
        {
            "features": [
                {"id": "ocean-atlantic", "name": "Océan Atlantique"},
                {"id": "ocean-indian", "name": "Océan Indien"},
            ]
        },
        allow_unicode=True,
        sort_keys=False,
    )
)
registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
