"""Shared backgrounds and target overlays in one content-addressed SVG sprite."""

import html
import json
import math
import xml.etree.ElementTree as ET

from shapely.geometry import shape

from french_geography.cartography import Projection, add_geometry
from french_geography.cartography.display import derive, fingerprint
from french_geography.cartography.shared_cache import cached_maps, visual_key
from french_geography.cartography.svg import SVG_NS, glyph, svg_body, technical_id

# Back-side alternate maps: a target layer shown again over another layer's outlines.
ALTERNATE_CONTEXT = {"mountains": "departments"}


def display_settings(project):
    data = json.loads((project.root / "geo/display-svg.json").read_text())
    if (
        data["version"] != 1
        or data["coordinate_space"] != "projected SVG pixels"
        or data["max_error_bound_px"] != 0.5
    ):
        raise ValueError("Unsupported shared SVG display profile")
    if data["source_fingerprint"] != fingerprint(project):
        raise ValueError(
            "stale geo/display-svg.json; review settings and refresh the source fingerprint"
        )
    settings = {(g["layer"], g["view"]): g for g in data["groups"]}
    if len(settings) != len(data["groups"]):
        raise ValueError("Duplicate shared SVG display settings")
    return data, settings


def validate_cards(project):
    for card in project.cards:
        if card.front_map == card.back_map == "none":
            continue
        if card.layer not in project.layers or card.target not in project.layers[card.layer]:
            raise ValueError(f"Missing SVG layer/target: {card.id}")
        if card.view not in project.views:
            raise ValueError(f"Missing SVG view: {card.id}")
        for mode in (card.front_map, card.back_map):
            if mode not in ("blank", "target", "none"):
                raise ValueError(f"Invalid SVG map mode: {card.id}")


