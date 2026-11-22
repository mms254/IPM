
"""
Reconocimiento de los movimientos de Move & Dance.

Recibe los puntos devueltos por DetectorCorporal.obtener_puntos()
y comprueba si el jugador realiza cada movimiento.
"""

VISIBILIDAD_MINIMA = 0.5

# Umbrales relativos al tamaño del cuerpo
ALTURA_BRAZOS = 0.30
DISTANCIA_LATERAL = 0.80
ALTURA_LATERAL = 0.40
SENTADILLA_UMBRAL = 0.55
RODILLA_UMBRAL = 0.30
PIERNA_APOYO_UMBRAL = 0.55
INCLINACION_UMBRAL = 0.25
SEPARACION_PIES_UMBRAL = 1.40


# ---------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------

def _visibles(puntos, *nombres):
    """Comprueba que los puntos existen y tienen visibilidad suficiente."""
    for nombre in nombres:
        punto = puntos.get(nombre)

        if punto is None:
            return False

        if punto.get("visibilidad", 0) < VISIBILIDAD_MINIMA:
            return False

    return True


def _medio(a, b):
    """Calcula el punto medio entre dos articulaciones."""
    return {
        "x": (a["x"] + b["x"]) / 2,
        "y": (a["y"] + b["y"]) / 2
    }


def _largo_torso(puntos):
    """Calcula la distancia vertical entre hombros y caderas."""
    hombros = _medio(
        puntos["hombro_izquierdo"],
        puntos["hombro_derecho"]
    )

    caderas = _medio(
        puntos["cadera_izquierda"],
        puntos["cadera_derecha"]
    )

    return caderas["y"] - hombros["y"]


def _ancho_hombros(puntos):
    """Calcula la distancia horizontal entre los hombros."""
    return abs(
        puntos["hombro_izquierdo"]["x"]
        - puntos["hombro_derecho"]["x"]
    )


# ---------------------------------------------------------
# 1. BRAZOS ARRIBA
# ---------------------------------------------------------

def brazos_arriba(puntos):
    """Los dos brazos deben estar elevados por encima de la cabeza."""

    nombres = (
        "hombro_izquierdo", "hombro_derecho",
        "cadera_izquierda", "cadera_derecha",
        "muneca_izquierda", "muneca_derecha"
    )

    if not _visibles(puntos, *nombres):
        return False

    torso = _largo_torso(puntos)

    if torso <= 0:
        return False

    hombros_y = min(
        puntos["hombro_izquierdo"]["y"],
        puntos["hombro_derecho"]["y"]
    )

    limite = hombros_y - ALTURA_BRAZOS * torso

    return (
        puntos["muneca_izquierda"]["y"] < limite
        and puntos["muneca_derecha"]["y"] < limite
    )


# ---------------------------------------------------------
# 2 Y 3. BRAZOS LATERALES
# ---------------------------------------------------------

def _brazo_lateral(puntos, lado):
    """Detecta un brazo extendido hacia un lado de la pantalla."""

    nombres = (
        "hombro_izquierdo", "hombro_derecho",
        "cadera_izquierda", "cadera_derecha"
    )

    if not _visibles(puntos, *nombres):
        return False

    torso = _largo_torso(puntos)
    ancho = _ancho_hombros(puntos)

    if torso <= 0 or ancho <= 0:
        return False

    hombros = [
        puntos["hombro_izquierdo"],
        puntos["hombro_derecho"]
    ]

    if lado == "izquierda":
        hombro = min(hombros, key=lambda p: p["x"])
    else:
        hombro = max(hombros, key=lambda p: p["x"])

    for nombre in ("muneca_izquierda", "muneca_derecha"):

        if not _visibles(puntos, nombre):
            continue

        muneca = puntos[nombre]

        if lado == "izquierda":
            distancia = hombro["x"] - muneca["x"]
        else:
            distancia = muneca["x"] - hombro["x"]

        altura_correcta = (
            abs(muneca["y"] - hombro["y"])
            < ALTURA_LATERAL * torso
        )

        if (
            distancia > DISTANCIA_LATERAL * ancho
            and altura_correcta
        ):
            return True

    return False


def brazo_izq_lateral(puntos):
    return _brazo_lateral(puntos, "izquierda")


