# Cartographie

## Pipeline implémenté

Règles YAML + catalogue éditorial + GeoJSON locaux → génération des notes en mémoire
→ validation avec vues et styles → scène projetée commune
→ SVG et PNG → galerie HTML et paquet Anki.

Les deux sorties utilisent les mêmes primitives et coordonnées. Le SVG ne contient aucune police embarquée pour les scènes sans texte ; le PNG est rendu par Pillow en double résolution puis réduit avec
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

Les images restent sans texte : aucun titre, crédit ou nom de cours d’eau n’est
dessiné dans les SVG/PNG. Les questions, réponses, explications et références sont
présentées par le template HTML Anki. Les crédits départementaux sont visibles sous
l’image, avec les liens vers le jeu source et la licence. Recto et verso gardent
le même cadrage ; seules les cartes de localisation changent la surbrillance.

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
toute sa couche géographique ; les noms canoniques et les formulations de la langue
sélectionnée servent à former les réponses. Les références propres à un objet
complètent celles de la règle. Les descriptions et questions localisées vivent
dans `locales/`, sous des clés stables ; voir [LOCALIZATION.md](LOCALIZATION.md).
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

## Sommets repères

Trois points Natural Earth v5.1.2 représentent le mont Blanc, le puy de Sancy et le
crêt de la Neige. `scripts/prepare_peaks.py` sélectionne ces points depuis un fichier
local ; le build utilise uniquement `geo/features/peaks.geojson`, vérifié par empreinte.
Les coordonnées généralisées sont conservées ; les attributs d’altitude sont exclus.
Le catalogue éditorial `catalog/peaks.yml` conserve leurs relations aux grands ensembles
Alpes, Massif central et Jura, avec références factuelles Larousse vérifiées le
20 octobre 2026. « Grand ensemble » distingue cette échelle des massifs locaux
(Mont-Blanc, monts Dore). Les trois sens génèrent neuf cartes, sans altitude à réciter.
Les sommets forment une couche de points séparée des polygones indicatifs de relief.

Paris, Nanterre, Bobigny et Créteil partagent désormais la vue francilienne avec
encart métropolitain : leurs points se confondaient à l’échelle nationale. Leurs
identifiants et coordonnées restent identiques.

## Extension du 21 octobre 2026

Le fond pays est désormais mondial (Natural Earth 50m v5.1.2), au lieu d’être découpé
sur l’Europe. Les cadrages métropolitains restent locaux ; les cartes de situation
ultramarine utilisent un planisphère unique en projection Equal Earth, sans zoom
ni encart. Les points de situation ultramarins sont
calculés à l’intérieur des cinq polygones départementaux et ne sont pas déplacés.
Les frontières du fond Natural Earth sont généralisées : leurs côtes peuvent différer
des cibles locales plus précises. Ce fond ne remplace pas un référentiel de limites.

Les deux nouvelles zones de relief sont des schémas indépendants dans
`data/relief/schematic-zones.geojson` (CC0), accompagnés de références BRGM sur la
situation des ensembles. Les références soutiennent le contexte géographique ; elles
ne sont pas présentées comme la source de ces polygones. Les schémas sont découpés
sur le contour français Natural Earth pour éviter de remplir la mer. Les limites
intérieures restent indicatives et ne remplacent aucun contour géologique officiel.

BD TOPAGE 2024 (IGN/OFB/Sandre, Licence Ouverte 2.0) complète 14 cours d’eau,
remplace la Saône et complète la partie frontalière du Rhin. Les codes sélectionnés
sont conservés dans `data/hydrography/selected-codes.json`. Les homonymes ne sont
pas fusionnés. La Somme réunit les objets « Fleuve la Somme » et le cours canalisé.
La simplification de 150 m utilise Lambert-93. Les tronçons étrangers absents du
référentiel national ne sont pas inventés ; le Rhin demeure incomplet à cette échelle.
Les instantanés WFS sélectionnés et leurs requêtes sont épinglés sous `data/`.

Les lacs d’Annecy et du Bourget ainsi que les retenues de Serre-Ponçon et de
Sainte-Croix viennent de BD TOPAGE ; le Léman vient de Natural Earth. Les vingt lacs et retenues utilisent le cadrage métropolitain commun, sans zoom local
ni encart, pour apprendre directement leur position en France. Les cinq zones marines
Natural Earth sont des étendues géographiques conventionnelles, sans valeur juridique.
Les crédits sont en HTML hors des images.

