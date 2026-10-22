"""Display-only geometry transformations with topology and error checks."""

import hashlib
import inspect
import json
from collections import Counter

import shapely
from shapely.geometry import LineString, MultiLineString

from french_geography.cartography import Projection, geometries


def fingerprint(project):
    value = {
        "sources": {s["id"]: s["sha256"] for s in project.sources},
        "views": {k: v.model_dump() for k, v in project.views.items()},
        "style": project.style.model_dump(),
        "projection": inspect.getsource(Projection),
    }
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def signature(geometry):
    parts = list(geometries(geometry))
    return (
        geometry.geom_type,
        Counter(g.geom_type for g in parts),
        sum(len(g.interiors) for g in parts if g.geom_type == "Polygon"),
    )


def endpoint_key(point):
    return tuple(round(v, 9) for v in point)


def river_nodes(items):
    return {
        endpoint_key(p)
        for geometry in items
        for part in geometries(geometry)
        for p in (part.coords[0], part.coords[-1])
    }


def simplify_river(geometry, tolerance, protected):
    if geometry.geom_type == "MultiLineString":
        return MultiLineString([simplify_river(g, tolerance, protected) for g in geometry.geoms])
    coordinates = list(geometry.coords)
    cuts = [
        0,
        *[i for i in range(1, len(coordinates) - 1) if endpoint_key(coordinates[i]) in protected],
        len(coordinates) - 1,
    ]
    result = []
    for start, end in zip(cuts, cuts[1:], strict=False):
        piece = list(LineString(coordinates[start : end + 1]).simplify(tolerance).coords)
        result.extend(piece if not result else piece[1:])
    return LineString(result)


def quantize(geometry, decimals):
    return shapely.transform(
        geometry, lambda x, y: (x.round(decimals), y.round(decimals)), interleaved=False
    )


def rounding_error(original, rounded):
    a, b = shapely.get_coordinates(original), shapely.get_coordinates(rounded)
    return float((((a - b) ** 2).sum(axis=1) ** 0.5).max(initial=0))


def protected_vertices_present(original, rounded, protected, decimals):
    expected = {
        tuple(round(v, decimals) for v in p)
        for p in shapely.get_coordinates(original)
        if endpoint_key(p) in protected
    }
    actual = {tuple(p) for p in shapely.get_coordinates(rounded)}
    return expected <= actual


def assess(source, candidate, *, coverage=False, protected=None, decimals=2):
    if any(
        b.is_empty or not b.is_valid or signature(a) != signature(b)
        for a, b in zip(source, candidate, strict=True)
    ):
        return "invalid-or-changed-parts"
    if coverage and not shapely.coverage_is_valid(candidate):
        return "coverage-broken"
    if protected and any(
        not protected_vertices_present(a, b, protected, decimals)
        for a, b in zip(source, candidate, strict=True)
    ):
        return "river-junction-lost"
    return None


def derive(source, setting):
    """Apply one reviewed setting, rejecting lost parts or broken shared borders."""
    tolerance, decimals = setting["tolerance_px"], setting["decimals"]
    if not 0 <= tolerance <= 0.6 or decimals not in (1, 2, 3, 5, 7, 8):
        raise ValueError("Invalid shared SVG display setting")
    method = setting["method"]
    if method == "unchanged-projected-invalid":
        if tolerance != 0 or decimals != 2:
            raise ValueError("Invalid unchanged geometry setting")
        return source
    coverage = method == "coverage"
    protected = river_nodes(source) if method == "river-nodes" else None
    if method not in ("coverage", "river-nodes", "preserve-topology"):
        raise ValueError("Unknown display simplification method")
    simplified = simplify(source, tolerance, method=method, protected=protected)
    candidate = [quantize(g, decimals) for g in simplified]
    reason = assess(source, candidate, coverage=coverage, protected=protected, decimals=decimals)
    if reason:
        raise ValueError(f"Unsafe shared SVG geometry: {reason}")
    bound = max(
        (0 if tolerance == 0 else a.hausdorff_distance(b)) + rounding_error(b, c)
        for a, b, c in zip(source, simplified, candidate, strict=True)
    )
    if bound > 0.5:
        raise ValueError("Shared SVG display error budget exceeded")
    return candidate


def simplify(source, tolerance, *, method, protected=None):
    """Simplify projected geometry while preserving shared borders and river nodes."""
    coverage = method == "coverage"
    if tolerance == 0:
        simplified = source
    elif coverage:
        simplified = list(shapely.coverage_simplify(source, tolerance))
    elif protected:
        simplified = [simplify_river(g, tolerance, protected) for g in source]
    else:
        simplified = [g.simplify(tolerance, preserve_topology=True) for g in source]
    return simplified
