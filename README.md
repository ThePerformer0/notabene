# NotaBene 📚

> *Nota bene* (latin) : "note bien", "remarque importante"

**NotaBene** est un outil d'aide à la recherche scientifique conçu pour centraliser, organiser et exploiter efficacement vos sources académiques et web lors de la rédaction de mémoires, thèses ou articles scientifiques.

## 🎯 Objectif

Faciliter le travail de recherche en offrant un système unifié pour :
- Gérer vos articles scientifiques (PDF) avec extraction automatique des métadonnées
- Organiser vos sources web avec traçabilité complète
- Prendre des notes structurées liées à vos sources
- Rechercher rapidement dans votre base de connaissances
- Exporter vos références vers BibTeX ou Markdown

## ✨ Fonctionnalités (MVP)

### 📄 Gestion des PDF
- Import de fichiers PDF
- Extraction automatique : titre, auteurs, résumé
- Stockage local des fichiers et métadonnées
- Notes personnelles par article

### 🌐 Gestion des sources web
- Enregistrement d'URLs avec extraction automatique des métadonnées
- Conservation du lien original pour citation
- Tags et notes personnelles
- Traçabilité complète

### 🏷️ Organisation
- Système de tags flexible
- Regroupement par thèmes/chapitres
- Liens entre sources et concepts
- Recherche multi-critères (mots-clés, tags, auteurs)

### 📝 Prise de notes
- Notes libres par source
- Marquage d'idées clés, arguments, questions
- Lien permanent entre idée et source

### 📤 Export
- Export BibTeX pour LaTeX
- Export Markdown pour documentation
- Génération de listes de sources par chapitre

## 🚀 Installation

### Prérequis
- Python 3.9 ou supérieur
- pip ou uv

### Installation en mode développement

```bash
# Cloner le repository
git clone https://github.com/ThePerformer0/notabene.git
cd notabene

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -e .

# Installer les dépendances de développement
pip install -e ".[dev]"
```

## 📖 Utilisation

NotaBene s'utilise via une interface en ligne de commande (CLI) avec deux alias disponibles : `notab` ou `nb`.

### Commandes principales

```bash
# Initialiser un nouveau projet de recherche
notab init

# Ajouter un PDF
notab add pdf /chemin/vers/article.pdf

# Ajouter une source web
notab add web https://example.com/article

# Rechercher dans vos sources
notab search "machine learning"

# Lister toutes les sources
notab list

# Ajouter une note à une source
notab note add <source-id> "Votre note ici"

# Exporter en BibTeX
notab export bibtex --output references.bib

# Afficher l'aide
notab --help
```

## 🏗️ Architecture

```
notabene/
├── cli/              # Interface en ligne de commande (Click)
├── core/             # Logique métier centrale
├── managers/         # Gestionnaires de domaine
│   ├── document_manager.py      # Gestion des PDF
│   ├── web_source_manager.py    # Gestion des sources web
│   ├── note_manager.py          # Gestion des notes
│   ├── knowledge_organizer.py   # Tags, liens, thèmes
│   └── search_engine.py         # Recherche et filtrage
├── models/           # Modèles de données (SQLAlchemy)
├── utils/            # Utilitaires (extraction, parsing)
└── data/             # Stockage local (SQLite, PDFs)
```

## 🛠️ Technologies

- **Langage** : Python 3.9+
- **CLI** : Click
- **Base de données** : SQLite + SQLAlchemy
- **Extraction PDF** : pdfplumber
- **Web scraping** : BeautifulSoup4 + requests
- **Interface** : Rich (affichage terminal)
- **Tests** : pytest
- **Qualité du code** : black, flake8, mypy

## 📋 Statut du projet

**Version actuelle** : 0.1.0 (MVP en développement)

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Avec couverture
pytest --cov=notabene --cov-report=html

# Tests spécifiques
pytest tests/unit/
pytest tests/integration/
```

## 🤝 Contribution

Ce projet est actuellement en développement actif pour un usage personnel (rédaction de mémoire). Les contributions seront bienvenues une fois le MVP stabilisé.

### Standards de code
- Formatage : Black (88 caractères)
- Linting : flake8
- Type hints : mypy
- Tests : pytest avec couverture > 80%

## 📚 Documentation

- [Guide utilisateur](docs/user_guide/) (à venir)
- [Documentation API](docs/api/) (à venir)
- [Cahier des charges MVP](MVP.md)

---

**Note** : Ce projet est en développement actif. L'API et les fonctionnalités peuvent évoluer rapidement.
