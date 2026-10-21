# Complete English translation and multilingual architecture — 21 October 2026

Status: implemented and validated locally. Publication is handled by CI after a successful push to main.

## Coverage

| Theme | French notes | English notes |
| --- | ---: | ---: |
| Cities | 437 | 437 |
| Departments | 303 | 303 |
| Regions | 148 | 148 |
| Rivers | 38 | 38 |
| Landforms | 26 | 26 |
| National parks | 22 | 22 |
| Coasts | 15 | 15 |
| Overseas | 15 | 15 |
| Lakes | 10 | 10 |
| Total | 1,014 | 1,014 |

The English text covers all 18 rules and 28 active layer/direction combinations.
Fifty independent editorial explanations are translated once, together with shared
administrative sentences, qualifiers, reference labels, headings, alt text and themes.
There are 42 explicit English proper-name overrides; canonical official names are
otherwise retained. The shared schema and stable keys are documented in
[LOCALIZATION.md](../LOCALIZATION.md).

## Architecture checks

- No French sentence is used as a lookup key for an English sentence.
- French and English use the same locale schema and generator.
- Catalogue prose moved to locale files; catalogues carry semantic references.
- Questions moved out of rules into locale files; published rule/note IDs are unchanged.
- Language registration, assets, namespaces, model/deck IDs and release labels are data.
- The renderer remains language-independent; all 326 English PNGs are byte-identical
  to the corresponding French PNGs and bundled under their content hashes.
- The third-locale regression fixture adds only registration/content data, builds its
  package and gallery and checks separate identity and its localized template.
- CI, publication and Deckdock obtain package coverage from the language registry.
- Preparation scripts emit semantic explanation/qualifier keys, not localized prose.

## Checks actually performed

- `make check`: 63 tests passed in about 16 seconds; schema checks passed.
- Complete EN and FR APKGs rebuilt with Python sockets blocked.
- All 1,014 French IDs, GUIDs, model IDs and note fields compared against the previous
  local package: no differences.
- The ten pre-existing English pilot note IDs, GUIDs and models remain unchanged;
  questions, answers, explanations and references remain unchanged. Credit typography
  now follows the localized UI strings.
- Actual package media hashes, media references and equal language coverage checked.
- Generated English text exported locally to `build/review/english-cards.tsv`; source
  files remain the canonical editable input, not this generated review inventory.
- English gallery generated at `build/preview-en/index.html`.
- In a disposable Anki collection: import ten-note English pilot, upgrade to 1,014
  English notes, verify an existing note/card and review record, import French to
  reach 2,028 notes, then reimport English without duplicates. This manual check is
  recorded as an observation, not a note-specific compatibility requirement.
  No personal Anki collection was accessed or modified.
- Deckdock contract check passed for both approximately 44 MiB packages against the
  local add-on checkout, using simulated GitHub transport; no release was published.

French/English completeness, source-data parity and cross-language identity separation
are tested for the entire note set. No per-note legacy identity fixture is retained.

## Editorial review

The translated shared prompts and all 50 independent explanations were read against
the French text. Tests exercise leading zeros, Corsican and overseas codes, Saint-Denis
qualifiers, river direction, name/code clue leakage and retained limitations:

- The Rhine outline is not the entire international course; the Oise retains its
  available-French-section qualification.
- Relief schemes remain indicative, not administrative/geological boundaries.
- Maritime outlines are not legal boundaries.
- Park core areas exclude membership/adjacent marine areas and retain the
  simplified-boundary/regulation-use warning.
- Lakes and reservoirs remain distinct; real overseas positions and insets are unchanged.

Terminology was checked against primary sources where English names needed review:
[INSEE's English regional names](https://www.insee.fr/en/statistiques/fichier/4195175/insee_activity_report_2022.pdf),
[EEA's use of Scheldt and Rhône](https://climate-adapt.eea.europa.eu/en/metadata/publications/green-infrastructure-and-flood-management-promoting-cost-efficient-flood-risk-reduction-via-green-infrastructure-solutions),
[CIPEL's Lake Geneva terminology](https://www.cipel.org/en/),
[European Commission maritime area names](https://oceans-and-fisheries.ec.europa.eu/document/download/5912d26d-7626-4c65-a1e3-bdcceb3de400_en),
[the park's own English name](https://www.parc-amazonien-guyane.fr/fr/node/2441/printable/print),
and the [national parks' English reference document](https://www.parcsnationaux.fr/sites/parcsnationaux.fr/files/atoms/files/pn_referencearea_en.pdf).
These support wording choices; the cards retain their original factual sources.

## Limits

This is an editorial/technical review by the implementing agent, not an independent
professional translation review. A fresh manual Anki/mobile visual review was not
performed. Geographic media are unchanged. Source-preparation scripts were updated
for the new catalogue schema but were not rerun against all upstream raw files.
No new language beyond French/English is shipped; the third locale is a test fixture.
