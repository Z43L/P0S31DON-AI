# Estructura recomendada del proyecto SAAM
saam-system/
├── src/
│   ├── sistema/
│   │   ├── __init__.py
│   │   ├── mcp.py           # Módulo de Comprensión y Planificación
│   │   ├── met.py           # Módulo de Ejecución de Tareas
│   │   ├── sm3.py           # Sistema de Memoria de Triple Capa
│   │   └── mao.py           # Módulo de Aprendizaje y Optimización
│   ├── herramientas/
│   │   ├── __init__.py
│   │   ├── base.py          # Clase base para todas las herramientas
│   │   ├── busqueda_web.py
│   │   ├── generacion_texto.py
│   │   └── api_clients.py   # Clientes para APIs externas
│   ├── memoria/
│   │   ├── __init__.py
│   │   ├── trabajo.py       # Gestión de memoria de trabajo
│   │   ├── conocimiento.py  # Base de conocimiento y habilidades
│   │   └── episodica.py     # Memoria episódica
│   ├── aprendizaje/
│   │   ├── __init__.py
│   │   ├── analizador.py    # Análisis estadístico de episodios
│   │   └── optimizador.py   # Optimización de configuraciones
│   └── main.py              # Punto de entrada principal
├── tests/
│   ├── unit/
│   └── integration/
├── config/
│   ├── development.yaml
│   ├── production.yaml
│   └── herramientas.yaml
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
└── docs/
    └── arquitectura.md