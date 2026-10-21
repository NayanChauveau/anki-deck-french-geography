import json
import re
import socket
import sqlite3
import zipfile
from dataclasses import replace
from pathlib import Path

import pytest

from french_geography.build import MODEL_ID, build_packages, note_guid
from french_geography.languages import english_pilot
from french_geography.project import load

ROOT = Path(__file__).resolve().parents[1]


def test_default_build_emits_two_distinct_offline_packages(tmp_path, monkeypatch):
    def offline(*args, **kwargs):
        raise AssertionError("Package build attempted network access")

    monkeypatch.setattr(socket, "socket", offline)
    project = load(ROOT)
    paths = build_packages(project, tmp_path)
    assert [path.name for path in paths] == ["french-geography-en.apkg", "french-geography-fr.apkg"]
    identities, models = [], []
    for path, language, expected in zip(paths, ("en", "fr"), (1, len(project.cards)), strict=True):
        with zipfile.ZipFile(path) as package:
            database = tmp_path / f"{language}.anki2"
            database.write_bytes(package.read("collection.anki2"))
            media = set(json.loads(package.read("media")).values())
        with sqlite3.connect(database) as db:
            notes = db.execute("select guid,mid,flds from notes").fetchall()
            assert len(notes) == expected
            identities.append({guid for guid, mid, fields in notes})
            models.append({mid for guid, mid, fields in notes})
            for _guid, _mid, fields in notes:
                assert set(re.findall(r'src="([^" ]+)"', fields)) <= media
            if language == "en":
                assert notes[0][2].split("\x1f")[1] == "Which river is highlighted on the map?"
                assert notes[0][2].split("\x1f")[3] == "The Loire"
                model = json.loads(db.execute("select models from col").fetchone()[0])
                assert "FRENCH GEOGRAPHY" in next(iter(model.values()))["tmpls"][0]["qfmt"]
    assert identities[0].isdisjoint(identities[1])
    assert models[0] == {1976423201} and models[1] == {MODEL_ID}
    assert note_guid("fr-geo-hydrographie-identification-loire") in identities[1]


def test_english_pilot_rejects_unknown_ids_instead_of_silent_fallback(tmp_path):
    (tmp_path / "locales").mkdir()
    (tmp_path / "locales/en.yml").write_text(
        "cards:\n  unknown:\n    question: Question?\n"
        "    answer: Answer\n    explanation: Explanation\n"
    )
    with pytest.raises(ValueError, match="Unknown English translation IDs"):
        english_pilot(replace(load(ROOT), root=tmp_path))
