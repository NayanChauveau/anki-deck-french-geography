# Géographie française — Anki

Deck de géographie physique française. Première série : **deux cartes d’identification,
la Loire et la Seine**. Le recto montre le fleuve surligné sans son nom ; le verso
révèle le nom, une annotation et une courte explication. Le cadrage reste identique.

## Construire et prévisualiser

Python 3.12 ou plus récent, [uv](https://docs.astral.sh/uv/) et Make sont nécessaires.
Depuis la racine du dépôt :

```sh
uv sync --frozen --extra dev
make check
make preview
make build
```

- Paquet : `dist/french-geography.apkg`, à importer via **Fichier → Importer** dans Anki.
- Galerie : ouvrir `build/preview/index.html` ; les rectos et versos sont côte à côte.
- Cartes SVG et PNG : `build/media/`, avec un manifeste par identifiant de fiche.

| Commande | Effet |
| --- | --- |
| `make validate` | Valide les fiches, références, géométries et empreintes des données |
| `make schema` | Régénère le schéma JSON des fiches |
| `make maps` | Produit les SVG et PNG, nommés par SHA-256 de leur contenu |
| `make preview` | Produit une galerie HTML autonome avec ses médias locaux |
| `make build` | Génère les cartes et le paquet Anki avec les PNG embarqués |
| `make check` | Validation, lint, format, tests et contrôle du schéma JSON |
| `make push` | Construit, importe via AnkiConnect puis demande la synchronisation |

`make push` nécessite Anki ouvert sur le bon profil et l’extension AnkiConnect
à l’adresse locale `127.0.0.1:8765`. La synchronisation concerne le profil entier.
Cette commande n’est pas nécessaire pour importer le paquet à la main.

Après l’installation initiale des dépendances, **les builds ne téléchargent aucune
donnée géographique**. `uv.lock` fige les dépendances ; les données sélectionnées et
la police sont embarquées dans le dépôt. Un environnement déjà installé peut aussi
exécuter `uv run --offline --frozen french-geography build`.

## Architecture

- `cards/` : contenu éditorial YAML, avec identifiants permanents.
- `schema/` : schéma JSON généré depuis les modèles Pydantic.
- `geo/features/` : données GeoJSON WGS84 locales sélectionnées.
- `geo/sources.yml` : provenance, version, licence, transformations et empreintes.
- `geo/views.yml` : projections, cadrages partagés et encarts facultatifs.
- `geo/styles.yml` : palette et épaisseur du surlignage.
- `assets/fonts/` : police Noto Sans et sa licence OFL.
- `src/french_geography/` : validation, projection, rendu, export Anki et CLI.
- `templates/anki/` : recto, verso et CSS adaptatif.
- `scripts/prepare_geography.py` : préparation explicite des sources, hors build.
- `tests/` : contrôles de données, géométrie, médias, paquet et identité.
- `.github/workflows/check.yml` : contrôles et artefacts du paquet et de la galerie.
- `build/`, `dist/` : fichiers générés, exclus de Git.

Le socle reprend les principes du dépôt voisin `anki-deck-diving` : Python/uv,
validation YAML, genanki, GUID stables et CLI Make. Le contenu, les modèles et les
identifiants de ce projet lui sont propres. Voir [l’identité Anki](docs/ANKI_IDS.md).

## Données et limites

Les fleuves proviennent de Natural Earth au 1:10 millions, et le fond des pays
au 1:50 millions, figés sur le tag `v5.1.2`. Ces données sont dans le domaine public.
Les tracés sont généralisés : ils servent à reconnaître un cours d’eau à l’échelle
nationale, pas à situer précisément une source ou chaque méandre. Les deux fiches
n’affichent donc pas de marqueur de source ou d’embouchure.

Le moteur accepte les points, lignes, polygones et leurs formes multiples, les
trous de polygones, les projections PROJ et les encarts. Les jeux actuellement
embarqués couvrent la métropole et son voisinage. Ajouter des cartes d’outre-mer
nécessitera des données locales et des vues adaptées.

Voir [CARTOGRAPHY.md](docs/CARTOGRAPHY.md) pour le fonctionnement et la préparation
des sources. Les rendus ont été inspectés en image ; l’import dans Anki Desktop
et la lecture sur téléphone restent à vérifier sur les applications réelles.
