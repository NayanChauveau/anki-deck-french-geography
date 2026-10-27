# Ultimate French Geography — roadmap

Document de référence pour la progression du contenu et du moteur.
Mise à jour : 21 octobre 2026.

Les cases cochées décrivent des fonctions implémentées ou des vérifications réalisées.
Les autres éléments sont des travaux à venir, sans date de livraison annoncée.
Les listes d’objets ci-dessous sont des sélections candidates à valider, pas des
inventaires déjà présents dans le deck ni des objectifs d’exhaustivité.

## 1. Ambition

Construire une carte mentale solide de la France : reconnaître les lieux, savoir
les situer et comprendre leurs relations. Couvrir progressivement géographie
administrative, physique et humaine, en métropole comme en outre-mer.

Le nom « Ultimate » désigne la richesse et la cohérence du parcours. Le nombre de
cartes n’est pas un objectif en soi. Une nouvelle série doit apporter des repères
utiles, lisibles et vérifiables, avec une charge de révision raisonnable.

### Principes pédagogiques

- Une question doit demander un rappel clairement défini.
- Privilégier les repères durables et les grandes relations géographiques.
- Commencer par les grands ensembles, puis ajouter leurs détails.
- Relier les éléments : ville → département → région ; rivière → affluent ou exutoire.
- Activer les sens de rappel utiles, sans multiplier automatiquement toutes les permutations.
- Distinguer un lieu, une zone, une relation et un ordre de grandeur.
- Garder les explications courtes, sous l’image, avec une référence adaptée au fait expliqué.
- Préférer les ordres de grandeur aux populations ou altitudes exactes systématiques.
- Documenter les ambiguïtés : limites approximatives, noms historiques, homonymes et statuts.

### Familles de cartes

| Famille | Exemple | Présentation attendue |
| --- | --- | --- |
| Reconnaître | Zone ou point → nom | Cible surlignée sans étiquette ; réponse au verso |
| Situer | Nom → position | Fond sans surbrillance au recto ; même cadre avec cible au verso |
| Identifier un code | Département surligné → numéro | Nom et code affichés au verso |
| Relier | Ville → département ; rivière → cours d’eau rejoint | Question textuelle ou carte avec contexte adapté |
| Comprendre | Massif → sommet repère ; fleuve → bassin | Relation courte accompagnée d’une explication sourcée |
| Estimer | Sommet → ordre de grandeur d’altitude | Réponse adaptée à l’objectif, sans précision inutile |

Les cartes de localisation actuelles se révisent mentalement ou en pointant la zone,
puis en comparant au verso. Elles ne comportent pas de clic interactif ni de correction
automatique. Ces possibilités seraient un chantier distinct.

## 2. État réel du projet

### Contenu disponible

- [x] 32 cartes d’identification de cours d’eau et six relations affluent → cours d’eau rejoint.
- [x] Catalogue des 101 départements, avec nom, code texte et géométrie associée.
- [x] 303 cartes départementales : nom → position, position → nom, position → numéro.
- [x] Verso des questions de numéro : nom et code, par exemple « Ain (01) ».
- [x] Ordre départemental par lots de dix : dix localisations, dix noms, dix numéros.
- [x] Autres sens du triangle implémentés, mais désactivés : nom → code, code → nom, code → position.
- [x] Vues locales ultramarines et vue francilienne avec encart métropolitain.

- [x] 148 cartes régionales et relations département → région, à partir du COG 2025.
- [x] 437 cartes urbaines : 113 communes, dont les 101 chefs-lieux, et relations départementales.
- [x] Sept zones de relief, dont deux schémas explicitement signalés ; quatorze cartes de localisation.
- [x] Quatre sommets repères et douze cartes : localisation dans les deux sens et grand ensemble associé.
- [x] Vingt lacs/retenues (quarante cartes), cinq zones maritimes et cinq relations port/façade (quinze cartes).
- [x] Situation de cinq territoires ultramarins et bassin océanique (quinze cartes).
- [x] Cœurs des onze parcs nationaux, dans les deux sens (vingt-deux cartes).

Total généré : **1 034 notes produisant chacune une carte**. Ce nombre ne décrit pas
nécessairement le nombre de notes d’une collection Anki déjà utilisée : les anciennes
notes issues des changements d’identifiants peuvent y subsister.

### Socle disponible

- [x] Python/uv, dépendances verrouillées, CLI et commandes Make.
- [x] Séparation des géométries, catalogues éditoriaux, règles et rendu.
- [x] Génération des notes en mémoire, sans répétition des questions dans les catalogues.
- [x] Validation des catalogues, références aux objets, vues et empreintes des données.
- [x] Projections, cadrages partagés, couches thématiques et encarts.
- [x] Rendu des points, lignes et polygones, dont formes multiples et trous.
- [x] SVG/PNG sans texte dessiné sur les images ; explications dans le template Anki.
- [x] Crédits départementaux sous l’image et références en bas de carte.
- [x] Médias nommés par empreinte et embarqués dans le paquet Anki.
- [x] Galerie HTML locale, export genanki et commandes AnkiConnect.
- [x] CI de contrôle et artefacts paquet/galerie définis dans le dépôt.
- [x] Tests automatiques : 57 tests réussis lors des dernières vérifications.
- [x] Paquet de 880 cartes construit et importé via AnkiConnect le 20 octobre 2026 ; synchronisation demandée.

