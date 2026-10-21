"""Exercise the built package against an actual Deck Manager checkout, without network or Anki UI."""

import argparse
import hashlib
import importlib
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from types import ModuleType

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from french_geography.distribution import PACKAGES  # noqa: E402


def check(checkout: Path, package: Path) -> dict:
    source = checkout.resolve() / "src"
    if not (source / "domain.py").is_file():
        raise ValueError("Expected a Deck Manager checkout containing src/domain.py")
    labels = dict(PACKAGES.values())
    if not package.is_file() or package.name not in labels:
        raise ValueError("Build the English and French packages first")
    label = labels[package.name]
    # Load the add-on's real modules without executing its Anki UI entry point.
    namespace = "_deck_manager_compatibility"
    module = ModuleType(namespace)
    module.__path__ = [str(source)]
    sys.modules[namespace] = module
    domain = importlib.import_module(namespace + ".domain")
    github = importlib.import_module(namespace + ".github")
    manager = importlib.import_module(namespace + ".manager")
    download = importlib.import_module(namespace + ".download")
    base = "https://github.com/example-owner/example-deck"
    asset_name = package.name
    size = package.stat().st_size

    def payload(tag):
        return {
            "id": 1 if tag == "v0.1.0" else 2,
            "tag_name": tag,
            "html_url": f"{base}/releases/tag/{tag}",
            "assets": [
                {
                    "id": 10 if tag == "v0.1.0" else 20,
                    "name": asset_name,
                    "label": label,
                    "size": size,
                    "state": "uploaded",
                    "browser_download_url": f"{base}/releases/download/{tag}/{asset_name}",
                }
            ],
        }

    initial = domain.parse_github_url(f"{base}/releases/download/v0.1.0/{asset_name}")
    first = github.fetch_release(
        initial,
        transport=lambda url, headers: github.HttpResponse(
            200, {}, json.dumps(payload("v0.1.0")).encode()
        ),
    ).release
    subscription = manager.make_subscription(initial, first, "test-geography")
    subscription = domain.commit_install(subscription, first, installed_at="2026-10-21T00:00:00Z")
    assert subscription.display_name == label
    newer = github.fetch_release(
        initial,
        latest=True,
        transport=lambda url, headers: github.HttpResponse(
            200, {}, json.dumps(payload("v0.1.1")).encode()
        ),
    ).release
    pending = domain.compare_subscription(subscription, newer)
    assert pending.available_version == "v0.1.1"
    assert domain.compare_subscription(subscription, first).available_version is None
    try:
        domain.parse_github_url(f"{base}/releases/download/latest-main/{asset_name}")
    except domain.UrlError:
        pass
    else:
        raise AssertionError("Deck Manager unexpectedly accepted latest-main")
    max_bytes = manager.DEFAULT_MAX_BYTES
    assert size < max_bytes
    asset = domain.find_apkg(newer, asset_name)
    with TemporaryDirectory(prefix="geography-deck-manager-") as folder:
        target = Path(folder) / asset_name

        def blocks():
            with package.open("rb") as handle:
                while block := handle.read(64 * 1024):
                    yield block

        download.download_asset(
            asset.download_url,
            target,
            max_bytes=max_bytes,
            announced_size=size,
            open_url=lambda url: download.DownloadResponse(
                200, {"content-length": str(size)}, blocks()
            ),
        )
        assert (
            hashlib.sha256(target.read_bytes()).digest()
            == hashlib.sha256(package.read_bytes()).digest()
        )
    return {
        "asset": asset_name,
        "bytes": size,
        "limit_bytes": max_bytes,
        "checks": [
            "versioned URL",
            "release metadata",
            "display label",
            "version change",
            "same version ignored",
            "latest-main rejected",
            "exact package download",
        ],
        "scope": (
            "Local contract test with simulated GitHub transport; no published release or UI import"
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deck-manager", type=Path, required=True)
    parser.add_argument("--package", type=Path, action="append")
    args = parser.parse_args()
    packages = args.package or [Path("dist") / name for name, label in PACKAGES.values()]
    print(
        json.dumps([check(args.deck_manager, path) for path in packages], ensure_ascii=False, indent=2)
    )


if __name__ == "__main__":
    main()
