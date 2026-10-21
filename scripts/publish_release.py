"""Publish the next stable patch release from the package built by CI."""

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

VERSION = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


def next_version(tags):
    versions = [
        tuple(map(int, match.groups())) for tag in tags if (match := VERSION.fullmatch(tag))
    ]
    if not versions:
        return "v0.1.0"
    major, minor, patch = max(versions)
    return f"v{major}.{minor}.{patch + 1}"


def gh_json(endpoint):
    result = subprocess.run(
        ["gh", "api", "--paginate", "--slurp", endpoint],
        check=True,
        capture_output=True,
        text=True,
    )
    return [item for page in json.loads(result.stdout) for item in page]


def publish(package, repository, commit):
    if not package.is_file() or package.suffix != ".apkg":
        raise ValueError(f"Missing built APKG: {package}")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Expected owner/repository")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Expected the exact commit SHA tested by CI")
    tags = gh_json(f"repos/{repository}/git/matching-refs/tags/v")
    releases = gh_json(f"repos/{repository}/releases")
    version = next_version(
        [item["ref"].removeprefix("refs/tags/") for item in tags]
        + [item["tag_name"] for item in releases]
    )
    subprocess.run(
        [
            "gh",
            "release",
            "create",
            version,
            f"{package}#Géographie française",
            "--repo",
            repository,
            "--target",
            commit,
            "--title",
            version,
            "--notes",
            f"Automated release from main at {commit}.",
            "--latest",
        ],
        check=True,
    )
    return version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    version = publish(args.package, os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_SHA"])
    print(f"Published {version}")


if __name__ == "__main__":
    main()
