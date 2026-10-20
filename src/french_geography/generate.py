"""Build identification notes in memory from geographic layers and editorial catalogs."""

from itertools import batched
from pathlib import Path

import yaml

from french_geography.schema import (
    Annotation,
    Card,
    CatalogFile,
    DepartmentRule,
    IdentificationRule,
)


def generate(
    root: Path, rules: list[IdentificationRule | DepartmentRule], layers: dict
) -> list[Card]:
    cards = []
    seen_rules = set()
    for rule in rules:
        if rule.id in seen_rules:
            raise ValueError(f"Duplicate rule: {rule.id}")
        seen_rules.add(rule.id)
        if rule.layer not in layers:
            raise ValueError(f"Unknown geographic layer: {rule.layer}")
        if isinstance(rule, DepartmentRule):
            cards.extend(generate_departments(root, rule, layers[rule.layer]))
            continue
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


def generate_departments(root, rule, geometries):
    from french_geography.schema import DepartmentCatalog

    path = (root / rule.catalog).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Catalog path escapes project")
    catalog = DepartmentCatalog.model_validate(yaml.safe_load(path.read_text()))
    entries = {entry.id: entry for entry in catalog.features}
    if len(entries) != len(catalog.features):
        raise ValueError("Duplicate department ID")
    if entries.keys() != geometries.keys():
        raise ValueError("Department catalog/layer mismatch")
    cards = []
    ordered_entries = sorted(
        catalog.features, key=lambda entry: entry.code.replace("2A", "20A").replace("2B", "20B")
    )
    for batch in batched(ordered_entries, rule.batch_size):
        for direction in rule.directions:
            for entry in batch:
                values = {"name": entry.name, "code": entry.code, "map": ""}
                start, end = direction.split("-")
                if end == "map":
                    question = f"Où se situe le département « {values[start]} » ?"
                elif start == "map":
                    question = (
                        "Quel est le nom du département surligné ?"
                        if end == "name"
                        else "Quel est le numéro du département surligné ?"
                    )
                elif end == "code":
                    question = f"Quel est le numéro du département « {entry.name} » ?"
                else:
                    question = f"Quel département porte le numéro {entry.code} ?"
                cards.append(
                    Card(
                        id=f"fr-geo-{rule.id}-{entry.code.lower()}-{direction}",
                        target=entry.id,
                        view=entry.view or rule.view,
                        layer=rule.layer,
                        theme="Départements",
                        direction=direction,
                        question=question,
                        answer=(
                            f"{entry.name} ({entry.code})"
                            if end == "map" or direction == "map-code"
                            else values[end]
                        ),
                        explanation=f"{entry.name} · code départemental {entry.code}.",
                        references=rule.references,
                        front_map="target"
                        if start == "map"
                        else "blank"
                        if end == "map"
                        else "none",
                        back_map="target" if "map" in (start, end) else "none",
                    )
                )
    return cards
