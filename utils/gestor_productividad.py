from utils.mongo_connector import MongoConnector
import pandas as pd
from datetime import datetime, timedelta

class GestorProductividad:
    def __init__(self):
        #Conectar a MongoDB usando MongoConnector
        self.mongo_connector = MongoConnector()
        self.coleccion = self.mongo_connector.db["Supervision"]
        #Atributo para almacenar el DataFrame obtenido
        self.df = None

    def obtener_ultima_hora_completa(self):
        ahora = datetime.now()
        #Redondea la hora actual a la hora en punto (descarta minutos, segundos y microsegundos)
        hora_actual = ahora.replace(minute=0, second=0, microsecond=0)
        #La última hora completa es una hora antes de la hora actual redondeada
        ultima_hora = hora_actual - timedelta(hours=1)
        return ultima_hora

    def obtener_data_mongo(self):
        cursor = self.coleccion.find()
        #Convertir el cursor a una lista de diccionarios
        data = list(cursor)
        #Convertir a DataFrame y almacenarlo en self.df
        self.df = pd.DataFrame(data)

    def eliminar_id_mongo(self):
        #Eliminar la columna _id si existe en el DataFrame
        if self.df is not None and '_id' in self.df.columns:
            self.df = self.df.drop(columns=['_id'])
        print(self.df.head())

    def reporte_por_intervalo(self):
        """
        Genera el reporte de eficiencia para el intervalo que inicia en 'hora_inicio'
        y termina una hora después.
        """
        hora_inicio = datetime(2025, 2, 27, 13, 0, 0)
        # Asegurarse de que las columnas de fecha sean datetime
        self.df['hora_entrada'] = pd.to_datetime(self.df['hora_entrada'])
        self.df['hora_salida'] = pd.to_datetime(self.df['hora_salida'])
        
        hora_fin = hora_inicio + timedelta(hours=1)
        registros = []
        
        # Para cada evento, calcular el solapamiento con el intervalo [hora_inicio, hora_fin)
        for _, row in self.df.iterrows():
            overlap_start = max(row['hora_entrada'], hora_inicio)
            overlap_end = min(row['hora_salida'], hora_fin)
            overlap = (overlap_end - overlap_start).total_seconds()
            if overlap > 0:
                registros.append({
                    'hora': hora_inicio,  # Representa el inicio del intervalo
                    'puesto_trabajo': row['zona_id'],
                    'tiempo_en_puesto': overlap
                })
        
        df_overlap = pd.DataFrame(registros)
        if df_overlap.empty:
            print("No se encontraron eventos en el intervalo.")
            return df_overlap
        
        # Agrupar por la hora (intervalo) y zona
        reporte = df_overlap.groupby(['hora', 'puesto_trabajo'], as_index=False).agg({'tiempo_en_puesto': 'sum'})
        # Calcular la eficiencia: porcentaje de la hora (3600 segundos) ocupado
        reporte['eficiencia'] = reporte['tiempo_en_puesto'] / 3600 * 100
        return reporte


    def ejecutar(self):
        self.obtener_data_mongo()
        self.eliminar_id_mongo()
        self.obtener_ultima_hora_completa()
        reporte = self.reporte_por_intervalo()
        print("Reporte de eficiencia ultima hora:")
        print(reporte)
        return reporte
