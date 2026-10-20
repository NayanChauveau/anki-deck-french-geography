from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Annotation(Strict):
    text: str = Field(min_length=1)
    lon: float = Field(ge=-180, le=180)
    lat: float = Field(ge=-90, le=90)
    side: Literal["both", "back"] = "back"


class Card(Strict):
    id: str = Field(pattern=r"^fr-geo-[a-z0-9-]+$")
    target: str = Field(min_length=1)
    view: str = Field(min_length=1)
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)
    explanation: str = ""
    references: list[str] = Field(min_length=1)
    annotations: list[Annotation] = Field(default_factory=list)


class View(Strict):
    projection: str
    bounds: tuple[float, float, float, float]
    width: int = Field(default=900, ge=320, le=2400)
    height: int = Field(default=900, ge=320, le=2400)
    inset: str | None = None

    @model_validator(mode="after")
    def ordered_bounds(self):
        west, south, east, north = self.bounds
        if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
            raise ValueError("Invalid WGS84 bounds")
        return self


Color = Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}$")]


class Style(Strict):
    ocean: Color = "#e8f1f5"
    land: Color = "#f9f7f0"
    neighbor: Color = "#e3e5df"
    border: Color = "#a4afa9"
    river: Color = "#b6ccd7"
    target: Color = "#006a85"
    ink: Color = "#203d48"
    target_width: float = Field(default=5, gt=0, le=20)


class LabelPosition(Strict):
    lon: float = Field(ge=-180, le=180)
    lat: float = Field(ge=-90, le=90)


class CatalogEntry(Strict):
    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str = Field(min_length=1)
    article: Literal["le", "la", "l’", "les"]
    explanation: str = ""
    references: list[str] = Field(default_factory=list)
    label: LabelPosition | None = None


class CatalogFile(Strict):
    features: list[CatalogEntry] = Field(min_length=1)


class IdentificationRule(Strict):
    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    layer: str = Field(min_length=1)
    catalog: str = Field(min_length=1)
    view: str = Field(min_length=1)
    question: str = Field(min_length=1)
    references: list[str] = Field(min_length=1)


class RuleFile(Strict):
    rules: list[IdentificationRule] = Field(min_length=1)