### Limites à traiter

- [ ] Valider méthodiquement les rendus, les mises à jour et les réglages sur Anki Desktop et mobile.
- [x] Compléter les références factuelles des 18 explications hydrographiques existantes.
- [ ] Étendre la revue factuelle aux prochaines explications et séries.
- [ ] Améliorer certains tracés hydrographiques incomplets, notamment Rhin et Saône.
- [ ] Vérifier les crédits et obligations de redistribution avant publication publique.
- [ ] Configurer et éprouver la publication des releases.

Un import ayant répondu sans erreur ne vaut pas contrôle visuel de toutes les cartes,
ni confirmation d’une synchronisation terminée sur tous les appareils.

## 3. Ordre de développement proposé

Alterner des séries administratives et physiques pour enrichir la carte mentale sans
concentrer tout le parcours sur les codes administratifs.

| Lot | Contenu principal | Résultat attendu | Dépendances |
| --- | --- | --- | --- |
| 0 | Qualité du socle existant | Textes sourcés, limitations explicites, import fiable | Aucun nouveau thème |
| 1 | Régions et chefs-lieux régionaux | Grands ensembles administratifs et premiers repères urbains | Catalogues de relations et points urbains |
| 2 | Grands massifs et relief | Lecture de la structure physique du pays | Zones approximatives documentées |
| 3 | Villes et préfectures départementales | Relier les villes aux départements et régions | Lots 1 et socle départemental |
| 4 | Hydrographie enrichie | Fleuves manquants, affluents et bassins | Sources plus complètes, relations hydrologiques |
| 5 | Littoral et grands lacs | Contours, façades et repères côtiers | Types de cibles et cadrages validés |
| 6 | Outre-mer à l’échelle mondiale | Localisation mondiale et connaissance locale | Fond mondial et projections adaptées |
| 7 | Paysages et territoires | Régions naturelles, historiques, forêts et parcs | Convention sur les zones floues et référentiels datés |
| 8 | Géographie humaine | Ports, axes et grands espaces d’activité | Relations et faits éditoriaux sourcés |

### Statut des lots après le dernier import

| Lot | Statut réel |
| --- | --- |
| 0 | Revue des 18 textes terminée ; contrôle complet dans les clients Anki encore ouvert |
| 1 | 18 régions et chefs-lieux générés et importés ; documentation institutionnelle à compléter |
| 2 | Pilote de cinq ensembles importé ; autres ensembles, sommets et cols à faire |
| 3 | 101 chefs-lieux et relations générés et importés ; grandes villes complémentaires à sélectionner |
| 4 à 8 | Non implémentés ; les séries existantes ne valent pas réalisation de ces extensions |

L’outre-mer doit aussi être inclus dans chaque lot pertinent. Le lot 6 approfondit
sa localisation et ses relations ; il ne signifie pas de l’ignorer avant cette étape.

## 4. Priorité 1 — régions, villes et structure administrative

### 4.1 Régions

- [x] Préparer un référentiel daté des régions et de leurs contours.
- [x] Ajouter le nom officiel, les éventuels noms usuels et le chef-lieu régional.
- [x] Relier chaque département à sa région dans les données.
- [x] Générer région → position et position → région.
- [x] Générer région → chef-lieu lorsque le bénéfice pédagogique est clair.
- [x] Générer département → région, en évitant d’ajouter le sens inverse sous forme d’une longue liste.
- [ ] Documenter les particularités institutionnelles sans confondre région, département et collectivité.

Le catalogue doit distinguer le libellé administratif retenu et la formulation de la
question. Les statuts ne doivent pas être déduits uniquement d’un polygone.

**Critère de fin :** toutes les régions du périmètre retenu sont représentées, les
relations département/région sont vérifiées, les vues ultramarines sont lisibles et
les nouveaux objets ne changent pas le fond des séries existantes.

### 4.2 Premiers repères urbains

- [x] Ajouter les chefs-lieux régionaux comme premier ensemble de villes.
- [x] Définir douze repères urbains complémentaires, sélection éditoriale sans classement de population.
- [ ] Distinguer commune, agglomération et aire d’attraction dans les éventuels critères de sélection.
- [x] Documenter le point géographique retenu pour représenter chaque ville.
- [x] Générer ville → position et position → ville.
- [x] Relier les villes à leurs départements et régions.
- [x] Distinguer les deux Saint-Denis dans les questions ; étendre le contrôle aux futurs ajouts.

