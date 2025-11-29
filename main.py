"""
POC para extracción de datos de contratos usando Gemini File Search API
Extrae: fecha, tipo de contrato, empresa, contraparte y otros datos importantes
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Cargar variables de entorno
load_dotenv()

class ContractExtractor:
    """Clase para extraer información de contratos usando Gemini File Search"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.store_name = os.getenv("FILE_SEARCH_STORE_NAME", "contracts-store")
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./results"))
        self.documents_dir = Path(os.getenv("DOCUMENTS_DIR", "./documents"))
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no está configurada en .env")
        
        # Inicializar cliente de Gemini
        self.client = genai.Client(api_key=self.api_key)
        
        # Crear directorios si no existen
        self.output_dir.mkdir(exist_ok=True)
        self.documents_dir.mkdir(exist_ok=True)
        
        # File Search Store
        self.file_search_store = None
    
    def create_file_search_store(self) -> str:
        """Crea un File Search Store si no existe, o reutiliza uno existente"""
        try:
            # Intentar crear el store
            self.file_search_store = self.client.file_search_stores.create(
                config={'display_name': self.store_name}
            )
            print(f"✓ File Search Store creado: {self.file_search_store.name}")
            return self.file_search_store.name
        except Exception as e:
            # Si ya existe, intentar listar y usar el existente
            print(f"⚠ Intentando reutilizar store existente...")
            try:
                # Listar stores existentes
                stores = list(self.client.file_search_stores.list())
                for store in stores:
                    if store.display_name == self.store_name or self.store_name in store.name:
                        self.file_search_store = store
                        print(f"✓ Store existente encontrado: {store.name}")
                        return store.name
                # Si no se encontró, crear uno nuevo con nombre único
                import uuid
                unique_name = f"{self.store_name}-{uuid.uuid4().hex[:8]}"
                self.file_search_store = self.client.file_search_stores.create(
                    config={'display_name': unique_name}
                )
                print(f"✓ Nuevo store creado con nombre único: {self.file_search_store.name}")
                return self.file_search_store.name
            except Exception as list_error:
                print(f"❌ Error al listar stores: {list_error}")
                raise
    
    def upload_document(self, file_path: str) -> str:
        """Sube un documento al File Search Store"""
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        # Asegurar que el store existe
        if not self.file_search_store:
            self.create_file_search_store()
        
        print(f"📤 Subiendo archivo: {file_path_obj.name}")
        
        # Subir y importar archivo
        operation = self.client.file_search_stores.upload_to_file_search_store(
            file=str(file_path_obj),
            file_search_store_name=self.file_search_store.name,
            config={
                'display_name': file_path_obj.stem,
            }
        )
        
        # Esperar a que termine la operación
        print("⏳ Esperando a que termine la indexación...")
        while not operation.done:
            time.sleep(5)
            operation = self.client.operations.get(operation)
        
        print("✓ Archivo indexado correctamente")
        # Esperar un poco más para asegurar que el documento esté completamente disponible
        time.sleep(2)
        return operation.name
    
    def extract_contract_data(self, file_name: str) -> Dict[str, Any]:
        """Extrae información estructurada del contrato"""
        
        prompt = """Por favor, busca y analiza el documento del contrato que está en el File Search Store. 
Lee todo el contenido del contrato y extrae la siguiente información en formato JSON estructurado:

{
  "fecha_contrato": "fecha del contrato en formato YYYY-MM-DD si está disponible",
  "tipo_contrato": "tipo de contrato (ej: arrendamiento, servicios, compraventa, etc.)",
  "empresa": "nombre de la empresa principal o contratante",
  "contraparte": "nombre de la contraparte o contratista",
  "monto": "monto o valor del contrato si está disponible",
  "moneda": "moneda del monto (USD, EUR, etc.)",
  "duracion": "duración del contrato si está disponible",
  "fecha_inicio": "fecha de inicio en formato YYYY-MM-DD",
  "fecha_fin": "fecha de fin en formato YYYY-MM-DD",
  "objeto_contrato": "descripción breve del objeto del contrato",
  "condiciones_importantes": ["lista de condiciones o cláusulas importantes"],
  "firmantes": ["lista de nombres de firmantes si están disponibles"],
  "ubicacion": "ubicación o jurisdicción del contrato si está disponible",
  "notas_adicionales": "cualquier otra información relevante"
}

IMPORTANTE: Debes buscar y leer el documento completo del contrato usando File Search. 
Si no encuentras información para algún campo, usa null para valores individuales o [] para arrays.
Responde SOLO con el JSON válido, sin texto adicional antes o después."""

        print(f"🔍 Extrayendo datos del contrato: {file_name}")
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(
                                file_search_store_names=[self.file_search_store.name]
                            )
                        )
                    ]
                )
            )
            
            # Intentar parsear el JSON de la respuesta
            response_text = response.text.strip()
            
            # Limpiar la respuesta si tiene markdown code blocks
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            contract_data = json.loads(response_text)
            contract_data["archivo_procesado"] = file_name
            contract_data["fecha_procesamiento"] = datetime.now().isoformat()
            contract_data["modelo_usado"] = self.model
            
            return contract_data
            
        except json.JSONDecodeError as e:
            print(f"⚠ Error al parsear JSON: {e}")
            print(f"Respuesta recibida: {response_text[:500]}")
            return {
                "error": "Error al parsear respuesta JSON",
                "respuesta_raw": response_text[:1000],
                "archivo_procesado": file_name,
                "fecha_procesamiento": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Error al extraer datos: {e}")
            return {
                "error": str(e),
                "archivo_procesado": file_name,
                "fecha_procesamiento": datetime.now().isoformat()
            }
    
    def save_results(self, data: Dict[str, Any], file_name: str):
        """Guarda los resultados en un archivo JSON con fecha de ejecución"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"resultado_{timestamp}.json"
        
        result = {
            "metadata": {
                "fecha_ejecucion": datetime.now().isoformat(),
                "archivo_procesado": file_name,
                "modelo": self.model,
                "store_name": self.store_name
            },
            "datos_extraidos": data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados guardados en: {output_file}")
        return output_file
    
    def process_contract(self, file_path: str) -> Dict[str, Any]:
        """Procesa un contrato completo: sube, indexa y extrae datos"""
        file_path_obj = Path(file_path)
        file_name = file_path_obj.name
        
        print(f"\n{'='*60}")
        print(f"📄 Procesando contrato: {file_name}")
        print(f"{'='*60}\n")
        
        # 1. Crear store si no existe
        if not self.file_search_store:
            self.create_file_search_store()
        
        # 2. Subir documento
        self.upload_document(file_path)
        
        # 3. Extraer datos
        contract_data = self.extract_contract_data(file_name)
        
        # 4. Guardar resultados
        output_file = self.save_results(contract_data, file_name)
        
        return {
            "success": True,
            "output_file": str(output_file),
            "data": contract_data
        }


def main():
    """Función principal"""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python main.py <ruta_al_archivo>")
        print("Ejemplo: python main.py documents/contrato.txt")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        extractor = ContractExtractor()
        result = extractor.process_contract(file_path)
        
        print(f"\n{'='*60}")
        print("✅ Procesamiento completado")
        print(f"{'='*60}")
        print(f"\n📊 Datos extraídos:")
        print(json.dumps(result["data"], indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

