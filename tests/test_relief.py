from pathlib import Path
from shutil import copytree

import pytest
import yaml
from shapely.geometry import Point

from french_geography.project import load

ROOT = Path(__file__).resolve().parents[1]


def test_summit_cards_have_three_directions_and_fact_sources():
    project = load(ROOT)
    cards = [card for card in project.cards if card.layer == "peaks"]
    assert len(cards) == 12
    assert all(isinstance(point, Point) for point in project.layers["peaks"].values())
    expected = {
        "peak-monte-cinto": "Reliefs corses",
        "peak-mont-blanc": "Alpes",
        "peak-puy-de-sancy": "Massif central",
        "peak-cret-de-la-neige": "Jura",
    }
    for target, massif in expected.items():
        selected = [card for card in cards if card.target == target]
        assert {card.direction for card in selected} == {"name-map", "map-name", "massif"}
        relation = next(card for card in selected if card.direction == "massif")
        assert relation.answer == massif
        assert relation.front_map == relation.back_map == "none"
        assert any("larousse.fr" in reference for reference in relation.references)
        assert "Insee" not in relation.explanation
        assert massif not in relation.question


def test_unknown_summit_massif_is_rejected(tmp_path):
    for directory in ("geo", "cards", "catalog", "data", "locales"):
        copytree(ROOT / directory, tmp_path / directory)
    path = tmp_path / "catalog/peaks.yml"
    catalog = yaml.safe_load(path.read_text())
    catalog["features"][0]["massif"] = "mountain-unknown"
    path.write_text(yaml.safe_dump(catalog))
    with pytest.raises(ValueError, match="Unknown massif"):
        load(tmp_path)


def test_regional_reliefs_have_both_directions_and_localized_context():
    import json

    from french_geography.languages import localize

    project = load(ROOT)
    source = json.loads((ROOT / "data/relief/regional-schematic-zones.geojson").read_text())
    targets = {feature["properties"]["id"] for feature in source["features"]}
    assert len(targets) == 29
    assert len(project.layers["mountains"]) == 36
    for language in ("fr", "en"):
        cards = [c for c in localize(project, language).cards if c.layer == "mountains"]
        assert len(cards) == 72
        for target in targets:
            selected = {c.direction: c for c in cards if c.target == target}
            assert set(selected) == {"name-map", "map-name"}
            locate, identify = selected["name-map"], selected["map-name"]
            assert locate.front_map == "blank" and identify.front_map == "target"
            assert locate.back_map == identify.back_map == "target"
            assert locate.view == identify.view == "metropolitan"
            assert locate.answer == identify.answer
            assert locate.explanation == identify.explanation
            assert locate.explanation
            assert (
                "Zone schématique" if language == "fr" else "Schematic area"
            ) not in locate.explanation
            assert len(locate.references) >= 2


def test_regional_envelopes_cover_landmarks_and_keep_neighboring_massifs_distinct():
    project = load(ROOT)
    # Representative peaks/interior landmarks, WGS84; not asserted to be precise borders.
    landmarks = {
        "morvan": (4.037, 46.991),  # Haut-Folin
        "chaine-des-puys": (2.964, 45.772),  # puy de Dôme
        "monts-dore": (2.814, 45.528),  # puy de Sancy
        "cantal": (2.761, 45.059),  # Plomb du Cantal
        "forez": (3.808, 45.653),  # Pierre-sur-Haute
        "livradois": (3.559, 45.565),  # Bois Noirs, Haut-Livradois
        "millevaches": (2.123, 45.57),  # mont Bessou
        "aubrac": (3.085, 44.621),  # signal de Mailhebiau
        "cevennes": (3.582, 44.122),  # mont Aigoual
        "lyonnais": (4.531, 45.733),  # Saint-Martin-en-Haut
        "beaujolais": (4.494, 46.225),  # mont Saint-Rigaud
        "pilat": (4.573, 45.382),  # crêt de la Perdrix
        "vercors": (5.529, 44.87),  # Vassieux
        "chartreuse": (5.79, 45.287),  # Chamechaude
        "bauges": (6.217, 45.719),  # mont Trélod
        "bornes": (6.278, 45.946),  # plateau des Glières
        "aravis": (6.557, 45.956),  # Pointe Percée
        "chablais": (6.735, 46.333),  # dent d'Oche
        "beaufortain": (6.633, 45.688),  # lac de Roselend
        "belledonne": (5.991, 45.172),  # Grand Pic de Belledonne
        "ecrins": (6.358, 44.922),  # Barre des Écrins
        "queyras": (6.875, 44.776),  # Château-Ville-Vieille
        "ventoux": (5.278, 44.174),
        "luberon": (5.467, 43.814),  # Mourre Nègre
        "alpilles": (4.892, 43.754),  # les Opies
        "sainte-victoire": (5.645, 43.532),  # pic des Mouches
        "sainte-baume": (5.757, 43.335),  # Saint-Pilon
        "maures": (6.367, 43.289),  # Collobrières
        "esterel": (6.891, 43.481),  # pic de l'Ours
    }
    for key, coordinate in landmarks.items():
        geom = project.layers["mountains"]["mountain-" + key]
        assert geom.is_valid and geom.geom_type == "Polygon"
        assert geom.contains(Point(coordinate)), key
    for west, east in (("livradois", "forez"), ("bornes", "aravis"), ("chartreuse", "belledonne")):
        left = project.layers["mountains"]["mountain-" + west]
        right = project.layers["mountains"]["mountain-" + east]
        assert left.centroid.x < right.centroid.x
        assert left.intersection(right).area < min(left.area, right.area) * 0.05
