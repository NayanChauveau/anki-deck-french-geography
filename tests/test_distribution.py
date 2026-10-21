import shlex
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def workflow(name):
    return yaml.safe_load((ROOT / ".github/workflows" / name).read_text())


def test_release_reuses_checks_and_publishes_the_uploaded_package_path():
    checks = workflow("check.yml")
    release = workflow("release.yml")
    assert "workflow_call" in checks["on"]
    assert release["jobs"]["check"]["uses"] == "./.github/workflows/check.yml"
    assert release["jobs"]["publish"]["needs"] == "check"
    upload = next(
        step["with"]
        for step in checks["jobs"]["check"]["steps"]
        if step.get("uses", "").startswith("actions/upload-artifact@")
    )
    download = next(
        step["with"]
        for step in release["jobs"]["publish"]["steps"]
        if step.get("uses", "").startswith("actions/download-artifact@")
    )
    assert upload["name"] == download["name"]
    command = release["jobs"]["publish"]["steps"][-1]["run"]
    asset = next(token.split("#")[0] for token in shlex.split(command) if ".apkg#" in token)
    assert str(Path(asset).relative_to(download["path"])) in upload["path"].splitlines()
    assert "--verify-tag" in command and "--latest" in command


@pytest.mark.parametrize(
    ("tag", "accepted"),
    [
        ("v0.1.0", True),
        ("v12.34.56", True),
        ("latest-main", False),
        ("v1.2", False),
        ("v1.2.3-beta", False),
        ("v1.2.3;echo bad", False),
    ],
)
def test_actual_release_gate_accepts_only_stable_versions(tag, accepted):
    gate = workflow("release.yml")["jobs"]["version"]["steps"][0]["run"]
    result = subprocess.run(["bash", "-c", gate], env={"RELEASE_TAG": tag}, check=False)
    assert (result.returncode == 0) is accepted