Ne pas utiliser « les plus grandes villes » sans préciser le critère et le millésime.
Un chiffre de population ne doit pas devenir une dépendance de l’identité de la note.

### 4.3 Préfectures départementales

- [x] Ajouter les 101 communes chefs-lieux départementaux du COG 2025.
- [x] Stocker la relation département → préfecture une seule fois.
- [x] Choisir les sens de rappel : département → préfecture et/ou ville → département.
- [x] Réutiliser une ville déjà présente dans le catalogue plutôt que la dupliquer.
- [ ] Vérifier les cas particuliers, les graphies et les distinctions chef-lieu/préfecture.
- [ ] Ajouter les sous-préfectures seulement en extension avancée, après validation de l’intérêt.

## 5. Priorité 2 — relief

### 5.1 Grands ensembles

Sélection candidate : Alpes, Pyrénées, Massif central, Jura, Vosges, Massif armoricain
et reliefs corses ; grands bassins, plaines et vallées structurantes.

- [ ] Distinguer les ensembles montagneux, massifs, bassins et plaines dans les types d’objets.
- [x] Choisir les zones indicatives du pilote : Alpes, Pyrénées, Massif central, Jura et Vosges.
- [x] Ajouter des schémas pédagogiques explicitement indicatifs pour le Massif armoricain et les reliefs corses.
- [ ] Étudier leur remplacement par un référentiel physique adapté ; bassins et plaines encore à faire.
- [x] Documenter les limites approximatives des cinq polygones Natural Earth du pilote.
- [x] Générer nom → zone et zone → nom pour les cinq ensembles du pilote.
- [x] Compléter les sept grands ensembles par 29 reliefs régionaux (2026-10-27) :
  Morvan, reliefs du Massif central et de la vallée de la Loire, massifs alpins et
  provençaux ; 72 cartes nom ↔ position, en français et en anglais. Zones
  schématiques sourcées, France entière, explication géographique par relief.
- [ ] Évaluer un fond de relief discret, sans nuire à la lecture des cibles.
- [ ] Prévoir des cadrages communs aux séries régionales.

### 5.2 Sommets et cols

- [x] Première sélection de trois sommets repères (mont Blanc, puy de Sancy, crêt de la Neige) ; autres ensembles à compléter.
- [ ] Stocker nom, position, massif et référence d’altitude avec son millésime si nécessaire.
- [x] Générer sommet → position, position → sommet et sommet → grand ensemble pour cette sélection.
- [ ] Réserver les altitudes exactes aux repères où elles ont une réelle utilité.
- [ ] Ajouter ensuite les cols structurants pour comprendre les passages entre vallées.
- [ ] Vérifier les questions transfrontalières et les conventions d’altitude.

**Critère de fin :** on peut reconnaître les grands ensembles et rattacher les sommets
sélectionnés à leur massif, sans donner aux zones approximatives une fausse précision.

## 6. Priorité 3 — hydrographie

La sélection actuelle correspond aux objets présents dans un fichier Natural Earth
simplifié. Elle ne constitue pas la liste des principaux cours d’eau à apprendre.

### 6.1 Compléter et corriger les tracés

- [ ] Établir une sélection éditoriale indépendante de la disponibilité dans Natural Earth.
- [ ] Ajouter les fleuves manquants importants, dont des fleuves côtiers.
- [x] Ajouter Adour, Somme, Vilaine, Charente, Aude, Hérault, Var et Orne via BD TOPAGE 2024.
- [ ] Choisir une source adaptée, par exemple BD TOPAGE/Sandre après étude de sa couverture et licence.
- [ ] Vérifier la continuité des tracés, confluences, embouchures et traversées de lacs.
- [x] Remplacer la Saône et compléter la portion frontalière française du Rhin avec BD TOPAGE.
- [ ] Compléter le cours international du Rhin avec une source adaptée : il reste partiel.
- [ ] Conserver les identifiants des objets lors d’un changement de géométrie.
- [ ] Contrôler le fond commun : tous les repères de la série visibles, une seule cible surlignée.

### 6.2 Affluents et bassins

- [ ] Ajouter les principaux affluents des grands bassins, selon une sélection documentée.
- [x] Ajouter Allier, Cher, Oise, Lot, Isère et Ain avec leurs identifiants Sandre.
- [x] Stocker explicitement six relations « rejoint tel cours d’eau ».
- [ ] Distinguer affluent direct, sous-affluent, bassin et débouché maritime.
- [x] Générer six premières cartes rivière → cours d’eau rejoint.
- [ ] Ajouter une vue d’ensemble des grands bassins versants.
- [ ] Générer bassin → position et, si utile, fleuve → mer ou océan de débouché.
- [ ] Traiter les estuaires communs et les cas de classement ambigus par une explication sourcée.

### 6.3 Grands lacs

