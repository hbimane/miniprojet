# Mini projet Big Data

Ce depot fournit un pipeline simple pour l'enonce "Web Scraping, HDFS et MapReduce en Python" en utilisant le site test e-commerce de Web Scraper :

- `https://webscraper.io/test-sites/e-commerce/static`

Le pipeline fait quatre choses :

1. scrape plusieurs pages produits avec `BeautifulSoup`;
2. enregistre les donnees brutes en `JSON` et `CSV`;
3. nettoie les donnees et genere un fichier `JSONL` adapte a `MapReduce`;
4. calcule des statistiques par categorie avec un `mapper` et un `reducer`.

## Structure

- `scraper.py` : collecte les produits sur `computers/laptops`, `computers/tablets` et `phones/touch`.
- `clean_data.py` : normalise les prix, le nombre d'avis et les categories.
- `mapper.py` : emet les enregistrements par categorie.
- `reducer.py` : calcule le nombre de produits, le prix moyen et les avis moyens.
- `run_local_pipeline.py` : execute tout le pipeline en local.
- `hdfs_commands.txt` : commandes pretes pour HDFS et Hadoop Streaming.

## Installation

```powershell
python -m pip install -r requirements.txt
```

## Execution locale

```powershell
python scraper.py
python clean_data.py
python run_local_pipeline.py
```

## Fichiers generes

- `data/raw/products_raw.json`
- `data/raw/products_raw.csv`
- `data/clean/products_clean.json`
- `data/clean/products_clean.jsonl`
- `data/clean/products_clean.csv`
- `data/mapreduce/reduced.txt`

## Analyse produite

Le reducer retourne, pour chaque categorie :

- le nombre de produits ;
- le prix moyen ;
- le nombre total d'avis ;
- le nombre moyen d'avis par produit.

## HDFS

Apres generation des fichiers locaux, utilisez les commandes de `hdfs_commands.txt` pour :

- creer l'arborescence HDFS ;
- deposer les donnees brutes et nettoyees ;
- lancer Hadoop Streaming avec `mapper.py` et `reducer.py`.

## Bonus deja couverts

- scraping de plusieurs pages ;
- pretraitement des donnees ;
- pipeline automatisable localement ;
- resultats directement exploitables pour le rapport.
