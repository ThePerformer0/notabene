# Architecture Technique NotaBene

NotaBene est conçu de manière modulaire pour séparer les responsabilités et faciliter l'extensibilité.

## 🏗️ Structure Globale

```
notabene/
├── cli/            # Interface utilisateur (Click + Rich)
├── core/           # Cœur stable (Config, Base de données)
├── managers/       # Logique métier par domaine
├── models/         # Définition des données (SQLAlchemy)
└── utils/          # Outils transversaux (Extraction, Export)
```

## 📊 Modèles de Données

Les données sont stockées dans une base **SQLite**.

- `Source` : Modèle de base pour toutes les références.
- `PDFDocument` : Étend `Source` avec des champs spécifiques aux fichiers (DOI, résumé, chemin).
- `WebSource` : Étend `Source` avec les métadonnées web (URL, domaine).
- `Note` : Annotations liées à une source avec typage (Idée, Argument, Question).
- `Tag` : Système de marquage many-to-many.

## ⚙️ Couche Manager

Chaque domaine fonctionnel a son propre manager qui encapsule la logique d'accès aux données et les règles métier :

- `DocumentManager` : Gère le cycle de vie des PDFs et l'extraction de métadonnées.
- `WebSourceManager` : Gère l'ajout et l'analyse des sources web.
- `NoteManager` : Gère les annotations.
- `KnowledgeOrganizer` : Centralise la gestion des tags et des futurs liens entre sources.
- `SearchEngine` : Implémente la recherche multicritères.

## 🔧 Utilitaires d'Extraction

L'outil utilise des bibliothèques robustes pour l'extraction :
- `pdfplumber` pour les PDFs (beaucoup plus précis sur les structures de texte que PyPDF2).
- `BeautifulSoup4` + `requests` pour le Web.

---
*NotaBene Architecture Document - Phase MVP*
