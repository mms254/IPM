"""
Catálogo de movimientos y coreografías de Move & Dance.
"""

MOVIMIENTOS = {
    "brazos_arriba": {
        "nombre": "¡Brazos arriba!",
        "descripcion": "Levanta los dos brazos por encima de la cabeza.",
        "instruccion": "Levanta ambos brazos."
    },
    "brazo_izq_lateral": {
        "nombre": "Brazo izquierdo lateral",
        "descripcion": "Extiende el brazo izquierdo hacia un lado.",
        "instruccion": "Extiende el brazo izquierdo."
    },
    "brazo_der_lateral": {
        "nombre": "Brazo derecho lateral",
        "descripcion": "Extiende el brazo derecho hacia un lado.",
        "instruccion": "Extiende el brazo derecho."
    },
    "brazos_en_cruz": {
        "nombre": "Brazos en cruz",
        "descripcion": "Extiende los dos brazos horizontalmente.",
        "instruccion": "Abre los brazos en cruz."
    },
    "sentadilla": {
        "nombre": "¡Sentadilla!",
        "descripcion": "Flexiona ligeramente las dos rodillas.",
        "instruccion": "Flexiona las rodillas."
    },
    "rodilla_arriba": {
        "nombre": "Rodilla arriba",
        "descripcion": "Levanta una rodilla mientras mantienes la otra pierna apoyada.",
        "instruccion": "Levanta una rodilla."
    },
    "inclinacion_lateral": {
        "nombre": "Inclinación lateral",
        "descripcion": "Inclina suavemente el tronco hacia un lado.",
        "instruccion": "Inclina el cuerpo hacia un lado."
    },
    "brazos_alternos": {
        "nombre": "Brazos alternos",
        "descripcion": "Levanta un brazo mientras el otro permanece abajo.",
        "instruccion": "Levanta un brazo y después el otro."
    },
    "paso_lateral": {
        "nombre": "Paso lateral",
        "descripcion": "Separa los pies lateralmente.",
        "instruccion": "Abre las piernas dando un paso lateral."
    }
}

DIFICULTADES = ("facil", "medio", "dificil")


def _crear_pasos(secuencia, intervalo, duracion):
    """Crea pasos con tiempos provisionales, expresados en segundos."""
    return [
        {
            "inicio": 2.0 + indice * intervalo,
            "duracion": duracion,
            "movimiento": movimiento
        }
        for indice, movimiento in enumerate(secuencia)
    ]


CANCIONES = [
    {
        "id": "bailando",
        "titulo": "Bailando",
        "nivel": "Fácil",
        "dificultad": "facil",
        "audio": "assets/musica/bailando.mp3",
        "pasos": _crear_pasos(
            [
                "brazos_arriba",
                "brazos_en_cruz",
                "brazo_izq_lateral",
                "brazo_der_lateral",
                "sentadilla",
                "brazos_arriba"
            ],
            intervalo=3.7,
            duracion=2.8
        )
    },
    {
        "id": "cant_stop_the_feeling",
        "titulo": "Can't Stop the Feeling",
        "nivel": "Medio",
        "dificultad": "medio",
        "audio": "assets/musica/cant_stop_the_feeling.mp3",
        "pasos": _crear_pasos(
            [
                "brazos_arriba",
                "paso_lateral",
                "brazo_izq_lateral",
                "brazo_der_lateral",
                "sentadilla",
                "rodilla_arriba",
                "brazos_en_cruz",
                "inclinacion_lateral",
                "brazos_alternos",
                "brazos_arriba"
            ],
            intervalo=2.6,
            duracion=2.1
        )
    },
    {
        "id": "waka_waka",
        "titulo": "Waka Waka",
        "nivel": "Difícil",
        "dificultad": "dificil",
        "audio": "assets/musica/waka_waka.mp3",
        "pasos": _crear_pasos(
            [
                "paso_lateral",
                "brazos_arriba",
                "rodilla_arriba",
                "brazos_en_cruz",
                "sentadilla",
                "brazo_izq_lateral",
                "brazo_der_lateral",
                "inclinacion_lateral",
                "brazos_alternos",
                "rodilla_arriba",
                "paso_lateral",
                "brazos_en_cruz",
                "sentadilla",
                "brazos_arriba"
            ],
            intervalo=1.9,
            duracion=1.45
        )
    }
]


def obtener_cancion(id_cancion):
    """Busca una coreografía por su identificador."""
    return next(
        (cancion for cancion in CANCIONES if cancion["id"] == id_cancion),
        None
    )


def obtener_movimiento(id_movimiento):
    """Busca la información de un movimiento."""
    return MOVIMIENTOS.get(id_movimiento)
