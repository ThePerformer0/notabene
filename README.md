# NOTABENE 📚

```text
███╗   ██╗ ██████╗ ████████╗ █████╗ ██████╗ ███████╗███╗   ██╗███████╗
████╗  ██║██╔═══██╗╚══██╔══╝██╔══██╗██╔══██╗██╔════╝████╗  ██║██╔════╝
██╔██╗ ██║██║   ██║   ██║   ███████║██████╔╝█████╗  ██╔██╗ ██║█████╗  
██║╚██╗██║██║   ██║   ██║   ██╔══██║██╔══██╗██╔══╝  ██║╚██╗██║██╔══╝  
██║ ╚████║╚██████╔╝   ██║   ██║  ██║██████╔╝███████╗██║ ╚████║███████╗
╚═╝  ╚═══╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═══╝╚══════╝
                                                                    
══════════════════════════════════════════════════════════════════════
 Research Knowledge Base                    by  The Performer  ◆
══════════════════════════════════════════════════════════════════════
```

**NotaBene** est un outil CLI puissant et élégant conçu pour centraliser, organiser et exploiter vos sources académiques et web.

## ✨ Points Forts

- **Minimalisme & Performance** : Une interface CLI conçue pour la rapidité et le focus.
- **Automatisation** : Extraction intelligente des métadonnées (titre, auteurs, résumé) pour les PDFs et les pages Web.
- **Organisation Flexible** : Système de tags et de notes structurées (Idées, Arguments, Questions).
- **Prêt pour la Rédaction** : Exportation directe vers BibTeX et Markdown.
- **Confidentialité** : Tout est stocké localement sur votre machine.

## 🚀 Installation

```bash
git clone https://github.com/ThePerformer0/notabene.git
cd notabene
python -m venv venv
# Activer le venv (Windows: venv\Scripts\activate)
pip install -e .
```

## 📖 Utilisation Rapide

```bash
# Initialiser votre base
notab init

# Ajouter un article scientifique
notab add pdf journal_article.pdf

# Ajouter une source web
notab add web https://arxiv.org/abs/2301.00000

# Rechercher et voir les détails
notab search "Transformer"
notab show 1

# Exporter vos notes
notab export markdown --output memoire_notes.md
```

## 📚 Documentation

- [Guide d'utilisation Complet](docs/user_guide/usage.md)
- [Architecture Technique](docs/api/architecture.md)
- [Changelog](CHANGELOG.md)

## 🛠️ Technologies

- **Python 3.12+**
- **Click** & **Rich** (Interface CLI)
- **SQLAlchemy** & **SQLite** (Base de données)
- **pdfplumber** (Extraction PDF de haute précision)

---
*Développé par [The Performer](https://github.com/ThePerformer0)*
