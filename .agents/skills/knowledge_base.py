# 📚 Knowledge Base - Base de Conocimiento
# Este módulo maneja el acceso a la base de conocimiento (empresa, productos, FAQ) almacenada en Firestore.

from typing import Dict, List, Optional, Any
from google.cloud import firestore
from utils.logging import logger
from utils.config import (
    FIRESTORE_COLLECTION_KNOWLEDGE,
    FIRESTORE_COLLECTION_PRODUCTS,
    FIRESTORE_COLLECTION_FAQ
)

# Inicializar cliente de Firestore
firestore_client = firestore.Client()


class KnowledgeBase:
    """
    Clase para acceder a la base de conocimiento almacenada en Firestore.
    
    La base de conocimiento incluye:
    - Información de la empresa (nombre, descripción, misión, visión).
    - Lista de productos (nombre, descripción, precio, características).
    - Preguntas frecuentes (FAQ).
    """
    
    def __init__(self):
        """Inicializa la base de conocimiento."""
        logger.info("✅ KnowledgeBase inicializada.")
    
    async def get_company_info(self) -> Dict[str, Any]:
        """
        Obtiene la información de la empresa.
        
        Returns:
            dict: Información de la empresa (nombre, descripción, misión, visión).
        """
        try:
            company_ref = firestore_client.collection(FIRESTORE_COLLECTION_KNOWLEDGE).document("company")
            company_doc = company_ref.get()
            
            if company_doc.exists:
                return company_doc.to_dict()
            else:
                logger.warning("No se encontró información de la empresa en Firestore.")
                return {
                    "name": "Mi Empresa",
                    "description": "Somos una empresa dedicada a ofrecer productos y servicios de calidad.",
                    "mission": "Ofrecer soluciones innovadoras a nuestros clientes.",
                    "vision": "Ser líderes en el mercado con productos sostenibles y de alta calidad."
                }
                
        except Exception as e:
            logger.error(f"Error al obtener información de la empresa: {e}", exc_info=True)
            return {}
    
    async def get_products(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de productos.
        
        Returns:
            list: Lista de productos (cada producto es un dict con nombre, descripción, precio, etc.).
        """
        try:
            products_ref = firestore_client.collection(FIRESTORE_COLLECTION_PRODUCTS)
            products = [doc.to_dict() for doc in products_ref.stream()]
            
            if not products:
                logger.warning("No se encontraron productos en Firestore.")
                return []
            
            return products
            
        except Exception as e:
            logger.error(f"Error al obtener productos: {e}", exc_info=True)
            return []
    
    async def get_product_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un producto por su nombre.
        
        Args:
            name: Nombre del producto.
        
        Returns:
            dict: Información del producto, o None si no se encuentra.
        """
        try:
            products = await self.get_products()
            for product in products:
                if product.get("name", "").lower() == name.lower():
                    return product
            return None
            
        except Exception as e:
            logger.error(f"Error al buscar producto por nombre: {e}", exc_info=True)
            return None
    
    async def get_faq(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de preguntas frecuentes (FAQ).
        
        Returns:
            list: Lista de FAQ (cada FAQ es un dict con pregunta y respuesta).
        """
        try:
            faq_ref = firestore_client.collection(FIRESTORE_COLLECTION_FAQ)
            faq = [doc.to_dict() for doc in faq_ref.stream()]
            
            if not faq:
                logger.warning("No se encontraron preguntas frecuentes en Firestore.")
                return []
            
            return faq
            
        except Exception as e:
            logger.error(f"Error al obtener FAQ: {e}", exc_info=True)
            return []
    
    async def get_knowledge_context(self) -> Dict[str, Any]:
        """
        Obtiene todo el contexto de la base de conocimiento.
        
        Returns:
            dict: Contexto completo con información de la empresa, productos y FAQ.
        """
        try:
            company_info = await self.get_company_info()
            products = await self.get_products()
            faq = await self.get_faq()
            
            return {
                "company": company_info,
                "products": products,
                "faq": faq
            }
            
        except Exception as e:
            logger.error(f"Error al obtener contexto de conocimiento: {e}", exc_info=True)
            return {"company": {}, "products": [], "faq": []}
    
    async def search_in_faq(self, question: str) -> Optional[str]:
        """
        Busca una respuesta en el FAQ para una pregunta dada.
        
        Args:
            question: Pregunta del usuario.
        
        Returns:
            str: Respuesta del FAQ, o None si no se encuentra.
        """
        try:
            faq = await self.get_faq()
            question_lower = question.lower()
            
            for item in faq:
                faq_question = item.get("question", "").lower()
                if faq_question in question_lower or question_lower in faq_question:
                    return item.get("answer")
            
            return None
            
        except Exception as e:
            logger.error(f"Error al buscar en FAQ: {e}", exc_info=True)
            return None
    
    async def get_product_recommendations(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtiene recomendaciones de productos según una categoría.
        
        Args:
            category: Categoría de productos (opcional).
        
        Returns:
            list: Lista de productos recomendados.
        """
        try:
            products = await self.get_products()
            
            if category:
                return [p for p in products if p.get("category", "").lower() == category.lower()]
            else:
                return products
                
        except Exception as e:
            logger.error(f"Error al obtener recomendaciones de productos: {e}", exc_info=True)
            return []
    
    async def update_company_info(self, company_info: Dict[str, Any]) -> bool:
        """
        Actualiza la información de la empresa.
        
        Args:
            company_info: Diccionario con la información de la empresa.
        
        Returns:
            bool: True si la actualización fue exitosa, False de lo contrario.
        """
        try:
            company_ref = firestore_client.collection(FIRESTORE_COLLECTION_KNOWLEDGE).document("company")
            company_ref.set(company_info)
            logger.info("Información de la empresa actualizada.")
            return True
            
        except Exception as e:
            logger.error(f"Error al actualizar información de la empresa: {e}", exc_info=True)
            return False
    
    async def add_product(self, product: Dict[str, Any]) -> bool:
        """
        Añade un nuevo producto a la base de conocimiento.
        
        Args:
            product: Diccionario con la información del producto.
        
        Returns:
            bool: True si el producto fue añadido, False de lo contrario.
        """
        try:
            products_ref = firestore_client.collection(FIRESTORE_COLLECTION_PRODUCTS)
            products_ref.add(product)
            logger.info(f"Producto añadido: {product.get('name')}")
            return True
            
        except Exception as e:
            logger.error(f"Error al añadir producto: {e}", exc_info=True)
            return False
    
    async def add_faq(self, question: str, answer: str) -> bool:
        """
        Añade una nueva pregunta frecuente al FAQ.
        
        Args:
            question: Pregunta.
            answer: Respuesta.
        
        Returns:
            bool: True si la FAQ fue añadida, False de lo contrario.
        """
        try:
            faq_ref = firestore_client.collection(FIRESTORE_COLLECTION_FAQ)
            faq_ref.add({"question": question, "answer": answer})
            logger.info(f"FAQ añadida: {question}")
            return True
            
        except Exception as e:
            logger.error(f"Error al añadir FAQ: {e}", exc_info=True)
            return False


# Instancia global de la base de conocimiento
knowledge_base = KnowledgeBase()
