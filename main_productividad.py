from utils.gestor_productividad import GestorProductividad
import sys


def main(opcion):
        
    if opcion == 'Reporte':
        self = GestorProductividad()
        GestorProductividad.ejecutar(self)
    else:
        print("Funcion no definida")

if __name__ == "__main__":
    opcion = sys.argv[1]
    main(opcion)