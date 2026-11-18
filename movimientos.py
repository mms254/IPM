"""
Reconocimiento de movimientos a partir de los puntos de vision.py.

Funciones que usa el juego:
    comprobar_movimiento(puntos, id_movimiento) -> bool
    reconocer_movimiento(puntos) -> str | None

`puntos` es el diccionario de DetectorCorporal.obtener_puntos()
(coordenadas normalizadas 0-1, la "y" crece hacia abajo) o None.

Los ids son los del catálogo MOVIMIENTOS de la persona 3:
    brazos_arriba, brazo_izq_lateral, brazo_der_lateral,
    sentadilla, rodilla_arriba

Izquierda y derecha:
    La imagen se voltea en espejo ANTES de detectar, así que las
    etiquetas "izquierdo"/"derecho" de MediaPipe pueden salir
    intercambiadas. Para no depender de ellas, los brazos laterales
    se reconocen por el LADO DE LA PANTALLA hacia el que se estira
    el brazo. En la imagen en espejo, el brazo izquierdo real del
    jugador sale a la izquierda de la pantalla (x pequeña), igual
    que en un espejo.
"""

from __future__ import annotations   # permite "dict | None" en Python 3.9

# Visibilidad mínima para fiarse de un punto (0-1)
VISIBILIDAD_MINIMA = 0.5

# Umbrales, en proporción al tamaño del cuerpo del jugador
# (así funcionan igual cerca o lejos de la cámara)
BRAZOS_ARRIBA_ALTURA = 0.3      # muñecas por encima del hombro (x largo del torso)
LATERAL_DISTANCIA = 0.8         # muñeca fuera del hombro (x ancho de hombros)
LATERAL_ALTURA = 0.4            # muñeca a la altura del hombro (x largo del torso)
SENTADILLA_MUSLO = 0.55         # rodilla cerca de la altura de la cadera (x largo del torso)
RODILLA_ARRIBA_MUSLO = 0.3      # rodilla levantada casi a la altura de la cadera
RODILLA_APOYO_MUSLO = 0.55      # la otra pierna sigue estirada


# Funciones auxiliares
def _visibles(puntos, *nombres):
    """True si todos los puntos existen y se ven bien."""
    for nombre in nombres:
        punto = puntos.get(nombre)
        if punto is None or punto.get("visibilidad", 0) < VISIBILIDAD_MINIMA:
            return False
    return True


def _medio(a, b):
    return {"x": (a["x"] + b["x"]) / 2, "y": (a["y"] + b["y"]) / 2}


def _largo_torso(puntos):
    """Distancia vertical de los hombros a las caderas (tamaño del cuerpo)."""
    hombros = _medio(puntos["hombro_izquierdo"], puntos["hombro_derecho"])
    caderas = _medio(puntos["cadera_izquierda"], puntos["cadera_derecha"])
    return caderas["y"] - hombros["y"]


def _ancho_hombros(puntos):
    return abs(puntos["hombro_izquierdo"]["x"] - puntos["hombro_derecho"]["x"])


# Un detector por movimiento: reciben puntos (nunca None) y devuelven bool

def brazos_arriba(puntos):
    """Las dos muñecas por encima de la cabeza."""
    if not _visibles(puntos, "hombro_izquierdo", "hombro_derecho",
                     "cadera_izquierda", "cadera_derecha",
                     "muneca_izquierda", "muneca_derecha"):
        return False

    torso = _largo_torso(puntos)
    if torso <= 0:
        return False

    hombros_y = min(puntos["hombro_izquierdo"]["y"], puntos["hombro_derecho"]["y"])
    limite = hombros_y - BRAZOS_ARRIBA_ALTURA * torso

    return (puntos["muneca_izquierda"]["y"] < limite
            and puntos["muneca_derecha"]["y"] < limite)