- [x] Première sélection : Léman, Bourget, Annecy, Serre-Ponçon et Sainte-Croix ; à étendre.
- [ ] Distinguer lac naturel, retenue et étang lorsque cette distinction est pertinente.
- [ ] Ajouter nom, géométrie, territoire et relation éventuelle à un cours d’eau.
- [x] Prévoir des vues locales avec encart pour les cinq lacs et retenues.
- [ ] Éviter de sélectionner uniquement les objets les mieux représentés par le jeu source.

## 7. Priorité 4 — littoral, mers et îles

### 7.1 Façades et grands repères

- [ ] Situer les mers et océans bordant les territoires français.
- [ ] Identifier les principales façades maritimes et portions de côte.
- [ ] Couvrir les grands détroits, golfes, caps et estuaires.
- [ ] Séparer les cibles ponctuelles, linéaires et les zones marines approximatives.
- [ ] Vérifier qu’une cible marine peut être surlignée sans être masquée par le fond terrestre.

Sélection candidate : Manche, mer du Nord, Atlantique, Méditerranée, Pas-de-Calais,
golfe de Gascogne, golfe du Lion, cap Gris-Nez, pointe du Raz, cap Corse et grands
estuaires. La granularité et les limites seront arrêtées à l’ouverture du lot.

### 7.2 Îles et archipels

- [ ] Ajouter les grandes îles et les archipels repères, en métropole et outre-mer.
- [ ] Relier île → façade maritime, territoire ou archipel selon le cas.
- [ ] Distinguer une île d’un ensemble administratif portant un nom voisin.
- [ ] Réutiliser les géométries déjà présentes lorsque le sens géographique est identique.
- [ ] Prévoir les encarts utiles pour les petites îles et archipels dispersés.

**Critère de fin :** la forme du littoral permet de reconnaître les principaux repères,
avec des cibles adaptées à leur nature et sans confusion entre zone et point précis.

## 8. Priorité 5 — outre-mer et contexte européen

### 8.1 Position mondiale

Les vues départementales ultramarines actuelles sont locales. Elles ne suffisent pas
à apprendre où ces territoires se trouvent dans le monde.

- [x] Embarquer le fond mondial Natural Earth 50m v5.1.2, local et documenté.
- [x] Ajouter les vues Atlantique/Antilles et océan Indien, avec encarts mondiaux.
- [ ] Couvrir les territoires ultramarins pertinents au-delà du seul catalogue départemental.
- [ ] Stocker explicitement le type de territoire et une référence datée pour les statuts.
- [ ] Relier territoire → océan, ensemble régional et principaux voisins.
- [ ] Ajouter les principales villes et chefs-lieux selon la progression urbaine.
- [ ] Tester les archipels, les territoires dispersés et les passages de l’antiméridien.
- [ ] Ne jamais déplacer des géométries sans signaler qu’il s’agit d’un schéma ou d’un encart.

### 8.2 France et voisins

- [ ] Situer la France dans l’Europe et identifier les pays limitrophes de métropole.
- [ ] Couvrir aussi les voisins terrestres des territoires ultramarins pertinents.
- [ ] Distinguer frontière, voisinage maritime et proximité géographique.
- [ ] Relier frontières et grands repères naturels quand la relation est exacte et utile.

## 9. Priorité 6 — paysages, régions naturelles et historiques

Ce volet vient après les repères administratifs et physiques structurants.

- [ ] Choisir une première liste de régions naturelles et historiques couramment rencontrées.
- [ ] Distinguer ces objets des régions administratives actuelles.
- [ ] Documenter les limites floues, variables ou historiques.
- [ ] Ajouter les grandes forêts comme repères de paysages.
- [x] Ajouter les cœurs des onze parcs nationaux depuis le jeu officiel du 11 février 2026.
- [ ] Distinguer parc national, parc naturel régional et autres catégories de protection.
- [ ] Évaluer séparément l’intérêt d’une extension aux parcs naturels régionaux.
- [ ] Relier les paysages aux grands ensembles physiques, sans réduire un territoire à un cliché.

Exemples de familles candidates : Beauce, Sologne, Camargue, Landes, Morvan, grandes
forêts et espaces protégés. L’appartenance à une famille et le contour retenu devront
être justifiés avant génération des cartes.

## 10. Priorité 7 — géographie humaine et organisation du territoire

### 10.1 Ports et transports

- [ ] Sélectionner les grands ports et leur façade maritime.
- [ ] Situer les principaux axes de transport et passages structurants.
- [ ] Distinguer axes schématiques et tracés géographiques précis.
- [ ] Privilégier les connexions utiles à comprendre plutôt que mémoriser tous les numéros routiers.
- [ ] Relier villes, vallées, cols, façades et grands corridors.

### 10.2 Peuplement et activités

- [ ] Définir quelques grands repères de répartition de la population.
- [ ] Ajouter les principaux espaces agricoles et industriels selon un périmètre explicite.
- [ ] Sourcer et dater les faits économiques et les éventuels classements.
- [ ] Distinguer information structurelle et statistique susceptible de devenir vite obsolète.
- [ ] Éviter les cartes dont la seule réponse est une longue liste ou un chiffre instable.

