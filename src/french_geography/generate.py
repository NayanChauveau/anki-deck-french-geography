"""Build identification notes in memory from geographic layers and editorial catalogs."""

from itertools import batched
from pathlib import Path

import yaml

from french_geography.locales import format_text, load_locale
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
    locale=None,
) -> list[Card]:
    locale = locale or load_locale(root, "fr")
    cards = []
    seen_rules = set()
    for rule in rules:
        if rule.id in seen_rules:
            raise ValueError(f"Duplicate rule: {rule.id}")
        seen_rules.add(rule.id)
        if rule.layer not in layers:
            raise ValueError(f"Unknown geographic layer: {rule.layer}")
        if isinstance(rule, (PlaceRule, RelationRule)):
            cards.extend(generate_places(root, rule, layers[rule.layer], locale))
            continue
        if isinstance(rule, DepartmentRule):
            cards.extend(generate_departments(root, rule, layers[rule.layer], locale))
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
            values = {"name": locale.name(entry)}
            values.update(
                {key + "_name": value for key, value in locale.text.forms.get(entry.id, {}).items()}
            )
            answer = format_text(locale.text.rules[rule.id].answer, **values)
            if entry.label:
                lon, lat = entry.label.lon, entry.label.lat
            else:
                # An editable label position is only needed when this default overlaps.
                point = geometries[entry.id].representative_point()
                lon, lat = point.x, point.y
            for direction in rule.directions:
                locate = direction == "name-map"
                cards.append(
                    Card(
                        id=(
                            f"fr-geo-{rule.id}-{entry.id.lower()}" + ("-name-map" if locate else "")
                        ),
                        target=entry.id,
                        view=rule.view,
                        question=locale.question(rule.id, direction, **values),
                        direction=direction,
                        layer=rule.layer,
                        front_map="blank" if locate else "target",
                        answer=answer,
                        explanation=locale.explanation(entry),
                        references=locale.references(
                            list(dict.fromkeys([*rule.references, *entry.references]))
                        ),
                        annotations=[Annotation(text=entry.name, lon=lon, lat=lat)],
                    )
                )
    return cards


def generate_departments(root, rule, geometries, locale):
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
                values = {"name": locale.name(entry), "code": entry.code, "map": ""}
                start, end = direction.split("-")
                question = locale.question(rule.id, direction, **values)
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
                            f"{locale.name(entry)} ({entry.code})"
                            if end == "map" or direction == "map-code"
                            else values[end]
                        ),
                        explanation=format_text(
                            locale.text.rules[rule.id].explanation,
                            base_name=locale.name(entry),
                            **values,
                        ),
                        references=locale.references(rule.references),
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


def generate_places(root, rule, geometries, locale):
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
            # Eligibility is a canonical fact/name check, independent of output language.
            if related[target].name.casefold() in entry.name.casefold():
                continue
            answer = locale.name(related[target])
            display_name = locale.display_name(entry)
            question = locale.question(rule.id, rule.relation, name=display_name)
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
                        locale.explanation(entry)
                        if rule.relation in ("massif", "downstream", "ocean", "coast")
                        else format_text(
                            locale.text.rules[rule.id].explanation,
                            name=display_name,
                            base_name=locale.name(entry),
                            answer=answer,
                        )
                    ),
                    references=locale.references(
                        list(dict.fromkeys([*rule.references, *entry.references]))
                    ),
                    front_map="none",
                    back_map="none",
                )
            )
        return cards
    unknown = set(rule.exclude_targets) - entries.keys()
    if unknown:
        raise ValueError(f"Unknown excluded place targets: {sorted(unknown)}")
    selected = [entry for entry in entries.values() if entry.id not in rule.exclude_targets]
    for batch in batched(selected, rule.batch_size):
        for direction in rule.directions:
            for entry in batch:
                locate = direction == "name-map"
                display_name = locale.display_name(entry)
                cards.append(
                    Card(
                        id=f"fr-geo-{rule.id}-{entry.id.lower()}-{direction}",
                        target=entry.id,
                        view=entry.view,
                        layer=rule.layer,
                        theme=rule.theme,
                        direction=direction,
                        question=locale.question(rule.id, direction, name=display_name),
                        answer=display_name,
                        explanation=locale.explanation(entry),
                        references=locale.references(
                            list(dict.fromkeys([*rule.references, *entry.references]))
                        ),
                        front_map="blank" if locate else "target",
                        back_map="target",
                    )
                )
    return cards
