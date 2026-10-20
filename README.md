# Acteurs français dans les projets européens

Application Streamlit qui présente la participation des entreprises et laboratoires français aux programmes
**Horizon 2020** et **Horizon Europe** (2014-2026), avec un classement par domaine et une comparaison
France – Allemagne sur le secteur automobile (routier, véhicule connecté et autonome, batteries).

Les données viennent de CORDIS (Commission européenne), traitées par le notebook Colab
`acteurs_FR_projets_europeens.ipynb`, qui produit un fichier Excel.

## Contenu du dépôt

| Fichier | Rôle |
|---|---|
| `app.py` | l'application |
| `requirements.txt` | les bibliothèques à installer |
| `data/*.xlsx` | l'export Excel du notebook (l'application lit le plus récent) |

## Mettre en ligne (sans rien installer)

1. Sur GitHub, créez un dépôt (par exemple `acteurs-fr-europe`), puis *Add file → Upload files* : déposez
   `app.py`, `requirements.txt`, `README.md` et le dossier `data`.
2. Sur [share.streamlit.io](https://share.streamlit.io), *Create app* → choisissez le dépôt, la branche `main`
   et le fichier `app.py` → *Deploy*.

## Mettre à jour les données

Relancez le notebook Colab, puis déposez le nouvel Excel dans `data/` sur GitHub : l'application lit le
fichier le plus récent (par ordre alphabétique, donc par date dans le nom). Vous pouvez aussi charger un
fichier ponctuellement depuis la barre latérale de l'application, sans toucher au dépôt.

## Onglets

- **Vue d'ensemble** : chiffres clés, évolution par année, comparaison avec cinq pays
- **Domaines** : part de la France et de l'Allemagne par domaine
- **France – Allemagne : automobile** : synthèse, comparaison par domaine et catégorie d'acteurs, évolution, 20 premiers acteurs de chaque pays
- **Acteurs** : liste filtrable et téléchargeable de tous les acteurs français, détail par domaine
- **Régions** : acteurs par région
- **Méthode et contrôle** : définitions, classement des laboratoires clés, échantillon de contrôle

## Limites

- Comptage par identifiant PIC : un groupe peut avoir plusieurs PIC ; les classements « Top » regroupent les principales filiales.
- Le classement par domaine repose sur des codes d'appels et des mots-clés : vérifiez l'onglet de contrôle.
- Les années 2025 et 2026 sont incomplètes.
