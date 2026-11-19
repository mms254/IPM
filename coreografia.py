
"""
Definición de los movimientos y coreografías del juego Move & Dance.
"""

# ---------------------------------------------------------
# 1. CATÁLOGO DE MOVIMIENTOS
# ---------------------------------------------------------

MOVIMIENTOS = {
    "brazos_arriba": {
        "nombre": "¡Brazos arriba!",
        "descripcion": "Levanta los dos brazos por encima de la cabeza.",
        "instruccion": "Levanta ambos brazos.",
        "dificultad": "facil"
    },

    "brazo_izq_lateral": {
        "nombre": "Brazo izquierdo lateral",
        "descripcion": "Extiende el brazo izquierdo hacia un lado.",
        "instruccion": "Extiende el brazo izquierdo.",
        "dificultad": "facil"
    },

    "brazo_der_lateral": {
        "nombre": "Brazo derecho lateral",
        "descripcion": "Extiende el brazo derecho hacia un lado.",
        "instruccion": "Extiende el brazo derecho.",
        "dificultad": "facil"
    },

    "sentadilla": {
        "nombre": "¡Sentadilla!",
        "descripcion": "Flexiona las dos rodillas ligeramente.",
        "instruccion": "Flexiona las rodillas.",
        "dificultad": "media"
    },

    "rodilla_arriba": {
        "nombre": "Rodilla arriba",
        "descripcion": "Levanta una rodilla mientras mantienes la otra pierna apoyada.",
        "instruccion": "Levanta una rodilla.",
        "dificultad": "media"
    }
}


# ---------------------------------------------------------
# 2. CATÁLOGO DE CANCIONES Y COREOGRAFÍAS
# ---------------------------------------------------------

CANCIONES = [
    {
        "id": "prueba_corta",
        "titulo": "Primera coreografía",
        "audio": "assets/musica/prueba_corta.ogg",

        "pasos": [
            {
                "inicio": 2.0,
                "duracion": 3.0,
                "movimiento": "brazos_arriba"
            },
            {
                "inicio": 5.5,
                "duracion": 3.0,
                "movimiento": "brazo_izq_lateral"
            },
            {
                "inicio": 9.0,
                "duracion": 3.0,
                "movimiento": "brazo_der_lateral"
            },
            {
                "inicio": 12.5,
                "duracion": 3.0,
                "movimiento": "sentadilla"
            },
            {
                "inicio": 16.0,
                "duracion": 3.0,
                "movimiento": "rodilla_arriba"
            }
        ]
    },

    {
        "id": "rutina_larga",
        "titulo": "¡A bailar!",
        "audio": "assets/musica/rutina_larga.ogg",

        "pasos": [
            {
                "inicio": 2.0,
                "duracion": 2.5,
                "movimiento": "brazos_arriba"
            },
            {
                "inicio": 5.0,
                "duracion": 2.5,
                "movimiento": "rodilla_arriba"
            },
            {
                "inicio": 8.0,
                "duracion": 2.5,
                "movimiento": "sentadilla"
            },
            {
                "inicio": 11.0,
                "duracion": 2.5,
                "movimiento": "brazo_izq_lateral"
            },
            {
                "inicio": 14.0,
                "duracion": 2.5,
                "movimiento": "brazo_der_lateral"
            },
            {
                "inicio": 17.0,
                "duracion": 2.5,
                "movimiento": "brazos_arriba"
            }
        ]
    }
]


# ---------------------------------------------------------
# 3. DIFICULTADES
# ---------------------------------------------------------

DIFICULTADES = {
    "facil": {
        "factor_tiempo": 1.3
    },

    "normal": {
        "factor_tiempo": 1.0
    },

    "dificil": {
        "factor_tiempo": 0.75
    }
}


# ---------------------------------------------------------
# 4. FUNCIONES AUXILIARES
# ---------------------------------------------------------

def obtener_cancion(id_cancion):
    """Devuelve una canción a partir de su identificador."""

    for cancion in CANCIONES:
        if cancion["id"] == id_cancion:
            return cancion

    return None


def obtener_movimiento(id_movimiento):
    """Devuelve la información de un movimiento."""

    return MOVIMIENTOS.get(id_movimiento)
