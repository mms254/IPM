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

CANCIONES = [
    {
        "id": "prueba_corta",
        "titulo": "Prueba corta",
        "audio": "assets/musica/prueba_corta.ogg",
        "pasos": [
            {"inicio": 2.0,  "duracion": 3.0, "movimiento": "brazos_arriba"},
            {"inicio": 5.5,  "duracion": 3.0, "movimiento": "brazo_izq_lateral"},
            {"inicio": 9.0,  "duracion": 3.0, "movimiento": "brazo_der_lateral"},
            {"inicio": 12.5, "duracion": 3.0, "movimiento": "sentadilla"},
        ],
    },
    {
        "id": "rutina_larga",
        "titulo": "Rutina larga",
        "audio": "assets/musica/rutina_larga.ogg",
        "pasos": [
            {"inicio": 2.0 + i * 3.0, "duracion": 2.5, "movimiento": m}
            for i, m in enumerate([
                "brazos_arriba", "rodilla_arriba", "sentadilla",
                "brazo_izq_lateral", "brazo_der_lateral", "brazos_arriba",
                "sentadilla", "rodilla_arriba",
            ])
        ],
    },
]

DIFICULTADES = ["facil", "normal", "dificil"]


class MotorCoreografia:
    """Versión sencilla del motor: acierto en la 1ª mitad del paso =
    'perfecto', en la 2ª mitad = 'bien', si se acaba el tiempo = 'fallo'."""

    PUNTOS = {"perfecto": 100, "bien": 50, "fallo": 0}

    def __init__(self, cancion, dificultad="normal"):
        factor = {"facil": 1.3, "normal": 1.0, "dificil": 0.75}[dificultad]
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