Les classements annuels, populations exactes, records anecdotiques et inventaires
très spécialisés restent des extensions facultatives, après le socle.

## 11. Qualité éditoriale et références

### Travail prioritaire sur l’existant

- [x] Relire les 18 explications hydrographiques.
- [x] Associer chaque affirmation à une référence qui la soutient réellement.
- [x] Commencer par les textes Loire, Seine et Rhône, initialement accompagnés surtout de références cartographiques.
- [x] Distinguer les références des géométries de celles des connaissances géographiques.
- [x] Retirer ou reformuler les affirmations non vérifiées.
- [ ] Vérifier noms français, articles, accents, alias et homonymes.
- [ ] Expliquer les tronçons partiels sans suggérer que leur extrémité est une source ou une embouchure.

Les petites phrases sont des résumés éditoriaux rédigés pour ce deck. Elles ne sont
ni extraites des GeoJSON ni présentées comme des citations. Une référence de tracé
ne constitue pas à elle seule une source pour tout le texte d’une carte.

### Convention à appliquer aux nouvelles séries

- [x] Prévoir des références factuelles au niveau des objets ou des relations.
- [x] Dater les faits administratifs et les sélections actuelles : COG/Etalab 2025.
- [ ] Dater les futurs faits statistiques et leurs critères de sélection.
- [x] Prévoir un état de revue éditoriale distinct de la validité technique du YAML.
- [ ] Établir une méthode pour signaler, corriger et suivre les erreurs de contenu.
- [ ] Garder les questions courtes et réserver le contexte au verso.

## 12. Évolution du modèle de données et de la génération

### Catalogues d’objets et relations

- [x] Étendre les catalogues aux régions, villes et cinq zones de relief.
- [ ] Étendre les catalogues aux sommets, lacs et repères côtiers.
- [x] Référencer département/région, ville/département et chefs-lieux par identifiants.
- [x] Ajouter les premières relations sommet/grand ensemble.
- [x] Ajouter six relations d’affluent direct ; autres affluents et débouchés à compléter.
- [x] Valider l’existence des cibles administratives et tester les correspondances avec le COG 2025.
- [ ] Étendre les contrôles de cohérence aux futures relations physiques.
- [x] Réutiliser un même objet dans plusieurs séries sans recopier ses propriétés.
- [x] Conserver la séparation entre source géographique, contenu éditorial et rendu.
- [x] Conserver les propriétés textuelles des codes et identifiants administratifs.

### Règles de génération

- [x] Ajouter les nouvelles familles de questions par règles communes.
- [x] Permettre l’activation explicite des sens utiles pour chaque série.
- [x] Étendre les lots d’apprentissage à d’autres séries quand cela apporte un bénéfice.
- [ ] Éviter de créer deux cartes équivalentes par deux chemins de génération différents.
- [ ] Produire un récapitulatif des objets, cartes et directions générées par série.
- [x] Séparer les sens effectivement activés des possibilités simplement disponibles dans le moteur.

Ne pas ajouter de compatibilité ou d’abstraction complexe avant un besoin concret.
L’existant fournit un modèle à étendre, pas une obligation de faire entrer tous les
thèmes dans la même règle.

### Identité et mises à jour

- [ ] Verrouiller les conventions d’identification avant la première publication publique.
- [ ] Garantir qu’une modification de texte, de cadrage ou de géométrie ne recrée pas la note.
- [ ] Documenter la suspension ou le retrait de cartes devenues inutiles.
- [ ] Tester une mise à jour sur une collection avec historique de révision.
- [x] Documenter séparément l’ordre du paquet, les positions déjà présentes dans Anki et l’ordre des révisions.

Les changements d’identifiants déjà autorisés pendant le développement ne doivent
pas devenir une pratique de maintenance après diffusion.

## 13. Cartographie et expérience de révision

### Lisibilité

- [ ] Vérifier les rendus sur petit écran et en mode sombre.
- [ ] Contrôler le contraste des cibles, des frontières et des repères de contexte.
- [ ] Contrôler les petites zones, îles et départements ainsi que les cibles proches d’une frontière.
- [x] Prévoir des vues communes par famille et des encarts lorsqu’ils sont nécessaires.
- [x] Distinguer les couches de contexte du thème étudié et éviter de surcharger les images.
- [x] Conserver un cadrage recto/verso identique pour une même question.
- [x] Garder les images sans textes décoratifs ; afficher réponses, explications et crédits en HTML.

### Nouvelles capacités à examiner

- [ ] Fond de relief discret pour les thèmes physiques.
- [ ] Fonds mondiaux et océaniques pour l’outre-mer.
- [ ] Représentation conventionnelle des zones approximatives et des axes schématiques.
- [ ] Repères multiples uniquement lorsque nécessaires à une relation demandée.
- [ ] Galerie filtrable par thème, vue et direction lorsque la taille du deck le justifie.
- [x] Cache de rendu persistant fondé sur les entrées effectives pour accélérer les builds répétés.

