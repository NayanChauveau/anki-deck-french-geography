"""Explicit English pilot, reusing geography without duplicating the source catalog."""

from dataclasses import replace

import yaml
from pydantic import Field

from french_geography.project import Project
from french_geography.schema import Strict


class Translation(Strict):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)
    explanation: str = Field(min_length=1)


class Translations(Strict):
    cards: dict[str, Translation] = Field(min_length=1)


def english_pilot(project: Project) -> Project:
    translations = Translations.model_validate(
        yaml.safe_load((project.root / "locales/en.yml").read_text())
    )
    source = {card.id: card for card in project.cards}
    unknown = translations.cards.keys() - source.keys()
    if unknown:
        raise ValueError(f"Unknown English translation IDs: {sorted(unknown)}")
    cards = [
        source[key].model_copy(update={"id": key + "-en", **value.model_dump()})
        for key, value in translations.cards.items()
    ]
    return replace(project, cards=cards)
