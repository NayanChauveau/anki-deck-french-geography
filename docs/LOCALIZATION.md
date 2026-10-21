# Localization architecture

All registered languages use the same generators, locale schema, templates, image
cache and package builder. There is no English-specific generation path. Both the
French and English editions currently contain 1,014 notes.

## Canonical data and localized text

Geometries stay under `geo/`; catalogue IDs, official names, department codes and
relations stay under `catalog/`; released rule IDs stay under `cards/`. A rule no
longer contains a French question or a French noun. A catalogue contains semantic
references rather than explanatory prose. For example:

```yaml
# catalog/rivers.yml
- id: loire
  name: Loire
  explanation_key: river.loire.summary
```

Both language files use **the same key**, independently of the source wording:

```yaml
# locales/fr.yml
explanations:
  river.loire.summary: Elle traverse notamment Orléans, Tours et Nantes avant de rejoindre l’Atlantique à Saint-Nazaire.
```

```yaml
# locales/en.yml
explanations:
  river.loire.summary: It passes through Orléans, Tours and Nantes before reaching the Atlantic at Saint-Nazaire.
```

Editing French punctuation never renames a key or invalidates an English lookup.
Shared notices (schematic landforms, park cores, natural lakes) are translated once
and referenced by multiple features. Geographic relationships remain canonical IDs,
not translated copies of facts.

`names` holds optional localized proper-name overrides keyed by feature ID. Keeping
a canonical proper name is an explicit policy, not a fallback for missing prose.
`forms` holds language-specific forms where grammar cannot use a shared pattern
(e.g. French river labels with an article). `qualifiers` uses semantic location keys.
`rules` holds questions/answer formats by permanent rule ID and direction, while
`explanations`, `reference_labels`, `themes` and `ui` hold their corresponding text.
The French rule IDs are historical Anki identity components and must not be renamed
merely to make their technical spelling English.

## Language registration and identity

`locales/languages.json` registers the build order, stable filename, release label,
GUID namespace, note suffix, model ID and theme deck IDs for each language. It is
standard-library JSON so the release publisher can read it without installing the
build environment. IDs are assigned explicitly and collisions are rejected.

The two published filenames and all published French/English identities are
preserved. Note IDs are derived uniformly from canonical rule/feature IDs and the
registered language suffix. No individual note has special identity or migration logic.

## Adding a language

1. Add a registry entry with its own explicit, permanent filename, namespace, note
   suffix and model/deck IDs. Never reuse another language's identities.
2. Create `locales/<code>.yml` with the shared schema and semantic keys; translate
   rules, editorial explanations, qualifiers, reference labels, UI and theme names.
   Choose appropriate proper names and grammatical forms explicitly.
3. Run `make check`, then `uv run --frozen french-geography build --lang <code>` and
   inspect the package. `uv run --frozen french-geography preview --lang <code>
   --out build/preview-<code>` provides a localized gallery.
4. Build all registered languages with `make build`. CI uploads `dist/*.apkg` and
   the publisher requires exactly one package per registered language. Deckdock's
   compatibility check also obtains its asset list from the registry.

No Python language branch or duplicated geographic input is required. A regression
test registers a private third-locale fixture using data files only, then verifies
its package, identities, translated template and gallery. This fixture is not a
shipped third-language translation.

## Validation and maintenance

Missing rules, explanation keys, qualifiers, source labels and required interface
fields fail the build. Duplicate YAML keys, unknown translated feature IDs, Anki
identity collisions and map-question placeholders that reveal a name/code are
rejected. Geometric preparation scripts emit semantic keys; they do not generate
localized prose. Schema files describe the new neutral rule/catalogue shape.

`load(root)` retains the historical French source-card API for compatibility;
`localize(project, code)` regenerates text through the same canonical rules in any
registered locale, preserving the selected note set and its order. `make push`
continues to import the French edition only. The default package build follows the
registry order, English first. No geography is downloaded during normal builds.
