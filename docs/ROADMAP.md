# Ultimate French Geography — roadmap

Document de référence pour la progression du contenu et du moteur.
Mise à jour : 20 octobre 2026.

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

- [x] 18 cartes d’identification de cours d’eau.
- [x] Catalogue des 101 départements, avec nom, code texte et géométrie associée.
- [x] 303 cartes départementales : nom → position, position → nom, position → numéro.
- [x] Verso des questions de numéro : nom et code, par exemple « Ain (01) ».
- [x] Ordre départemental par lots de dix : dix localisations, dix noms, dix numéros.
- [x] Autres sens du triangle implémentés, mais désactivés : nom → code, code → nom, code → position.
- [x] Vues locales ultramarines et vue francilienne avec encart métropolitain.

- [x] 148 cartes régionales et relations département → région, à partir du COG 2025.
- [x] 401 cartes urbaines : 101 chefs-lieux réutilisables et relations départementales.
- [x] Pilote de cinq grandes zones de relief, dix cartes avec limites approximatives explicites.
- [x] Trois sommets repères et neuf cartes : localisation dans les deux sens et grand ensemble associé.

Total généré : **889 notes produisant chacune une carte**. Ce nombre ne décrit pas
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
- [x] Tests automatiques : 43 tests réussis lors des dernières vérifications.
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
- [ ] Définir une sélection explicite de grandes villes complémentaires.
- [ ] Distinguer commune, agglomération et aire d’attraction dans les éventuels critères de sélection.
- [x] Documenter le point géographique retenu pour représenter chaque ville.
- [x] Générer ville → position et position → ville.
- [x] Relier les villes à leurs départements et régions.
- [ ] Distinguer clairement les villes homonymes dans les questions.

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
- [ ] Compléter les géométries pour le Massif armoricain, les reliefs corses, les bassins et les plaines.
- [x] Documenter les limites approximatives des cinq polygones Natural Earth du pilote.
- [x] Générer nom → zone et zone → nom pour les cinq ensembles du pilote.
- [ ] Étendre les cartes aux autres grands ensembles retenus.
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
- [ ] Examiner notamment Adour, Somme, Vilaine, Charente, Aude, Hérault, Var et Orne.
- [ ] Choisir une source adaptée, par exemple BD TOPAGE/Sandre après étude de sa couverture et licence.
- [ ] Vérifier la continuité des tracés, confluences, embouchures et traversées de lacs.
- [ ] Corriger ou remplacer les tronçons incomplets du Rhin et de la Saône.
- [ ] Conserver les identifiants des objets lors d’un changement de géométrie.
- [ ] Contrôler le fond commun : tous les repères de la série visibles, une seule cible surlignée.

### 6.2 Affluents et bassins

- [ ] Ajouter les principaux affluents des grands bassins, selon une sélection documentée.
- [ ] Examiner notamment Allier, Cher, Oise, Lot, Isère et Ain.
- [ ] Stocker explicitement la relation « rejoint tel cours d’eau ».
- [ ] Distinguer affluent direct, sous-affluent, bassin et débouché maritime.
- [ ] Générer rivière → cours d’eau rejoint pour les relations importantes.
- [ ] Ajouter une vue d’ensemble des grands bassins versants.
- [ ] Générer bassin → position et, si utile, fleuve → mer ou océan de débouché.
- [ ] Traiter les estuaires communs et les cas de classement ambigus par une explication sourcée.

### 6.3 Grands lacs

- [ ] Constituer une sélection de grands lacs et de quelques petits lacs repères.
- [ ] Distinguer lac naturel, retenue et étang lorsque cette distinction est pertinente.
- [ ] Ajouter nom, géométrie, territoire et relation éventuelle à un cours d’eau.
- [ ] Prévoir des vues locales avec encart pour les surfaces trop petites à l’échelle nationale.
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

- [ ] Embarquer un fond mondial local, documenté et adapté à cet usage.
- [ ] Ajouter les vues par océan et les encarts de situation mondiale.
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
- [ ] Ajouter les parcs nationaux à partir d’un référentiel daté.
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
- [ ] Ajouter les relations affluent/exutoire.
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

### Suite en cours, reprise autorisée

- [ ] Contrôler visuellement les nouvelles séries dans Anki et vérifier leur ordre effectif.
- [ ] Terminer la documentation des cas institutionnels et des homonymes urbains.
- [ ] Compléter le pilote relief : géométries adaptées pour les reliefs corses et armoricains.
- [x] Ajouter trois sommets repères avec sources géométriques et factuelles distinctes.
- [ ] Définir les grandes villes complémentaires, au-delà des seuls chefs-lieux.
- [ ] Préparer ensuite l’hydrographie enrichie : tracés incomplets et cours d’eau manquants.

La poursuite a repris à la demande de l’auteur. Les validations dans les clients
Anki restent ouvertes ; un build local ne les remplace pas.

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
