"""Generate any registered language through the same canonical rules and facts."""

from dataclasses import replace

import yaml

from french_geography.generate import generate
from french_geography.locales import load_locale
from french_geography.project import Project
from french_geography.schema import RuleFile


def localize(project: Project, language: str) -> Project:
    locale = load_locale(project.root, language)
    rules = [
        rule
        for path in sorted((project.root / "cards").rglob("*.yml"))
        for rule in RuleFile.model_validate(yaml.safe_load(path.read_text())).rules
    ]
    if locale.text.rules.keys() != {rule.id for rule in rules}:
        raise ValueError(f"Rule translation coverage mismatch: {language}")
    catalogs = {rule.catalog for rule in rules}
    catalogs.update(rule.related_catalog for rule in rules if hasattr(rule, "related_catalog"))
    entries = []
    for relative in catalogs:
        path = (project.root / relative).resolve()
        if not path.is_relative_to(project.root.resolve()):
            raise ValueError("Catalog path escapes project")
        entries.extend(yaml.safe_load(path.read_text())["features"])
    ids = {entry["id"] for entry in entries}
    for mapping in (locale.text.names, locale.text.forms):
        if mapping.keys() - ids:
            raise ValueError(f"Unknown localized feature IDs: {sorted(mapping.keys() - ids)}")
    required = {entry["explanation_key"] for entry in entries if entry.get("explanation_key")}
    if required != locale.text.explanations.keys():
        raise ValueError(f"Explanation translation coverage mismatch: {language}")
    qualifiers = {entry["qualifier_key"] for entry in entries if entry.get("qualifier_key")}
    if qualifiers != locale.text.qualifiers.keys():
        raise ValueError(f"Qualifier translation coverage mismatch: {language}")
    generated = generate(project.root, rules, project.layers, locale)
    by_id = {card.id: card for card in generated}
    for original in project.cards:
        if original.id not in by_id:
            raise ValueError(f"Unknown source note: {original.id}")
    cards = [
        by_id[card.id].model_copy(update={"id": card.id + locale.export["note_suffix"]})
        for card in project.cards
    ]
    return replace(project, cards=cards)
