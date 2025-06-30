<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Proyecto Frontend React + Backend Python

Este es un proyecto de transporte de productos entre ciudades que utiliza:

- **Frontend**: React + TypeScript + Vite
- **Backend**: Python con métodos Simplex (Gran M y Dos Fases)
- **Integración**: API REST para conectar React con Python

## Contexto del Proyecto

El proyecto implementa un solver de problemas de transporte utilizando:
1. Método de la Gran M (`project.py`)
2. Método de Dos Fases (`dosfases.py`)

## Componentes Principales

- `TransportSolver`: Componente principal del frontend
- `ConfigurationStep`: Configuración del método y tipo de optimización
- `VariableDefinition`: Definición de variables de decisión
- `DataInput`: Entrada de costos, capacidades y demandas
- `Results`: Visualización de iteraciones y solución óptima

## Estilo de Código

- Usar TypeScript estricto
- Componentes funcionales con hooks
- Tailwind CSS para estilos
- Iconos de Lucide React
- Manejo de errores apropiado
- Comentarios en español para el contexto del negocio
