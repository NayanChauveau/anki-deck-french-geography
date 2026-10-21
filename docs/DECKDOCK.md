# Distribution et compatibilité Deckdock

État vérifié le 21 octobre 2026, avec le code réel de
[anki-deckdock](https://github.com/NayanChauveau/anki-deckdock), révision
`34c797fa8f6546ece8aa0a7e31f90f745ef7a38e`.

## Contrat

Deckdock suit un fichier `.apkg` dans les releases stables d’un dépôt GitHub public.
Les noms définitifs sont `french-geography-en.apkg` et `french-geography-fr.apkg`.
Chaque changement publié
utilise une nouvelle version `vX.Y.Z`. Il compare les tags, sans comparer le contenu
lorsque le tag est identique. `latest-main` et les liens vers une page de dépôt ou
vers `releases/latest` ne sont pas des liens d’installation acceptés.

Le lien d’installation aura la forme suivante, **après publication de cette version** :

```text
https://github.com/NayanChauveau/anki-deck-french-geography/releases/download/vX.Y.Z/french-geography-en.apkg
https://github.com/NayanChauveau/anki-deck-french-geography/releases/download/vX.Y.Z/french-geography-fr.apkg
```

`vX.Y.Z` est un emplacement à remplacer, pas une release disponible. Le dépôt est public. La CI est désormais configurée pour publier automatiquement
la prochaine version stable après chaque push validé sur `main`.

## Vérifié localement

- Paquet courant : 1 014 notes/cartes, neuf sous-decks, 326 médias embarqués.
- Taille : 46 143 943 octets lors du test ; inférieure à la limite par défaut
  de 536 870 912 octets de Deckdock.
- Parseur d’URL, lecture de métadonnées et reconnaissance du nom d’asset.
- Label « Géographie française », détection d’une nouvelle version et absence de
  proposition de mise à jour pour un tag inchangé.
- Rejet du tag `latest-main`.
- Téléchargement simulé du vrai paquet avec le transport injectable de l’add-on :
  taille contrôlée et contenu final identique par SHA-256.
- Les 67 tests de Deckdock passent sur cette révision.
- Import puis mise à jour d’une question dans une collection temporaire via le
  backend Anki 26.9.3 : toujours 1 014 notes/cartes, même identité, conservation d’un
  historique synthétique et de valeurs de planification de test. La collection
  personnelle de l’auteur n’a pas été touchée.

Test reproductible du contrat, avec un checkout local de l’add-on :

```sh
uv run --frozen python scripts/check_deckdock.py --deckdock /chemin/vers/anki-deckdock
```

La commande utilise le code de cet add-on et le paquet déjà construit. GitHub est
simulé, donc elle ne nécessite ni réseau ni Anki ouvert. Ce contrôle est ajouté à la
CI contre la révision épinglée. Actualiser cette révision demande de rejouer le test.

## Publication automatique sur main

Comme sur WSET 3, `.github/workflows/check.yml` teste et construit le paquet sur les
pull requests et les pushes de `main`. Sur un push de `main` uniquement, le job
`release` attend le succès de ces contrôles, récupère leur artefact et publie le
paquet exact construit depuis ce commit.

Les publications sont sérialisées. `scripts/publish_release.py` lit les tags et les
releases existants : la première version est `v0.1.0`, puis le numéro de patch du
plus grand numéro stable est incrémenté (`v0.1.9` → `v0.1.10`). Les tags non conformes,
comme `latest-main`, sont ignorés. Une erreur de lecture GitHub interrompt la
publication ; elle ne déclenche pas un retour au numéro initial.

Chaque release conserve les deux noms de fichiers définis dans
`src/french_geography/distribution.py`, avec un label propre à chaque langue.
Elle cible le SHA vérifié par la CI et devient la release stable la plus récente.
Une release existante n’est jamais remplacée. Une pull request ne publie rien.
Aucun tag manuel n’est nécessaire pour une publication normale.

La preuve de publication distante et le lien d’installation seront consignés ici
après le premier passage réussi. Le dialogue d’import de l’add-on reste distinct des
tests locaux de contrat et du backend Anki.

## Identités et mises à jour

Les GUID, IDs de modèles et IDs de decks restent ceux de `ANKI_IDS.md`. Deckdock
ouvre le dialogue d’import standard : les options d’import d’Anki restent celles de
l’utilisateur. Le test de mise à jour emploie la mise à jour des notes activée et
l’import de planification désactivé. Il ne prouve pas que toutes les combinaisons
possibles des options conservent le même comportement.

Une note absente d’un nouveau paquet n’est pas supprimée automatiquement. Les
retraits et suspensions devront suivre une politique explicite ; ne pas changer les
identifiants pour résoudre un problème de présentation ou d’ordre.

## Transition bilingue minimale

La release automatique `v0.1.0` a été publiée avec succès depuis le commit `7fd154d`.
Elle utilisait l’ancien fichier unique `french-geography.apkg`. À la demande de l’auteur,
les noms sont désormais figés avec les suffixes `-en` et `-fr` ; aucune troisième copie
n’est publiée. Si cet ancien fichier a été suivi dans Deckdock, remplacer son suivi
par le lien versionné du nouveau fichier français. Les identités des notes françaises
sont conservées : le renommage de fichier ne recrée pas les notes.

`make build` produit les deux éditions. L’anglais est un pilote explicite d’une seule
carte Loire ; le français reste à 1 014 cartes. Les deux paquets ont des identités
isolées. Le contrôle Deckdock teste les deux assets et la publication refuse un lot
auquel manquerait une édition. La traduction complète n’a pas été entreprise.
