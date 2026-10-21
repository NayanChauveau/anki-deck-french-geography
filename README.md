# Géographie française — Anki

**1 014 cartes** réparties dans neuf sous-decks :

| Série | Cartes | Contenu |
| --- | ---: | --- |
| Fleuves | 38 | 32 identifications et 6 relations affluent → cours d’eau rejoint |
| Départements | 303 | 101 départements × 3 sens, par lots de dix |
| Régions | 148 | Localisation, noms, chefs-lieux et département → région |
| Villes | 437 | 113 communes : 101 chefs-lieux et 12 repères complémentaires |
| Relief | 26 | 7 zones indicatives et 4 sommets repères |
| Lacs | 10 | 5 lacs et retenues, dans les deux sens |
| Littoral | 15 | 5 zones maritimes et 5 relations ville portuaire → façade |
| Outre-mer | 15 | Situation de 5 territoires et relation au bassin océanique |
| Paysages | 22 | Les cœurs des 11 parcs nationaux, dans les deux sens |

Les questions relationnelles qui contiennent déjà leur réponse sont écartées.
Les référentiels administratifs sont ceux du **COG au 1er janvier 2025**. Les points
urbains représentent les mairies du millésime 2025, pas la forme des agglomérations.
Voir [les régions et villes](docs/ADMINISTRATION.md), [les départements](docs/DEPARTMENTS.md)
et [la revue hydrographique](docs/reviews/HYDROGRAPHY_2026-10-20.md).

L’hydrographie réunit les 18 objets initiaux Natural Earth et 14 ajouts BD TOPAGE
2024 sélectionnés explicitement. Les noms homonymes sont départagés par identifiant
Sandre. La Saône possède désormais un tracé plus complet ; le Rhin reste partiel
à l’échelle internationale. La Somme inclut le cours canalisé. La série contient
fleuves et rivières, sans prétendre à l’exhaustivité ; son chemin Anki initial est conservé.

Les zones armoricaines et corses sont des schémas pédagogiques indépendants,
annoncés au verso. Les parcs nationaux utilisent des contours officiels simplifiés,
avec une distinction explicite entre cœur et aire d’adhésion. Les nouveaux lots sont
construits localement ; le dernier import Anki confirmé reste celui de 880 cartes.

La progression prévue est détaillée dans la [roadmap complète](docs/ROADMAP.md).

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

- `cards/` : règles communes de génération des cartes.
- `catalog/` : noms français, codes départementaux, articles et annotations éditoriales.
- `schema/` : schéma JSON généré depuis les modèles Pydantic.
- `geo/selection.yml` : correspondance des noms amont vers les identifiants locaux.
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

Les cours d’eau proviennent de Natural Earth au 1:10 millions, et le fond des pays
au 1:50 millions, figés sur le tag `v5.1.2`. Ces données sont dans le domaine public.
Les tracés sont généralisés : ils servent à reconnaître un cours d’eau à l’échelle
nationale, pas à situer précisément une source ou chaque méandre. Les fiches
n’affichent donc pas de marqueur de source ou d’embouchure. Certains tracés sont
partiels, notamment ceux du Rhin et de la Saône. Les portions étrangères présentes
dans les éléments sélectionnés sont conservées dans le cadre de la carte.

Le moteur accepte les points, lignes, polygones et leurs formes multiples, les
trous de polygones, les projections PROJ et les encarts. Les jeux actuellement
embarqués couvrent la métropole et son voisinage. Les départements ultramarins disposent de leurs données et vues locales.
D’autres thèmes d’outre-mer nécessiteront des jeux adaptés.

## Ajouter ou modifier une carte

Les cartes ne sont pas écrites une par une. `cards/identification.yml` définit une
règle pour chaque série : couche géographique, catalogue, question, vue et références
communes. À chaque build, elle génère une note par objet de la couche locale.

`catalog/rivers.yml` contient uniquement les particularités éditoriales, par exemple :

```yaml
features:
  - id: ariege
    name: Ariège
    article: l’
    explanation: Affluent de la Garonne, elle descend des Pyrénées vers le nord.
```

L’ID correspond à celui du GeoJSON, pas à un identifiant de carte à inventer.
Le générateur compose « L’Ariège », reprend la question commune et calcule l’identité
Anki. `explanation` et `references` sont facultatifs. Les images n’affichent pas
d’étiquettes ; le nom de la réponse est présenté par le template du verso.

Pour ajouter un objet : préparer sa géométrie locale avec provenance et empreinte,
ajouter son nom et son article au catalogue, puis lancer `make check preview build`.
Une géométrie sans entrée éditoriale, ou une entrée sans géométrie, est signalée par
la validation. Aucun fichier de cartes générées n’est conservé dans le dépôt.

Voir [CARTOGRAPHY.md](docs/CARTOGRAPHY.md) pour le fonctionnement et la préparation
des sources. Les rendus ont été inspectés en image ; l’import dans Anki Desktop
et la lecture sur téléphone restent à vérifier sur les applications réelles.

## Présentation des images

Les images contiennent uniquement la géographie et la surbrillance éventuelle :
aucun titre, nom ou crédit n’est dessiné sur la carte. Le nom de la réponse et les
explications restent dans le texte du verso. Les crédits départementaux sont affichés
sous l’image en HTML, avec les liens vers le jeu de données et sa licence.
Les références restent disponibles dans « Sources ».

Les champs `explanation` sont des résumés éditoriaux, pas des citations. Les textes
hydrographiques ont une référence factuelle et une revue datée. Les références des
géométries restent distinctes de celles des explications.

Le relief est un pilote : les zones Natural Earth sont approximatives. Les reliefs corses et le Massif armoricain sont représentés par des zones
schématiques, distinctes des contours administratifs et signalées comme telles.

Le pilote comprend aussi quatre sommets repères et douze cartes : localisation dans
les deux sens et rattachement à un grand ensemble. Les relations sont sourcées
séparément des points Natural Earth ; aucune altitude exacte n’est demandée.

## Deckdock et consolidation

Le paquet est vérifié avec le code de [Deckdock](https://github.com/NayanChauveau/anki-deckdock).
Après un push sur `main`, la CI publie une nouvelle release stable versionnée
si les tests, le build et le contrôle Deckdock réussissent. Les contrôles effectués et le workflow préparé
sont décrits dans [DECKDOCK.md](docs/DECKDOCK.md).

Les prochaines extensions de contenu sont mises de côté. La priorité est la
[revue d’architecture et son plan de consolidation](docs/reviews/ARCHITECTURE_2026-10-21.md).
