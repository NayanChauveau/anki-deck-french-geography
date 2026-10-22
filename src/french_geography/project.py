import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import yaml
from pyproj import CRS
from shapely.geometry import box, shape

from french_geography.generate import generate
from french_geography.schema import Card, RuleFile, Style, View


@dataclass
class Project:
    root: Path
    cards: list[Card]
    views: dict[str, View]
    style: Style
    countries: list[dict]
    features: dict
    sources: list[dict]
    layers: dict


def load(root: Path) -> Project:
    sources = yaml.safe_load((root / "geo/sources.yml").read_text())["sources"]
    layers = {}
    for source in sources:
        if source["id"] in layers:
            raise ValueError(f"Duplicate source ID: {source['id']}")
        for field in (
            "source",
            "version",
            "url",
            "license",
            "license_url",
            "modifications",
            "upstream_sha256",
        ):
            if not source.get(field):
                raise ValueError(f"Missing source field: {field}")
        path = (root / source["file"]).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError("Dataset path escapes project")
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError(f"Dataset checksum mismatch: {path}")
        for item in source.get("inputs", []):
            if "file" in item:
                input_path = (root / item["file"]).resolve()
                if not input_path.is_relative_to(root.resolve()):
                    raise ValueError("Dataset input path escapes project")
                if hashlib.sha256(input_path.read_bytes()).hexdigest() != item["sha256"]:
                    raise ValueError(f"Dataset input checksum mismatch: {input_path}")
        if source.get("kind") != "reference":
            layers[source["id"]] = json.loads(path.read_text())["features"]
    features = {}
    for feature in [f for key, layer in layers.items() if key != "countries" for f in layer]:
        key = feature["properties"]["id"]
        if key in features:
            raise ValueError(f"Duplicate feature: {key}")
        features[key] = shape(feature["geometry"])
    countries = list(layers["countries"])
    context = next((s for s in sources if s["id"] == "country-context"), None)
    if context:
        countries.extend(json.loads((root / context["file"]).read_text())["features"])
    for feature in countries:
        geom = shape(feature["geometry"])
        if geom.is_empty or not geom.is_valid:
            raise ValueError("Invalid country geometry")
    for geom in features.values():
        if geom.is_empty or not geom.is_valid:
            raise ValueError("Invalid target geometry")
    views = {
        key: View.model_validate(value)
        for key, value in yaml.safe_load((root / "geo/views.yml").read_text())["views"].items()
    }
    for key, view in views.items():
        CRS.from_user_input(view.projection)
        if view.inset and (view.inset not in views or view.inset == key):
            raise ValueError(f"Invalid inset: {view.inset}")
    rules = []
    for path in sorted((root / "cards").rglob("*.yml")):
        rules.extend(RuleFile.model_validate(yaml.safe_load(path.read_text())).rules)
    geographic_layers = {
        key: {
            feature["properties"]["id"]: features[feature["properties"]["id"]] for feature in layer
        }
        for key, layer in layers.items()
        if key != "countries"
    }
    cards = generate(root, rules, geographic_layers)
    if not cards or len({card.id for card in cards}) != len(cards):
        raise ValueError("Empty collection or duplicate note IDs")
    for card in cards:
        if card.target not in features or card.view not in views:
            raise ValueError(f"Unknown feature/view: {card.id}")
        if not features[card.target].intersects(box(*views[card.view].bounds)):
            raise ValueError(f"Target outside view: {card.id}")
    style = Style.model_validate(yaml.safe_load((root / "geo/styles.yml").read_text())["styles"])
    return Project(root, cards, views, style, countries, features, sources, geographic_layers)
