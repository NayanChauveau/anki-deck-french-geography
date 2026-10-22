"""Safety gates for display-only simplification, independent of the editorial corpus."""

import shapely
from shapely.geometry import LineString, Polygon

from french_geography.cartography import display


def test_shared_boundaries_are_simplified_as_a_coverage():
    left = Polygon([(0, 0), (1, 0), (1.1, 0.2), (0.9, 0.5), (1.1, 0.7), (1, 1), (0, 1)])
    right = Polygon([(1, 0), (2, 0), (2, 1), (1, 1), (1.1, 0.7), (0.9, 0.5), (1.1, 0.2)])
    source = [left, right]
    assert shapely.coverage_is_valid(source)
    simplified = shapely.coverage_simplify(source, 0.4)
    assert display.assess(source, simplified, coverage=True) is None
    assert simplified[0].intersection(simplified[1]).area == 0
    assert simplified[0].boundary.intersection(simplified[1].boundary).length > 0


def test_river_junction_vertices_survive_simplification():
    trunk = LineString([(0, 0), (0.03, 0.2), (0, 0.5), (-0.03, 0.8), (0, 1)])
    branch = LineString([(1, 0.5), (0, 0.5)])
    nodes = display.river_nodes([trunk, branch])
    simplified = [display.simplify_river(g, 0.2, nodes) for g in (trunk, branch)]
    assert (0, 0.5) in list(simplified[0].coords)
    rounded = [display.quantize(g, 1) for g in simplified]
    assert display.assess([trunk, branch], rounded, protected=nodes, decimals=1) is None
    assert rounded[0].intersects(rounded[1])


def test_rounding_that_collapses_a_small_island_is_rejected():
    source = Polygon([(0, 0), (0.001, 0), (0.001, 0.001), (0, 0.001)])
    assert display.assess([source], [display.quantize(source, 1)]) == "invalid-or-changed-parts"
    assert source.is_valid and source.area > 0  # Source was never repaired or overwritten.


def test_precision_grid_can_preserve_subpixel_components():
    source = Polygon([(514, 249), (514.00000004, 249), (514, 249.00000004)])
    assert not display.quantize(source, 7).is_valid
    assert display.quantize(source, 8).is_valid
