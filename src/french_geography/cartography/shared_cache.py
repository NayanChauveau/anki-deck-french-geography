"""Integrity-checked media and visual-contract cache, independent of note language."""

import hashlib
import json
import shutil
from importlib.metadata import version
from pathlib import Path


def visual_key(card, mode):
    return json.dumps((card.layer, card.view, card.target, mode))


def cached_maps(project, out, configuration, settings, *, render):
    cache_dir = project.root / "build/media"
    cache_dir.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    inputs = {
        "configuration": configuration,
        "dependencies": {p: version(p) for p in ("shapely", "pyproj")},
        "renderer": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(Path(__file__).parent.glob("*.py"))
        },
        "visuals": sorted(
            {
                visual_key(c, mode)
                for c in project.cards
                for mode in (c.front_map, c.back_map)
                if mode != "none"
            }
        ),
        "layers": {
            layer: {k: g.wkb_hex for k, g in items.items()}
            for layer, items in project.layers.items()
        },
        "countries": project.countries,
    }
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    index = cache_dir / ".shared-svg-cache.json"
    try:
        cached = json.loads(index.read_text())
        name = cached["media"][0]
        if Path(name).name != name:
            raise ValueError("Invalid cached SVG filename")
        data = (cache_dir / name).read_bytes()
        valid = (
            cached["version"] == 1
            and cached["format"] == "shared-svg"
            and cached["fingerprint"] == key
            and name == media_name(data)
            and cached["contract_sha256"] == contract_hash(cached["visuals"])
        )
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        valid = False
    if not valid:
        data, visuals = render(project, settings)
        name = media_name(data)
        (cache_dir / name).write_bytes(data)
        for record in visuals.values():
            record["shared_svg"] = name
        cached = {
            "version": 1,
            "format": "shared-svg",
            "fingerprint": key,
            "media": [name],
            "visuals": visuals,
            "contract_sha256": contract_hash(visuals),
        }
        index.write_text(json.dumps(cached, sort_keys=True) + "\n")
    if out.resolve() != cache_dir.resolve():
        shutil.copyfile(cache_dir / name, out / name)
    manifest = {
        c.id: {
            side: cached["visuals"][visual_key(c, mode)] if mode != "none" else {}
            for side, mode in (("front", c.front_map), ("back", c.back_map))
        }
        for c in project.cards
    }
    (out / "manifest.json").write_text(json.dumps({**cached, "cards": manifest}, indent=2) + "\n")
    return manifest


def contract_hash(cards):
    return hashlib.sha256(json.dumps(cards, sort_keys=True).encode()).hexdigest()


def media_name(data):
    return "geo-" + hashlib.sha256(data).hexdigest() + ".svg"
