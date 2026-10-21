"""Prepare first lakes, marine zones and overseas landmarks from local pinned inputs."""

import argparse
import hashlib
import json
from pathlib import Path

import yaml
from prepare_lakes import prepare_lakes
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


# Lake preparation has its own declarative selection and offline entry point.

prepare_lakes(root, args.lakes)
registry = yaml.safe_load(registry_path.read_text())

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
    "971": ("Guadeloupe", "world", "atlantic"),
    "972": ("Martinique", "world", "atlantic"),
    "973": ("Guyane", "world", "atlantic"),
    "974": ("La Réunion", "world", "indian"),
    "976": ("Mayotte", "world", "indian"),
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