Les cœurs terrestres et marins des onze parcs nationaux sont issus du jeu officiel
Parcs nationaux de France/OFB du 11 février 2026, sous Licence Ouverte 2.0. Les codes
CTPN et CMPN sont réunis par parc ; les aires d’adhésion et les aires maritimes adjacentes
sont exclues. Simplification de 100 m en Lambert-93 ou UTM local, puis retour en WGS84.
Le verso précise ce périmètre. Ces cartes servent à apprendre des lieux, pas à décider
des règles applicables à une parcelle ou à une navigation.

### Préparation séparée du build

Les scripts prennent des entrées locales ; ils ne sont jamais appelés par le build.
`prepare_world_context.py` prépare le fond mondial ; `prepare_relief.py` réunit les
cinq zones NE et les schémas locaux ; `prepare_hydrography.py` combine les cours d’eau
NE et l’instantané TOPAGE ; `prepare_water_places.py` prépare lacs, mers et points
ultramarins ; `prepare_parks.py` sélectionne les cœurs du jeu officiel. Les URL,
versions, licences, empreintes et modifications sont dans `geo/sources.yml`.
Les fichiers locaux référencés par `inputs` sont aussi vérifiés par le chargeur.

Attention à l’ordre de préparation : `prepare_geography.py` produit le socle NE initial,
avant les extensions hydrographiques et le fond mondial. Il ne suffit pas à régénérer
la version enrichie. `prepare_relief.py` dépend du fond pays ; les points outre-mer
dépendent des départements. La revue d’architecture doit examiner l’orchestration
explicite de ces dépendances. `make check`, `make preview` et `make build` utilisent
uniquement les données préparées, sans accès réseau.

## Cache de rendu

Un passage de génération partage les fonds projetés par couche et par vue, encarts
compris. Ce cache en mémoire reste limité au projet courant. Le cache disque conserve
les médias nommés par empreinte ; chaque fichier réutilisé est vérifié une fois par
passage et chaque média de galerie est copié une seule fois. Les clés dépendent des
vues effectivement utilisées, des données, du style, du moteur et de ses dépendances.
La CI restaure `build/media` entre exécutions ; les empreintes internes invalident les
entrées incompatibles, même après une restauration partielle. Le build complet reste
exécuté après les tests ; le test bilingue utilise seulement un échantillon de notes.

Les tests affichent leur nom avant exécution et les dix durées les plus longues.
Après 120 secondes dans un test, pytest imprime les piles des threads pour diagnostiquer
un éventuel blocage, sans interrompre automatiquement le test.

## Extension des grands lacs

La sélection comprend 20 lacs et retenues, soit 40 cartes par langue. Elle complète
le pilote par Hourtin-Carcans, Cazaux-Sanguinet, Grand-Lieu, Parentis-Biscarrosse,
Lacanau, Der-Chantecoq, Orient, Temple, Vouglans, Pareloup, Madine, Bort-les-Orgues,
Vassivière, Naussac et Salagou. C’est une sélection pédagogique des grands plans
d’eau douce métropolitains, pas un classement exhaustif par superficie. Les lagunes
salées (Thau, Berre…) et les lacs ultramarins ne sont pas compris dans cette série.

`data/lakes/selection.yml` associe chaque identifiant aux codes Sandre exacts.
Hourtin et Carcans sont réunis ; les petits homonymes de Vassivière sont exclus.
Les contours TOPAGE ne représentent pas les niveaux actuels, particulièrement
variables pour Grand-Lieu. Aucune surface chiffrée n’est déduite de ces contours.
Le catalogue éditorial et les traductions restent séparés de cette sélection.

Préparation autonome, hors build et sans téléchargement :

```sh
uv run --frozen python scripts/prepare_lakes.py /chemin/ne_10m_lakes.geojson
```

L’entrée Natural Earth est vérifiée contre son empreinte épinglée. Les 20 objets
TOPAGE locaux (dont deux pour Hourtin-Carcans) et les requêtes d’acquisition sont
conservés sous `data/lakes/`, avec leurs empreintes dans le registre des sources.
