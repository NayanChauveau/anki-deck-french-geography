"""Shared projected scene rendered to SVG and PNG without network access."""

import base64
import hashlib
import html
import io
import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pyproj import Transformer
from shapely import transform
from shapely.geometry import box, shape

from french_geography.project import Project
from french_geography.schema import Card, View


@dataclass
class Primitive:
    kind: str
    points: list
    fill: str
    stroke: str = "none"
    width: float = 1
    text: str = ""


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


def scene_for(project: Project, card: Card, back: bool):
    view = project.views[card.view]
    style = project.style
    scene = []
    show_target = (card.back_map if back else card.front_map) == "target"
    background = {key: project.features[key] for key in project.layers[card.layer]}

    def layer(v, rect=None):
        projection = Projection(v, rect)
        for feature in project.countries:
            add_geometry(
                scene,
                projection.geometry(shape(feature["geometry"])),
                style.land if feature["properties"]["france"] else style.neighbor,
                style.border,
                0.8,
            )
        if card.layer == "cities" and card.view == "paris-region" and rect is None:
            for geom in project.layers["departments"].values():
                add_geometry(scene, projection.geometry(geom), style.land, style.border, 1.1)
        for geom in background.values():
            if card.layer in ("departments", "regions", "mountains"):
                add_geometry(scene, projection.geometry(geom), style.land, style.border, 1.1)
            else:
                add_geometry(scene, projection.geometry(geom), style.river, style.river, 1.5)
        target = projection.geometry(project.features[card.target])
        if target.is_empty:
            raise ValueError(f"Target outside view: {card.id}")
        if show_target:
            add_geometry(scene, target, style.target, style.target, style.target_width)
        return projection

    layer(view)
    if view.inset:
        inset = project.views[view.inset]
        rect = (view.width - 235, view.height - 245, 205, 180)
        x, y, w, h = rect
        scene.append(
            Primitive(
                "polygon",
                [[(x - 5, y - 5), (x + w + 5, y - 5), (x + w + 5, y + h + 5), (x - 5, y + h + 5)]],
                style.ocean,
                style.border,
            )
        )
        layer(inset, rect)
    # Reject projection failures before either renderer can produce broken output.
    for item in scene:
        points = (
            [p for ring in item.points for p in ring] if item.kind == "polygon" else item.points
        )
        if any(not math.isfinite(c) for point in points for c in point):
            raise ValueError("Non-finite projected coordinate")
    return view, scene


def render_svg(view, scene, ocean, font_path):
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{view.width}" '
        f'height="{view.height}" viewBox="0 0 {view.width} {view.height}">',
        f'<rect width="100%" height="100%" fill="{ocean}"/>',
    ]
    font_data = base64.b64encode(font_path.read_bytes()).decode()
    parts.append(
        "<style>@font-face{font-family:GeoSans;src:url(data:font/ttf;base64,"
        + font_data
        + ")} text{font-family:GeoSans,sans-serif}</style>"
    )
    for item in scene:
        attrs = (
            f'fill="{item.fill}" stroke="{item.stroke}" stroke-width="{item.width}" '
            'stroke-linejoin="round" stroke-linecap="round"'
        )
        if item.kind in ("polygon", "line"):
            rings = item.points if item.kind == "polygon" else [item.points]
            commands = []
            for ring in rings:
                commands.append(
                    "M"
                    + " L".join(f"{x:.2f},{y:.2f}" for x, y in ring)
                    + (" Z" if item.kind == "polygon" else "")
                )
            parts.append(f'<path d="{" ".join(commands)}" {attrs} fill-rule="evenodd"/>')
        elif item.kind == "point":
            x, y = item.points[0]
            parts.append(
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{max(2.5, item.width * 1.4):.2f}" {attrs}/>'
            )
        else:
            x, y = item.points[0]
            parts.append(
                f'<text x="{x:.2f}" y="{y:.2f}" font-family="sans-serif" '
                f'font-size="18" fill="{item.fill}">{html.escape(item.text)}</text>'
            )
    return ("".join(parts) + "</svg>\n").encode()


def render_png(view, scene, ocean, font_path):
    factor = 2
    image = Image.new("RGB", (view.width * factor, view.height * factor), ocean)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(str(font_path), size=18 * factor)

    def scaled(points):
        return [(round(x * factor), round(y * factor)) for x, y in points]

    for item in scene:
        width = max(1, round(item.width * factor))
        if item.kind == "polygon":
            mask = Image.new("L", image.size)
            md = ImageDraw.Draw(mask)
            for i, ring in enumerate(item.points):
                md.polygon(scaled(ring), fill=255 if i == 0 else 0)
            image.paste(item.fill, mask=mask)
            for ring in item.points:
                draw.line(scaled(ring), fill=item.stroke, width=width, joint="curve")
        elif item.kind == "line":
            draw.line(scaled(item.points), fill=item.stroke, width=width, joint="curve")
        elif item.kind == "point":
            x, y = scaled(item.points)[0]
            radius = max(2.5, item.width * 1.4) * factor
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=item.fill)
        else:
            x, y = scaled(item.points)[0]
            draw.text((x, y), item.text, fill=item.fill, font=font, anchor="ls")
    buffer = io.BytesIO()
    image.resize((view.width, view.height), Image.Resampling.LANCZOS).save(buffer, format="PNG")
    return buffer.getvalue()


def render(project: Project, card: Card, back: bool, out: Path):
    view, scene = scene_for(project, card, back)
    result = {}
    out.mkdir(parents=True, exist_ok=True)
    for extension, data in [
        (
            "svg",
            render_svg(
                view, scene, project.style.ocean, project.root / "assets/fonts/NotoSans-Regular.ttf"
            ),
        ),
        (
            "png",
            render_png(
                view, scene, project.style.ocean, project.root / "assets/fonts/NotoSans-Regular.ttf"
            ),
        ),
    ]:
        name = "geo-" + hashlib.sha256(data).hexdigest() + "." + extension
        path = out / name
        path.write_bytes(data)
        result[extension] = path
    return result
