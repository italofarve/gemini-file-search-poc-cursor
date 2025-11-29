# Documentación de Implementación - POC File Search

## Fecha de Implementación
2025-01-XX

## Resumen
Se ha implementado una Prueba de Concepto (POC) para extraer información estructurada de contratos utilizando la API de Gemini File Search. El sistema permite procesar documentos de texto y PDF, extrayendo automáticamente datos clave como fechas, tipos de contrato, empresas, contrapartes, montos, y otros datos relevantes.

## Arquitectura Implementada

### 1. Clase ContractExtractor

La clase principal `ContractExtractor` encapsula toda la lógica de procesamiento:

#### Inicialización (`__init__`)
- Carga variables de entorno desde `.env`
- Valida presencia de `GEMINI_API_KEY` (obligatorio)
- Inicializa cliente de Gemini con la API key
- Configura directorios de salida y documentos
- Establece modelo por defecto: `gemini-2.5-flash` (configurable)

#### Gestión de File Search Store (`create_file_search_store`)
- Crea un nuevo File Search Store con nombre configurable
- Implementa lógica de reutilización: si el store ya existe, lo busca y reutiliza
- Si no encuentra uno existente, crea uno nuevo con nombre único
- Maneja errores de creación/listado de stores

#### Carga de Documentos (`upload_document`)
- Valida existencia del archivo
- Sube el archivo al File Search Store usando `uploadToFileSearchStore`
- Espera a que termine la indexación (polling cada 5 segundos)
- Retorna el nombre de la operación completada

#### Extracción de Datos (`extract_contract_data`)
- Construye un prompt estructurado que solicita JSON específico
- Utiliza File Search para recuperar información contextual del documento
- Parsea la respuesta JSON del modelo
- Limpia la respuesta (elimina markdown code blocks si existen)
- Maneja errores de parsing y retorna estructura de error si falla

#### Guardado de Resultados (`save_results`)
- Genera timestamp único para cada ejecución
- Crea archivo JSON con estructura:
  - `metadata`: información de ejecución
  - `datos_extraidos`: datos extraídos del contrato
- Guarda en directorio configurable (`OUTPUT_DIR`)

#### Procesamiento Completo (`process_contract`)
- Orquesta todo el flujo:
  1. Crear/reutilizar store
  2. Subir documento
  3. Extraer datos
  4. Guardar resultados
- Retorna estructura con éxito y datos

### 2. Estructura de Datos Extraídos

El sistema extrae los siguientes campos:

```json
{
  "fecha_contrato": "YYYY-MM-DD",
  "tipo_contrato": "tipo identificado",
  "empresa": "nombre empresa principal",
  "contraparte": "nombre contraparte",
  "monto": "valor numérico",
  "moneda": "USD, EUR, etc.",
  "duracion": "duración textual",
  "fecha_inicio": "YYYY-MM-DD",
  "fecha_fin": "YYYY-MM-DD",
  "objeto_contrato": "descripción",
  "condiciones_importantes": ["array de condiciones"],
  "firmantes": ["array de nombres"],
  "ubicacion": "ubicación/jurisdicción",
  "notas_adicionales": "información adicional"
}
```

### 3. Configuración mediante Variables de Entorno

Todas las configuraciones se manejan mediante `.env`:

- **GEMINI_API_KEY**: Clave de API (obligatoria)
- **GEMINI_MODEL**: Modelo a usar (default: `gemini-2.5-flash`)
- **FILE_SEARCH_STORE_NAME**: Nombre del store
- **CHUNK_SIZE**: Tamaño de chunks (preparado para futuras versiones)
- **CHUNK_OVERLAP**: Overlap entre chunks (preparado para futuras versiones)
- **OUTPUT_DIR**: Directorio de resultados
- **DOCUMENTS_DIR**: Directorio de documentos

### 4. Manejo de Errores

El sistema implementa manejo de errores en múltiples niveles:

- **Validación de configuración**: Verifica API key al inicializar
- **Archivos no encontrados**: `FileNotFoundError` con mensaje claro
- **Errores de API**: Captura y reporta errores de Gemini
- **Errores de parsing JSON**: Retorna estructura de error con respuesta raw
- **Stores existentes**: Reutiliza stores en lugar de fallar

### 5. Flujo de Ejecución

```
1. Usuario ejecuta: python main.py documents/contrato.txt
2. ContractExtractor se inicializa
3. Se crea/reutiliza File Search Store
4. Se sube el documento al store
5. Se espera indexación (polling)
6. Se envía prompt con File Search tool
7. Se recibe y parsea respuesta JSON
8. Se guarda resultado en JSON con timestamp
9. Se muestra resumen al usuario
```

## Decisiones de Diseño

### 1. Uso de `uploadToFileSearchStore`
Se eligió este método en lugar de subir e importar por separado porque:
- Es más eficiente (una sola operación)
- Menos complejidad en el código
- Mejor para POCs rápidas

### 2. Polling para Indexación
Se implementa polling cada 5 segundos porque:
- La API no proporciona webhooks
- Es simple y efectivo para POCs
- En producción se podría optimizar con backoff exponencial

### 3. Reutilización de Stores
Se implementa lógica para reutilizar stores existentes porque:
- Evita crear múltiples stores innecesarios
- Reduce costos de almacenamiento
- Mejora la experiencia del usuario

### 4. Estructura de Resultados con Timestamp
Cada ejecución genera un archivo único porque:
- Permite historial de ejecuciones
- Facilita comparación de resultados
- No sobrescribe resultados anteriores

## Características Implementadas

✅ Extracción estructurada de datos de contratos
✅ Soporte para archivos .txt
✅ Configuración mediante .env
✅ Guardado de resultados en JSON con fecha
✅ Manejo de errores robusto
✅ Reutilización de File Search Stores
✅ Documentación completa en README.md
✅ Archivo de ejemplo de contrato para pruebas

## Características Pendientes

🔄 Soporte completo para PDF (la API lo soporta, pero se puede mejorar la validación)
🔄 Procesamiento por lotes
🔄 Interfaz web o CLI interactiva
🔄 Validación de esquemas de datos
🔄 Configuración avanzada de chunks (cuando la API lo permita)
🔄 Logging detallado
🔄 Tests unitarios

## Notas Técnicas

### Límites de la API
- Tamaño máximo por archivo: 100 MB
- Tamaño total del store según nivel de cuenta
- Recomendación: mantener stores < 20 GB

### Costos
- Embeddings en indexación: USD 0.15 por 1M tokens
- Almacenamiento: sin costo
- Embeddings en consulta: sin costo
- Tokens de documentos recuperados: se cobran como tokens de contexto

### Formatos Soportados
La API de File Search soporta múltiples formatos automáticamente:
- Texto: .txt, .md, etc.
- Documentos: .pdf, .docx, .xlsx, etc.
- Código: múltiples lenguajes
- Y muchos más según la documentación

## Próximos Pasos Sugeridos

1. **Mejora de Prompt**: Refinar el prompt para mejor precisión
2. **Validación de Datos**: Implementar validación de esquemas JSON
3. **Procesamiento por Lotes**: Procesar múltiples archivos en una ejecución
4. **Interfaz Mejorada**: CLI más interactiva o interfaz web
5. **Métricas**: Agregar métricas de precisión y tiempo de procesamiento
6. **Tests**: Implementar tests unitarios y de integración

## Referencias Utilizadas

- [Documentación Gemini File Search](https://ai.google.dev/gemini-api/docs/file-search?hl=es-419)
- API de Google Gemini (`google-genai`)

## Autor
Implementado siguiendo los patrones y guidelines de la documentación oficial de Gemini File Search API.

