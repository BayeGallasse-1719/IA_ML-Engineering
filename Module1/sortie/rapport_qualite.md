# Rapport qualité — ImmoAnalyse

Généré le : 2026-10-27 20:44

## Synthèse

- Enregistrements analysés : **3184**
- Conservés conformes : **2930** (92.0% du total si total non nul)
- Conservés avec avertissement : **67**
- Mis en quarantaine : **187**
- Doublons exacts signalés : **14**
- Enregistrements impliqués dans un doublon probable : **0**

## Résultats par source

| source             |   enregistrements |   quarantaine |   avertissements |   conformes |
|:-------------------|------------------:|--------------:|-----------------:|------------:|
| agence_teranga     |               640 |             9 |               11 |         620 |
| import_historique  |               528 |            10 |                0 |         518 |
| notaires           |               410 |            20 |                0 |         390 |
| particuliers       |               731 |           136 |               20 |         575 |
| plateforme_immo_sn |               875 |            12 |               36 |         827 |

## Valeurs manquantes (schéma canonique)

|             |   valeurs_manquantes |
|:------------|---------------------:|
| description |                 2474 |
| quartier    |                 2309 |
| transaction |                  640 |
| sdb         |                  410 |
| prix_fcfa   |                   93 |
| surface_m2  |                   84 |
| ville       |                    8 |
| date        |                    6 |
| id_source   |                    0 |
| source      |                    0 |
| region      |                    0 |
| type_bien   |                    0 |
| pieces      |                    0 |
| statut      |                    0 |

## Échecs de conversion

|            |   échecs |
|:-----------|---------:|
| prix_fcfa  |        8 |
| surface_m2 |        4 |
| pieces     |        0 |
| sdb        |        0 |

## Méthode et limites

- Les fichiers bruts ne sont jamais modifiés.
- Les corrections de format (espaces, casse, dates et nombres) sont appliquées de façon déterministe.
- Les valeurs atypiques sont conservées avec avertissement ; elles ne sont pas supprimées automatiquement.
- Les villes/régions incompatibles avec le référentiel sont signalées sans correction automatique.
- Les doublons exacts sont signalés ; les doublons probables sont des candidats inter-sources selon ville, type, surface (±2 %), prix (±3 %) et date (±30 jours). Aucun rapprochement probabiliste n'est fusionné automatiquement.
- Le champ transaction peut être absent lorsque la source ne l'indique pas.
- Les données sont synthétiques et ne représentent pas des transactions immobilières réelles.
