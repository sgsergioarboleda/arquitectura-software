import logging
from typing import List, Dict, Any, Optional
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.database import Database
from pymongo.collection import Collection
from bson import ObjectId

class MongoDBService:
    """
    Servicio para interactuar con MongoDB
    Maneja conexiones y operaciones de lectura y escritura
    """
    def __init__(self, uri: str, database_name: str):
        """
        Inicializa el servicio de MongoDB
        
        Args:
            uri: URI de conexión a MongoDB
            database_name: Nombre de la base de datos
        """
        self.uri = uri
        self.database_name = database_name
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self._connected = False
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """
        Establece conexión con MongoDB usando ServerApi
        """
        try:
            if not self.uri or not self.database_name:
                raise ValueError("MongoDB URI or database name not provided")
            
            self.logger.info(f"Conectando a la base de datos: {self.database_name}")
            self.client = MongoClient(
                self.uri,
                server_api=ServerApi('1'),
                serverSelectionTimeoutMS=5000  # 5 segundos de timeout
            )
            self.database = self.client[self.database_name]
            
            # Prueba la conexión
            self.client.admin.command('ping')
            self._connected = True
            self.logger.info("Conexión a MongoDB Atlas exitosa")
            return True
        except Exception as e:
            self.logger.error(f"Error de conexión a MongoDB Atlas: {e}")
            self._connected = False
            return False

    def disconnect(self):
        """Cierra la conexión con MongoDB"""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            self._connected = False

    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """
        Obtiene una colección específica
        """
        if not self.is_connected():
            if not self.connect():
                return None
        return self.database[collection_name]

    def find_all(self, collection_name: str, filter_query: Dict = None, limit: int = 0) -> List[Dict[str, Any]]:
        """
        Busca todos los documentos en una colección
        """
        try:
            collection = self.get_collection(collection_name)
            if collection is None:
                return []
            query = filter_query if filter_query else {}
            cursor = collection.find(query)
            if limit > 0:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            self.logger.error(f"Error en find_all: {e}")
            return []

    def find_one(self, collection_name: str, filter_query: Dict) -> Optional[Dict[str, Any]]:
        """
        Busca un documento específico en una colección
        """
        try:
            collection = self.get_collection(collection_name)
            if collection is None:
                return None
            return collection.find_one(filter_query)
        except Exception as e:
            self.logger.error(f"Error en find_one: {e}")
            return None

    def find_by_id(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca un documento por su ID
        """
        try:
            collection = self.get_collection(collection_name)
            if collection is None or not ObjectId.is_valid(document_id):
                return None
            return collection.find_one({"_id": ObjectId(document_id)})
        except Exception as e:
            self.logger.error(f"Error en find_by_id: {e}")
            return None

    def find_by_id_with_validation(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca un documento por su ID con validación adicional
        """
        try:
            # Validar formato del ID
            if not ObjectId.is_valid(document_id):
                self.logger.error(f"ID inválido: {document_id}")
                return None
                
            # Buscar documento
            collection = self.get_collection(collection_name)
            if collection is None:
                self.logger.error(f"Colección no encontrada: {collection_name}")
                return None
                
            document = collection.find_one({"_id": ObjectId(document_id)})
            if not document:
                self.logger.error(f"Documento no encontrado con ID: {document_id}")
                return None
                
            return document
            
        except Exception as e:
            self.logger.error(f"Error en find_by_id_with_validation: {e}")
            return None

    def count_documents(self, collection_name: str, filter_query: Dict = None) -> int:
        """
        Cuenta documentos en una colección
        """
        try:
            collection = self.get_collection(collection_name)
            if collection is None:
                return 0
            query = filter_query if filter_query else {}
            return collection.count_documents(query)
        except Exception as e:
            self.logger.error(f"Error en count_documents: {e}")
            return 0

    def aggregate(self, collection_name: str, pipeline: List[Dict]) -> List[Dict[str, Any]]:
        """
        Ejecuta una agregación en la colección
        """
        try:
            collection = self.get_collection(collection_name)
            if collection is None:
                return []
            return list(collection.aggregate(pipeline))
        except Exception as e:
            self.logger.error(f"Error en aggregate: {e}")
            return []

    def is_valid_object_id(self, id_str: str) -> bool:
        """Verifica si un string es un ObjectId válido"""
        return ObjectId.is_valid(id_str)

    def is_connected(self) -> bool:
        """
        Verifica si la conexión está activa
        """
        return self._connected

    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Búsqueda segura por email con sanitización"""
        if not isinstance(email, str):
            return None
            
        # Sanitizar email
        email = email.lower().strip()
        if not self._is_valid_email(email):
            return None
            
        return self.find_one("usuarios", {"correo": email})

    def _is_valid_email(self, email: str) -> bool:
        """Validación de formato de email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))