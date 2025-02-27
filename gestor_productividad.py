from utils.mongo_connector import MongoConnector
import pandas as pd

class GestorProductividad():

    def __init__(self):

        # Conectar a MongoDB (ajusta la URI, base de datos y colección según corresponda)
        self_mongo = MongoConnector()
        self.coleccion = self_mongo.db["Supervision"]

    def obtener_data_mongo(self):

        cursor = self.coleccion.find()
        # Convertir el cursor a una lista de diccionarios
        data = list(cursor)

        # Convertir a DataFrame
        df = pd.DataFrame(data)

    def eliminar_id_mongo(self):

        # (Opcional) Si deseas eliminar la columna _id, puedes hacerlo:
        if '_id' in df.columns:
            df = df.drop(columns=['_id'])

        print(df.head())


    
    def ejecutar(self):

        self.obtener_data_mongo()
        self.eliminar_id_mongo()