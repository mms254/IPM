"""
Reconocimiento de movimientos a partir de los puntos de vision.py.

Funciones que usa el juego:
    comprobar_movimiento(puntos, id_movimiento) -> bool
    reconocer_movimiento(puntos) -> str | None

`puntos` son los puntos de UN jugador: el diccionario de
obtener_puntos() o uno de los valores de obtener_jugadores()
(coordenadas normalizadas 0-1, la "y" crece hacia abajo), o None.
Con dos jugadores se llama una vez por cada uno.

Los ids son los del catálogo MOVIMIENTOS de coreografias.py (persona 3).

Izquierda y derecha:
    La imagen se voltea en espejo ANTES de detectar, y por eso MediaPipe
    intercambia "izquierdo" y "derecho" (lo comprobamos con la webcam).
    Para que no importe, los movimientos de un solo lado se reconocen
    por el LADO DE LA PANTALLA: en la imagen en espejo, el brazo
    izquierdo real del jugador sale a la izquierda de la pantalla.
"""

from __future__ import annotations   # permite "dict | None" en Python 3.9

# Visibilidad mínima para fiarse de un punto (0-1)
VISIBILIDAD_MINIMA = 0.5

# Umbrales, en proporción al tamaño del cuerpo del jugador
# (así funcionan igual cerca o lejos de la cámara)
BRAZOS_ARRIBA_ALTURA = 0.3      # muñecas por encima del hombro (x largo del torso)
LATERAL_DISTANCIA = 0.8         # muñeca fuera del hombro (x ancho de hombros)
LATERAL_ALTURA = 0.4            # muñeca a la altura del hombro (x largo del torso)
CRUZ_DISTANCIA = 0.5            # en cruz basta con algo menos de extensión
SENTADILLA_MUSLO = 0.55         # rodilla cerca de la altura de la cadera (x largo del torso)
RODILLA_ARRIBA_MUSLO = 0.55     # rodilla levantada (de pie, el muslo mide ~0,8-0,9)
RODILLA_APOYO_MUSLO = 0.65      # la otra pierna sigue estirada
RODILLA_DIFERENCIA = 0.25       # una rodilla bastante más alta que la otra
INCLINACION_DESPLAZAMIENTO = 0.25   # hombros desplazados respecto a caderas (x torso)
ALTERNOS_ALTURA = 0.2           # muñeca levantada por encima del hombro (x torso)
PASO_LATERAL_SEPARACION = 1.4   # separación de tobillos (x ancho de hombros)
PIES_JUNTOS_SEPARACION = 0.45   # separación de tobillos (x ancho de hombros)
CADERAS_DISTANCIA = 0.4         # muñeca cerca de la cadera (x torso)
CADERAS_CODOS = 0.2             # codos hacia fuera (x ancho de hombros)
HOMBROS_DISTANCIA = 0.55        # muñeca cerca del hombro (x torso)
CRUZADOS_DISTANCIA = 0.75       # muñeca cerca del hombro contrario (x torso)
RODILLAS_DISTANCIA = 0.35       # muñeca junto a la rodilla (x torso)


# ----------------------------------------------------------------------
# Funciones auxiliares
# ----------------------------------------------------------------------

TORSO = ("hombro_izquierdo", "hombro_derecho",
         "cadera_izquierda", "cadera_derecha")
MUNECAS = ("muneca_izquierda", "muneca_derecha")


def _visibles(puntos, *nombres):
    """True si todos los puntos existen y se ven bien."""
    for nombre in nombres:
        punto = puntos.get(nombre)
        if punto is None or punto.get("visibilidad", 0) < VISIBILIDAD_MINIMA:
            return False
    return True


def _medio(a, b):
    return {"x": (a["x"] + b["x"]) / 2, "y": (a["y"] + b["y"]) / 2}


