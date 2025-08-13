from typing import List, Dict, Any, Optional
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.database import Database
from pymongo.collection import Collection
import logging
from config import MONGO_URI

class MongoDBService:
    """
    Servicio para interactuar con MongoDB
    Maneja conexiones y operaciones de lectura
    """
    
    def __init__(self, database_name: str):
        """
        Inicializa el servicio de MongoDB
        
        Args:
            database_name: Nombre de la base de datos
        """
        self.uri = MONGO_URI
        self.database_name = database_name
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """
        Establece conexión con MongoDB usando ServerApi
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        try:
            # Crear un nuevo cliente y conectar al servidor
            self.client = MongoClient(self.uri, server_api=ServerApi('1'))
            
            # Enviar un ping para confirmar la conexión exitosa
            self.client.admin.command('ping')
            self.database = self.client[self.database_name]
            self.logger.info(f"Pinged your deployment. You successfully connected to MongoDB: {self.database_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error al conectar a MongoDB: {str(e)}")
            return False
    
    def disconnect(self):
        """Cierra la conexión con MongoDB"""
        if self.client:
            self.client.close()
            self.logger.info("Conexión a MongoDB cerrada")
    
    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """
        Obtiene una colección específica
        
        Args:
            collection_name: Nombre de la colección
            
        Returns:
            Collection: Objeto de colección de MongoDB o None si no hay conexión
        """
        if not self.database:
            self.logger.error("No hay conexión a MongoDB")
            return None
        return self.database[collection_name]
    
    def find_all(self, collection_name: str, filter_query: Dict = None, limit: int = 0) -> List[Dict[str, Any]]:
        """
        Busca todos los documentos en una colección
        
        Args:
            collection_name: Nombre de la colección
            filter_query: Filtro de búsqueda (opcional)
            limit: Límite de resultados (0 = sin límite)
            
        Returns:
            List[Dict]: Lista de documentos encontrados
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                return []
            
            filter_query = filter_query or {}
            cursor = collection.find(filter_query)
            
            if limit > 0:
                cursor = cursor.limit(limit)
            
            documents = list(cursor)
            self.logger.info(f"Encontrados {len(documents)} documentos en {collection_name}")
            return documents
            
        except Exception as e:
            self.logger.error(f"Error al buscar documentos en {collection_name}: {str(e)}")
            return []
    
    def find_one(self, collection_name: str, filter_query: Dict) -> Optional[Dict[str, Any]]:
        """
        Busca un documento específico en una colección
        
        Args:
            collection_name: Nombre de la colección
            filter_query: Filtro de búsqueda
            
        Returns:
            Dict: Documento encontrado o None si no se encuentra
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                return None
            
            document = collection.find_one(filter_query)
            if document:
                self.logger.info(f"Documento encontrado en {collection_name}")
            else:
                self.logger.info(f"No se encontró documento en {collection_name}")
            
            return document
            
        except Exception as e:
            self.logger.error(f"Error al buscar documento en {collection_name}: {str(e)}")
            return None
    
    def find_by_id(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca un documento por su ID
        
        Args:
            collection_name: Nombre de la colección
            document_id: ID del documento
            
        Returns:
            Dict: Documento encontrado o None si no se encuentra
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                return None
            
            from bson import ObjectId
            document = collection.find_one({"_id": ObjectId(document_id)})
            
            if document:
                self.logger.info(f"Documento con ID {document_id} encontrado en {collection_name}")
            else:
                self.logger.info(f"No se encontró documento con ID {document_id} en {collection_name}")
            
            return document
            
        except Exception as e:
            self.logger.error(f"Error al buscar documento por ID en {collection_name}: {str(e)}")
            return None
    
    def count_documents(self, collection_name: str, filter_query: Dict = None) -> int:
        """
        Cuenta documentos en una colección
        
        Args:
            collection_name: Nombre de la colección
            filter_query: Filtro de búsqueda (opcional)
            
        Returns:
            int: Número de documentos
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                return 0
            
            filter_query = filter_query or {}
            count = collection.count_documents(filter_query)
            self.logger.info(f"Colección {collection_name} tiene {count} documentos")
            return count
            
        except Exception as e:
            self.logger.error(f"Error al contar documentos en {collection_name}: {str(e)}")
            return 0
    
    def aggregate(self, collection_name: str, pipeline: List[Dict]) -> List[Dict[str, Any]]:
        """
        Ejecuta un pipeline de agregación
        
        Args:
            collection_name: Nombre de la colección
            pipeline: Lista de operaciones de agregación
            
        Returns:
            List[Dict]: Resultados de la agregación
        """
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                return []
            
            results = list(collection.aggregate(pipeline))
            self.logger.info(f"Agregación ejecutada en {collection_name}, {len(results)} resultados")
            return results
            
        except Exception as e:
            self.logger.error(f"Error en agregación en {collection_name}: {str(e)}")
            return []
    
    def is_connected(self) -> bool:
        """
        Verifica si hay una conexión activa
        
        Returns:
            bool: True si está conectado, False en caso contrario
        """
        try:
            if self.client:
                self.client.admin.command('ping')
                return True
            return False
        except:
            return False 