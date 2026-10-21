# Régions, chefs-lieux et relations administratives

Les catalogues utilisent le COG au 1er janvier 2025 : 18 régions, 101 départements et
101 communes chefs-lieux. `data/administration/cog-2025.json` conserve les lignes
INSEE sélectionnées. Il est vérifié par empreinte, sans être traité comme une couche
de géométries. Les noms et codes ne sont pas inférés depuis les contours.

- `catalog/regions.yml` : code, nom, chef-lieu et vue régionale.
- `catalog/departments.yml` : département, région et commune chef-lieu.
- `catalog/cities.yml` : commune, département et région, réutilisés par plusieurs règles.
- `geo/features/regions.geojson` : contours régionaux Etalab/IGN, millésime 2025, 1000m.
- `geo/features/cities.geojson` : positions des mairies Etalab/IGN, millésime 2025.

Les positions sont des points de repérage urbain, pas les contours des agglomérations.
Les noms, relations et chefs-lieux sont datés de 2025 ; les villes ne sont pas une
sélection des plus grandes populations. Les métropoles complémentaires restent
un lot ultérieur. Les cinq DROM disposent de vues locales adaptées.

## Cartes générées

Les règles de `cards/regions.yml` et `cards/cities.yml` produisent 148 cartes régionales
et 401 cartes urbaines. Les questions incluent la reconnaissance et la localisation,
région → chef-lieu, département → région, département → chef-lieu et ville → département.
Les questions dont le libellé contient déjà toute la réponse sont exclues. Les noms
et codes sont saisis une fois ; les réponses textuelles n’embarquent aucune image.

Les cartes de position sont groupées par lots de dix, avec les localisations puis
les reconnaissances. Le même point ou polygone est réutilisé entre les sens. Les
références sont accessibles dans le verso Anki et la galerie.

## Provenance et reproduction

Le registre `geo/sources.yml` contient les URL, versions, licences et empreintes.
Le COG est sous Licence Ouverte 2.0 (Source : Insee, 2025). Les contours régionaux
et positions des mairies proviennent du jeu Etalab déclaré sous ODbL 1.0.
Leur attribution est affichée en HTML sous les images. Les bases dérivées restent
fournies dans le dépôt avec les transformations documentées.

Préparation hors build, après acquisition explicite des fichiers du registre :

```sh
uv run --frozen python scripts/prepare_administration.py \
  /chemin/regions-1000m.geojson \
  /chemin/v_region_2025.csv \
  /chemin/v_departement_2025.csv \
  /chemin/v_commune_2025.csv \
  /chemin/mairies.geojson
```

Le script exclut les COM du catalogue régional, répare les polygones invalides et
réduit les propriétés géographiques aux IDs. Les clés de liaison et les noms restent
dans les catalogues. La préparation départementale initiale peut être suivie de cette
étape pour restaurer les champs région et chef-lieu. Aucun accès réseau au build.

Les tests vérifient les relations avec les tables COG, les chefs-lieux de Normandie
et de Bourgogne-Franche-Comté, la couverture des points et régions et la stabilité
des anciennes notes. L’affichage dans chaque client Anki reste une validation réelle
à distinguer de ces contrôles automatiques.

## Sélection urbaine complémentaire du 21 octobre 2026

Douze repères éditoriaux s’ajoutent aux 101 chefs-lieux : Antibes, Cannes,
Aix-en-Provence, Brest, Saint-Malo, Reims, Roubaix, Tourcoing, Mulhouse,
Villeurbanne, Le Havre et Saint-Denis (Seine-Saint-Denis). Il ne s’agit pas d’un
classement de population. La sélection et les codes COG sont dans
`catalog/additional-cities.yml`, réutilisés par la préparation administrative.
Les 113 points restent des mairies 2025, sans prétendre représenter les agglomérations.

Les questions précisent « Île-de-France » ou « océan Indien » pour les deux
Saint-Denis ; ces indications évitent de divulguer le département dans une question
ville → département. Le Saint-Denis francilien partage le cadrage local parisien.
