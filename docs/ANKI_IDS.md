# Identité Anki

Ces valeurs sont propres au projet et permanentes :

- Namespace GUID : `ultimate-french-geography-v1`.
- Deck `Géographie française::Fleuves` : `1976423100`.
- Modèle `Géographie française — carte physique` : `1976423101`.
- GUID : `genanki.guid_for(namespace, card.id)` ; le nom du fleuve, le texte,
  la géométrie et le chemin du fichier YAML n’y participent pas.
- Modèle : `NoteId`, `Question`, `MapFront`, `Answer`, `MapBack`, `Explanation`, `Sources`.
- Une note produit une seule carte, template `Identifier`, ordinal 0.

Identifiants réservés dès cette première série :

| ID | Objet |
| --- | --- |
| `fr-geo-fleuve-loire-001` | Identification de la Loire |
| `fr-geo-fleuve-seine-001` | Identification de la Seine |

Ne jamais renommer ou réaffecter un ID diffusé. Pour mettre à jour, importer le
nouveau paquet dans la même collection sans supprimer les notes existantes.
Conserver aussi les IDs du modèle et du deck, les noms/champs du modèle et
l’ordinal du template. Un test verrouille les GUID des deux premières notes.
