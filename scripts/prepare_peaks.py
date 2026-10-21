"""Select four representative summit points from a local Natural Earth v5.1.2 file."""

import argparse
import hashlib
import json
from pathlib import Path

import yaml

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("input", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
selection = {
    "Monte Cinto": (
        "monte-cinto",
        "Monte Cinto",
        "corse",
        "Reliefs corses",
        "https://www.larousse.fr/encyclopedie/mont/monte_Cinto/113690",
    ),
    "Mont Blanc": (
        "mont-blanc",
        "Mont Blanc",
        "alpes",
        "Alpes",
        "https://www.larousse.fr/encyclopedie/mont/mont_Blanc/109035",
    ),
    "Puy de Sancy": (
        "puy-de-sancy",
        "Puy de Sancy",
        "massif-central",
        "Massif central",
        "https://www.larousse.fr/encyclopedie/autre-region/Massif_central/132176",
    ),
    "Crêt de la Neige": (
        "cret-de-la-neige",
        "Crêt de la Neige",
        "jura",
        "Jura",
        "https://www.larousse.fr/encyclopedie/mont/cr%C3%AAt_de_la_Neige/134922",
    ),
}
features, entries = [], []
for feature in json.loads(args.input.read_text())["features"]:
    name = feature["properties"].get("name")
    if name not in selection:
        continue
    key, french, massif, massif_name, reference = selection[name]
    key = "peak-" + key
    features.append({"type": "Feature", "properties": {"id": key}, "geometry": feature["geometry"]})
    entries.append(
        {
            "id": key,
            "name": french,
            "massif": "mountain-" + massif,
            "explanation_key": key.replace("peak-", "peak.", 1) + ".context",
            "view": "corsica-relief" if massif == "corse" else "metropolitan",
            "references": [reference],
        }
    )
if len(features) != len(selection):
    raise ValueError("Incomplete or duplicated summit selection")
output = root / "geo/features/peaks.geojson"
output.write_text(
    json.dumps(
        {"type": "FeatureCollection", "features": features},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    + "\n"
)
(root / "catalog/peaks.yml").write_text(
    yaml.safe_dump({"features": entries}, allow_unicode=True, sort_keys=False)
)
registry_path = root / "geo/sources.yml"
registry = yaml.safe_load(registry_path.read_text())
registry["sources"] = [s for s in registry["sources"] if s["id"] != "peaks"]
registry["sources"].append(
    {
        "id": "peaks",
        "source": "Natural Earth, elevation points",
        "version": "v5.1.2",
        "url": "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_10m_geography_regions_elevation_points.geojson",
        "license": "Public domain",
        "license_url": "https://www.naturalearthdata.com/about/terms-of-use/",
        "upstream_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "file": "geo/features/peaks.geojson",
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "modifications": (
            "Four named summit points selected; coordinates unchanged; IDs prefixed peak-; "
            "elevation attributes omitted. Generalized positions are learning landmarks, "
            "not navigation data. Massif membership documented separately in the editorial catalog."
        ),
    }
)
registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
