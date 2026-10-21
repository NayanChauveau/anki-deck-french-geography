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
    PlaceCatalog,
    PlaceRule,
    RelationRule,
)


def generate(
    root: Path,
    rules: list[IdentificationRule | DepartmentRule | PlaceRule | RelationRule],
    layers: dict,
) -> list[Card]:
    cards = []
    seen_rules = set()
    for rule in rules:
        if rule.id in seen_rules:
            raise ValueError(f"Duplicate rule: {rule.id}")
        seen_rules.add(rule.id)
        if rule.layer not in layers:
            raise ValueError(f"Unknown geographic layer: {rule.layer}")
        if isinstance(rule, (PlaceRule, RelationRule)):
            cards.extend(generate_places(root, rule, layers[rule.layer]))
            continue
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
                    id=f"fr-geo-{rule.id}-{entry.id.lower()}",
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


def place_catalog(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Catalog path escapes project")
    # Department catalogs share these relation fields.
    catalog = PlaceCatalog.model_validate(yaml.safe_load(path.read_text()))
    entries = {entry.id: entry for entry in catalog.features}
    if len(entries) != len(catalog.features):
        raise ValueError(f"Duplicate catalog ID: {relative}")
    return entries


def generate_places(root, rule, geometries):
    entries = place_catalog(root, rule.catalog)
    valid_coverage = (
        entries.keys() <= geometries.keys()
        if isinstance(rule, RelationRule)
        else entries.keys() == geometries.keys()
    )
    if not valid_coverage:
        raise ValueError(f"Catalog/layer mismatch: {rule.catalog}")
    cards = []
    if isinstance(rule, RelationRule):
        related = place_catalog(root, rule.related_catalog)
        for entry in entries.values():
            target = getattr(entry, rule.relation)
            if target not in related:
                raise ValueError(f"Unknown {rule.relation} for {entry.id}: {target}")
            answer = related[target].name
            display_name = f"{entry.name} ({entry.qualifier})" if entry.qualifier else entry.name
            question = rule.question.format(name=display_name)
            if answer.casefold() in question.casefold():
                continue  # A relation already disclosed by its question adds no recall value.
            cards.append(
                Card(
                    id=f"fr-geo-{rule.id}-{entry.id.lower()}",
                    target=entry.id,
                    view=entry.view,
                    theme=rule.theme,
                    layer=rule.layer,
                    direction=rule.relation,
                    question=question,
                    answer=answer,
                    explanation=(
                        entry.explanation
                        if rule.relation in ("massif", "downstream", "ocean", "coast")
                        else f"{entry.name} → {answer} · Source : Insee, COG 2025."
                    ),
                    references=list(dict.fromkeys([*rule.references, *entry.references])),
                    front_map="none",
                    back_map="none",
                )
            )
        return cards
    for batch in batched(list(entries.values()), rule.batch_size):
        for direction in rule.directions:
            for entry in batch:
                locate = direction == "name-map"
                display_name = (
                    f"{entry.name} ({entry.qualifier})" if entry.qualifier else entry.name
                )
                cards.append(
                    Card(
                        id=f"fr-geo-{rule.id}-{entry.id.lower()}-{direction}",
                        target=entry.id,
                        view=entry.view,
                        layer=rule.layer,
                        theme=rule.theme,
                        direction=direction,
                        question=(
                            f"Où se situe {rule.noun} « {display_name} » ?"
                            if locate
                            else "Quel est le nom de l’élément surligné sur la carte ?"
                        ),
                        answer=display_name,
                        explanation=entry.explanation,
                        references=list(dict.fromkeys([*rule.references, *entry.references])),
                        front_map="blank" if locate else "target",
                        back_map="target",
                    )
                )
    return cards