def brazo_der_lateral(puntos):
    return _brazo_lateral(puntos, "derecha")


# ---------------------------------------------------------
# 4. BRAZOS EN CRUZ
# ---------------------------------------------------------

def brazos_en_cruz(puntos):
    """Los dos brazos extendidos horizontalmente hacia los lados."""

    nombres = (
        "hombro_izquierdo", "hombro_derecho",
        "cadera_izquierda", "cadera_derecha",
        "muneca_izquierda", "muneca_derecha"
    )

    if not _visibles(puntos, *nombres):
        return False

    torso = _largo_torso(puntos)
    ancho = _ancho_hombros(puntos)

    if torso <= 0 or ancho <= 0:
        return False

    hombro_izq = puntos["hombro_izquierdo"]
    hombro_der = puntos["hombro_derecho"]

    muneca_izq = puntos["muneca_izquierda"]
    muneca_der = puntos["muneca_derecha"]

    izquierda_correcta = (
        hombro_izq["x"] - muneca_izq["x"] > 0.5 * ancho
        and abs(muneca_izq["y"] - hombro_izq["y"]) < 0.4 * torso
    )

    derecha_correcta = (
        muneca_der["x"] - hombro_der["x"] > 0.5 * ancho
        and abs(muneca_der["y"] - hombro_der["y"]) < 0.4 * torso
    )

    return izquierda_correcta and derecha_correcta


# ---------------------------------------------------------
# 5. SENTADILLA
# ---------------------------------------------------------

def _muslos(puntos):
    """Calcula la altura relativa de ambas rodillas."""

    torso = _largo_torso(puntos)

    if torso <= 0:
        return None

    izquierda = (
        puntos["rodilla_izquierda"]["y"]
        - puntos["cadera_izquierda"]["y"]
    ) / torso

    derecha = (
        puntos["rodilla_derecha"]["y"]
        - puntos["cadera_derecha"]["y"]
    ) / torso

    return izquierda, derecha


def sentadilla(puntos):
    """Detecta si ambas piernas están flexionadas."""

    nombres = (
        "hombro_izquierdo", "hombro_derecho",
        "cadera_izquierda", "cadera_derecha",
        "rodilla_izquierda", "rodilla_derecha"
    )

    if not _visibles(puntos, *nombres):
        return False

    muslos = _muslos(puntos)

    if muslos is None:
        return False

    return max(muslos) < SENTADILLA_UMBRAL


# ---------------------------------------------------------
# 6. RODILLA ARRIBA
# ---------------------------------------------------------

def rodilla_arriba(puntos):
    """Una rodilla elevada y la otra pierna extendida."""

    nombres = (
        "hombro_izquierdo", "hombro_derecho",
        "cadera_izquierda", "cadera_derecha",
        "rodilla_izquierda", "rodilla_derecha"
    )

    if not _visibles(puntos, *nombres):
        return False

    muslos = _muslos(puntos)

    if muslos is None:
        return False

    return (
        min(muslos) < RODILLA_UMBRAL
        and max(muslos) > PIERNA_APOYO_UMBRAL
    )


# ---------------------------------------------------------
# 7. INCLINACIÓN LATERAL
# ---------------------------------------------------------

def inclinacion_lateral(puntos):
    """Detecta una inclinación del tronco hacia un lado."""

    nombres = (
        "hombro_izquierdo", "hombro_derecho",
        "cadera_izquierda", "cadera_derecha"
    )

    if not _visibles(puntos, *nombres):
        return False

    torso = _largo_torso(puntos)

    if torso <= 0:
        return False

    hombros = _medio(
        puntos["hombro_izquierdo"],
        puntos["hombro_derecho"]
    )

    caderas = _medio(
        puntos["cadera_izquierda"],
        puntos["cadera_derecha"]
    )

    desplazamiento = abs(hombros["x"] - caderas["x"])

    return desplazamiento > INCLINACION_UMBRAL * torso


# ---------------------------------------------------------
# 8. BRAZOS ALTERNOS
# ---------------------------------------------------------

