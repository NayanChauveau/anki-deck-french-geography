# Translation and localization plan

Scope: complete English coverage of the existing French deck, with a shared system
for future languages. Each batch has fewer than ten tasks. All implementation batches
below are complete locally. Publication is handled by CI after a successful push to main.

No individual note receives compatibility code or special identity handling. Names,
codes, relations and geometry are canonical facts; localized prose lives only under
stable semantic keys in locale files. The registry owns per-language Anki identities.

## Batch 1 — shared architecture (8 tasks)

- [x] Inventory all nine themes, 18 rules and 28 active layer/direction combinations.
- [x] Separate the 50 independent editorial explanations from generated sentences.
- [x] Define one schema for every locale, including French.
- [x] Replace source-sentence lookup keys with stable semantic keys.
- [x] Move questions, descriptions and qualifiers out of canonical rules/catalogues.
- [x] Register language assets, namespaces and model/deck IDs explicitly in data.
- [x] Route all languages through the same generator, templates and image cache.
- [x] Document the architecture and how to add a language in `LOCALIZATION.md`.

## Batch 2 — departments (7 tasks)

- [x] Translate the three active prompts once, rather than copying 303 cards.
- [x] Keep official department names and canonical string codes.
- [x] Use “department code” consistently, including 2A and 2B.
- [x] Cover leading zeros, accented names, Corsican letters and three-digit codes.
- [x] Translate the generated explanation and explanatory source label.
- [x] Preserve grouping, map modes, target geometry and question clue restrictions.
- [x] Verify 303 English notes and the localized Departments subdeck.

## Batch 3 — regions and cities (8 tasks)

- [x] Translate position, capital, department and region prompts.
- [x] Distinguish department prefectures from regional administrative capitals.
- [x] Review English region names and retain official city names.
- [x] Preserve the two Saint-Denis qualifiers, with English ocean terminology.
- [x] Generate explanations from canonical related IDs and localized names.
- [x] Keep canonical exclusion of relations whose answer is already disclosed.
- [x] Verify 148 region notes and 437 city notes, including relation direction.
- [x] Verify source URLs, subdecks and unlabelled map questions.

## Batch 4 — rivers (7 tasks)

- [x] Translate identification and downstream-relation prompts.
- [x] Review grammatical forms and English names, including Rhine and Scheldt.
- [x] Translate all 32 river summaries once, sharing them across relevant catalogues.
- [x] Preserve incomplete international-course and available-section qualifications.
- [x] Preserve tributary direction and the original factual source links.
- [x] Verify all 38 river notes and the Rivers subdeck.
- [x] Check translation coverage, answer leakage and reuse of the same map media.

## Batch 5 — relief and summits (7 tasks)

- [x] Distinguish broad landform areas, individual summits and their relations.
- [x] Translate the position and broad-landform-relation prompts.
- [x] Review English landform names while retaining official summit names.
- [x] Translate approximate and schematic-boundary notices without weakening them.
- [x] Preserve the summit context explanations and related source IDs.
- [x] Verify all 26 notes and the Landforms subdeck.
- [x] Check that schematic areas remain clearly distinct from geological/administrative limits.

## Batch 6 — lakes, coasts and overseas (8 tasks)

- [x] Distinguish natural lakes from dam reservoirs in names and questions.
- [x] Review Lake Geneva and the English maritime area names.
- [x] Translate the non-legal maritime boundary qualification.
- [x] Translate port/coast prompts and explanations, including inland estuary ports.
- [x] Preserve overseas location points and world insets without moving targets.
- [x] Translate ocean relations and distinguish the five overseas departments from all territories.
- [x] Verify 10 lake notes, 15 coast notes and 15 overseas notes.
- [x] Verify canonical relations, source links and the corresponding subdecks.

## Batch 7 — parks and interface (7 tasks)

- [x] Translate the park core-area prompts and review English park naming.
- [x] Preserve exclusion of membership areas and adjacent marine areas.
- [x] Preserve the simplified-boundary and regulation-use qualification.
- [x] Translate headings, alt text, front/back captions and theme labels.
- [x] Keep source organisations, dataset names and licences identifiable.
- [x] Localize attribution wording and the pinned dataset month.
- [x] Verify all 22 park notes and the localized gallery/template output.

## Batch 8 — completeness, extensibility and packages (8 tasks)

- [x] Verify complete source/translation parity: 1,014 notes per language.
- [x] Reject missing translations, duplicate keys and invalid interpolation.
- [x] Check canonical data invariance and cross-language identity separation generically.
- [x] Build a third private-locale fixture using registration/content data only.
- [x] Make CI, the publisher and Deck Manager consume the language registry.
- [x] Build both complete APKGs offline and verify their 326 identical PNGs.
- [x] Check import/reimport and coexistence in a disposable Anki collection.
- [x] Record results, limitations and terminology sources in the final report.

## Editorial conventions

Use clear, neutral English and one fact to recall per card. Preserve accents and
canonical codes. Retain official proper names unless a reviewed localized name is
provided. Do not invent facts while translating. Preserve every uncertainty and
approximation. Missing prose must fail validation; retaining an official proper name
is an explicit, separate policy. New languages translate the same semantic keys.

## Result and remaining release work

[Final validation report](reviews/TRANSLATION_COMPLETE_2026-10-21.md).
Source-preparation scripts now emit neutral keys but have not been rerun against all
upstream raw files. No independent professional translation review or new manual
Anki/mobile visual review is claimed. Commit and publication are separate actions.
