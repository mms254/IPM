"""
Simulación de las partes de las Personas 1 y 3
"""

import pygame

# ----------------------------------------------------------------------
# Imitación de la PERSONA 1 (movimientos.py)
# ----------------------------------------------------------------------

def comprobar_movimiento(puntos, id_movimiento):
    """Falso: el movimiento es correcto si se pulsa la barra espaciadora."""
    return pygame.key.get_pressed()[pygame.K_SPACE]


# ----------------------------------------------------------------------
# Imitación de la PERSONA 3 (coreografias.py)
# ----------------------------------------------------------------------

MOVIMIENTOS = {
    "brazos_arriba":     {"nombre": "¡Brazos arriba!"},
    "brazo_izq_lateral": {"nombre": "Brazo izquierdo en cruz"},
    "brazo_der_lateral": {"nombre": "Brazo derecho en cruz"},
    "sentadilla":        {"nombre": "¡Sentadilla!"},
    "rodilla_arriba":    {"nombre": "Rodilla arriba"},
}

# Tiempos de las rutinas (en segundos, dificultad "normal").
# Es un juego de rehabilitación también para personas mayores,
# así que se deja tiempo de sobra para reaccionar y hacer cada ejercicio.
TIEMPO_PREPARACION = 3.0    # antes del primer ejercicio
DURACION_EJERCICIO = 6.0    # tiempo para hacer cada ejercicio
DESCANSO = 2.0              # pausa entre un ejercicio y el siguiente


def crear_pasos(movimientos):
    """Reparte los ejercicios en el tiempo con los valores de arriba."""
    return [
        {"inicio": TIEMPO_PREPARACION + i * (DURACION_EJERCICIO + DESCANSO),
         "duracion": DURACION_EJERCICIO, "movimiento": m}
        for i, m in enumerate(movimientos)
    ]


# Cada canción es una rutina con su dificultad.
# "inicio_audio": segundo de la canción desde el que empieza a sonar
# (por si tiene una introducción larga).
CANCIONES = [
    {
        "id": "bailando",
        "titulo": "Bailando",
        "artista": "Enrique Iglesias",
        "audio": "assets/musica/bailando.mp3",
        "inicio_audio": 0.0,
        "dificultad": "facil",
        "pasos": crear_pasos([
            "brazos_arriba", "brazo_izq_lateral", "brazo_der_lateral",
            "brazos_arriba", "brazo_izq_lateral", "brazo_der_lateral",
        ]),
    },
    {
        "id": "cant_stop_the_feeling",
        "titulo": "Can't Stop the Feeling!",
        "artista": "Justin Timberlake",
        "audio": "assets/musica/cant_stop_the_feeling.mp3",
        "inicio_audio": 0.0,
        "dificultad": "normal",
        "pasos": crear_pasos([
            "brazos_arriba", "rodilla_arriba", "brazo_izq_lateral",
            "brazo_der_lateral", "rodilla_arriba", "brazos_arriba",
            "brazo_izq_lateral", "brazo_der_lateral",
        ]),
    },
    {
        "id": "waka_waka",
        "titulo": "Waka Waka",
        "artista": "Shakira",
        "audio": "assets/musica/waka_waka.mp3",
        "inicio_audio": 0.0,
        "dificultad": "dificil",
        "pasos": crear_pasos([
            "brazos_arriba", "sentadilla", "brazo_izq_lateral", "rodilla_arriba",
            "brazo_der_lateral", "sentadilla", "brazos_arriba", "rodilla_arriba",
            "brazo_izq_lateral", "brazo_der_lateral",
        ]),
    },
]

DIFICULTADES = ["facil", "normal", "dificil"]


class MotorCoreografia:
    """Versión sencilla del motor: acierto en la 1ª mitad del paso =
    'perfecto', en la 2ª mitad = 'bien', si se acaba el tiempo = 'fallo'."""

    PUNTOS = {"perfecto": 100, "bien": 50, "fallo": 0}

    def __init__(self, cancion, dificultad="normal"):
        # fácil: 50 % más de tiempo; difícil: 25 % menos
        factor = {"facil": 1.5, "normal": 1.0, "dificil": 0.75}[dificultad]
        self.pasos = [
            {**p, "inicio": p["inicio"] * factor, "duracion": p["duracion"] * factor}
            for p in cancion["pasos"]
        ]
        ultimo = self.pasos[-1]
        self.duracion_total = ultimo["inicio"] + ultimo["duracion"] + 1.0
        self.indice = 0
        self.resultados = []

    def paso_actual(self, t):
        if self.indice < len(self.pasos) and self.pasos[self.indice]["inicio"] <= t:
            return self.pasos[self.indice]
        return None

    def siguiente_paso(self, t):
        if self.paso_actual(t) is not None:
            i = self.indice + 1
        else:
            i = self.indice
        return self.pasos[i] if i < len(self.pasos) else None

    def actualizar(self, t, correcto):
        paso = self.paso_actual(t)
        if paso is None:
            return None
        transcurrido = t - paso["inicio"]
        if correcto:
            resultado = "perfecto" if transcurrido < paso["duracion"] / 2 else "bien"
        elif transcurrido >= paso["duracion"]:
            resultado = "fallo"
        else:
            return None
        evento = {"resultado": resultado, "puntos": self.PUNTOS[resultado],
                  "movimiento": paso["movimiento"]}
        self.resultados.append(evento)
        self.indice += 1
        return evento

    def terminado(self):
        return self.indice >= len(self.pasos)

    def puntuacion(self):
        return sum(r["puntos"] for r in self.resultados)

    def resumen(self):
        aciertos = sum(1 for r in self.resultados if r["resultado"] != "fallo")
        total = len(self.pasos)
        return {
            "puntos": self.puntuacion(),
            "aciertos": aciertos,
            "fallos": total - aciertos,
            "total_pasos": total,
            "porcentaje": 100 * aciertos / total if total else 0.0,
        }