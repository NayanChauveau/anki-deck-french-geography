# Distribution et compatibilité Deckdock

État vérifié le 21 octobre 2026, avec le code réel de
[anki-deckdock](https://github.com/NayanChauveau/anki-deckdock), révision
`34c797fa8f6546ece8aa0a7e31f90f745ef7a38e`.

## Contrat

Deckdock suit un fichier `.apkg` dans les releases stables d’un dépôt GitHub public.
Le nom du fichier doit rester `french-geography.apkg`, et chaque changement publié
utilise une nouvelle version `vX.Y.Z`. Il compare les tags, sans comparer le contenu
lorsque le tag est identique. `latest-main` et les liens vers une page de dépôt ou
vers `releases/latest` ne sont pas des liens d’installation acceptés.

Le lien d’installation aura la forme suivante, **après publication de cette version** :

```text
https://github.com/NayanChauveau/anki-deck-french-geography/releases/download/vX.Y.Z/french-geography.apkg
```

`vX.Y.Z` est un emplacement à remplacer, pas une release disponible. La vérification
n’a créé ni tag ni release. Le dépôt est public et `main` est poussé. Ce push ne publie pas de release.

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

## Workflow de publication préparé

`.github/workflows/release.yml` se déclenche sur les tags `v*`, exige précisément
`vX.Y.Z`, puis réutilise les contrôles de `check.yml`. Ceux-ci construisent le paquet,
la galerie et exercent le contrat Deckdock. Le job de publication récupère l’artefact
et crée une nouvelle release stable, avec le fichier de nom constant et son label.
Il ne remplace pas une release déjà existante.

Le workflow est configuré et contrôlé localement. Sa publication complète depuis
un tag, le téléchargement distant et le dialogue d’import de Deckdock ne sont pas
encore éprouvés sur une release réelle. Ne pas annoncer un lien de téléchargement
fonctionnel tant que cette étape n’a pas eu lieu.

## Identités et mises à jour

Les GUID, IDs de modèles et IDs de decks restent ceux de `ANKI_IDS.md`. Deckdock
ouvre le dialogue d’import standard : les options d’import d’Anki restent celles de
l’utilisateur. Le test de mise à jour emploie la mise à jour des notes activée et
l’import de planification désactivé. Il ne prouve pas que toutes les combinaisons
possibles des options conservent le même comportement.

Une note absente d’un nouveau paquet n’est pas supprimée automatiquement. Les
retraits et suspensions devront suivre une politique explicite ; ne pas changer les
identifiants pour résoudre un problème de présentation ou d’ordre.
