<h1 align="center">
  <a href="https://www.statamcp.com"><img src="../../../src/img/logo_with_name.jpg" alt="logo" width="300"/></a>
</h1>

[![en](https://img.shields.io/badge/lang-English-red.svg)](../../../README.md)
[![cn](https://img.shields.io/badge/语言-中文-yellow.svg)](../cn/README.md)
[![fr](https://img.shields.io/badge/langue-Français-blue.svg)](README.md)
[![sp](https://img.shields.io/badge/Idioma-Español-green.svg)](../sp/README.md)
![Version](https://img.shields.io/badge/version-1.2.2-blue.svg)
[![smithery badge](https://smithery.ai/badge/@SepineTam/stata-mcp)](https://smithery.ai/server/@SepineTam/stata-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../License)
[![Issue](https://img.shields.io/badge/Issue-report-green.svg)](https://github.com/sepinetam/stata-mcp/issues/new)


> Laissez les modèles de langage (LLM) vous aider à réaliser vos analyses de régression avec Stata.
> 
> **Windows** est désormais pris en charge!

---

> Vous cherchez d'autres intégrations Stata?
>
> - Une intégration VScode ou Cursor [ici](https://github.com/hanlulong/stata-mcp). Vous êtes perdu? 💡 [Différence](docs/Difference.md)
> - Utilisation de Jupyter Lab (Important: Stata 17+) [ici](https://github.com/sepinetam/Jupyter-Stata)
> - [NBER-MCP](https://github.com/sepinetam/NBER-MCP) 🔧 en cours de construction

## 💡 Démarrage Rapide
Pour des informations d'utilisation plus détaillées, consultez le [guide d'utilisation](../../Usage.md).

### Prérequis
- [uv](https://github.com/astral-sh/uv) - Gestionnaire de paquets et d'environnements virtuels
- Claude, Cline, ChatWise, ou autre service LLM
- Licence Stata
- Votre clé API pour le service LLM

### Installation
```bash
# Cloner le dépôt
git clone https://github.com/sepinetam/stata-mcp.git
cd stata-mcp

# Copier le fichier de configuration exemple
cp example.config.py config.py

# Utilisation avec uv (recommandé)
uv run stata_mcp.py 17 se  # Test avec Stata 17 SE

# Configuration alternative avec pip
# python3.11 -m venv .venv
# source .venv/bin/activate
# pip install -r requirements.txt
```

**Remarque :** La compatibilité Windows n'est pas disponible actuellement. Si vous possédez une licence Stata pour Windows et souhaitez contribuer, veuillez soumettre une PR.

## 🔧 Configuration du Serveur MCP

### [Claude](https://claude.ai/)
```json
{
  "stata-mcp": {
    "command":"uv",
    "args":[
      "--directory",
      "/Users/votrenom/chemin/vers/repo/",
      "run",
      "stata_mcp.py",
      "17",
      "se"
    ]
  }
}
```

### [ChatWise](https://chatwise.app/)
Ouvrez l'application ChatWise et accédez à l'onglet outils (abonnement requis) :

```
type: stdio
ID: stata-mcp
command: uv --directory /Users/votrenom/chemin/vers/repo/ run stata_mcp.py 17 se
```

### [Cline](https://github.com/cline/cline)
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command":"uv",
      "args":[
        "--directory",
        "/Users/votrenom/chemin/vers/repo/",
        "run",
        "stata_mcp.py",
        "17",
        "se"
      ]
    }
  }
}
```

## 📝 Documentation
Pour des informations d'utilisation plus détaillées, consultez le [guide d'utilisation](../../Usage.md).

## 🚀 Feuille de Route
- [x] Support macOS
- [ ] Support Windows
- [ ] Intégrations supplémentaires de LLM
- [ ] Optimisations de performance

## 💡 Questions
- [Cherry Studio 32000 wrong](../../../docs/Questions.md#cherry-studio-32000-wrong)

## ⚠️ Avertissement
Ce projet est destiné uniquement à des fins de recherche. Je ne suis pas responsable des dommages causés par ce projet. Veuillez vous assurer que vous disposez des licences appropriées pour utiliser Stata.

Pour plus d'informations, consultez la [Déclaration](../../Statement.md).

## 🐛 Signaler des Problèmes
Si vous rencontrez des bugs ou avez des demandes de fonctionnalités, veuillez [ouvrir un ticket](https://github.com/sepinetam/stata-mcp/issues/new).

## 📄 Licence
[Licence MIT](../../../License) et extensions

## 📚 Citation
Si vous utilisez Stata-MCP dans vos recherches, veuillez citer ce référentiel en utilisant l'un des formats suivants:

### BibTeX
```bibtex
@software{sepinetam2025stata,
  author = {Song Tan},
  title = {Stata-MCP: Let LLM help you achieve your regression analysis with Stata},
  year = {2025},
  url = {https://github.com/sepinetam/stata-mcp},
  version = {1.0.3}
}
```

### APA
```
Song Tan. (2025). Stata-MCP: Let LLM help you achieve your regression analysis with Stata (Version 1.0.3) [Computer software]. https://github.com/sepinetam/stata-mcp
```

### Chicago
```
Song Tan. 2025. "Stata-MCP: Let LLM help you achieve your regression analysis with Stata." Version 1.0.3. https://github.com/sepinetam/stata-mcp.
```

## 📬 Contact
Email : [sepinetam@gmail.com](mailto:sepinetam@gmail.com)

Ou contribuez directement en soumettant une [Pull Request](https://github.com/sepinetam/stata-mcp/pulls) ! Nous accueillons les contributions de toutes sortes, des corrections de bugs aux nouvelles fonctionnalités.

## ✨ Histoire des étoiles

[![Star History Chart](https://api.star-history.com/svg?repos=sepinetam/stata-mcp&type=Date)](https://www.star-history.com/#sepinetam/stata-mcp&Date)
