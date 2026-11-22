"""
Prueba de movimientos.py con la webcam, para uno o dos jugadores.
Muestra cuántas personas se detectan, qué movimiento hace cada jugador
y, en la lista, qué movimientos cumple cada uno (verde) y cuáles no (gris).
Salir con ESC, Q o cerrando la ventana.

Se escribe "I" junto a la muñeca que MediaPipe llama "izquierda" y "D"
junto a la "derecha", para comprobar el intercambio por el espejo.
"""

import cv2
from vision import Camara, COLORES_JUGADOR
from movimientos import DETECTORES, comprobar_movimiento, reconocer_movimiento, _muslos


VENTANA = "MOVE & DANCE - Prueba de movimientos"
FUENTE = cv2.FONT_HERSHEY_SIMPLEX
VERDE = (0, 255, 0)
GRIS = (120, 120, 120)


def texto(frame, mensaje, x, y, color, escala=0.6, grosor=2):
    # Contorno negro para que se lea sobre cualquier fondo
    cv2.putText(frame, mensaje, (x, y), FUENTE, escala, (0, 0, 0), grosor + 2)
    cv2.putText(frame, mensaje, (x, y), FUENTE, escala, color, grosor)


camara = Camara()

if camara.error is not None:
    camara.cerrar()
    raise RuntimeError(camara.error)

try:
    while True:
        frame, jugadores = camara.leer_jugadores()

        if frame is None:
            print(camara.error)
            break

        alto, ancho = frame.shape[:2]

        # Número de personas (el estable es el que usará el juego)
        modo = {0: "nadie", 1: "1 jugador", 2: "2 jugadores a la vez"}[camara.num_jugadores]
        texto(frame, f"Personas: {camara.personas}  ->  {modo}", 20, 35, (0, 255, 255), 0.8)
        # Diagnóstico: poses que devuelve MediaPipe antes de filtrar
        texto(frame, f"MediaPipe ve: {camara.detector.poses_mediapipe}", ancho - 210, 35,
              (200, 200, 200), 0.6, 1)

        # Movimiento reconocido de cada jugador
        for i, jugador in enumerate(("jugador_1", "jugador_2")):
            if jugador in jugadores:
                movimiento = reconocer_movimiento(jugadores[jugador]) or "-"
                etiqueta = "J1" if jugador == "jugador_1" else "J2"
                # muslos: altura de cada rodilla respecto a la cadera (para ajustar
                # sentadilla y rodilla_arriba; de pie salen ~0.8)
                try:
                    muslos = "  muslos %.2f/%.2f" % _muslos(jugadores[jugador])
                except (KeyError, TypeError):
                    muslos = ""
                texto(frame, f"{etiqueta}: {movimiento}{muslos}", 20, 70 + 32 * i,
                      COLORES_JUGADOR[jugador], 0.7)

        # Lista de movimientos: J1 y J2 en verde si lo están haciendo
        # (sobre un fondo oscuro semitransparente para que se lea)
        fondo = frame.copy()
        cv2.rectangle(fondo, (10, 130), (285, 135 + 22 * len(DETECTORES)), (0, 0, 0), -1)
        frame = cv2.addWeighted(fondo, 0.5, frame, 0.5, 0)
        y = 150
        for id_movimiento in DETECTORES:
            texto(frame, id_movimiento, 20, y, (255, 255, 255), 0.5, 1)
            for columna, jugador in ((210, "jugador_1"), (250, "jugador_2")):
                if jugador in jugadores:
                    activo = comprobar_movimiento(jugadores[jugador], id_movimiento)
                    etiqueta = "J1" if jugador == "jugador_1" else "J2"
                    texto(frame, etiqueta, columna, y, VERDE if activo else GRIS, 0.5, 1)
            y += 22

        # Etiquetas de MediaPipe en las muñecas
        for puntos in jugadores.values():
            for nombre, letra in (("muneca_izquierda", "I"), ("muneca_derecha", "D")):
                p = puntos[nombre]
                texto(frame, letra, int(p["x"] * ancho), int(p["y"] * alto),
                      (255, 255, 255), 1.0)

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