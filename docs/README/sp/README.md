<h1 align="center">
  <a href="https://www.statamcp.com"><img src="../../../src/img/logo_with_name.jpg" alt="logo" width="300"></a>
</h1>

[![en](https://img.shields.io/badge/lang-English-red.svg)](../../../README.md)
[![cn](https://img.shields.io/badge/语言-中文-yellow.svg)](../cn/README.md)
[![fr](https://img.shields.io/badge/langue-Français-blue.svg)](../fr/README.md)
[![sp](https://img.shields.io/badge/Idioma-Español-green.svg)](README.md)
![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)
[![smithery badge](https://smithery.ai/badge/@SepineTam/stata-mcp)](https://smithery.ai/server/@SepineTam/stata-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../License)
[![Issue](https://img.shields.io/badge/Issue-report-green.svg)](https://github.com/sepinetam/stata-mcp/issues/new)

> Deja que LLM te ayude a realizar tu análisis de regresión con Stata.
> 
> ¡**Windows** es compatible ahora!

---

> ¿Buscando otras integraciones de Stata u otras opciones?
>
> - Una integración para VScode o Cursor [aquí](https://github.com/hanlulong/stata-mcp). ¿Confundido? 💡 [Diferencias](docs/Difference.md)
> - Uso en Jupyter Lab (Importante: Stata 17+) [aquí](https://github.com/sepinetam/Jupyter-Stata)
> - [NBER-MCP](https://github.com/sepinetam/NBER-MCP) 🔧 en construcción

## 💡 Inicio Rápido
Para información más detallada sobre el uso, visita la [guía de Uso](../../Usage.md). Si estás usando **Windows**, sigue la [guía de Uso para Windows](../../Usage_Windows.md)

### Requisitos previos
- [uv](https://github.com/astral-sh/uv) - Instalador de paquetes y gestor de entornos virtuales
- Claude, Cline, ChatWise u otro servicio LLM
- Licencia de Stata
- Tu API-KEY del LLM

### Instalación
```bash
# Clonar el repositorio
git clone https://github.com/sepinetam/stata-mcp.git
cd stata-mcp

# Copiar el ejemplo de configuración
cp example.config.py config.py

# Usando uv (recomendado)
uv run stata_mcp.py 17 se  # Ejecución de prueba con Stata 17 SE

# Configuración alternativa con pip
# python3.11 -m venv .venv
# source .venv/bin/activate
# pip install -r requirements.txt
```

**Nota:** Windows es compatible ahora. Si tienes una licencia de Stata para Windows y deseas contribuir, por favor envía un PR.

## 🔧 Configuración del Servidor MCP

### [Claude](https://claude.ai/)
```json
{
  "stata-mcp": {
    "command":"uv",
    "args":[
      "--directory",
      "/Users/yourname/path/to/repo/",
      "run",
      "stata_mcp.py",
      "17",
      "se"
    ]
  }
}
```

### [ChatWise](https://chatwise.app/)
Abre la aplicación ChatWise y navega a la pestaña de herramientas (se requiere suscripción):

```
type: stdio
ID: stata-mcp
command: uv --directory /Users/yourname/path/to/repo/ run stata_mcp.py 17 se
```

### [Cline](https://github.com/cline/cline)
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command":"uv",
      "args":[
        "--directory",
        "/Users/yourname/path/to/repo/",
        "run",
        "stata_mcp.py",
        "17",
        "se"
      ]
    }
  }
}
```

## 📝 Documentación
Para información más detallada sobre el uso, visita la [guía de Uso](../../Usage.md).

## 💡 Preguntas
- [Cherry Studio 32000 wrong](../../../docs/Questions.md#cherry-studio-32000-wrong)

## 🚀 Hoja de ruta
- [x] Soporte para macOS
- [x] Soporte para Windows
- [ ] Integraciones adicionales de LLM
- [ ] Optimizaciones de rendimiento

## ⚠️ Descargo de responsabilidad
Este proyecto es solo para fines de investigación. No soy responsable de ningún daño causado por este proyecto. Por favor, asegúrate de tener las licencias adecuadas para usar Stata.

Para más información, consulta la [Declaración](../../Statement.md).

## 🐛 Reportar problemas
Si encuentras algún error o tienes solicitudes de funciones, por favor [abre un issue](https://github.com/sepinetam/stata-mcp/issues/new).

## 📄 Licencia
[Licencia MIT](../../../License) y Extensiones

## 📚 Cita
Si utilizas Stata-MCP en tu investigación, por favor cita este repositorio utilizando uno de los siguientes formatos:

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

## 📬 Contacto
Correo electrónico: [sepinetam@gmail.com](mailto:sepinetam@gmail.com)

¡O contribuye directamente enviando un [Pull Request](https://github.com/sepinetam/stata-mcp/pulls)! Damos la bienvenida a contribuciones de todo tipo, desde correcciones de errores hasta nuevas funcionalidades.

## ✨ Historial de Estrellas

[![Star History Chart](https://api.star-history.com/svg?repos=sepinetam/stata-mcp&type=Date)](https://www.star-history.com/#sepinetam/stata-mcp&Date)
