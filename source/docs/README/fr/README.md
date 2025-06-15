<h1 align="center">
  <a href="https://www.statamcp.com"><img src="../../../img/logo_with_name.jpg" alt="logo" width="300"/></a>
</h1>

<h1 align="center">Stata-MCP</h1>

<p align="center"> Laissez les modèles de langage (LLM) vous aider à réaliser vos analyses de régression avec Stata. ✨</p>

[![en](https://img.shields.io/badge/lang-English-red.svg)](../../../../README.md)
[![cn](https://img.shields.io/badge/语言-中文-yellow.svg)](../cn/README.md)
[![fr](https://img.shields.io/badge/langue-Français-blue.svg)](README.md)
[![sp](https://img.shields.io/badge/Idioma-Español-green.svg)](../sp/README.md)
[![PyPI version](https://img.shields.io/pypi/v/stata-mcp.svg)](https://pypi.org/project/stata-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../../LICENSE)
[![Issue](https://img.shields.io/badge/Issue-report-green.svg)](https://github.com/sepinetam/stata-mcp/issues/new)

---

> Vous cherchez d'autres intégrations Stata?
>
> - Une intégration VScode ou Cursor [ici](https://github.com/hanlulong/stata-mcp). Vous êtes perdu? 💡 [Différence](../../Difference.md)
> - Utilisation de Jupyter Lab (Important: Stata 17+) [ici](https://github.com/sepinetam/Jupyter-Stata)
> - [NBER-MCP](https://github.com/sepinetam/NBER-MCP) 🔧 en cours de construction
> - [AER-MCP](https://github.com/sepinetam/AER-MCP)
> - [Econometrics-Agent](https://github.com/FromCSUZhou/Econometrics-Agent)

## 💡 Démarrage Rapide
> La configuration standard nécessite que Stata soit installé sur le chemin par défaut et que l'interface en ligne de commande de Stata (pour macOS et Linux) soit disponible.

Le fichier json de configuration standard est le suivant, vous pouvez personnaliser votre configuration en ajoutant des variables d'environnement.
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "uvx",
      "args": [
        "stata-mcp"
      ]
    }
  }
}
```

Pour des informations d'utilisation plus détaillées, consultez le [guide d'utilisation](../../Usages/Usage.md).

Et pour une utilisation avancée, visitez le [Guide avancé](../../Usages/Advanced.md)

### Prérequis
- [uv](https://github.com/astral-sh/uv) - Gestionnaire de paquets et d'environnements virtuels
- Claude, Cline, ChatWise, ou autre service LLM
- Licence Stata
- Votre clé API pour le service LLM

### Installation
Pour la nouvelle version, il n'est plus nécessaire d'installer le paquet `stata-mcp`. Utilisez simplement les commandes suivantes pour vérifier que votre ordinateur peut l'exécuter :
```bash
uvx stata-mcp --usable
uvx stata-mcp --version
```

Si vous souhaitez l'utiliser localement, vous pouvez l'installer via pip ou télécharger le code source puis le compiler.

**Installation via pip**
```bash
pip install stata-mcp
```

**Télécharger le code source et compiler**
```bash
git clone https://github.com/sepinetam/stata-mcp.git
cd stata-mcp

uv build
```
Vous trouverez ensuite le binaire `stata-mcp` compilé dans le répertoire `dist`. Vous pouvez l'utiliser directement ou l'ajouter à votre PATH.

Par exemple :
```bash
uvx /path/to/your/whl/stata_mcp-1.3.10-py3-non-any.whl  # modifiez le nom du fichier selon votre version
```

## 📝 Documentation
- Pour des informations d'utilisation plus détaillées, consultez le [guide d'utilisation](../../Usages/Usage.md).
- Utilisation avancée, visitez le [Guide avancé](../../Usages/Advanced.md)
- Quelques questions, visitez les [Questions](../../Usages/Questions.md)
- Différence avec [Stata-MCP@hanlulong](https://github.com/hanlulong/stata-mcp), visitez la [Différence](../../Difference.md)

## 💡 Questions
- [Cherry Studio 32000 wrong](../../Usages/Questions.md#cherry-studio-32000-wrong)
- [Cherry Studio 32000 error](../../Usages/Questions.md#cherry-studio-32000-error)
- [Support Windows](../../Usages/Questions.md#windows-supports)
- [Problèmes de réseau](../../Usages/Questions.md#network-errors-when-running-stata-mcp)

## 🚀 Feuille de Route
- [x] Support macOS
- [x] Support Windows
- [ ] Intégrations supplémentaires de LLM
- [ ] Optimisations de performance

## ⚠️ Avertissement
Ce projet est destiné uniquement à des fins de recherche. Je ne suis pas responsable des dommages causés par ce projet. Veuillez vous assurer que vous disposez des licences appropriées pour utiliser Stata.

Pour plus d'informations, consultez la [Déclaration](../../Rights/Statement.md).

## 🐛 Signaler des Problèmes
Si vous rencontrez des bugs ou avez des demandes de fonctionnalités, veuillez [ouvrir un ticket](https://github.com/sepinetam/stata-mcp/issues/new).

## 📄 Licence
[Licence MIT](../../../../LICENSE) et extensions

## 📚 Citation
Si vous utilisez Stata-MCP dans vos recherches, veuillez citer ce référentiel en utilisant l'un des formats suivants:

### BibTeX
```bibtex
@software{sepinetam2025stata,
  author = {Song Tan},
  title = {Stata-MCP: Let LLM help you achieve your regression analysis with Stata},
  year = {2025},
  url = {https://github.com/sepinetam/stata-mcp},
  version = {1.3.10}
}
```

### APA
```
Song Tan. (2025). Stata-MCP: Let LLM help you achieve your regression analysis with Stata (Version 1.3.10) [Computer software]. https://github.com/sepinetam/stata-mcp
```

### Chicago
```
Song Tan. 2025. "Stata-MCP: Let LLM help you achieve your regression analysis with Stata." Version 1.3.10. https://github.com/sepinetam/stata-mcp.
```

## 📬 Contact
Email : [sepinetam@gmail.com](mailto:sepinetam@gmail.com)

Ou contribuez directement en soumettant une [Pull Request](https://github.com/sepinetam/stata-mcp/pulls) ! Nous accueillons les contributions de toutes sortes, des corrections de bugs aux nouvelles fonctionnalités.

## ❤️ Remerciements
L'auteur remercie sincèrement l'équipe officielle de Stata pour son soutien et la licence Stata pour avoir autorisé le développement du test.

## ✨ Histoire des étoiles

[![Star History Chart](https://api.star-history.com/svg?repos=sepinetam/stata-mcp&type=Date)](https://www.star-history.com/#sepinetam/stata-mcp&Date)