def _distancia(a, b):
    return ((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2) ** 0.5


def _largo_torso(puntos):
    """Distancia vertical de los hombros a las caderas (tamaño del cuerpo)."""
    hombros = _medio(puntos["hombro_izquierdo"], puntos["hombro_derecho"])
    caderas = _medio(puntos["cadera_izquierda"], puntos["cadera_derecha"])
    return caderas["y"] - hombros["y"]


def _ancho_hombros(puntos):
    return abs(puntos["hombro_izquierdo"]["x"] - puntos["hombro_derecho"]["x"])


def _hombro_pantalla(puntos, lado):
    """El hombro que está a la izquierda o a la derecha de la pantalla."""
    hombros = [puntos["hombro_izquierdo"], puntos["hombro_derecho"]]
    if lado == "izquierda":
        return min(hombros, key=lambda p: p["x"])
    return max(hombros, key=lambda p: p["x"])


# ----------------------------------------------------------------------
# Un detector por movimiento: reciben puntos (nunca None) y devuelven bool
# ----------------------------------------------------------------------

# 1. BRAZOS ARRIBA ------------------------------------------------------

def brazos_arriba(puntos):
    """Las dos muñecas por encima de la cabeza."""
    if not _visibles(puntos, *TORSO, *MUNECAS):
        return False

    torso = _largo_torso(puntos)
    if torso <= 0:
        return False

    hombros_y = min(puntos["hombro_izquierdo"]["y"], puntos["hombro_derecho"]["y"])
    limite = hombros_y - BRAZOS_ARRIBA_ALTURA * torso

    return (puntos["muneca_izquierda"]["y"] < limite
            and puntos["muneca_derecha"]["y"] < limite)


# 2, 3 y 4. BRAZOS LATERALES Y EN CRUZ ----------------------------------

def _brazo_estirado(puntos, lado, distancia_minima):
    """Alguna muñeca estirada hacia el lado de la pantalla indicado
    ("izquierda" o "derecha"), a la altura del hombro."""
    if not _visibles(puntos, *TORSO):
        return False

    torso = _largo_torso(puntos)
    ancho = _ancho_hombros(puntos)
    if torso <= 0 or ancho <= 0:
        return False

    hombro = _hombro_pantalla(puntos, lado)

    for nombre in MUNECAS:
        if not _visibles(puntos, nombre):
            continue
        muneca = puntos[nombre]

        if lado == "izquierda":
            fuera = hombro["x"] - muneca["x"]
        else:
            fuera = muneca["x"] - hombro["x"]

        a_la_altura = abs(muneca["y"] - hombro["y"]) < LATERAL_ALTURA * torso

        if fuera > distancia_minima * ancho and a_la_altura:
            return True

    return False


def brazo_izq_lateral(puntos):
    """Brazo izquierdo del jugador en cruz (sale a la izquierda de la
    pantalla) y el derecho no."""
    return (_brazo_estirado(puntos, "izquierda", LATERAL_DISTANCIA)
            and not _brazo_estirado(puntos, "derecha", CRUZ_DISTANCIA))


def brazo_der_lateral(puntos):
    """Brazo derecho del jugador en cruz (sale a la derecha de la
    pantalla) y el izquierdo no."""
    return (_brazo_estirado(puntos, "derecha", LATERAL_DISTANCIA)
            and not _brazo_estirado(puntos, "izquierda", CRUZ_DISTANCIA))


def brazos_en_cruz(puntos):
    """Los dos brazos estirados en horizontal, uno hacia cada lado."""
    return (_brazo_estirado(puntos, "izquierda", CRUZ_DISTANCIA)
            and _brazo_estirado(puntos, "derecha", CRUZ_DISTANCIA))


# 5 y 6. SENTADILLA Y RODILLA ARRIBA -------------------------------------

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
    if not _visibles(puntos, *TORSO, "rodilla_izquierda", "rodilla_derecha"):
        return False

    muslos = _muslos(puntos)
    if muslos is None:
        return False

    return max(muslos) < SENTADILLA_MUSLO


def rodilla_arriba(puntos):
    """Una rodilla levantada (cualquiera) y la otra pierna estirada."""
    if not _visibles(puntos, *TORSO, "rodilla_izquierda", "rodilla_derecha"):
        return False

    muslos = _muslos(puntos)
    if muslos is None:
        return False

    return (min(muslos) < RODILLA_ARRIBA_MUSLO
            and max(muslos) > RODILLA_APOYO_MUSLO
            and max(muslos) - min(muslos) > RODILLA_DIFERENCIA)


# 7. INCLINACIÓN LATERAL ------------------------------------------------

def inclinacion_lateral(puntos):
    """El tronco inclinado hacia un lado: los hombros se desplazan
    respecto a las caderas."""
    if not _visibles(puntos, *TORSO):
        return False

    torso = _largo_torso(puntos)
    if torso <= 0:
        return False

    hombros = _medio(puntos["hombro_izquierdo"], puntos["hombro_derecho"])
    caderas = _medio(puntos["cadera_izquierda"], puntos["cadera_derecha"])

    return abs(hombros["x"] - caderas["x"]) > INCLINACION_DESPLAZAMIENTO * torso


# 8. BRAZOS ALTERNOS ----------------------------------------------------

def brazos_alternos(puntos):
    """Un brazo levantado por encima del hombro y el otro no."""
    if not _visibles(puntos, *TORSO, *MUNECAS):
        return False

    torso = _largo_torso(puntos)
    if torso <= 0:
        return False

    hombros_y = min(puntos["hombro_izquierdo"]["y"], puntos["hombro_derecho"]["y"])
    limite = hombros_y - ALTERNOS_ALTURA * torso

    izq_arriba = puntos["muneca_izquierda"]["y"] < limite
    der_arriba = puntos["muneca_derecha"]["y"] < limite

    return izq_arriba != der_arriba


# 9 y 12. PASO LATERAL Y PIES JUNTOS -------------------------------------

def _separacion_pies(puntos):
    """Separación de los tobillos dividida por el ancho de hombros."""
    ancho = _ancho_hombros(puntos)
    if ancho <= 0:
        return None
    return abs(puntos["tobillo_izquierdo"]["x"] - puntos["tobillo_derecho"]["x"]) / ancho


def paso_lateral(puntos):
    """Los pies muy separados."""
    if not _visibles(puntos, "hombro_izquierdo", "hombro_derecho",
                     "tobillo_izquierdo", "tobillo_derecho"):
        return False

    separacion = _separacion_pies(puntos)
    return separacion is not None and separacion > PASO_LATERAL_SEPARACION


def pies_juntos(puntos):
    """Los pies juntos (más juntos que al estar de pie normal)."""
    if not _visibles(puntos, "hombro_izquierdo", "hombro_derecho",
                     "tobillo_izquierdo", "tobillo_derecho"):
        return False

    separacion = _separacion_pies(puntos)
    return separacion is not None and separacion < PIES_JUNTOS_SEPARACION


# 10. MANOS EN LAS CADERAS ----------------------------------------------

def manos_caderas(puntos):
    """Las muñecas en las caderas y los codos hacia fuera (si los codos
    no salen, son los brazos caídos y no cuenta)."""
    if not _visibles(puntos, *TORSO, *MUNECAS, "codo_izquierdo", "codo_derecho"):
        return False

    torso = _largo_torso(puntos)
    ancho = _ancho_hombros(puntos)
    if torso <= 0 or ancho <= 0:
        return False

    manos_en_caderas = all(
        _distancia(puntos[f"muneca_{lado}"], puntos[f"cadera_{lado}"])
        < CADERAS_DISTANCIA * torso
        for lado in ("izquierda", "derecha")
    )

    codos_x = [puntos["codo_izquierdo"]["x"], puntos["codo_derecho"]["x"]]
    codos_fuera = (
        min(codos_x) < _hombro_pantalla(puntos, "izquierda")["x"] - CADERAS_CODOS * ancho
        and max(codos_x) > _hombro_pantalla(puntos, "derecha")["x"] + CADERAS_CODOS * ancho
    )

    return manos_en_caderas and codos_fuera


# 11 y 14. BRAZOS CRUZADOS Y MANOS EN LOS HOMBROS -------------------------

def _manos_y_hombros(puntos):
    """Para cada muñeca: (distancia a su hombro, distancia al hombro
    contrario), divididas por el torso. None si no se ve bien."""
    if not _visibles(puntos, *TORSO, *MUNECAS):
        return None

    torso = _largo_torso(puntos)
    if torso <= 0:
        return None

    pares = (("muneca_izquierda", "hombro_izquierdo", "hombro_derecho"),
             ("muneca_derecha", "hombro_derecho", "hombro_izquierdo"))

    return [
        (_distancia(puntos[muneca], puntos[propio]) / torso,
         _distancia(puntos[muneca], puntos[contrario]) / torso)
        for muneca, propio, contrario in pares
    ]


def brazos_cruzados(puntos):
    """Cada muñeca junto al hombro contrario (brazos cruzados en el pecho)."""
    distancias = _manos_y_hombros(puntos)
    if distancias is None:
        return False

    return all(
        contrario < CRUZADOS_DISTANCIA and contrario < propio
        for propio, contrario in distancias
    )


def manos_hombros(puntos):
    """Cada mano tocando el hombro de su mismo lado."""
    distancias = _manos_y_hombros(puntos)
    if distancias is None:
        return False

    return all(
        propio < HOMBROS_DISTANCIA and propio < contrario
        for propio, contrario in distancias
    )


# 13. BRAZOS ABAJO ------------------------------------------------------

def brazos_abajo(puntos):
    """Las dos muñecas por debajo de las caderas.
    Ojo: es la postura de estar quieto, se cumple sin hacer nada."""
    if not _visibles(puntos, "cadera_izquierda", "cadera_derecha", *MUNECAS):
        return False

    return (puntos["muneca_izquierda"]["y"] > puntos["cadera_izquierda"]["y"]
            and puntos["muneca_derecha"]["y"] > puntos["cadera_derecha"]["y"])


# 15. TOCAR LAS RODILLAS ------------------------------------------------

def toque_rodilla(puntos):
    """Las dos muñecas junto a las rodillas."""
    if not _visibles(puntos, *TORSO, *MUNECAS,
                     "rodilla_izquierda", "rodilla_derecha"):
        return False

    torso = _largo_torso(puntos)
    if torso <= 0:
        return False

    return all(
        _distancia(puntos[f"muneca_{lado}"], puntos[f"rodilla_{lado}"])
        < RODILLAS_DISTANCIA * torso
        for lado in ("izquierda", "derecha")
    )


# ----------------------------------------------------------------------
# Funciones que usa el juego
# ----------------------------------------------------------------------

# id del catálogo -> función que lo reconoce.
# Si la persona 3 añade un movimiento, hay que añadirlo aquí.
# El orden importa en reconocer_movimiento(): primero los más concretos.
DETECTORES = {
    "brazos_arriba": brazos_arriba,
    "sentadilla": sentadilla,
    "rodilla_arriba": rodilla_arriba,
    "brazos_en_cruz": brazos_en_cruz,
    "brazo_izq_lateral": brazo_izq_lateral,
    "brazo_der_lateral": brazo_der_lateral,
    "brazos_alternos": brazos_alternos,
    "brazos_cruzados": brazos_cruzados,
    "manos_hombros": manos_hombros,
    "manos_caderas": manos_caderas,
    "toque_rodilla": toque_rodilla,
    "inclinacion_lateral": inclinacion_lateral,
    "paso_lateral": paso_lateral,
    "pies_juntos": pies_juntos,
    "brazos_abajo": brazos_abajo,
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
    except (KeyError, TypeError, ValueError, ZeroDivisionError, AttributeError):
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