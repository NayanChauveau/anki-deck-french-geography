"""SVG primitives and safe technical identifiers, without embedded fonts or translations."""

import re
import xml.etree.ElementTree as ET

from french_geography.cartography import add_geometry

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def technical_id(*parts):
    text = "-".join(parts)
    if not re.fullmatch(r"[a-z][a-zA-Z0-9-]*", text):
        raise ValueError(f"Unsafe SVG ID: {text}")
    return "fg-" + text


def svg_body(view, scene, *, precision=2, compact=False):
    nodes = []

    def number(value):
        text = f"{value:.{precision}f}"
        if compact:
            text = text.rstrip("0").rstrip(".") if "." in text else text
        return "0" if text in ("-0", "-0.0") else text

    for primitive in scene:
        attrs = {
            "fill": primitive.fill,
            "stroke": primitive.stroke,
            "stroke-width": str(primitive.width),
            "stroke-linejoin": "round",
            "stroke-linecap": "round",
        }
        if primitive.kind in ("line", "polygon"):
            node = ET.Element(f"{{{SVG_NS}}}path", {"d": "", **attrs, "fill-rule": "evenodd"})
        elif primitive.kind == "point":
            node = ET.Element(
                f"{{{SVG_NS}}}circle",
                {"cx": "", "cy": "", "r": f"{max(2.5, primitive.width * 1.4):.2f}", **attrs},
            )
        else:
            raise ValueError(f"Unsupported SVG primitive: {primitive.kind}")
        nodes.append(node)
        if primitive.kind in ("line", "polygon"):
            rings = primitive.points if primitive.kind == "polygon" else [primitive.points]
            separator = " " if compact else " L"
            node.set(
                "d",
                " ".join(
                    "M"
                    + separator.join(f"{number(x)},{number(y)}" for x, y in ring)
                    + ("Z" if primitive.kind == "polygon" else "")
                    for ring in rings
                ),
            )
        elif primitive.kind == "point":
            node.set("cx", number(primitive.points[0][0]))
            node.set("cy", number(primitive.points[0][1]))
    return nodes


def glyph(view, geometry, glyph_id, *, radius=2.5, precision=2, compact=False):
    scene = []
    add_geometry(scene, geometry, "#000000", "#000000", 1)
    group = ET.Element("g", id=glyph_id)
    for element, primitive in zip(
        svg_body(view, scene, precision=precision, compact=compact), scene, strict=True
    ):
        for key in ("fill", "stroke", "stroke-width"):
            element.attrib.pop(key, None)
        if primitive.kind == "line":
            element.set("fill", "none")
            # Flat ends preserve the appearance of tiny detached segments.
            element.set("stroke-linecap", "butt")
        if primitive.kind == "point":
            element.set("r", str(radius))
            element.set("stroke", "#ffffff")
            element.set("stroke-width", "1.8")
        group.append(element)
    return group
