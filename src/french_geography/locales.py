"""Shared locale schema and formatting, independent of generation and rendering."""

from dataclasses import dataclass
from pathlib import Path
from string import Formatter
from typing import Annotated, Literal

import yaml
from pydantic import Field

from french_geography.distribution import THEME_KEYS, load_registry
from french_geography.schema import Strict

SemanticKey = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]*(?:\.[a-z0-9_-]+)+$")]


class RuleTranslation(Strict):
    questions: dict[str, str] = Field(min_length=1)
    answer: str | None = None
    explanation: str | None = None


class ThemeTranslation(Strict):
    name: str
    tag: str


class Translations(Strict):
    proper_names: Literal["retain_official_unless_translated"]
    names: dict[str, str]
    qualifiers: dict[SemanticKey, str]
    forms: dict[str, dict[str, str]]
    rules: dict[str, RuleTranslation] = Field(min_length=1)
    explanations: dict[SemanticKey, str] = Field(min_length=1)
    reference_labels: dict[SemanticKey, str]
    themes: dict[str, ThemeTranslation]
    ui: dict[str, str]


class UniqueKeysLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        keys = set()
        for key, _value in node.value:
            name = self.construct_object(key, deep=deep)
            if name in keys:
                raise ValueError(f"Duplicate translation key: {name}")
            keys.add(name)
        return super().construct_mapping(node, deep=deep)


def format_text(text, **values):
    if not text or not text.strip():
        raise ValueError("Empty translation")
    fields = set()
    for _literal, field, spec, conversion in Formatter().parse(text):
        if field is not None:
            if spec or conversion or field not in values:
                raise ValueError(f"Invalid translation template field: {field}")
            fields.add(field)
    return text.format(**values)


@dataclass
class Locale:
    code: str
    export: dict
    text: Translations

    def name(self, entry):
        return self.text.names.get(entry.id, entry.name)

    def display_name(self, entry):
        name = self.name(entry)
        if getattr(entry, "qualifier_key", None):
            if entry.qualifier_key not in self.text.qualifiers:
                raise ValueError(f"Missing qualifier translation: {entry.qualifier_key}")
            name += f" ({self.text.qualifiers[entry.qualifier_key]})"
        return name

    def explanation(self, entry):
        if not entry.explanation_key:
            return ""
        if entry.explanation_key not in self.text.explanations:
            raise ValueError(f"Missing explanation translation: {entry.explanation_key}")
        return self.text.explanations[entry.explanation_key]

    def question(self, rule, direction, **values):
        if rule not in self.text.rules or direction not in self.text.rules[rule].questions:
            raise ValueError(
                f"Missing translation for rule/direction: {self.code}/{rule}/{direction}"
            )
        template = self.text.rules[rule].questions[direction]
        # A map question must not accidentally interpolate a name or code clue.
        if direction in ("map-name", "map-code", "identification") and any(
            field is not None for _literal, field, _spec, _conv in Formatter().parse(template)
        ):
            raise ValueError(f"Map question contains a clue: {rule}/{direction}")
        return format_text(template, **values)

    def references(self, references):
        result = []
        for reference in references:
            if reference.startswith(("https://", "http://")):
                result.append(reference)
            elif reference.startswith("@") and reference[1:] in self.text.reference_labels:
                result.append(self.text.reference_labels[reference[1:]])
            else:
                raise ValueError(f"Missing reference translation: {self.code}/{reference}")
        return result


UI_KEYS = {
    "heading",
    "title",
    "model_name",
    "template_name",
    "sources",
    "map_alt",
    "front",
    "back",
    "gallery_title",
    "gallery_count",
    "credits_label",
    "public_domain",
    "parks_date",
}


def load_locale(root: Path, code: str) -> Locale:
    registry = load_registry(root)
    if code not in registry:
        raise ValueError(f"Unsupported language: {code}")
    text = Translations.model_validate(
        yaml.load((root / f"locales/{code}.yml").read_text(), Loader=UniqueKeysLoader)
    )
    for mapping in (
        text.names,
        text.qualifiers,
        text.explanations,
        text.reference_labels,
        text.ui,
        *text.forms.values(),
        *[r.questions for r in text.rules.values()],
    ):
        if any(not key.strip() or not value.strip() for key, value in mapping.items()):
            raise ValueError(f"Empty translation: {code}")
    if text.ui.keys() != UI_KEYS or text.themes.keys() != set(THEME_KEYS.values()):
        raise ValueError(f"Incomplete locale interface/theme coverage: {code}")
    for theme in text.themes.values():
        if not theme.name.strip() or not theme.tag.strip():
            raise ValueError(f"Empty theme translation: {code}")
    return Locale(code, registry[code], text)