L’interactivité, les réponses cliquables et la correction automatique sont à évaluer
plus tard. Le fonctionnement de base doit rester utilisable avec les cartes Anki
classiques et les clients mobiles.

## 14. Données, licences et reproductibilité

- [x] Pour chaque nouveau jeu, documenter source, URL, version, licence et modifications.
- [x] Conserver les empreintes amont et celles des fichiers préparés.
- [x] Séparer acquisition/préparation et build ordinaire ; ne jamais télécharger les sources au build.
- [ ] Vérifier l’adéquation de l’échelle et de la précision au thème représenté.
- [ ] Conserver les scripts de préparation reproductibles et contrôler les modifications de géométrie.
- [x] Documenter les réparations de géométries et les exclusions de périmètre.
- [ ] Vérifier les obligations d’attribution, de partage de base dérivée et de redistribution des médias.
- [x] Conserver les crédits nécessaires associés aux cartes, hors des PNG lorsque possible.
- [x] Garder tous les médias référencés embarqués et nommés par leur contenu.

Sources candidates à étudier selon les lots : référentiels administratifs et codes
INSEE, contours IGN/Etalab, BD TOPAGE/Sandre, données des organismes géographiques
ou environnementaux compétents. Leur disponibilité ne vaut pas validation de licence,
de millésime ni d’adéquation au besoin.

## 15. Tests, intégration Anki et publication

### Tests automatiques à étendre selon les fonctionnalités

- [ ] Couverture des objets attendus par série et absence d’objets orphelins.
- [ ] Cohérence des noms, codes, relations et directions générées.
- [ ] Absence de réponse divulguée dans l’image ou le texte du recto.
- [ ] Fond commun cohérent et cible unique dans les séries d’identification.
- [ ] Cadrage recto/verso cohérent et comportement des vues locales/encarts.
- [ ] Stabilité des identités et ordre des lots dans le paquet.
- [ ] Absence de téléchargement pendant le build.
- [ ] Présence de tous les médias référencés, y compris après réutilisation entre cartes.
- [ ] Couverture des géométries complexes, cas ultramarins et cibles minuscules.

Les contrôles existants couvrent déjà une partie de ces propriétés. Les étendre
lorsqu’un nouveau type de données ou comportement crée un risque réel, sans ajouter
de tests qui se contentent de recopier l’implémentation.

### Validation sur les applications

- [ ] Import propre sur Anki Desktop.
- [ ] Mise à jour du même paquet sans doublon ni perte d’historique.
- [ ] Contrôle visuel sur AnkiMobile et AnkiDroid selon appareils disponibles.
- [ ] Vérification de l’ordre des nouvelles cartes avec les réglages recommandés.
- [ ] Vérification du comportement après réimport sur une collection déjà utilisée.
- [ ] Vérification de la synchronisation des médias et des liens de sources.
- [ ] Procédure explicite pour les anciennes notes de développement.

### Publication

- [ ] Définir les licences du code et du contenu éditorial, distinctes des licences des données.
- [ ] Définir le nom public, les sous-decks et la première version diffusée.
- [ ] Configurer les releases de main et les releases versionnées sur tags.
- [ ] Publier paquet, galerie ou aperçu accessible, notes de version et provenance des données.
- [ ] Documenter installation, mise à jour et signalement d’erreurs.
- [ ] Vérifier le workflow de release sur un cas réel avant de l’annoncer comme fonctionnel.

## 16. Définition de fin d’un lot

Un lot est terminé lorsque tous les points suivants sont vrais :

1. Le périmètre éditorial et les exclusions sont explicites.
2. Les données sont locales, documentées et adaptées à l’échelle de rendu.
3. Les noms, codes et faits sont vérifiés ; les limites sont expliquées.
4. Les catalogues et règles génèrent les cartes sans duplication manuelle inutile.
5. Les identités des notes existantes sont conservées.
6. Les rendus sont inspectés en galerie, avec les cas difficiles du lot.
7. Les contrôles pertinents et le build réussissent ; les médias sont embarqués.
8. Les nouveaux comportements sont vérifiés dans Anki lorsque le lot les modifie.
9. La documentation distingue clairement ce qui fonctionne et ce qui reste prévu.

## 17. Prochaine séquence concrète

### Réalisé dans la dernière séquence

- [x] Revue des 18 explications hydrographiques, avec rapport et références factuelles.
- [x] Catalogues COG 2025 des régions, chefs-lieux et relations administratives.
- [x] Génération de 148 cartes régionales et 401 cartes urbaines.
- [x] Pilote relief de cinq ensembles, dix cartes et limites approximatives explicites.
- [x] Cache persistant de rendu et références consultables dans la galerie.
- [x] 40 tests réussis, paquet de 880 cartes construit et importé ; synchronisation demandée.

