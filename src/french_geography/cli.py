import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from french_geography.build import build, build_packages, maps, preview
from french_geography.project import load
from french_geography.schema import CatalogFile, DepartmentCatalog, PlaceCatalog, RuleFile


def anki(action: str, **params):
    request = urllib.request.Request(
        "http://127.0.0.1:8765",
        json.dumps({"action": action, "version": 6, "params": params}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.load(response)
    if result.get("error"):
        raise RuntimeError(f"AnkiConnect: {result['error']}")
    return result["result"]


def main():
    parser = argparse.ArgumentParser(description="French geography — Anki decks")
    parser.add_argument(
        "command", choices=["validate", "schema", "maps", "preview", "build", "check", "push"]
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path)
    parser.add_argument(
        "--lang",
        default=None,
        help="Registered language code, or all (build defaults to all; preview to fr)",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.command == "schema":
            for name, model in [
                ("cards", RuleFile),
                ("catalog", CatalogFile),
                ("departments", DepartmentCatalog),
                ("places", PlaceCatalog),
            ]:
                (root / f"schema/{name}.schema.json").write_text(
                    json.dumps(model.model_json_schema(), ensure_ascii=False, indent=2) + "\n"
                )
            return
        project = load(root)
        if args.command == "validate":
            print(f"{len(project.cards)} fiches valides ; données locales vérifiées.")
        elif args.command == "maps":
            maps(project, args.out or root / "build/media")
        elif args.command == "preview":
            print(preview(project, args.out or root / "build/preview", language=args.lang or "fr"))
        elif args.command == "build":
            for path in build_packages(project, args.out or root / "dist", args.lang or "all"):
                print(path)
        elif args.command == "push":
            path = build(project, args.out or root / "dist")
            print(path)
            if args.command == "push":
                anki("version")
                anki("importPackage", path=str(path.resolve()))
                anki("sync")
                print("Paquet importé ; synchronisation demandée.")
        else:
            for command in [["ruff", "check", "."], ["ruff", "format", "--check", "."], ["pytest"]]:
                subprocess.run([sys.executable, "-m", *command], cwd=root, check=True)
            for name, model in [
                ("cards", RuleFile),
                ("catalog", CatalogFile),
                ("departments", DepartmentCatalog),
                ("places", PlaceCatalog),
            ]:
                actual = json.loads((root / f"schema/{name}.schema.json").read_text())
                if actual != model.model_json_schema():
                    raise ValueError("Stale schema: run make schema")
            print(f"Contrôles réussis : {len(project.cards)} fiches.")
    except (ValueError, KeyError, OSError, RuntimeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Erreur : {error}\n")


if __name__ == "__main__":
    main()
