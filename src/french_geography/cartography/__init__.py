"""Projection and geometry primitives for shared SVG maps, without network access."""

from dataclasses import dataclass

from pyproj import Transformer
from shapely import transform
from shapely.geometry import box

from french_geography.schema import View


@dataclass
class Primitive:
    kind: str
    points: list
    fill: str
    stroke: str = "none"
    width: float = 1


class Projection:
    def __init__(self, view: View, rectangle=None):
        self.transformer = Transformer.from_crs("EPSG:4326", view.projection, always_xy=True)
        west, south, east, north = view.bounds
        # Densify bounds before projection: projected edges need not be straight.
        ring = [(west + (east - west) * i / 100, lat) for lat in [south, north] for i in range(101)]
        ring += [
            (lon, south + (north - south) * i / 100) for lon in [west, east] for i in range(101)
        ]
        pts = [self.transformer.transform(*p, errcheck=True) for p in ring]
        xs, ys = zip(*pts, strict=True)
        self.bounds = min(xs), min(ys), max(xs), max(ys)
        x, y, width, height = rectangle or (24, 24, view.width - 48, view.height - 48)
        self.scale = min(width / (max(xs) - min(xs)), height / (max(ys) - min(ys)))
        self.ox = x + (width - (max(xs) - min(xs)) * self.scale) / 2
        self.oy = y + (height - (max(ys) - min(ys)) * self.scale) / 2
        self.window = box(*view.bounds)

    def pixel(self, x, y, z=None):
        return (
            self.ox + (x - self.bounds[0]) * self.scale,
            self.oy + (self.bounds[3] - y) * self.scale,
        )

    def point(self, lon, lat):
        return self.pixel(*self.transformer.transform(lon, lat, errcheck=True))

    def geometry(self, geom):
        clipped = geom.intersection(self.window)
        return transform(
            transform(clipped, self.transformer.transform, interleaved=False),
            self.pixel,
            interleaved=False,
        )


def geometries(geom):
    if geom.is_empty:
        return
    if hasattr(geom, "geoms"):
        for part in geom.geoms:
            yield from geometries(part)
    else:
        yield geom


def add_geometry(scene, geom, fill, stroke, width):
    for part in geometries(geom):
        if part.geom_type == "Polygon":
            rings = [list(part.exterior.coords), *[list(r.coords) for r in part.interiors]]
            scene.append(Primitive("polygon", rings, fill, stroke, width))
        elif part.geom_type in ("LineString", "LinearRing"):
            scene.append(Primitive("line", list(part.coords), "none", stroke, width))
        elif part.geom_type == "Point":
            scene.append(Primitive("point", [(part.x, part.y)], fill, stroke, width))
        else:
            raise ValueError(f"Unsupported geometry: {part.geom_type}")
