"""
Imágenes de referencia de cada movimiento
"""

import math
import pygame
from interfaz import estilo as e


DE_PIE = {
    "cabeza": (0.50, 0.12),
    "cuello": (0.50, 0.22),
    "hombro_i": (0.38, 0.26), "hombro_d": (0.62, 0.26),
    "codo_i": (0.35, 0.42), "codo_d": (0.65, 0.42),
    "muneca_i": (0.34, 0.57), "muneca_d": (0.66, 0.57),
    "cadera_i": (0.43, 0.56), "cadera_d": (0.57, 0.56),
    "rodilla_i": (0.42, 0.75), "rodilla_d": (0.58, 0.75),
    "tobillo_i": (0.41, 0.94), "tobillo_d": (0.59, 0.94),
}

PARTES = {
    "brazo_i": [("hombro_i", "codo_i"), ("codo_i", "muneca_i")],
    "brazo_d": [("hombro_d", "codo_d"), ("codo_d", "muneca_d")],
    "pierna_i": [("cadera_i", "rodilla_i"), ("rodilla_i", "tobillo_i")],
    "pierna_d": [("cadera_d", "rodilla_d"), ("rodilla_d", "tobillo_d")],
    "tronco": [("cuello", "hombro_i"), ("cuello", "hombro_d"),
               ("hombro_i", "cadera_i"), ("hombro_d", "cadera_d"),
               ("cadera_i", "cadera_d")],
}
PARTE_SUPERIOR = ("cabeza", "cuello", "hombro_i", "hombro_d", "codo_i", "codo_d",
                  "muneca_i", "muneca_d")


def _inclinar(postura, grados):
    """Gira la parte de arriba del cuerpo alrededor de las caderas."""
    cx, cy = 0.50, 0.56
    a = math.radians(grados)
    nueva = dict(postura)
    for punto in PARTE_SUPERIOR:
        x, y = postura[punto][0] - cx, postura[punto][1] - cy
        nueva[punto] = (cx + x * math.cos(a) - y * math.sin(a),
                        cy + x * math.sin(a) + y * math.cos(a))
    return nueva


def _postura(**cambios):
    return {**DE_PIE, **cambios}


