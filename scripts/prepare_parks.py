"""Prepare national park cores from the official February 2026 PNF GeoJSON."""

import argparse
import hashlib
import json
from pathlib import Path

import yaml
from pyproj import Transformer
from shapely import make_valid, transform
from shapely.geometry import mapping, shape
from shapely.ops import unary_union

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("input", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
selection = {
    "PNV": ("vanoise", "Vanoise", "metropolitan", 2154),
    "PNPC": ("port-cros", "Port-Cros", "metropolitan", 2154),
    "PNP": ("pyrenees", "Pyrénées", "metropolitan", 2154),
    "PNC": ("cevennes", "Cévennes", "metropolitan", 2154),
    "PNE": ("ecrins", "Écrins", "metropolitan", 2154),
    "PNM": ("mercantour", "Mercantour", "metropolitan", 2154),
    "PNG": ("guadeloupe", "Guadeloupe", "world", 32620),
    "PNRUN": ("reunion", "La Réunion", "world", 32740),
    "PAG": ("guyane", "Parc amazonien de Guyane", "world", 32622),
    "PNCAL": ("calanques", "Calanques", "metropolitan", 2154),
    "PNFOR": ("forets", "Forêts", "metropolitan", 2154),
}
parts = {key: [] for key in selection}
for f in json.loads(args.input.read_text())["features"]:
    p = f["properties"]
    if p["code_r_enp"] not in ("CTPN", "CMPN"):
        continue
    key = p["id_local"].split("_", 1)[1]
    parts[key].append(make_valid(shape(f["geometry"])))
features, entries = [], []
for key, (slug, name, view, epsg) in selection.items():
    if not parts[key]:
        raise ValueError(f"Missing national park core: {key}")
    forward = Transformer.from_crs(4326, epsg, always_xy=True).transform
    inverse = Transformer.from_crs(epsg, 4326, always_xy=True).transform
    geom = unary_union(parts[key])
    geom = transform(
        transform(geom, forward, interleaved=False).simplify(100), inverse, interleaved=False
    )
    target = "park-" + slug
    features.append({"type": "Feature", "properties": {"id": target}, "geometry": mapping(geom)})
    entries.append(
        {
            "id": target,
            "name": name,
            "view": view,
            "explanation_key": "parks.core_areas_notice",
            "references": [
                "https://www.data.gouv.fr/datasets/contours-des-11-parcs-nationaux-de-france"
            ],
        }
    )
output = root / "geo/features/parks.geojson"
output.write_text(
    json.dumps(
        {"type": "FeatureCollection", "features": features},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    + "\n"
)
(root / "catalog/parks.yml").write_text(
    yaml.safe_dump({"features": entries}, allow_unicode=True, sort_keys=False)
)
p = root / "geo/sources.yml"
registry = yaml.safe_load(p.read_text())
registry["sources"][:] = [s for s in registry["sources"] if s["id"] != "parks"]
registry["sources"].append(
    {
        "id": "parks",
        "source": "Parcs nationaux de France / OFB",
        "version": "2026-02-11",
        "url": "https://www.data.gouv.fr/api/1/datasets/r/87b31eb7-b4e5-444c-b635-d071b319d14d",
        "license": "Licence Ouverte 2.0",
        "license_url": "https://www.etalab.gouv.fr/licence-ouverte-open-licence/",
        "upstream_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "file": "geo/features/parks.geojson",
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "modifications": "CTPN and CMPN cores selected by id_local for all eleven parks; "
        "Terrestrial and marine parts unioned per park; "
        "adhesion and adjacent marine areas excluded. "
        "make_valid applied, simplified at 100 m in Lambert-93 (metropolitan) or local UTM "
        "(overseas), reprojected to WGS84. Editorial names normalised; no new boundaries drawn.",
    }
)
p.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
