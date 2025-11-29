# POC: Extracción de Datos de Contratos con Gemini File Search

## Descripción

Esta es una Prueba de Concepto (POC) que utiliza la API de Gemini File Search para extraer información estructurada de contratos. El sistema puede procesar documentos de texto (.txt) y PDF, identificando automáticamente:

- **Fecha del contrato**
- **Tipo de contrato** (arrendamiento, servicios, compraventa, etc.)
- **Empresa** (contratante principal)
- **Contraparte** (contratista)
- **Monto y moneda**
- **Duración del contrato**
- **Fechas de inicio y fin**
- **Objeto del contrato**
- **Condiciones importantes**
- **Firmantes**
- **Ubicación/jurisdicción**
- **Notas adicionales**

## Arquitectura

### Componentes Principales

1. **ContractExtractor**: Clase principal que maneja:
   - Creación y gestión del File Search Store
   - Carga de documentos al store
   - Extracción de datos usando prompts estructurados
   - Guardado de resultados en JSON

2. **File Search Store**: Almacén de Gemini que:
   - Indexa automáticamente los documentos
   - Divide en chunks para búsqueda eficiente
   - Permite recuperación contextual de información

3. **Sistema de Resultados**: Guarda cada ejecución en:
   - Archivos JSON con timestamp: `resultado_YYYYMMDD_HHMMSS.json`
   - Incluye metadata completa de la ejecución

## Configuración

### 1. Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configuración de Variables de Entorno

Copia el archivo `.env.example` a `.env` y configura:

```bash
cp .env.example .env
```

Edita `.env` con tus valores:

```env
# Gemini API Configuration
GEMINI_API_KEY=tu_api_key_aqui
GEMINI_MODEL=gemini-2.5-flash

# File Search Configuration
FILE_SEARCH_STORE_NAME=contracts-store
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Processing Configuration
OUTPUT_DIR=./results
DOCUMENTS_DIR=./documents
```

### Variables de Entorno

- **GEMINI_API_KEY**: Tu clave de API de Google Gemini (obligatorio)
- **GEMINI_MODEL**: Modelo a usar (default: `gemini-2.5-flash`)
- **FILE_SEARCH_STORE_NAME**: Nombre del store de File Search
- **CHUNK_SIZE**: Tamaño de chunks para indexación (configurable para futuras versiones)
- **CHUNK_OVERLAP**: Overlap entre chunks (configurable para futuras versiones)
- **OUTPUT_DIR**: Directorio donde se guardan los resultados
- **DOCUMENTS_DIR**: Directorio donde se colocan los documentos a procesar

## Uso

### Procesar un Contrato

```bash
python main.py <ruta_al_archivo>
```

**Ejemplos:**

```bash
# Procesar un archivo de texto
python main.py documents/contrato.txt

# Procesar un PDF (cuando esté implementado)
python main.py documents/contrato.pdf
```

### Flujo de Ejecución

1. **Inicialización**: Crea el cliente de Gemini y verifica configuración
2. **Creación de Store**: Crea un File Search Store si no existe
3. **Carga de Documento**: Sube el archivo al store y espera indexación
4. **Extracción**: Usa File Search para extraer datos estructurados
5. **Guardado**: Almacena resultados en JSON con timestamp

## Estructura de Resultados

Los resultados se guardan en `results/resultado_YYYYMMDD_HHMMSS.json` con la siguiente estructura:

```json
{
  "metadata": {
    "fecha_ejecucion": "2025-01-XX...",
    "archivo_procesado": "contrato.txt",
    "modelo": "gemini-2.5-flash",
    "store_name": "contracts-store"
  },
  "datos_extraidos": {
    "fecha_contrato": "2024-01-15",
    "tipo_contrato": "arrendamiento",
    "empresa": "Empresa ABC S.A.",
    "contraparte": "Inmobiliaria XYZ",
    "monto": "5000",
    "moneda": "USD",
    "duracion": "12 meses",
    "fecha_inicio": "2024-01-15",
    "fecha_fin": "2025-01-15",
    "objeto_contrato": "Arrendamiento de oficina",
    "condiciones_importantes": ["...", "..."],
    "firmantes": ["Juan Pérez", "María García"],
    "ubicacion": "Madrid, España",
    "notas_adicionales": "..."
  }
}
```

## Características Técnicas

### File Search API

- **Modelo**: Gemini 2.5 Flash (configurable)
- **Indexación Automática**: Los documentos se dividen y indexan automáticamente
- **Búsqueda Contextual**: File Search recupera información relevante según el prompt
- **Soporte de Formatos**: 
  - Texto plano (.txt) ✅
  - PDF (próximamente) 🔄

### Parámetros de Chunks

Actualmente, Gemini File Search maneja automáticamente la división en chunks. Los parámetros `CHUNK_SIZE` y `CHUNK_OVERLAP` están configurados para futuras personalizaciones cuando la API lo permita.

### Límites de la API

Según la documentación de Gemini:
- **Tamaño máximo por archivo**: 100 MB
- **Tamaño total del store** (según nivel):
  - Gratuito: 1 GB
  - Nivel 1: 10 GB
  - Nivel 2: 100 GB
  - Nivel 3: 1 TB
- **Recomendación**: Mantener stores < 20 GB para óptima latencia

## Estructura del Proyecto

```
file-search-cursor/
├── .env                    # Variables de entorno (no commitear)
├── .env.example            # Template de variables de entorno
├── .gitignore
├── requirements.txt        # Dependencias Python
├── main.py                 # Código principal
├── README.md               # Esta documentación
├── documents/              # Directorio para documentos a procesar
│   └── .gitkeep
└── results/                # Directorio para resultados JSON
    └── resultado_*.json
```

## Próximas Mejoras

- [ ] Soporte completo para PDF
- [ ] Procesamiento por lotes de múltiples archivos
- [ ] Interfaz web o CLI más interactiva
- [ ] Validación de esquemas de datos extraídos
- [ ] Configuración avanzada de chunks cuando esté disponible
- [ ] Manejo de errores más robusto
- [ ] Logging detallado
- [ ] Tests unitarios

## Notas de Implementación

### Decisión de Diseño: File Search vs. Upload Directo

Se eligió usar `uploadToFileSearchStore` en lugar de subir e importar por separado porque:
- Es más eficiente (una sola operación)
- Menos complejidad en el código
- Mejor para POCs rápidas

### Prompt de Extracción

El prompt está diseñado para:
- Solicitar JSON estructurado específico
- Incluir todos los campos relevantes para contratos
- Ser claro y específico para minimizar errores de parsing

### Manejo de Errores

El sistema maneja:
- Archivos no encontrados
- Errores de API
- Errores de parsing JSON
- Stores ya existentes

## Referencias

- [Documentación de Gemini File Search](https://ai.google.dev/gemini-api/docs/file-search?hl=es-419)
- [API de Gemini](https://ai.google.dev/)

## Licencia

Este es un proyecto de prueba de concepto para uso interno.