def _brazo_lateral(puntos, lado):
    """Un brazo estirado en cruz hacia el lado de la pantalla indicado
    ("izquierda" o "derecha"), con la muñeca a la altura del hombro."""
    if not _visibles(puntos, "hombro_izquierdo", "hombro_derecho",
                     "cadera_izquierda", "cadera_derecha"):
        return False

    torso = _largo_torso(puntos)
    ancho = _ancho_hombros(puntos)
    if torso <= 0 or ancho <= 0:
        return False

    hombros = [puntos["hombro_izquierdo"], puntos["hombro_derecho"]]
    if lado == "izquierda":
        hombro = min(hombros, key=lambda p: p["x"])
    else:
        hombro = max(hombros, key=lambda p: p["x"])

    for nombre in ("muneca_izquierda", "muneca_derecha"):
        if not _visibles(puntos, nombre):
            continue
        muneca = puntos[nombre]

        if lado == "izquierda":
            fuera = hombro["x"] - muneca["x"]
        else:
            fuera = muneca["x"] - hombro["x"]

        a_la_altura = abs(muneca["y"] - hombro["y"]) < LATERAL_ALTURA * torso

        if fuera > LATERAL_DISTANCIA * ancho and a_la_altura:
            return True

    return False


def brazo_izq_lateral(puntos):
    """Brazo izquierdo del jugador en cruz (sale a la izquierda de la pantalla)."""
    return _brazo_lateral(puntos, "izquierda")


def brazo_der_lateral(puntos):
    """Brazo derecho del jugador en cruz (sale a la derecha de la pantalla)."""
    return _brazo_lateral(puntos, "derecha")


def _muslos(puntos):
    """Altura de cada rodilla respecto a su cadera, dividida por el torso.
    Un valor grande es la pierna estirada; uno pequeño, la rodilla subida."""
    torso = _largo_torso(puntos)
    if torso <= 0:
        return None
    izq = (puntos["rodilla_izquierda"]["y"] - puntos["cadera_izquierda"]["y"]) / torso
    der = (puntos["rodilla_derecha"]["y"] - puntos["cadera_derecha"]["y"]) / torso
    return izq, der


def sentadilla(puntos):
    """Las dos rodillas dobladas: las caderas bajan casi hasta las rodillas."""
    if not _visibles(puntos, "hombro_izquierdo", "hombro_derecho",
                     "cadera_izquierda", "cadera_derecha",
                     "rodilla_izquierda", "rodilla_derecha"):
        return False

    muslos = _muslos(puntos)
    if muslos is None:
        return False

    return max(muslos) < SENTADILLA_MUSLO


def rodilla_arriba(puntos):
    """Una rodilla levantada (cualquiera) y la otra pierna estirada."""
    if not _visibles(puntos, "hombro_izquierdo", "hombro_derecho",
                     "cadera_izquierda", "cadera_derecha",
                     "rodilla_izquierda", "rodilla_derecha"):
        return False

    muslos = _muslos(puntos)
    if muslos is None:
        return False

    return (min(muslos) < RODILLA_ARRIBA_MUSLO
            and max(muslos) > RODILLA_APOYO_MUSLO)


# Funciones que usa el juego

# id del catálogo -> función que lo reconoce.
# Si la persona 3 añade un movimiento, hay que añadirlo aquí.
DETECTORES = {
    "brazos_arriba": brazos_arriba,
    "brazo_izq_lateral": brazo_izq_lateral,
    "brazo_der_lateral": brazo_der_lateral,
    "sentadilla": sentadilla,
    "rodilla_arriba": rodilla_arriba,
}

_ids_desconocidos_avisados = set()


def comprobar_movimiento(puntos: dict | None, id_movimiento: str) -> bool:
    """True si el jugador está haciendo AHORA el movimiento id_movimiento.
    Si puntos es None (no se ve a nadie) debe devolver False."""
    if puntos is None:
        return False

    detector = DETECTORES.get(id_movimiento)
    if detector is None:
        # Aviso una sola vez para no llenar la consola (se llama ~30 veces/s)
        if id_movimiento not in _ids_desconocidos_avisados:
            _ids_desconocidos_avisados.add(id_movimiento)
            print(f"[movimientos] Movimiento desconocido: {id_movimiento!r}")
        return False

    try:
        return bool(detector(puntos))
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        # Puntos incompletos o con formato raro: no se cuenta como correcto
        return False


def reconocer_movimiento(puntos: dict | None) -> str | None:
    """Devuelve el id del movimiento que se está haciendo, o None."""
    if puntos is None:
        return None

    for id_movimiento in DETECTORES:
        if comprobar_movimiento(puntos, id_movimiento):
            return id_movimiento

    return None