POSTURAS = {
    "brazos_arriba": (_postura(
        codo_i=(0.35, 0.12), codo_d=(0.65, 0.12),
        muneca_i=(0.33, 0.01), muneca_d=(0.67, 0.01)),
        ["brazo_i", "brazo_d"]),
    "brazo_izq_lateral": (_postura(
        codo_i=(0.22, 0.26), muneca_i=(0.06, 0.26)),
        ["brazo_i"]),
    "brazo_der_lateral": (_postura(
        codo_d=(0.78, 0.26), muneca_d=(0.94, 0.26)),
        ["brazo_d"]),
    "brazos_en_cruz": (_postura(
        codo_i=(0.22, 0.26), muneca_i=(0.06, 0.26),
        codo_d=(0.78, 0.26), muneca_d=(0.94, 0.26)),
        ["brazo_i", "brazo_d"]),
    "brazos_alternos": (_postura(
        codo_i=(0.35, 0.12), muneca_i=(0.33, 0.01)),
        ["brazo_i", "brazo_d"]),
    "brazos_abajo": (_postura(
        codo_i=(0.37, 0.42), muneca_i=(0.37, 0.60),
        codo_d=(0.63, 0.42), muneca_d=(0.63, 0.60)),
        ["brazo_i", "brazo_d"]),
    "brazos_cruzados": (_postura(
        codo_i=(0.31, 0.40), muneca_i=(0.68, 0.30),
        codo_d=(0.69, 0.40), muneca_d=(0.32, 0.30)),
        ["brazo_i", "brazo_d"]),
    "manos_caderas": (_postura(
        codo_i=(0.25, 0.42), muneca_i=(0.42, 0.55),
        codo_d=(0.75, 0.42), muneca_d=(0.58, 0.55)),
        ["brazo_i", "brazo_d"]),
    "manos_hombros": (_postura(
        codo_i=(0.25, 0.37), muneca_i=(0.39, 0.23),
        codo_d=(0.75, 0.37), muneca_d=(0.61, 0.23)),
        ["brazo_i", "brazo_d"]),
    "inclinacion_lateral": (_inclinar(DE_PIE, 18),
        ["tronco"]),
    "sentadilla": (_postura(
        cabeza=(0.50, 0.24), cuello=(0.50, 0.34),
        hombro_i=(0.38, 0.38), hombro_d=(0.62, 0.38),
        codo_i=(0.28, 0.48), codo_d=(0.72, 0.48),
        muneca_i=(0.20, 0.57), muneca_d=(0.80, 0.57),
        cadera_i=(0.43, 0.66), cadera_d=(0.57, 0.66),
        rodilla_i=(0.32, 0.76), rodilla_d=(0.68, 0.76)),
        ["pierna_i", "pierna_d"]),
    "rodilla_arriba": (_postura(
        rodilla_d=(0.70, 0.55), tobillo_d=(0.68, 0.76)),
        ["pierna_d"]),
    "paso_lateral": (_postura(
        rodilla_i=(0.34, 0.75), tobillo_i=(0.26, 0.94),
        rodilla_d=(0.66, 0.75), tobillo_d=(0.74, 0.94)),
        ["pierna_i", "pierna_d"]),
    "pies_juntos": (_postura(
        rodilla_i=(0.47, 0.75), tobillo_i=(0.48, 0.94),
        rodilla_d=(0.53, 0.75), tobillo_d=(0.52, 0.94)),
        ["pierna_i", "pierna_d"]),
    "toque_rodilla": (_postura(
        cabeza=(0.50, 0.30), cuello=(0.50, 0.39),
        hombro_i=(0.39, 0.42), hombro_d=(0.61, 0.42),
        codo_i=(0.31, 0.57), codo_d=(0.69, 0.57),
        muneca_i=(0.35, 0.73), muneca_d=(0.65, 0.73),
        rodilla_i=(0.37, 0.75), rodilla_d=(0.63, 0.75)),
        ["brazo_i", "brazo_d", "tronco"]),
    "estrella": (_postura(
        codo_i=(0.27, 0.15), muneca_i=(0.16, 0.04),
        codo_d=(0.73, 0.15), muneca_d=(0.84, 0.04),
        rodilla_i=(0.34, 0.75), tobillo_i=(0.26, 0.94),
        rodilla_d=(0.66, 0.75), tobillo_d=(0.74, 0.94)),
        ["brazo_i", "brazo_d", "pierna_i", "pierna_d"]),
    "mano_rodilla_contraria": (_postura(
        codo_i=(0.42, 0.45), muneca_i=(0.59, 0.59),
        codo_d=(0.75, 0.36), muneca_d=(0.86, 0.45),
        rodilla_d=(0.62, 0.60), tobillo_d=(0.64, 0.80)),
        ["brazo_i", "pierna_d"]),
    "manos_cabeza": (_postura(
        codo_i=(0.24, 0.15), muneca_i=(0.42, 0.10),
        codo_d=(0.76, 0.15), muneca_d=(0.58, 0.10)),
        ["brazo_i", "brazo_d"]),
}


def dibujar_figura(superficie, id_movimiento, rect, resaltar=True,
                   color=e.TEXTO, color_resaltado=e.ACENTO_2, fondo=e.FONDO_CLARO):
    """Dibuja el monigote del movimiento dentro de rect.
    Si el movimiento no tiene postura, dibuja la figura de pie."""
    if fondo is not None:
        pygame.draw.rect(superficie, fondo, rect, border_radius=16)

    postura, partes = POSTURAS.get(id_movimiento, (DE_PIE, []))
    if not resaltar:
        partes = []

    lado = min(rect.width, rect.height) * 0.86
    x0 = rect.centerx - lado / 2
    y0 = rect.centery - lado / 2

    def punto(nombre):
        x, y = postura[nombre]
        return (int(x0 + x * lado), int(y0 + y * lado))

    grosor = max(3, int(lado * 0.045))

    orden = [p for p in PARTES if p not in partes] + [p for p in PARTES if p in partes]
    for parte in orden:
        c = color_resaltado if parte in partes else color
        for a, b in PARTES[parte]:
            pygame.draw.line(superficie, c, punto(a), punto(b), grosor)
            pygame.draw.circle(superficie, c, punto(a), grosor // 2)
            pygame.draw.circle(superficie, c, punto(b), grosor // 2)

    # cabeza
    pygame.draw.circle(superficie, color, punto("cabeza"), int(lado * 0.075))