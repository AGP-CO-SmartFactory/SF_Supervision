from data_loader.importer import *

def fps_monitor_call(self) -> float:
    return self.fps

sv.FPSMonitor.__call__ = fps_monitor_call

COLORS = sv.ColorPalette.from_hex(["#E6194B", "#3CB44B", "#FFE119", "#3C76D1"])
COLOR_ANNOTATOR = sv.ColorAnnotator(color=COLORS)
LABEL_ANNOTATOR = sv.LabelAnnotator(
    color=COLORS, text_color=sv.Color.from_hex("#000000")
)


class CustomSink:
    def __init__(self, zone_configuration_path: str, classes: List[int]):
        self.classes = classes
        self.tracker = sv.ByteTrack(minimum_matching_threshold=0.5)
        self.fps_monitor = sv.FPSMonitor()
        self.polygons = load_zones_config(file_path=zone_configuration_path)
        self.timers = [ClockBasedTimer() for _ in self.polygons]
        self.zones = [
            sv.PolygonZone(
                polygon=polygon,
                triggering_anchors=(sv.Position.CENTER,),
            )
            for polygon in self.polygons
        ]
        # Diccionario para detecciones activas: por cada zona se registra el tracker_id y su hora de entrada
        self.active_detections = {idx: {} for idx in range(len(self.zones))}
        # (Opcional) Backup local de eventos
        self.logged_events = []

    def on_prediction(self, result: dict, frame: VideoFrame) -> None:
        self.fps_monitor.tick()
        fps = self.fps_monitor.fps

        detections = sv.Detections.from_inference(result)
        detections = detections[find_in_list(detections.class_id, self.classes)]
        detections = self.tracker.update_with_detections(detections)

        annotated_frame = frame.image.copy()
        annotated_frame = sv.draw_text(
            scene=annotated_frame,
            text=f"{fps:.1f}",
            text_anchor=sv.Point(40, 30),
            background_color=sv.Color.from_hex("#A351FB"),
            text_color=sv.Color.from_hex("#000000"),
        )

        current_time = time.time()

        for idx, zone in enumerate(self.zones):
            annotated_frame = sv.draw_polygon(
                scene=annotated_frame, polygon=zone.polygon, color=COLORS.by_idx(idx)
            )

            detections_in_zone = detections[zone.trigger(detections)]
            time_in_zone = self.timers[idx].tick(detections_in_zone)
            custom_color_lookup = np.full(detections_in_zone.class_id.shape, idx)

            annotated_frame = COLOR_ANNOTATOR.annotate(
                scene=annotated_frame,
                detections=detections_in_zone,
                custom_color_lookup=custom_color_lookup,
            )
            labels = [
                f"#{tracker_id} {int(time_val // 60):02d}:{int(time_val % 60):02d}"
                for tracker_id, time_val in zip(detections_in_zone.tracker_id, time_in_zone)
            ]
            annotated_frame = LABEL_ANNOTATOR.annotate(
                scene=annotated_frame,
                detections=detections_in_zone,
                labels=labels,
                custom_color_lookup=custom_color_lookup,
            )

            # Obtener tracker_ids actuales en la zona
            current_ids = set(detections_in_zone.tracker_id)
            # Tracker_ids previamente activos en la zona
            active_ids = set(self.active_detections[idx].keys())

            # Registrar nuevos ingresos
            for tracker_id in current_ids - active_ids:
                self.active_detections[idx][tracker_id] = current_time

            # Detectar salidas: objetos que estaban activos y que ya no se detectan en esta zona
            for tracker_id in active_ids - current_ids:
                if tracker_id in self.active_detections[idx]:

                    entry_time = self.active_detections[idx].pop(tracker_id)
                    dwell_time = current_time - entry_time

                    # Convertir los timestamps a objetos datetime
                    hora_entrada = datetime.datetime.fromtimestamp(entry_time)
                    hora_salida = datetime.datetime.fromtimestamp(current_time)

                    # Crear el diccionario para MongoDB
                    evento = {
                        "zona_id": int(idx),
                        "id_rastreador": int(tracker_id),
                        "hora_entrada": hora_entrada,
                        "hora_salida": hora_salida,
                        "tiempo_permanencia": dwell_time
                    }

                    self_mongo = MongoConnector()
                    coleccion_supervision = self_mongo.db["Supervision"]
                    MongoConnector.insert_single_document(self_mongo, evento, coleccion_supervision)
                    self.logged_events.append(evento)
                else:
                    # Opcional: registrar un log si el tracker_id no tiene entry_time
                    print(f"Advertencia: No se encontró 'entry_time' para tracker_id {tracker_id} en zona {idx}")


        cv2.imshow("Processed Video", annotated_frame)
        cv2.waitKey(1)


def main(
    rtsp_url: str,
    zone_configuration_path: str,
    model_id: str,
    confidence: float,
    iou: float,
    classes: List[int],
) -> None:
    sink = CustomSink(zone_configuration_path=zone_configuration_path, classes=classes)

    pipeline = InferencePipeline.init(
        model_id=model_id,
        video_reference=rtsp_url,
        on_prediction=sink.on_prediction,
        confidence=confidence,
        iou_threshold=iou,
    )

    pipeline.start()

    try:
        pipeline.join()
    except KeyboardInterrupt:
        pipeline.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculating detections dwell time in zones, using RTSP stream."
    )
    parser.add_argument(
        "--zone_configuration_path",
        type=str,
        required=True,
        help="Path to the zone configuration JSON file.",
    )
    parser.add_argument(
        "--rtsp_url",
        type=str,
        required=True,
        help="Complete RTSP URL for the video stream.",
    )
    parser.add_argument(
        "--model_id", type=str, default="yolov8s-640", help="Roboflow model ID."
    )
    parser.add_argument(
        "--confidence_threshold",
        type=float,
        default=0.3,
        help="Confidence level for detections (0 to 1). Default is 0.3.",
    )
    parser.add_argument(
        "--iou_threshold",
        default=0.7,
        type=float,
        help="IOU threshold for non-max suppression. Default is 0.7.",
    )
    parser.add_argument(
        "--classes",
        nargs="*",
        type=int,
        default=[],
        help="List of class IDs to track. If empty, all classes are tracked.",
    )
    args = parser.parse_args()

    main(
        rtsp_url=args.rtsp_url,
        zone_configuration_path=args.zone_configuration_path,
        model_id=args.model_id,
        confidence=args.confidence_threshold,
        iou=args.iou_threshold,
        classes=args.classes,
    )