def brazos_alternos(puntos):
    """Un brazo elevado mientras el otro permanece abajo."""

    nombres = (
        "hombro_izquierdo", "hombro_derecho",
        "cadera_izquierda", "cadera_derecha",
        "muneca_izquierda", "muneca_derecha"
    )

    if not _visibles(puntos, *nombres):
        return False

    torso = _largo_torso(puntos)

    if torso <= 0:
        return False

    hombros_y = min(
        puntos["hombro_izquierdo"]["y"],
        puntos["hombro_derecho"]["y"]
    )

    limite_arriba = hombros_y - 0.20 * torso

    izq_arriba = (
        puntos["muneca_izquierda"]["y"] < limite_arriba
    )

    der_arriba = (
        puntos["muneca_derecha"]["y"] < limite_arriba
    )

    # Solo uno de los dos brazos debe estar elevado.
    return izq_arriba != der_arriba


# ---------------------------------------------------------
# 9. PASO LATERAL
# ---------------------------------------------------------

def paso_lateral(puntos):
    """Detecta una separación amplia entre los dos tobillos."""

    nombres = (
        "hombro_izquierdo", "hombro_derecho",
        "tobillo_izquierdo", "tobillo_derecho"
    )

    if not _visibles(puntos, *nombres):
        return False

    ancho = _ancho_hombros(puntos)

    if ancho <= 0:
        return False

    separacion = abs(
        puntos["tobillo_izquierdo"]["x"]
        - puntos["tobillo_derecho"]["x"]
    )

    return separacion > SEPARACION_PIES_UMBRAL * ancho


# ---------------------------------------------------------
# 10. MANOS EN LAS CADERAS
# ---------------------------------------------------------

def manos_caderas(puntos):
    """Detecta ambas muñecas cerca de sus respectivas caderas."""
    nombres = (
        "hombro_izquierdo", "hombro_derecho",
        "cadera_izquierda", "cadera_derecha",
        "muneca_izquierda", "muneca_derecha"
    )
    if not _visibles(puntos, *nombres):
        return False

    torso = _largo_torso(puntos)
    if torso <= 0:
        return False

    return all(
        (
            (puntos[f"muneca_{lado}"]["x"] - puntos[f"cadera_{lado}"]["x"]) ** 2
            + (puntos[f"muneca_{lado}"]["y"] - puntos[f"cadera_{lado}"]["y"]) ** 2
        ) ** 0.5 < 0.4 * torso
        for lado in ("izquierda", "derecha")
    )


# ---------------------------------------------------------
# 11. BRAZOS CRUZADOS
# ---------------------------------------------------------

def brazos_cruzados(puntos):
    """Detecta cada muñeca cerca del hombro del lado contrario."""
    nombres = (
        "hombro_izquierdo", "hombro_derecho",
        "cadera_izquierda", "cadera_derecha",
        "muneca_izquierda", "muneca_derecha"
    )
    if not _visibles(puntos, *nombres):
        return False

    torso = _largo_torso(puntos)
    if torso <= 0:
        return False

    izquierda_cerca_del_hombro_derecho = (
        (
            (puntos["muneca_izquierda"]["x"] - puntos["hombro_derecho"]["x"]) ** 2
            + (puntos["muneca_izquierda"]["y"] - puntos["hombro_derecho"]["y"]) ** 2
        ) ** 0.5 < 0.75 * torso
    )
    derecha_cerca_del_hombro_izquierdo = (
        (
            (puntos["muneca_derecha"]["x"] - puntos["hombro_izquierdo"]["x"]) ** 2
            + (puntos["muneca_derecha"]["y"] - puntos["hombro_izquierdo"]["y"]) ** 2
        ) ** 0.5 < 0.75 * torso
    )
    return (
        izquierda_cerca_del_hombro_derecho
        and derecha_cerca_del_hombro_izquierdo
    )


# ---------------------------------------------------------
# 12. PIES JUNTOS
# ---------------------------------------------------------

def pies_juntos(puntos):
    """Detecta los tobillos próximos entre sí, en proporción a los hombros."""
    nombres = (
        "hombro_izquierdo", "hombro_derecho",
        "tobillo_izquierdo", "tobillo_derecho"
    )
    if not _visibles(puntos, *nombres):
        return False

    ancho = _ancho_hombros(puntos)
    if ancho <= 0:
        return False

    separacion = abs(
        puntos["tobillo_izquierdo"]["x"]
        - puntos["tobillo_derecho"]["x"]
    )
    return separacion < 0.85 * ancho


