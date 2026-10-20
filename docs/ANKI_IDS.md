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
