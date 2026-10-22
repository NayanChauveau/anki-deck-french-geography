# Migration des images — état final

Le SVG mutualisé est le seul rendu de production depuis le 22 octobre 2026.
Chaque édition comporte 1 034 cartes et pèse environ 5 Mo, contre 50 Mo auparavant.

- [x] Inventaire et référence PNG.
- [x] Prototype et choix du SVG partagé.
- [x] Optimisation des géométries sans modifier les sources.
- [x] Intégration commune au build, à la galerie et à `make push`.
- [x] Revue des dix couches : départements, régions, villes, sommets, fleuves,
  lacs, massifs, parcs, outre-mer et mers.
- [x] Contrôles Chromium/WebKit et imports dans des collections jetables.
- [x] Bascule et `make push` demandés par l’auteur ; import confirmé dans Anki.
- [x] Suppression de l’ancien moteur et des outils/rapports temporaires.
- [ ] Retour d’usage Android/AnkiWeb ; iOS non vérifié.

Les essais backend ont conservé les identités, cinq révisions et une suspension,
avec mise à jour des notes activée et import de planification désactivé. Ils ne
remplacent pas les essais visuels sur téléphone. L’auteur a demandé la bascule
avant la fin de ces essais. Aucun commit ou push Git n’a été effectué.

Le fonctionnement courant est décrit dans [CARTOGRAPHY.md](CARTOGRAPHY.md).
Les captures et mesures locales restent dans le dossier ignoré `build/review/`.
