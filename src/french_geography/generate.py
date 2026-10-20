"""Build identification notes in memory from geographic layers and editorial catalogs."""

from pathlib import Path

import yaml

from french_geography.schema import Annotation, Card, CatalogFile, IdentificationRule


def generate(root: Path, rules: list[IdentificationRule], layers: dict) -> list[Card]:
    cards = []
    seen_rules = set()
    for rule in rules:
        if rule.id in seen_rules:
            raise ValueError(f"Duplicate rule: {rule.id}")
        seen_rules.add(rule.id)
        if rule.layer not in layers:
            raise ValueError(f"Unknown geographic layer: {rule.layer}")
        path = (root / rule.catalog).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError("Catalog path escapes project")
        catalog = CatalogFile.model_validate(yaml.safe_load(path.read_text()))
        entries = {entry.id: entry for entry in catalog.features}
        if len(entries) != len(catalog.features):
            raise ValueError(f"Duplicate catalog ID: {rule.catalog}")
        geometries = layers[rule.layer]
        if entries.keys() != geometries.keys():
            missing = sorted(geometries.keys() - entries.keys())
            unknown = sorted(entries.keys() - geometries.keys())
            raise ValueError(f"Catalog/layer mismatch: missing={missing}, unknown={unknown}")
        for entry in catalog.features:
            separator = "" if entry.article == "l’" else " "
            answer = entry.article.capitalize() + separator + entry.name
            if entry.label:
                lon, lat = entry.label.lon, entry.label.lat
            else:
                # An editable label position is only needed when this default overlaps.
                point = geometries[entry.id].representative_point()
                lon, lat = point.x, point.y
            cards.append(
                Card(
                    id=f"fr-geo-{rule.id}-{entry.id}",
                    target=entry.id,
                    view=rule.view,
                    question=rule.question,
                    answer=answer,
                    explanation=entry.explanation,
                    references=list(dict.fromkeys([*rule.references, *entry.references])),
                    annotations=[Annotation(text=entry.name, lon=lon, lat=lat)],
                )
            )
    return cards
