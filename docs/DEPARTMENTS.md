# Départements : nom, numéro et position

Le catalogue `catalog/departments.yml` contient 101 objets (96 métropolitains et les
cinq DROM du référentiel). Chaque objet possède un identifiant géographique,
un code départemental **texte**, un nom et, au besoin, une vue particulière.
La géométrie est séparée, dans `geo/features/departments.geojson`, sous le même ID.
Les codes conservent leurs zéros (`01`), leurs lettres (`2A`, `2B`) et les trois
chiffres ultramarins (`971`, `972`, `973`, `974`, `976`).

`cards/departments.yml` définit une seule règle. Les trois sens actifs sont :

| Sens | Recto | Verso |
| --- | --- | --- |
| `name-map` | Nom et carte sans surbrillance | Zone du département surlignée |
| `map-name` | Zone surlignée, sans nom ni code | Nom du département |
| `map-code` | Même zone surlignée, sans nom ni code | Code départemental |

Le premier sens se révise en situant mentalement ou en pointant la zone, puis en
comparant au verso. Il n’y a pas de clic interactif ni de correction automatique.
Les deux autres sens sont des rappels libres, avec la notation habituelle d’Anki.
La carte du verso des trois sens garde le même cadrage que le recto.

Cela produit **303 notes/cartes**, sous `Géographie française::Départements`.
Les 18 cartes hydrographiques restent dans leur sous-deck initial.
Les tags `direction::name-map`, `direction::map-name` et `direction::map-code`
permettent de travailler un sens particulier.

Trois sens supplémentaires sont implémentés mais désactivés : `name-code`,
`code-name`, `code-map`. Pour les activer, les ajouter à `directions` dans la règle.
Les deux premiers sont textuels : aucune image n’est générée ou embarquée pour eux.
Le nom et le code ne doivent être saisis qu’une fois, dans le catalogue.

## Vues et lisibilité

Les cartes de départements montrent les limites départementales, sans le réseau
hydrographique. Les cartes de cours d’eau gardent leur fond hydrographique sans
les départements. Une seule cible est surlignée, et aucun nom ni numéro n’est dessiné
sur les images des questions.

La vue métropolitaine est partagée. Paris et la petite couronne utilisent un cadrage
francilien avec un encart métropolitain. Les cinq DROM ont chacun une vue locale
avec une projection UTM adaptée. Les contours ultramarins restent à leurs vraies
coordonnées ; les vues locales ne sont pas un planisphère de localisation mondiale.

## Données et reproduction

Source : Etalab / data.gouv.fr, **Contours administratifs, millésime 2025, 1000m**,
issu d’IGN Admin Express pour les départements. La fiche du jeu annonce la licence
[ODbL 1.0](https://www.data.gouv.fr/datasets/contours-administratifs).
L’URL datée, les empreintes amont et locale, et les modifications sont conservées
dans `geo/sources.yml`. La base dérivée est distribuée dans le dépôt, sous cette
licence ; les cartes Anki et la galerie affichent l’attribution Etalab / IGN et le lien de
licence sous l’image, hors du SVG/PNG.

Le fichier amont comprend aussi des collectivités d’outre-mer, exclues de cette
série départementale. Les polygones invalides sont réparés avec `make_valid` ; les
résidus linéaires d’effondrement sont écartés. Aucune simplification supplémentaire
n’est appliquée. Les contours au kilomètre servent au repérage pédagogique.

Pour reproduire la préparation, télécharger explicitement le fichier amont du
registre, vérifier son empreinte `upstream_sha256`, puis exécuter :

```sh
uv run --frozen python scripts/prepare_departments.py /chemin/departements-1000m.geojson
make check preview build
```

Le script prépare les géométries, extrait le catalogue des noms/codes et met à jour
le registre. Relire les éventuels choix de vues après cette opération.
Le build ordinaire utilise uniquement les fichiers locaux.

Les identifiants Anki sont dérivés de la règle, du code et du sens, par exemple
`fr-geo-departements-01-map-code`. Changer une question ou un cadrage ne les change pas.
