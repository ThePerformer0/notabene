# NotaBene - Guide d'utilisation

Bienvenue dans **NotaBene**, votre assistant personnel pour la recherche scientifique.

## 🚀 Démarrage Rapide

### 1. Initialisation
Avant de commencer, initialisez votre environnement de recherche :
```bash
notab init
```
Ceci créera le dossier `.notabene` dans votre dossier utilisateur avec la base de données et le dossier de stockage des PDFs.

### 2. Ajouter des sources

#### Ajouter un document PDF
NotaBene copie le fichier dans son stockage interne et tente d'extraire automatiquement le titre, les auteurs et le résumé.
```bash
notab add pdf /chemin/vers/article.pdf
```

#### Ajouter une source Web
NotaBene récupère le titre et les métadonnées de la page.
```bash
notab add web https://site-web.com/article
```

## 📖 Gestion du Savoir

### Lister vos sources
Affichez toutes vos sources enregistrées :
```bash
notab list
```
Vous pouvez filtrer par type : `notab list --type pdf` ou `notab list --type web`.

### Voir les détails
Pour voir toutes les informations d'une source (incluant notes et tags) :
```bash
notab show <id>
```

### Rechercher
Utilisez la recherche textuelle pour retrouver une source :
```bash
notab search "intelligence artificielle"
```

## 📝 Annotations et Tags

### Ajouter une note
Idéal pour capturer des idées ou des citations :
```bash
notab note add <id> "Contenu de la note" --type idea
```
Types disponibles : `idea`, `argument`, `question`.

### Ajouter un tag
Organisez vos sources par thématiques :
```bash
notab tag add <id> recherche
```

## 📤 Exportation

NotaBene vous aide à passer du stockage à la rédaction.

### Export BibTeX
Pour vos projets LaTeX :
```bash
notab export bibtex --output references.bib
```

### Export Markdown
Générez un fichier récapitulatif de toutes vos notes par source :
```bash
notab export markdown --output notes_recherche.md
```

---
*NotaBene - Développé avec passion par The Performer*
