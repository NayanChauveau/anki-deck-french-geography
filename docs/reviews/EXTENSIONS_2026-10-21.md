# Revue du contenu ajouté — 21 octobre 2026

## Périmètre local

1 014 cartes, neuf thèmes. Le lot étend les catalogues sans changer les identités
existantes. Il n’a pas encore été importé dans Anki. Les vérifications sur Desktop
et mobile restent distinctes du contrôle des données et du build.

- Relief : deux schémas indépendants armoricain/corse, références de contexte BRGM ;
  quatre sommets dont Monte Cinto (relation aux reliefs corses soutenue par Larousse).
- Villes : douze communes ajoutées par code COG, avec points de mairie 2025 ; aucune
  affirmation de classement. Les deux Saint-Denis sont qualifiés dans les questions.
- Hydrographie : quatorze ajouts sélectionnés par identifiant Sandre, huit fleuves
  côtiers et six affluents. Les phrases et relations ont des références Larousse dans
  les catalogues. Les instantanés TOPAGE sont séparés du contenu éditorial.
- Saône : remplacement du fragment NE par le cours TOPAGE. Rhin : complément de la
  portion frontalière française, sans affirmer une couverture internationale complète.
- Somme : sélection du fleuve picard et de son cours canalisé, pas des homonymes
  bourguignons. Les petits homonymes de l’Orne, de la Vilaine, de l’Allier, du Var
  et de l’Ain sont exclus par leurs codes.
- Lacs : Léman, Annecy, Bourget et deux retenues (Serre-Ponçon et Sainte-Croix).
  Le type est soutenu par les attributs TOPAGE ; les deux retenues et leur cours d’eau
  associé sont confirmés par [Larousse, Durance](https://www.larousse.fr/encyclopedie/riviere-lac/la_Durance/117449).
- Mers : cinq étendues Natural Earth conventionnelles, sans portée juridique.
- Outre-mer : cinq points intérieurs aux départements, positions réelles en vues
  océaniques avec encarts mondiaux. Bassins océaniques vérifiés sur la
  [carte Géoconfluences 2025](https://geoconfluences.ens-lyon.fr/images/glossaire/img-france/monde-outre-mer-francais-2025.pdf/download).
- Parcs : les cœurs terrestre et marin des onze parcs nationaux sont regroupés ; les
  aires d’adhésion et maritimes adjacentes sont exclues. Le jeu
  [PNF/OFB de février 2026](https://www.data.gouv.fr/datasets/contours-des-11-parcs-nationaux-de-france)
  fournit les noms, catégories et contours, avec sa Licence Ouverte 2.0.
- Ports : cinq relations ville/façade, références institutionnelles propres à chaque
  entrée ; Rouen est explicitement traité comme port de fond d’estuaire sur la Seine.
  Aucune nouvelle localisation urbaine équivalente n’est générée.

## Vérifications et limites

50 tests réussis : homonymes hydrographiques, prolongement amont de la Saône,
relations d’affluent direct, points ultramarins intérieurs, fond mondial, homonymes
urbains sans réponse divulguée, onze cœurs de parcs et réutilisation des villes.
Les empreintes des entrées composites locales sont vérifiées au chargement.

Rendus inspectés : Somme, Saône, reliefs corses et armoricains, Bourget, Manche,
Guadeloupe, La Réunion, Port-Cros et parc amazonien. Le fond mondial 50m est
moins précis que certaines cibles ; il peut manquer de petites îles. Cette différence
d’échelle est une limite de contexte à examiner, pas une modification des cibles.

Les zones schématiques restent des approximations rédigées pour ce deck. Elles ne
sont ni extraites d’une carte BRGM ni présentées comme un zonage officiel. Leurs
contours côtiers sont découpés sur le fond français pour ne pas remplir la mer.
Les contours de parcs sont simplifiés : ils ne permettent pas de décider du droit
applicable à un lieu. Les altitudes, populations, classements et statuts institutionnels
ne sont pas ajoutés implicitement.
