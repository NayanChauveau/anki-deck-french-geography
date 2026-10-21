# Identité Anki

- Namespace GUID : `ultimate-french-geography-v1`.
- Deck `Géographie française::Fleuves` : `1976423100`.
- Modèle `Géographie française — carte physique` : `1976423101`.
- Identifiant de note : `fr-geo-{rule.id}-{feature.id}`.
- GUID : `genanki.guid_for(namespace, identifiant_de_note)`.
- Une note produit une carte, template `Identifier`, ordinal 0.

Par exemple, la règle `hydrographie-identification` et l’objet `loire` donnent
`fr-geo-hydrographie-identification-loire`. Le texte de la question, le nom français,
le chemin du catalogue et les coordonnées ne participent pas à cette identité.
Il n’y a plus de registre manuel d’identifiants de cartes.

Les anciens IDs `fr-geo-fleuve-…` et `fr-geo-cours-eau-…` ont été remplacés avec
l’accord explicite de l’auteur pendant le développement. Cette bascule ne migre
pas les notes déjà importées dans Anki. Aucune importation n’est lancée par le build.

À partir de cette convention, conserver les IDs de règle et d’objet pour garder
les révisions lors des mises à jour. Ne jamais réaffecter un ID diffusé à un autre
objet. Les IDs du deck et du modèle restent propres à ce projet.

## Départements

- Sous-deck `Géographie française::Départements` : `1976423102`.
- Modèle partagé : `1976423101`, mêmes champs et même ordinal de template.
- Identifiant : `fr-geo-{rule.id}-{code en minuscules}-{direction}`.
- Exemple : `fr-geo-departements-2a-map-name`.
- Le GUID utilise le même namespace que les notes hydrographiques.

Chaque direction a une identité distincte. Les codes du catalogue restent des
chaînes (`01`, `2A`, `971`) ; seul le composant de l’ID est mis en minuscules.

## Régions, villes et relief

- Régions : deck `1976423103`, noms et positions `fr-geo-regions-reg-{code}-{direction}`.
- Villes : deck `1976423104`, positions `fr-geo-villes-chefs-lieux-city-{code}-{direction}`.
- Relief : deck `1976423105`, positions `fr-geo-relief-massifs-mountain-{id}-{direction}`.
- Relations : `fr-geo-{id de règle}-{id de l’objet source en minuscules}`.

Le modèle et le namespace existants sont partagés. Les anciens IDs des cours d’eau
et départements ne changent pas. Une correction de texte ou de géométrie conserve
l’identité de la note ; les relations sans valeur de rappel sont exclues avant export.

## Lacs, littoral, outre-mer et paysages

- Lacs : sous-deck `1976423106`, règle `hydrographie-lacs`.
- Littoral : sous-deck `1976423107`, règles `littoral-mers` et `villes-portuaires-facade`.
- Outre-mer : sous-deck `1976423108`, règles `outre-mer-situation` et `outre-mer-ocean`.
- Paysages : sous-deck `1976423109`, règle `parcs-nationaux-coeurs`.

Le modèle `1976423101` et le namespace existants restent communs. Les notes des
villes complémentaires conservent la règle historique `villes-chefs-lieux` afin de ne
pas renommer les notes existantes ; ce nom technique ne définit plus le périmètre.
Les nouvelles relations utilisent des identités distinctes, sans dupliquer les
localisations de villes déjà présentes.

## Pilote anglais et noms de paquets figés

- Français : `french-geography-fr.apkg`, namespace, IDs de modèles/decks et IDs de notes inchangés.
- Anglais : `french-geography-en.apkg`, namespace `ultimate-french-geography-v1-en`.
- Modèle anglais : `1976423201` ; sous-deck `French geography::Rivers` : `1976423200`.
- Note anglaise : ID français source suivi de `-en`, avec un GUID dans le namespace anglais.

Le pilote sélectionne explicitement les traductions de `locales/en.yml` ; une carte
sans traduction n’est pas incluse dans le paquet anglais. Les deux fichiers ne sont
donc pas annoncés comme ayant le même contenu. Les noms d’assets sont figés dans
`src/french_geography/distribution.py` pour les futures versions.
