from pymongo import MongoClient, collection, database, DESCENDING
import logging, json  # Modulo estandar para registrar eventos en un archivo o consola.
#MongoConnector es una clase que permite la conexión a servidor de NoSQL para consultar y/o
#Insertar docuemntos para el almacenamiento de log_errors.


class MongoConnector:
    def __init__(self):
        with open('data_loader\datos_mongo.json', 'r') as file:
            credentials = json.load(file)
        self.client = MongoClient(credentials["HOST"])
        self.db = self.get_database(credentials["DATABASE"])
        self.coll = self.get_collection(credentials["COLLECTION"])

    def get_database(self, db_name: str):
        return self.client[db_name]

    def get_collection(self, collection_name: str, db: database = None):
        if db is None:
            db = self.db
        return db[collection_name]

    def get_document(self, doc_filter: dict, collection: collection = None):
        if collection is None:
            collection = self.coll
        return collection.find_one(doc_filter)

    def insert_single_document(self, post: dict, collection: collection = None):
        if collection is None:
            collection = self.coll
        try:
            collection.insert_one(post)
            return True
        except Exception as e:
            logging.error(
                f"Se ha detectado el siguiente problema en MongoDB: {e}", exc_info=True
            )
            return False

    def update_document(
        self, doc_filter: dict, update: dict, collection: collection = None
    ):
        """Actualiza, a partir de un diccionario de valores, un documento en la colección especificada, con los filtros ingresados como parámetros

        Args:
            collection (collection): Colección de MongoDB y objeto de PyMongo
            doc_filter (dict): Filtros de la colección. Tienen que entregarse como un diccionario. Ej: {'color':'amarillo', 'edad': 25}
            update (dict): Valores a modificar en la colección. Se entregan como un diccionario. Ej: {'color': 'azul', 'edad': 27}

        """
        if not collection:
            collection = self.coll
        try:
            collection.update_one(doc_filter, {"$set": update})
            return True
        except Exception as e:
            logging.error(
                f"Se ha detectado el siguiente problema en MongoDB: {e}", exc_info=True
            )
            return False

    def get_last_document(self, doc_filter: dict, collection: collection = None):
        if not collection:
            collection = self.coll
        return collection.find_one(doc_filter, sort=[("_id", DESCENDING)])