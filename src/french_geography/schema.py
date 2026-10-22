from datetime import date
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
    layer: str = "rivers"
    theme: str = Field(default="Fleuves", min_length=1)
    front_map: Literal["none", "blank", "target"] = "target"
    back_map: Literal["none", "blank", "target"] = "target"
    direction: str = "identification"


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
    marker_radius: float = Field(default=3.2, gt=0, le=20)
    target_marker_radius: float = Field(default=9, gt=0, le=20)


class LabelPosition(Strict):
    lon: float = Field(ge=-180, le=180)
    lat: float = Field(ge=-90, le=90)


class EditorialReview(Strict):
    status: Literal["verified", "needs-review"]
    checked_on: date


class CatalogEntry(Strict):
    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str = Field(min_length=1)
    explanation_key: str | None = None
    references: list[str] = Field(default_factory=list)
    label: LabelPosition | None = None
    review: EditorialReview | None = None


class CatalogFile(Strict):
    features: list[CatalogEntry] = Field(min_length=1)


class IdentificationRule(Strict):
    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    layer: str = Field(min_length=1)
    catalog: str = Field(min_length=1)
    view: str = Field(min_length=1)
    references: list[str] = Field(min_length=1)


DepartmentDirection = Literal[
    "name-map", "map-name", "map-code", "name-code", "code-name", "code-map"
]


class DepartmentRule(Strict):
    type: Literal["departments"] = "departments"
    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    layer: str = "departments"
    catalog: str = "catalog/departments.yml"
    view: str = "metropolitan"
    references: list[str] = Field(min_length=1)
    batch_size: int = Field(default=10, ge=1, le=101)
    directions: list[DepartmentDirection] = Field(
        default_factory=lambda: ["name-map", "map-name", "map-code"], min_length=1
    )

    @model_validator(mode="after")
    def unique_directions(self):
        if len(set(self.directions)) != len(self.directions):
            raise ValueError("Duplicate department direction")
        return self


class DepartmentEntry(Strict):
    id: str = Field(pattern=r"^dep-(?:0[1-9]|[1-8][0-9]|9[0-5]|2[AB]|97[12346])$")
    code: str = Field(pattern=r"^(?:0[1-9]|[1-8][0-9]|9[0-5]|2[AB]|97[12346])$", strict=True)
    name: str = Field(min_length=1)
    view: str | None = None
    region: str | None = None
    capital: str | None = None

    @model_validator(mode="after")
    def consistent_id(self):
        if self.code == "20" or self.id != f"dep-{self.code}":
            raise ValueError("Department ID must match its code; Corsica uses 2A and 2B")
        return self


class DepartmentCatalog(Strict):
    features: list[DepartmentEntry] = Field(min_length=1)


class PlaceEntry(Strict):
    id: str = Field(pattern=r"^[a-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*$")
    name: str = Field(min_length=1)
    code: str | None = None
    capital: str | None = None
    department: str | None = None
    region: str | None = None
    coast: str | None = None
    ocean: str | None = None
    downstream: str | None = None
    massif: str | None = None
    qualifier_key: str | None = None
    view: str = "metropolitan"
    explanation_key: str | None = None
    references: list[str] = Field(default_factory=list)


class PlaceCatalog(Strict):
    features: list[PlaceEntry] = Field(min_length=1)


class PlaceRule(Strict):
    type: Literal["places"] = "places"
    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    layer: str
    catalog: str
    theme: str
    directions: list[Literal["name-map", "map-name"]] = Field(
        default_factory=lambda: ["name-map", "map-name"], min_length=1
    )
    exclude_targets: list[str] = Field(default_factory=list)
    batch_size: int = Field(default=10, ge=1)
    references: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_directions(self):
        if len(set(self.directions)) != len(self.directions):
            raise ValueError("Duplicate place direction")
        return self


class RelationRule(Strict):
    type: Literal["relations"] = "relations"
    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    layer: str
    catalog: str
    related_catalog: str
    relation: Literal["region", "department", "capital", "massif", "downstream", "ocean", "coast"]
    theme: str
    references: list[str] = Field(min_length=1)


class RuleFile(Strict):
    rules: list[IdentificationRule | DepartmentRule | PlaceRule | RelationRule] = Field(
        min_length=1
    )