### Suite du travail

- [ ] Contrôler visuellement les nouvelles séries dans Anki et vérifier leur ordre effectif.
- [ ] Terminer la documentation des cas institutionnels et des homonymes urbains.
- [x] Compléter le pilote relief par deux zones schématiques corses et armoricaines, sans les présenter comme des contours officiels.
- [x] Ajouter trois sommets repères avec sources géométriques et factuelles distinctes.
- [x] Définir et intégrer douze villes complémentaires, sans classement de population.
- [x] Intégrer quatorze cours d’eau supplémentaires, six relations, la correction de la Saône et un complément du Rhin.

La poursuite des ajouts est mise en pause à la demande de l’auteur après ce lot,
pour un commit puis une revue globale de l’architecture et de la maintenabilité.
Les validations dans les clients Anki restent ouvertes ; un build local ne les remplace pas.

## 18. Liens de référence

- [README](../README.md) : commandes et fonctionnement actuel.
- [Cartographie](CARTOGRAPHY.md) : pipeline, vues et limites des données.
- [Départements](DEPARTMENTS.md) : triangle de rappel et ordre des lots.
- [Identifiants Anki](ANKI_IDS.md) : conventions d’identité et migrations de développement.
- [Éduscol : approches de la montagne et repères géographiques](https://eduscol.education.gouv.fr/6582/la-montagne-approches-croisees) : contexte pédagogique.

Cette roadmap décrit les choix du projet ; elle ne prétend pas reproduire un
programme scolaire officiel ni proposer un inventaire exhaustif des lieux français.

## Avancement du 20 octobre 2026 — état après import

La revue hydrographique est consignée dans `docs/reviews/`. Le lot administratif
prépare les 18 régions, leurs chefs-lieux, les 101 relations départementales et les
101 points urbains à partir du COG/Etalab 2025. Les catalogues sont séparés des
règles, et les images inchangées sont réutilisées par un cache contrôlé par empreinte.
Le relief a un pilote de cinq zones ; le lot relief complet reste ouvert.
Le commit `fec1eb1` contient cet ensemble. `make build` et `make push` ont réussi
pour 880 cartes, puis la synchronisation a été demandée. La validation visuelle
exhaustive dans les clients Anki et les futures séries restent à faire.

### Reprise : sommets et cadrages urbains

Neuf cartes de sommets portent le total local à 889. Les quatre chefs-lieux de
Paris et de la petite couronne utilisent la vue francilienne, avec frontières
départementales de contexte et encart national. Les identifiants existants sont
conservés. Cette extension reste locale, sans nouvel import Anki.

Validation locale de cette reprise : 43 tests réussis, 889 fiches validées ;
aperçus du mont Blanc et de Bobigny inspectés. Contrôle sur mobile et import
de cette extension restent à faire.

## État au 21 octobre 2026 — pause pour revue

Le lot local contient 1 014 cartes : Fleuves 38, Départements 303, Régions 148,
Villes 437, Relief 26, Lacs 10, Littoral 15, Outre-mer 15 et Paysages 22.
Les 50 tests passent. Aucun import de ce lot n’est annoncé ; le dernier import
confirmé reste celui de 880 cartes. Les paragraphes datés précédents sont historiques.

La priorité demandée devient la revue de la logique, du DRY, de la préparation des
données et du coût d’ajout d’un thème. Les lots restent extensibles : basins/plaines,
cols, autres sommets, îles/caps/estuaires, territoires ultramarins hors des cinq DOM,
régions naturelles/historiques et transports ne sont pas considérés comme terminés.
Le Rhin international reste incomplet. Les schémas de relief ne sont pas des limites
physiques de référence. Les choix éditoriaux des villes ne constituent pas un palmarès.

### Priorités révisées à la demande de l’auteur

Les bassins/plaines, cols, autres sommets, caps/îles/estuaires, autres territoires
ultramarins et transports sont **différés**, sans reprise automatique. Ils restent
des idées de contenu, pas des tâches de la prochaine séquence.

La priorité porte sur la consolidation de l’existant : voir la
[revue d’architecture](reviews/ARCHITECTURE_2026-10-21.md). La compatibilité avec
Deck Manager est vérifiée localement ; le workflow de releases versionnées est préparé,
mais une publication depuis un tag reste à éprouver. Voir [DECK_MANAGER.md](DECK_MANAGER.md).
Le commit de contenu `7353175` est poussé sur `origin/main`. La revue et les ajouts
Deck Manager sont séparés du lot de contenu.

Revue globale terminée : huit constats priorisés et un ordre de consolidation dans
le rapport. Les refactorings du moteur ne sont pas encore appliqués. Les contrôles
locaux comptent désormais 57 tests, en plus du contrôle direct avec Deck Manager. Le
dépôt est public ; une release stable reste nécessaire pour installer via l’add-on.

### Publication automatique demandée ensuite

Le workflow suit maintenant le fonctionnement WSET 3 : release stable à chaque push
validé de `main`, numéro de patch incrémenté automatiquement, paquet de nom constant.
Les pull requests ne publient pas. Le premier passage distant doit être vérifié
avant d’annoncer une version téléchargeable ; suivi dans `docs/DECK_MANAGER.md`.

### Build bilingue — périmètre volontairement minimal

- [x] Publication automatique `v0.1.0` vérifiée depuis `main`.
- [x] README principal en anglais ; notes de travail historiques conservées en français.
- [x] `make build` produit deux paquets : `french-geography-en.apkg` et `french-geography-fr.apkg`.
- [x] Pilote anglais limité à la Loire, une carte ; édition française à 1 014 cartes.
- [x] Identités françaises conservées et identités anglaises séparées.
- [x] Publication adaptée pour attacher les deux fichiers à une même release.
- [x] Traduction complète des 1 014 cartes ; structure multilingue décrite dans `LOCALIZATION.md`.

Les noms de fichiers sont désormais figés. La première release mono-fichier précède
cette transition autorisée par l’auteur ; les futurs assets gardent les suffixes de langue.

### Optimisation des builds et des tests

- [x] Test bilingue limité à un échantillon fleuve/département/ville ; build complet maintenu en CI.
- [x] Tests déterministes du rendu sur quatre fleuves représentatifs, avec tests distincts des
  points, polygones troués et encarts.
- [x] Fonds projetés partagés par couche/vue pendant une génération.
- [x] Police embarquée uniquement pour les scènes contenant réellement du texte.
- [x] Vérifications d’empreinte et copies dédupliquées par média ; réparation des fichiers corrompus testée.
- [x] Cache `build/media` ajouté au workflow CI (gain distant à mesurer après exécution).

### Complete translation and shared localization architecture

- [x] 1,014 English notes covering all nine existing themes.
- [x] Shared schema for French/English, stable semantic text keys and neutral catalogues/rules.
- [x] Explicit language registry for asset names, namespaces, models and decks.
- [x] Shared generator, localized UI/templates/gallery and registry-driven publication.
- [x] Data-only third-locale fixture exercises addition of another language.
Publication of the translation and multilingual refactoring uses the existing
automatic release workflow after a successful main-branch build.

Current architecture: [LOCALIZATION.md](LOCALIZATION.md). The earlier pilot-only
translation log describes a previous step and is superseded by this completion.

### Lake map framing

- [x] Show all five lakes on the shared metropolitan France map, without local zooms or insets.
- [x] Update preparation defaults and remove the two unused lake views.

### Overseas map framing

- [x] Show the five overseas location points on one shared world map, without zooms or insets.
- [x] Align preparation defaults, localized descriptions and the existing geography check.

### Major lakes expansion

- [x] Extend from 5 to 20 metropolitan freshwater lakes/reservoirs (40 cards per language).
- [x] Pin exact Sandre codes and contours; unite Hourtin-Carcans and exclude Vassivière homonyms.
- [x] Separate lake preparation, geographic selection, editorial catalogue and localized text.
- [x] Keep a shared France view, without zooms; explain seasonal Grand-Lieu outlines.

Current total: **1,044 cards per language**. Earlier audit totals describe their dated snapshots.

### Relief map framing

- [x] Show all mountain areas and peaks on the shared France map, including Corsica, without zooms or insets.

- [x] Étendre le cadrage France sans zoom aux huit parcs nationaux métropolitains.

- [x] Planisphère commun pour toutes les cartes ultramarines : régions, départements, villes et parcs compris ; suppression des vues locales.

- [x] Retirer les dix cartes de localisation des cinq villes ultramarines et conserver les relations ville/département. Total courant : **1 034 cartes par langue**.

### Cartes SVG mutualisées

- [x] Remplacer les PNG par un SVG mutualisé ; environ 5 Mo par édition au lieu de 50 Mo.
- [x] Vérifier les dix couches et préserver textes, cadrages et identités Anki.
- [x] Vérifier import, historique, suspension et réimport avec le backend Anki.
- [x] Importer le nouveau deck avec `make push` et demander sa synchronisation.
- [x] Retirer le moteur PNG, les prototypes et les outils/rapports temporaires de migration.
- [ ] Confirmer le rendu et la synchronisation sur Android et AnkiWeb ; iOS non vérifié.

Fonctionnement et limites : [cartographie](CARTOGRAPHY.md).

### Cartographic appearance

- [x] Add a pinned, detailed European background (Natural Earth 10m, joint 250 m simplification).
- [x] Crop after projection to remove artificial interior edges, preserving shared frames.
- [x] Refine the palette and line weights; add legible white-ringed point markers.
- [x] Compress the APKG archive using standard ZIP deflate.
- [x] Keep preparation separate from offline builds and retain stable Anki identities.
