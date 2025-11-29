# Inicio Rápido - POC File Search

## Pasos para comenzar

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto (puedes copiar de `env_template.txt`):

```bash
# Opción 1: Copiar template
cp env_template.txt .env

# Opción 2: Crear manualmente
touch .env
```

Edita `.env` y agrega tu API key:

```env
GEMINI_API_KEY=tu_api_key_aqui
GEMINI_MODEL=gemini-2.5-flash
FILE_SEARCH_STORE_NAME=contracts-store
OUTPUT_DIR=./results
DOCUMENTS_DIR=./documents
```

**⚠️ IMPORTANTE**: Necesitas obtener tu API key de [Google AI Studio](https://makersuite.google.com/app/apikey)

### 3. Probar con el ejemplo

```bash
python main.py documents/ejemplo_contrato.txt
```

### 4. Procesar tu propio contrato

Coloca tu archivo en `documents/` y ejecuta:

```bash
python main.py documents/tu_contrato.txt
```

## Resultados

Los resultados se guardan automáticamente en `results/resultado_YYYYMMDD_HHMMSS.json`

Cada archivo contiene:
- Metadata de la ejecución
- Datos extraídos del contrato en formato JSON estructurado

## Solución de Problemas

### Error: "GEMINI_API_KEY no está configurada"
- Verifica que el archivo `.env` existe
- Verifica que tiene la variable `GEMINI_API_KEY=tu_key`

### Error: "Archivo no encontrado"
- Verifica que la ruta al archivo es correcta
- Usa rutas relativas desde la raíz del proyecto

### Error al crear store
- El sistema intentará reutilizar stores existentes automáticamente
- Si persiste, verifica tu API key y permisos

## Próximos Pasos

- Lee `README.md` para documentación completa
- Lee `IMPLEMENTACION.md` para detalles técnicos
- Personaliza el prompt en `main.py` según tus necesidades

