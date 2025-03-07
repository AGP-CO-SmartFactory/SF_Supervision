Para implementar la detección de ausentismos en cualquier puesto de trabajo se requiere lo siguiente:

1) identificar la cámara en cuestión a supervisar y encontrar la dirección IP asociada, en caso de ser una cámara análoga usar la dirección IP del VCR y rutear el canal asociado a la cámara.
    y abrirlo usando VLC media player mediante medio > abrirubicación de red e ingresar la url de la cámara como el ejemplo siguiente:
    - Ejemplo: "rtsp://USER:PSW@IP:PUERTO/cam/realmonitor?channel=8&subtype=#" 

2) Dibujar las zonas de detección utilizando la ejecución de la siguiente linea de código desde el root:  
    python scripts/draw_zones.py --source_path "rstpurl" --zone_configuration_path video_files/"nombre de la zona".json

3) Ejecutar el código mediante la siguiente línea de código desde el root:

    python main.py --rtsp_url "rstpurl" --zone_configuration_path video_files\"nombre de la zona".json --classes 0

    la función de ejecución tiene mas argumentos con los que variar, ejemplo:  
        rtsp_url
        zone_configuration_path
        model_id
        confidence
        iou
        classes

    sin embargo, la mayoria de estos argumentos se pueden dejar vacios y se tomarán los valores por defecto, classes = 0 es únicamente detección de personas.

4) El código enviará la información de detección a MongoDBcompass, para la ejecución de la supervisión de productividad (Gestor de producividad), se debe realizar la ejecución mediante:
    
    python main_productividad.py Reporte    
