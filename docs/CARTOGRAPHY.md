# Cartographie

## Pipeline implémenté

Règles YAML + catalogue éditorial + GeoJSON locaux → génération des notes en mémoire
→ validation avec vues et styles → scène projetée commune
→ SVG et PNG → galerie HTML et paquet Anki.

Les deux sorties utilisent les mêmes primitives et coordonnées. Le SVG embarque
la police ; le PNG est rendu par Pillow en double résolution puis réduit avec
Lanczos. Chaque média porte le SHA-256 complet de ses octets. Les PNG recto et verso
référencés par les notes sont tous inclus dans le paquet Anki.

Les sources sont vérifiées par empreinte avant le rendu. Le build ne contient
aucune acquisition de données. Les champs éditoriaux sont échappés pour l’HTML.

## Géométries et vues

Les entrées sont des GeoJSON WGS84 (longitude, latitude). Le moteur gère Point,
LineString, Polygon et leurs collections/formes multiples, y compris les trous.
Une zone approximative peut être fournie comme polygone ; son caractère approximatif
doit être expliqué dans la fiche et dans la provenance des données.

Chaque vue définit une projection PROJ/EPSG, des limites WGS84, une largeur et une
hauteur. Le cadrage utilise des limites densifiées avant projection, sans zoom
propre à chaque cible. Les coordonnées sont découpées au cadre de la vue.
La vue `metropolitan` utilise Lambert-93 (`EPSG:2154`). Une autre projection et un
jeu de données adapté permettront les futures vues d’outre-mer.

Le champ facultatif `inset` désigne une autre vue : celle-ci apparaît en bas à droite
avec la même cible surlignée, pour situer un détail régional. Les encarts ne sont
pas récursifs. Un test exerce une vue régionale avec un encart national.

Les annotations définissent texte, longitude, latitude et côté (`back` par défaut,
`both` pour un repère commun). Elles ne changent pas le cadrage recto/verso. Le moteur
ne place pas automatiquement les étiquettes : il faut vérifier leur position dans
la galerie. Pour les pilotes, seuls les noms des cours d’eau apparaissent au verso.

## Sources locales

`geo/sources.yml` est le registre de référence : URL amont figée, tag, licence et
son URL, SHA-256 amont, transformations, chemin local et SHA-256 du fichier préparé.
Les rivières au 1:10 millions sont sélectionnées par nom et réunies par cours d’eau ;
les pays au 1:50 millions et les rivières sont découpés à `[-7, 40, 12, 53]`.
Aucune coordonnée n’est ajoutée ni ajustée à la main.

Natural Earth est dans le [domaine public](https://www.naturalearthdata.com/about/terms-of-use/).
Le tag du dépôt est `v5.1.2` ; les couches peuvent avoir un numéro de version propre
différent du tag de distribution. Les tracés sont généralisés, sans garantie de
précision pour les extrémités, les petits détails ou une mesure de distance.
Le fond administratif sert de contexte ; il ne représente pas le relief.

Pour reproduire la préparation, télécharger **explicitement** les deux URL inscrites
dans `geo/sources.yml`, vérifier leurs `upstream_sha256`, puis exécuter :

```sh
uv run --frozen python scripts/prepare_geography.py /chemin/rivers.geojson /chemin/countries.geojson
make check
make preview
```

Le script attend les couches Natural Earth indiquées dans le registre et sélectionne
les 18 cours d’eau de `geo/selection.yml`. Il n’est appelé par aucune commande de build.
Lors d’une évolution des données, examiner les différences de géométrie et la galerie,
puis conserver ensemble les nouveaux fichiers et le registre mis à jour.

## Validation visuelle

Les 18 cours d’eau utilisent un cadrage national partagé. La galerie
montre recto et verso côte à côte. Le build et les médias embarqués sont testés hors
réseau ; l’affichage dans Anki Desktop et sur téléphone reste une validation manuelle.
Les dix autres catégories envisagées pour la série de douze exemples sont différées.

Le Rhône inclut le tronçon `Rhne` de type `Lake Centerline` de Natural Earth
pour assurer la continuité du tracé à travers le lac Léman. Ce segment est un axe
cartographique du lac, pas un chenal matérialisé à sa surface.

## Série hydrographique

La sélection comporte 18 objets distincts, issus de 21 éléments Natural Earth.
Les alias d’origine (`Maas`, `Mosel`, `Schelde`, `Sane`, `Segre`, etc.) sont conservés
dans `geo/selection.yml` ; les fiches affichent les noms français. Les données sont
réunies par ces alias, sans supposer que `rivernum` est un identifiant mondial unique.

L’intersection avec le contour national sert à choisir les cours d’eau, pas à couper
leur tracé à la frontière : leurs portions étrangères disponibles restent visibles.
C’est particulièrement utile pour l’Escaut, la Meuse, la Moselle et le Sègre.
La généralisation peut supprimer des tronçons : la Saône ne montre ici que l’aval,
et le Rhin seulement une partie de son parcours. Les fiches signalent ces deux cas.
Les limites des vues ne représentent pas des sources ni des embouchures.

Les notes sont créées par `src/french_geography/generate.py` à partir des règles
`cards/identification.yml` et du catalogue `catalog/rivers.yml`. Chaque règle parcourt
toute sa couche géographique ; les noms et articles du catalogue servent à former
les réponses. Les références propres à un objet complètent celles de la règle.
La question et la vue sont communes. Une explication peut être omise, ainsi que
le placement d’étiquette ; celui-ci utilise alors un point représentatif du tracé.

Le catalogue est validé indépendamment du schéma géographique. Un ID manquant,
inconnu ou dupliqué est une erreur. Les objets générés existent uniquement en mémoire
pendant la validation ou le build ; aucun YAML de notes n’est produit.

Les identifiants des cartes sont calculés depuis les IDs de la règle et de l’objet.
Les anciens identifiants ont été abandonnés à la demande de l’auteur pendant cette
phase de développement. Voir `ANKI_IDS.md` pour la convention actuelle.

## Couches thématiques et départements

Chaque note indique sa couche : les 18 cours d’eau utilisent uniquement le fond
hydrographique ; les départements utilisent leurs limites polygonales. Les notes
peuvent demander une image sans cible (`blank`), avec cible (`target`) ou aucune
image (`none`). Le build réutilise les images identiques entre les sens d’une même
série. Les images restent nommées par empreinte et toutes celles référencées sont
embarquées dans le paquet. Voir [DEPARTMENTS.md](DEPARTMENTS.md) pour les données,
la licence, les six sens disponibles et les trois sens actuellement activés.
