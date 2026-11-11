"""Shared backgrounds and target overlays in one content-addressed SVG sprite."""

import copy
import html
import json
import math
import xml.etree.ElementTree as ET
from dataclasses import replace

import shapely
from shapely.geometry import shape

from french_geography.cartography import Projection, add_geometry, geometries
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


def city_layer(project, settings, layer, view_key):
    view = project.views[view_key]
    setting = settings.get((layer, view_key))
    if setting is None:
        raise ValueError(f"Missing SVG display settings: {layer}/{view_key}")
    # Error bound applies at maximum zoom, where one pixel covers 1/max_zoom units.
    max_error = 0.5 / view.max_zoom
    projection = Projection(view)
    items = {k: projection.geometry(g) for k, g in project.layers[layer].items()}
    # Street pieces shorter than the error bound stay invisible even at maximum zoom.
    items = {
        k: shapely.multilinestrings([p for p in geometries(g) if p.length >= max_error])
        if g.geom_type == "MultiLineString"
        else g
        for k, g in items.items()
    }
    items = {k: g for k, g in items.items() if not g.is_empty}
    values = derive(list(items.values()), setting, max_error=max_error)
    return dict(zip(items, values, strict=True)), setting["decimals"]


# One em is 100 screen pixels in map units, staying above WebView minimum font sizes.
# Default for pages without the reviewer: about 900 map units over a 680 px card.
EM_PIXELS = 100
CITY_STROKE_SCALE = 130


def em(width):
    return f"{float(width) / EM_PIXELS:g}em"


def zoom_strokes(nodes):
    # Widths in em follow the font size the reviewer sets for each zoom, so strokes keep
    # their screen width without recomputing outlines on every redraw (non-scaling-stroke).
    for node in nodes:
        for element in node.iter():
            if "stroke-width" in element.attrib:
                element.set("stroke-width", em(element.get("stroke-width")))
    return nodes


def city_sprite(project, settings):
    """Zoomable city maps: one context background per view, street targets reused on top."""
    validate_cards(project)
    root = ET.Element(f"{{{SVG_NS}}}svg")
    definitions = ET.SubElement(root, "defs")
    visuals = {}
    for view_key in sorted({c.view for c in project.cards}):
        view = project.views[view_key]
        context, precision = city_layer(project, settings, view.context, view_key)
        scene = []
        for key, geom in context.items():
            if geom.geom_type in ("Polygon", "MultiPolygon"):
                fill = project.style.neighbor if key.endswith("-neighbours") else project.style.land
                add_geometry(scene, geom, fill, project.style.border, 1.0)
        background = svg_body(view, scene, precision=precision, compact=True)
        for key, geom in context.items():
            if geom.geom_type in ("LineString", "MultiLineString"):
                major = key.endswith("-major-streets")
                color = project.style.street_major if major else project.style.street
                lines = []
                add_geometry(lines, geom, "none", color, 1.6 if major else 0.8)
                # One path per street class: repeated attributes would outweigh coordinates.
                nodes = svg_body(view, lines, precision=precision, compact=True)
                nodes[0].set("d", " ".join(n.get("d") for n in nodes))
                nodes[0].attrib.pop("fill-rule")
                background.append(nodes[0])
        layers = sorted({c.layer for c in project.cards if c.view == view_key})
        for layer in layers:
            map_id = technical_id("map", layer, view_key)
            group = ET.SubElement(definitions, "g", id=map_id)
            ET.SubElement(
                group,
                "rect",
                width=str(view.width),
                height=str(view.height),
                fill=project.style.ocean,
            )
            group.extend(zoom_strokes(copy.deepcopy(background)))
            items, precision = city_layer(project, settings, layer, view_key)
            boxes = {}
            for target, geom in items.items():
                target_id = technical_id("shape", layer, view_key, target)
                definitions.append(glyph(view, geom, target_id, precision=precision, compact=True))
                x0, y0, x1, y1 = geom.bounds
                boxes[target] = target_id, [round(v, 1) for v in (x0, y0, x1 - x0, y1 - y0)]
            for card in project.cards:
                if (card.layer, card.view) != (layer, view_key):
                    continue
                if card.target not in boxes:
                    raise ValueError(f"SVG target outside view: {card.id}/{view_key}")
                target_id, box = boxes[card.target]
                for mode in (card.front_map, card.back_map):
                    if mode == "none":
                        continue
                    visuals[visual_key(card, mode)] = {
                        "view_box": f"0 0 {view.width} {view.height}",
                        "panes": [
                            {
                                "background": map_id,
                                "target": target_id if mode == "target" else None,
                            }
                        ],
                        "zoom": {"max": view.max_zoom, "target_box": box},
                    }
    return ET.tostring(root, encoding="utf-8"), visuals


def maps(project, out):
    """Validate requests, then reuse the language-independent geographic artifacts.

    City views get their own sprite so national cards never load street networks.
    """
    validate_cards(project)
    configuration, settings = display_settings(project)
    groups = {}
    for card in project.cards:
        view = project.views.get(card.view)
        groups.setdefault(card.view if view and view.context else None, []).append(card)
    manifest, entries = {}, {}
    for group, cards in sorted(groups.items(), key=lambda item: item[0] or ""):
        part, entry = cached_maps(
            replace(project, cards=cards),
            out,
            configuration,
            settings,
            render=city_sprite if group else sprite,
            group=group,
        )
        manifest.update(part)
        entries[group or "national"] = entry
    manifest = {card.id: manifest[card.id] for card in project.cards}
    (out / "manifest.json").write_text(
        json.dumps({"sprites": entries, "cards": manifest}, indent=2) + "\n"
    )
    return manifest


def markup(project, record, *, alt, prefix="", alternate=False):
    if not record:
        return ""
    source = html.escape(prefix + record["shared_svg"], quote=True)
    zoom = record.get("zoom")
    highlight = (
        f'fill="{project.style.target}" stroke="{project.style.target}" '
        f'stroke-width="{em(project.style.target_width) if zoom else project.style.target_width}"'
    )
    panes = record.get("alternate") if alternate else None
    classes = "fg-map" + (" fg-has-alternate" if panes else "") + (" fg-zoomable" if zoom else "")
    data = (
        f' font-size="{CITY_STROKE_SCALE}" data-max-zoom="{zoom["max"]:g}" '
        f'data-target-box="{" ".join(f"{v:g}" for v in zoom["target_box"])}"'
        if zoom
        else ""
    )
    result = (
        f'<svg class="{classes}" viewBox="{record["view_box"]}"{data} role="img" '
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
