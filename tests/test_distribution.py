import shlex
import subprocess
from pathlib import Path

import pytest
import yaml

from scripts import publish_release as publisher

ROOT = Path(__file__).resolve().parents[1]


def test_release_waits_for_checks_and_uses_the_uploaded_package():
    workflow = yaml.safe_load((ROOT / ".github/workflows/check.yml").read_text())
    release = workflow["jobs"]["release"]
    assert release["needs"] == "check"
    assert release["if"] == "github.event_name == 'push' && github.ref == 'refs/heads/main'"
    assert release["concurrency"]["cancel-in-progress"] is False
    assert release["permissions"]["contents"] == "write"
    upload = next(
        step["with"]
        for step in workflow["jobs"]["check"]["steps"]
        if step.get("uses", "").startswith("actions/upload-artifact@")
    )
    download = next(
        step["with"]
        for step in release["steps"]
        if step.get("uses", "").startswith("actions/download-artifact@")
    )
    assert upload["name"] == download["name"]
    args = shlex.split(release["steps"][-1]["run"])
    assert args[-2:] == ["--package-dir", "release/dist"]
    assert "dist/*.apkg" in upload["path"].splitlines()
    assert Path(args[-1]).relative_to(download["path"]) == Path("dist")
    assert release["steps"][0]["with"]["ref"] == "${{ github.sha }}"


@pytest.mark.parametrize(
    ("tags", "expected"),
    [
        ([], "v0.1.0"),
        (["latest-main", "v1.2.3-beta", "unrelated"], "v0.1.0"),
        (["v0.1.9", "v0.1.10", "v0.1.2"], "v0.1.11"),
        (["v1.9.99", "v2.0.3"], "v2.0.4"),
    ],
)
def test_next_patch_version_uses_numeric_order(tags, expected):
    assert publisher.next_version(tags) == expected


def test_publish_avoids_tags_and_release_collisions_and_targets_tested_sha(tmp_path, monkeypatch):
    packages = [tmp_path / name for name, label in publisher.PACKAGES.values()]
    for package in packages:
        package.write_bytes(b"built package")
    sha = "a" * 40
    monkeypatch.setattr(
        publisher,
        "gh_json",
        lambda endpoint: (
            [{"ref": "refs/tags/v0.1.4"}] if "/git/" in endpoint else [{"tag_name": "v0.1.5"}]
        ),
    )
    commands = []
    monkeypatch.setattr(publisher.subprocess, "run", lambda args, **kwargs: commands.append(args))
    assert publisher.publish(packages, "owner/repo", sha) == "v0.1.6"
    command = commands[0]
    assert command[:4] == ["gh", "release", "create", "v0.1.6"]
    assert command[command.index("--target") + 1] == sha
    for package, (_name, label) in zip(packages, publisher.PACKAGES.values(), strict=True):
        assert f"{package}#{label}" in command
    assert "--latest" in command


def test_failed_metadata_request_never_publishes(tmp_path, monkeypatch):
    packages = [tmp_path / name for name, label in publisher.PACKAGES.values()]
    for package in packages:
        package.write_bytes(b"built package")
    commands = []

    def fail(args, **kwargs):
        commands.append(args)
        raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr(publisher.subprocess, "run", fail)
    with pytest.raises(subprocess.CalledProcessError):
        publisher.publish(packages, "owner/repo", "a" * 40)
    assert all(command[:3] != ["gh", "release", "create"] for command in commands)
