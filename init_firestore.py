# 🔥 Script de Inicialización de Firestore
# Este script carga la base de conocimiento inicial en Firestore desde config.yaml.

import yaml
from pathlib import Path
from google.cloud import firestore
from typing import Dict, List, Any
import argparse

# Cargar configuración desde config.yaml
CONFIG_PATH = Path(__file__).parent / "config.yaml"

try:
    with open(CONFIG_PATH, "r") as f:
        config: Dict[str, Any] = yaml.safe_load(f)
except FileNotFoundError:
    print(f"❌ Error: No se encontró el archivo de configuración en {CONFIG_PATH}")
    exit(1)
except yaml.YAMLError as e:
    print(f"❌ Error al cargar config.yaml: {e}")
    exit(1)

# Inicializar cliente de Firestore
firestore_client = firestore.Client()


def init_knowledge_base():
    """
    Inicializa la base de conocimiento en Firestore con los datos de config.yaml.
    """
    print("🔥 Inicializando base de conocimiento en Firestore...")
    
    # Cargar datos de config.yaml
    knowledge_base_config = config.get("knowledge_base", {})
    company_info = knowledge_base_config.get("company", {})
    products = knowledge_base_config.get("products", [])
    faq = knowledge_base_config.get("faq", [])
    
    # Guardar información de la empresa
    if company_info:
        company_ref = firestore_client.collection(
            config["gcp"]["firestore"]["collections"]["knowledge_base"]
        ).document("company")
        company_ref.set(company_info)
        print(f"✅ Información de la empresa guardada: {company_info.get('name')}")
    
    # Guardar productos
    if products:
        products_ref = firestore_client.collection(
            config["gcp"]["firestore"]["collections"]["products"]
        )
        for product in products:
            products_ref.add(product)
            print(f"✅ Producto guardado: {product.get('name')}")
    
    # Guardar FAQ
    if faq:
        faq_ref = firestore_client.collection(
            config["gcp"]["firestore"]["collections"]["faq"]
        )
        for item in faq:
            faq_ref.add(item)
            print(f"✅ FAQ guardada: {item.get('question')}")
    
    print("🎉 Base de conocimiento inicializada correctamente.")


def clear_collections():
    """
    Elimina todos los documentos de las colecciones de Firestore.
    ⚠️ ADVERTENCIA: Esto eliminará todos los datos existentes.
    """
    print("⚠️  ¿Estás seguro de que quieres eliminar todos los datos de Firestore? (s/n)")
    confirm = input().strip().lower()
    
    if confirm != "s":
        print("❌ Operación cancelada.")
        return
    
    collections = [
        "knowledge_base",
        "products", 
        "faq",
        "chat_sessions",
        "response_cache",
        "token_usage",
        "complaints"
    ]
    
    for collection_name in collections:
        try:
            collection_ref = firestore_client.collection(collection_name)
            docs = collection_ref.stream()
            
            deleted_count = 0
            for doc in docs:
                doc.reference.delete()
                deleted_count += 1
            
            print(f"✅ Colección '{collection_name}': {deleted_count} documentos eliminados.")
        except Exception as e:
            print(f"❌ Error al eliminar colección '{collection_name}': {e}")
    
    print("🎉 Todas las colecciones han sido limpiadas.")


def list_collections():
    """
    Lista todas las colecciones y documentos en Firestore.
    """
    print("📋 Listando colecciones en Firestore...")
    
    collections = firestore_client.collections()
    for collection in collections:
        print(f"\n📁 Colección: {collection.id}")
        docs = collection.stream()
        for doc in docs:
            print(f"  - 📄 Documento: {doc.id}")


def main():
    """
    Función principal del script.
    """
    parser = argparse.ArgumentParser(
        description="Script de inicialización de Firestore para el Agente de WhatsApp"
    )
    parser.add_argument(
        "--init", 
        action="store_true",
        help="Inicializar base de conocimiento desde config.yaml"
    )
    parser.add_argument(
        "--clear",
        action="store_true", 
        help="Eliminar todos los datos de Firestore (¡PELIGRO!)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Listar todas las colecciones y documentos"
    )
    
    args = parser.parse_args()
    
    if args.init:
        init_knowledge_base()
    elif args.clear:
        clear_collections()
    elif args.list:
        list_collections()
    else:
        print("📌 Uso:")
        print("  python init_firestore.py --init    # Inicializar base de conocimiento")
        print("  python init_firestore.py --clear   # Eliminar todos los datos")
        print("  python init_firestore.py --list    # Listar colecciones")


if __name__ == "__main__":
    main()
