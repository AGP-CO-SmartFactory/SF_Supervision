from functions.mongo_connector import MongoConnector
import logging  # Modulo estandar para registrar eventos en un archivo o consola.
from datetime import datetime  # Capturar marcas de tiempo en los errores.
from functools import wraps  # Funciones decoradas
    

# LogManager es una clase diseñada para capturar y registrar errores de manera estructurada.
# Proporciona un decorador (@log_errors) que permite agregar trazabilidad de errores a métodos o funciones.

class LogManager:

    def __init__(self, log_file='error.log'):
        logging.basicConfig(
            filename=log_file,
            level=logging.ERROR,
            format="%(asctime)s [%(levelname)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger(__name__)

    def log_errors(self, sector="Sector Indefinido"): 
            #Si no se le da el parametro sector, tendrá valor predeterminado "Sector indefinido"
            #decorador parametrizado para registrar errores con información del sector
            def decorator(func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        #obtener información básica del error
                        class_name = args[0].__class__.__name__ if args else 'Global'
                        method_name = func.__name__
                        error_message = str(e)
                        timestamp = datetime.now()

                        #crear un diccionario para MongoDB
                        error_document = {
                            "Sector": sector,
                            "Proceso": f"{class_name}.{method_name}",
                            "Anomalia": "Se ha producido una excepción en el código",
                            "Error": error_message,
                            "FechaCreacion": datetime.now(),
                        }

                        #loguear el error en archivo
                        self.logger.error(f"{error_document}")
                        
                        self_mongo = MongoConnector()
                        MongoConnector.insert_single_document(self_mongo, error_document)

                        raise e  #Re-lanzar la excepción
                return wrapper
            return decorator
        



