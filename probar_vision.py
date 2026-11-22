"""
Prueba corta de la parte de visión: abre la webcam con Camara
y muestra la imagen con el esqueleto de cada persona (hasta 2). Salir con ESC, Q o cerrando la ventana.
"""

import cv2
from vision import Camara


VENTANA = "MOVE & DANCE - Prueba de vision"

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

        mensaje = {
            0: "No se detecta ninguna persona",
            1: "1 persona detectada",
            2: "2 personas detectadas"
        }[camara.personas]

        cv2.putText(frame, mensaje, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

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