def sprite(project, settings):
    """One geometry per layer/projection; overlay selection never calculates coordinates."""
    validate_cards(project)
    root = ET.Element(f"{{{SVG_NS}}}svg")
    definitions = ET.SubElement(root, "defs")
    panes, targets, countries, projected_cache, shapes = {}, {}, {}, {}, {}
    mapped = {
        (c.layer, c.view) for c in project.cards if c.front_map != "none" or c.back_map != "none"
    }
    alternates = {
        (ALTERNATE_CONTEXT[layer], view)
        for layer, view in mapped
        if ALTERNATE_CONTEXT.get(layer) in project.layers
    }
    combinations = sorted(mapped | alternates)

    def projected(layer, view_key, rectangle):
        key = layer, view_key, rectangle
        if key not in projected_cache:
            projection = Projection(project.views[view_key], rectangle)
            detailed = view_key != "world" and any(
                f["properties"].get("detail") for f in project.countries
            )
            source = (
                {
                    str(i): shape(f["geometry"])
                    for i, f in enumerate(project.countries)
                    if bool(f["properties"].get("detail")) == detailed
                }
                if layer == "countries"
                else project.layers[layer]
            )
            items = {k: projection.geometry(g) for k, g in source.items()}
            items = {k: g for k, g in items.items() if not g.is_empty}
            if not items:
                raise ValueError(f"Empty SVG layer: {layer}/{view_key}")
            # Insets use the parent's pixel frame; retain precision at their small scale.
            setting = settings.get((layer, view_key)) if rectangle is None else None
            if rectangle is None and setting is None:
                raise ValueError(f"Missing SVG display settings: {layer}/{view_key}")
            precision = setting["decimals"] if setting else 8
            values = derive(list(items.values()), setting) if setting else list(items.values())
            projected_cache[key] = dict(zip(items, values, strict=True)), precision
        return projected_cache[key]

    for layer, parent_key in combinations:
        parent = project.views[parent_key]
        specifications = [(parent_key, None, parent_key)]
        if parent.inset:
            specifications.append(
                (
                    parent.inset,
                    (parent.width - 235, parent.height - 245, 205, 180),
                    parent_key + "-inset-" + parent.inset,
                )
            )
        pane_records = []
        for view_key, rectangle, pane_key in specifications:
            view = project.views[view_key]
            if pane_key not in countries:
                country_group = ET.SubElement(
                    definitions, "g", id=technical_id("countries", pane_key)
                )
                items, precision = projected("countries", view_key, rectangle)
                scene = []
                for key, geom in items.items():
                    add_geometry(
                        scene,
                        geom,
                        project.style.land
                        if project.countries[int(key)]["properties"]["france"]
                        else project.style.neighbor,
                        project.style.border,
                        1.0,
                    )
                country_group.extend(svg_body(view, scene, precision=precision, compact=True))
                countries[pane_key] = country_group.attrib["id"]
            map_id = technical_id("map", layer, pane_key)
            group = ET.SubElement(definitions, "g", id=map_id)
            if rectangle:
                x, y, w, h = rectangle
                ET.SubElement(
                    group,
                    "rect",
                    x=str(x - 5),
                    y=str(y - 5),
                    width=str(w + 10),
                    height=str(h + 10),
                    fill=project.style.ocean,
                    stroke=project.style.border,
                )
            else:
                ET.SubElement(
                    group,
                    "rect",
                    width=str(parent.width),
                    height=str(parent.height),
                    fill=project.style.ocean,
                )
            ET.SubElement(group, "use", href="#" + countries[pane_key])
            if layer == "cities" and parent_key == "paris-region" and rectangle is None:
                departments, precision = projected("departments", view_key, rectangle)
                scene = []
                for geom in departments.values():
                    add_geometry(scene, geom, project.style.land, project.style.border, 1.1)
                group.extend(svg_body(view, scene, precision=precision, compact=True))
            items, precision = projected(layer, view_key, rectangle)
            filled = layer in ("departments", "regions", "mountains")
            for target, geom in items.items():
                base_id = technical_id("shape", layer, pane_key, target)
                shape_group = glyph(
                    view,
                    geom,
                    base_id,
                    radius=project.style.marker_radius,
                    precision=precision,
                    compact=True,
                )
                if filled:
                    # Keep administrative/relief outlines identical when highlighted.
                    shape_group.set("stroke-width", "1.0")
                definitions.append(shape_group)
                shapes.setdefault((layer, pane_key), []).append(base_id)
                ET.SubElement(
                    group,
                    "use",
                    href="#" + base_id,
                    fill=project.style.land if filled else project.style.river,
                    stroke=project.style.border if filled else project.style.river,
                    **{"stroke-width": "1.0" if filled else "1.3"},
                )
                target_id = base_id
                if geom.geom_type in ("Point", "MultiPoint"):
                    target_id = technical_id("marker", layer, pane_key, target)
                    definitions.append(
                        glyph(
                            view,
                            geom,
                            target_id,
                            precision=precision,
                            compact=True,
                            radius=project.style.target_marker_radius,
                        )
                    )
                targets[(layer, parent_key, pane_key, target)] = target_id
            pane_records.append({"background": map_id, "key": pane_key})
        panes[(layer, parent_key)] = pane_records

    outlines = {}
    for layer, parent_key in sorted(alternates):
        for pane in panes[(layer, parent_key)]:
            # Context borders drawn above the highlight, so covered units stay readable.
            outline_id = technical_id("outline", layer, pane["key"])
            outline = ET.SubElement(
                definitions,
                "g",
                id=outline_id,
                fill="none",
                stroke=project.style.border,
                **{"stroke-width": "1.0"},
            )
            for shape_id in shapes[(layer, pane["key"])]:
                ET.SubElement(outline, "use", href="#" + shape_id)
            outlines[(layer, pane["key"])] = outline_id

    ids = [n.attrib["id"] for n in root.iter() if "id" in n.attrib]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate shared SVG identifiers")
    # Reject non-finite values before writing media, including high-precision insets.
    for node in root.iter():
        if node.tag.endswith("path") and any(
            v in node.get("d", "").lower() for v in ("nan", "inf")
        ):
            raise ValueError("Non-finite SVG path")
        for attr in ("cx", "cy"):
            if attr in node.attrib and not math.isfinite(float(node.attrib[attr])):
                raise ValueError("Non-finite SVG point")
    visuals = {}
    for card in project.cards:
        for mode in (card.front_map, card.back_map):
            if mode == "none":
                continue
            records = []
            for pane in panes[(card.layer, card.view)]:
                # Require the target even on blank questions, never silently omit it.
                key = card.layer, card.view, pane["key"], card.target
                if key not in targets:
                    raise ValueError(f"SVG target outside view: {card.id}/{pane['key']}")
                records.append(
                    {
                        "background": pane["background"],
                        "target": targets[key] if mode == "target" else None,
                    }
                )
            view = project.views[card.view]
            visual = {"view_box": f"0 0 {view.width} {view.height}", "panes": records}
            context = ALTERNATE_CONTEXT.get(card.layer)
            if (context, card.view) in alternates and mode == "target":
                visual["alternate"] = [
                    {
                        "background": pane["background"],
                        "target": targets[(card.layer, card.view, pane["key"], card.target)],
                        "outline": outlines[(context, pane["key"])],
                    }
                    for pane in panes[(context, card.view)]
                ]
            visuals[visual_key(card, mode)] = visual
    return ET.tostring(root, encoding="utf-8"), visuals


def maps(project, out):
    """Validate requests, then reuse the language-independent geographic artifact."""
    validate_cards(project)
    configuration, settings = display_settings(project)
    return cached_maps(project, out, configuration, settings, render=sprite)


def markup(project, record, *, alt, prefix="", alternate=False):
    if not record:
        return ""
    source = html.escape(prefix + record["shared_svg"], quote=True)
    highlight = (
        f'fill="{project.style.target}" stroke="{project.style.target}" '
        f'stroke-width="{project.style.target_width}"'
    )
    panes = record.get("alternate") if alternate else None
    result = (
        f'<svg class="fg-map{" fg-has-alternate" if panes else ""}" '
        f'viewBox="{record["view_box"]}" role="img" '
        f'aria-label="{html.escape(alt, quote=True)}">'
    )
    for pane in record["panes"]:
        result += f'<use class="fg-background" href="{source}#{pane["background"]}"/>'
        if pane["target"]:
            result += f'<use class="fg-highlight" href="{source}#{pane["target"]}" {highlight}/>'
    if panes:
        # Hidden second map, shown while pressed; distinct classes keep pane pairing intact.
        result += '<g class="fg-alternate">'
        for pane in panes:
            result += (
                f'<use href="{source}#{pane["background"]}"/>'
                f'<use href="{source}#{pane["target"]}" {highlight}/>'
                f'<use href="{source}#{pane["outline"]}"/>'
            )
        result += "</g>"
    # Explicit img reference exposes media to Anki's ordinary media scanner.
    return result + f'</svg><img src="{source}" alt="" hidden style="display:none">'