# ---------------------------------------------------------
# 13. BRAZOS ABAJO
# ---------------------------------------------------------

def brazos_abajo(puntos):
    """Detecta ambas muñecas por debajo de las caderas."""
    nombres = (
        "cadera_izquierda", "cadera_derecha",
        "muneca_izquierda", "muneca_derecha"
    )
    if not _visibles(puntos, *nombres):
        return False

    return (
        puntos["muneca_izquierda"]["y"]
        > puntos["cadera_izquierda"]["y"]
        and puntos["muneca_derecha"]["y"]
        > puntos["cadera_derecha"]["y"]
    )


# ---------------------------------------------------------
# 14. MANOS EN LOS HOMBROS
# ---------------------------------------------------------

def manos_hombros(puntos):
    """Detecta cada muñeca cerca del hombro del mismo lado."""
    nombres = (
        "hombro_izquierdo", "hombro_derecho",
        "cadera_izquierda", "cadera_derecha",
        "muneca_izquierda", "muneca_derecha"
    )
    if not _visibles(puntos, *nombres):
        return False

    torso = _largo_torso(puntos)
    if torso <= 0:
        return False

    return all(
        (
            (puntos[muneca]["x"] - puntos[hombro]["x"]) ** 2
            + (puntos[muneca]["y"] - puntos[hombro]["y"]) ** 2
        ) ** 0.5 < 0.55 * torso
        for muneca, hombro in (
            ("muneca_izquierda", "hombro_izquierdo"),
            ("muneca_derecha", "hombro_derecho")
        )
    )


# ---------------------------------------------------------
# 15. TOCAR LAS RODILLAS
# ---------------------------------------------------------

def toque_rodilla(puntos):
    """Detecta ambas muñecas cerca de las rodillas."""
    nombres = (
        "hombro_izquierdo", "hombro_derecho",
        "cadera_izquierda", "cadera_derecha",
        "rodilla_izquierda", "rodilla_derecha",
        "muneca_izquierda", "muneca_derecha"
    )
    if not _visibles(puntos, *nombres):
        return False

    torso = _largo_torso(puntos)
    if torso <= 0:
        return False

    return all(
        (
            (puntos[f"muneca_{lado}"]["x"] - puntos[f"rodilla_{lado}"]["x"]) ** 2
            + (puntos[f"muneca_{lado}"]["y"] - puntos[f"rodilla_{lado}"]["y"]) ** 2
        ) ** 0.5 < 0.7 * torso
        for lado in ("izquierda", "derecha")
    )


# ---------------------------------------------------------
# CATÁLOGO DE DETECTORES
# ---------------------------------------------------------

DETECTORES = {
    "brazos_arriba": brazos_arriba,
    "brazo_izq_lateral": brazo_izq_lateral,
    "brazo_der_lateral": brazo_der_lateral,
    "brazos_en_cruz": brazos_en_cruz,
    "sentadilla": sentadilla,
    "rodilla_arriba": rodilla_arriba,
    "inclinacion_lateral": inclinacion_lateral,
    "brazos_alternos": brazos_alternos,
    "paso_lateral": paso_lateral,
    "manos_caderas": manos_caderas,
    "brazos_cruzados": brazos_cruzados,
    "pies_juntos": pies_juntos,
    "brazos_abajo": brazos_abajo,
    "manos_hombros": manos_hombros,
    "toque_rodilla": toque_rodilla
}


def comprobar_movimiento(puntos, id_movimiento):
    """
    Comprueba si se realiza un movimiento concreto.

    Devuelve False si no hay puntos o el movimiento es desconocido.
    """

    if puntos is None:
        return False

    detector = DETECTORES.get(id_movimiento)

    if detector is None:
        return False

    try:
        return bool(detector(puntos))
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def reconocer_movimiento(puntos):
    """Devuelve el primer movimiento reconocido o None."""

    if puntos is None:
        return None

    for id_movimiento in DETECTORES:
        if comprobar_movimiento(puntos, id_movimiento):
            return id_movimiento

    return None
