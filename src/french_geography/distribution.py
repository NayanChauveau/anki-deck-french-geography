"""Language registration and permanent Anki identities; standard library only."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
THEME_KEYS = {
    "Fleuves": "rivers",
    "Départements": "departments",
    "Régions": "regions",
    "Villes": "cities",
    "Relief": "landforms",
    "Lacs": "lakes",
    "Littoral": "coasts",
    "Outre-mer": "overseas",
    "Paysages": "parks",
}


def load_registry(root: Path = ROOT) -> dict:
    registry = json.loads((root / "locales/languages.json").read_text())
    if not registry:
        raise ValueError("Empty language registry")
    identities, filenames, namespaces, suffixes = set(), set(), set(), set()
    expected = {"filename", "label", "namespace", "note_suffix", "model_id", "deck_ids"}
    for code, definition in registry.items():
        if code == "all" or not re.fullmatch(r"[a-z]{2,3}(?:-[a-z0-9]+)*", code):
            raise ValueError(f"Invalid language code: {code}")
        if definition.keys() != expected:
            raise ValueError(f"Invalid language definition: {code}")
        if not re.fullmatch(r"[a-z0-9-]+\.apkg", definition["filename"]):
            raise ValueError(f"Invalid package filename: {code}")
        if not definition["label"].strip() or not definition["namespace"].strip():
            raise ValueError(f"Empty language label/namespace: {code}")
        if not re.fullmatch(r"(?:-[a-z0-9-]+)?", definition["note_suffix"]):
            raise ValueError(f"Invalid note suffix: {code}")
        for field, used in (
            ("filename", filenames),
            ("namespace", namespaces),
            ("note_suffix", suffixes),
        ):
            if definition[field] in used:
                raise ValueError(f"Duplicate language {field}: {definition[field]}")
            used.add(definition[field])
        if definition["deck_ids"].keys() != set(THEME_KEYS.values()):
            raise ValueError(f"Invalid theme coverage: {code}")
        for identity in [definition["model_id"], *definition["deck_ids"].values()]:
            if type(identity) is not int or not 0 < identity < 2**63 or identity in identities:
                raise ValueError(f"Invalid or duplicate Anki identity: {identity}")
            identities.add(identity)
    return registry


PACKAGES = {code: (item["filename"], item["label"]) for code, item in load_registry().items()}
