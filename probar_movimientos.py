"""
Prueba de movimientos.py con la webcam.
Muestra qué movimiento reconoce y si cada uno está activo. Salir con ESC, Q o cerrando la ventana.

Sirve también para comprobar izquierda/derecha: se escribe "I" junto a
la muñeca que MediaPipe llama "izquierda" y "D" junto a la "derecha".
"""

import cv2
from vision import Camara
from movimientos import DETECTORES, comprobar_movimiento, reconocer_movimiento


VENTANA = "MOVE & DANCE - Prueba de movimientos"

camara = Camara()

if camara.error is not None:
    camara.cerrar()
    raise RuntimeError(camara.error)

try:
    while True:
        frame, puntos = camara.leer()

        if frame is None:
            print(camara.error)
            break

        alto, ancho = frame.shape[:2]

        # Movimiento reconocido
        movimiento = reconocer_movimiento(puntos)
        texto = movimiento if movimiento else "-"
        cv2.putText(frame, f"Movimiento: {texto}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

        # Estado de cada movimiento
        for i, id_movimiento in enumerate(DETECTORES):
            activo = comprobar_movimiento(puntos, id_movimiento)
            color = (0, 255, 0) if activo else (0, 0, 255)
            cv2.putText(frame, id_movimiento, (20, 80 + 30 * i),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # Etiquetas de MediaPipe en las muñecas
        if puntos is not None:
            for nombre, letra in (("muneca_izquierda", "I"), ("muneca_derecha", "D")):
                p = puntos[nombre]
                cv2.putText(frame, letra, (int(p["x"] * ancho), int(p["y"] * alto)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

        cv2.imshow(VENTANA, frame)

        # Salir pulsando ESC o Q (con la ventana seleccionada)
        tecla = cv2.waitKey(1) & 0xFF
        if tecla in (27, ord("q")):
            break

        # Salir al cerrar la ventana con la X
        if cv2.getWindowProperty(VENTANA, cv2.WND_PROP_VISIBLE) < 1:
            break

finally:
    camara.cerrar()
    cv2.destroyAllWindows()