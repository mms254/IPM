"""
Catálogo de movimientos y coreografías de Move & Dance.
"""

import random

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
    "brazos_en_cruz": {
        "nombre": "Brazos en cruz",
        "descripcion": "Extiende los dos brazos horizontalmente.",
        "instruccion": "Abre los brazos en cruz.",
        "dificultad": "facil"
    },
    "sentadilla": {
        "nombre": "¡Sentadilla!",
        "descripcion": "Flexiona ligeramente las dos rodillas.",
        "instruccion": "Flexiona las rodillas.",
        "dificultad": "medio"
    },
    "rodilla_arriba": {
        "nombre": "Rodilla arriba",
        "descripcion": "Levanta una rodilla mientras mantienes la otra pierna apoyada.",
        "instruccion": "Levanta una rodilla.",
        "dificultad": "medio"
    },
    "inclinacion_lateral": {
        "nombre": "Inclinación lateral",
        "descripcion": "Inclina suavemente el tronco hacia un lado.",
        "instruccion": "Inclina el cuerpo hacia un lado.",
        "dificultad": "medio"
    },
    "brazos_alternos": {
        "nombre": "Brazos alternos",
        "descripcion": "Levanta un brazo mientras el otro permanece abajo.",
        "instruccion": "Levanta un brazo y después el otro.",
        "dificultad": "medio"
    },
    "paso_lateral": {
        "nombre": "Paso lateral",
        "descripcion": "Separa los pies lateralmente.",
        "instruccion": "Abre las piernas dando un paso lateral.",
        "dificultad": "medio"
    },
    "manos_caderas": {
        "nombre": "Manos en las caderas",
        "descripcion": "Apoya las dos manos sobre las caderas.",
        "instruccion": "Pon las manos en las caderas.",
        "dificultad": "facil"
    },
    "brazos_cruzados": {
        "nombre": "Brazos cruzados",
        "descripcion": "Cruza los brazos delante del pecho.",
        "instruccion": "Cruza los brazos delante del pecho.",
        "dificultad": "medio"
    },
    "pies_juntos": {
        "nombre": "Pies juntos",
        "descripcion": "Junta los pies manteniendo el equilibrio.",
        "instruccion": "Junta los pies.",
        "dificultad": "facil"
    },
    "brazos_abajo": {
        "nombre": "Brazos abajo",
        "descripcion": "Mantén las dos manos por debajo de las caderas.",
        "instruccion": "Baja los brazos.",
        "dificultad": "facil"
    },
    "manos_hombros": {
        "nombre": "Manos en los hombros",
        "descripcion": "Lleva cada mano hacia el hombro del mismo lado.",
        "instruccion": "Toca tus hombros.",
        "dificultad": "facil"
    },
    "toque_rodilla": {
        "nombre": "Toca las rodillas",
        "descripcion": "Inclínate y acerca las manos a las rodillas.",
        "instruccion": "Toca tus rodillas.",
        "dificultad": "dificil"
    },
    "estrella": {
        "nombre": "¡Estrella!",
        "descripcion": "Levanta los brazos y separa los pies.",
        "instruccion": "Levanta los brazos y abre las piernas.",
        "dificultad": "medio"
    },
    "mano_rodilla_contraria": {
        "nombre": "Mano a la rodilla contraria",
        "descripcion": "Inclínate y toca una rodilla con la mano opuesta.",
        "instruccion": "Toca la rodilla derecha con la mano izquierda, o al revés.",
        "dificultad": "dificil"
    }
}

DIFICULTADES = ("facil", "medio", "dificil")
_ULTIMAS_SECUENCIAS = {}


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


def _catalogo_por_dificultad(dificultad):
    if dificultad == "normal":
        dificultad = "medio"
    niveles = {"facil": 0, "medio": 1, "dificil": 2}
    if dificultad not in niveles:
        raise ValueError("Dificultad no válida")

    return [
        id_movimiento
        for id_movimiento, movimiento in MOVIMIENTOS.items()
        if niveles[movimiento["dificultad"]] <= niveles[dificultad]
    ]


def generar_secuencia_aleatoria(cantidad, rng=None, dificultad="dificil"):
    """Genera movimientos del nivel indicado, evitando repeticiones seguidas."""
    if not isinstance(cantidad, int) or cantidad < 0:
        raise ValueError("La cantidad de pasos debe ser un entero no negativo")

    generador = random if rng is None else rng
    catalogo = _catalogo_por_dificultad(dificultad)
    if cantidad and not catalogo:
        raise ValueError("No hay movimientos disponibles")

    secuencia = []
    while len(secuencia) < cantidad:
        bloque = generador.sample(catalogo, len(catalogo))
        if secuencia and bloque[0] == secuencia[-1] and len(bloque) > 1:
            indice = next(
                indice
                for indice, movimiento in enumerate(bloque[1:], start=1)
                if movimiento != secuencia[-1]
            )
            bloque[0], bloque[indice] = bloque[indice], bloque[0]
        secuencia.extend(bloque)

    return secuencia[:cantidad]


def crear_coreografia_aleatoria(cancion, rng=None):
    """Devuelve una copia aleatoria, distinta a la anterior de esa canción."""
    pasos = cancion.get("pasos")
    if not pasos:
        raise ValueError("La coreografía no tiene pasos")

    dificultad = cancion.get("dificultad", "dificil")
    generador = random if rng is None else rng
    movimientos = generar_secuencia_aleatoria(
        len(pasos),
        generador,
        dificultad
    )
    id_cancion = cancion.get("id")
    if id_cancion is not None:
        anterior = _ULTIMAS_SECUENCIAS.get(id_cancion)
        if anterior == tuple(movimientos):
            catalogo = _catalogo_por_dificultad(dificultad)
            usados = set(movimientos)
            for indice, movimiento in enumerate(movimientos):
                alternativas = [
                    candidato
                    for candidato in catalogo
                    if candidato != movimiento and candidato not in usados
                ]
                if alternativas:
                    movimientos[indice] = generador.choice(alternativas)
                    break
        _ULTIMAS_SECUENCIAS[id_cancion] = tuple(movimientos)

    pasos_aleatorios = [
        {**paso, "movimiento": movimiento}
        for paso, movimiento in zip(pasos, movimientos)
    ]
    return {**cancion, "pasos": pasos_aleatorios}


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
    },
    {
        "id": "shape_of_you",
        "titulo": "Shape of You",
        "nivel": "Fácil",
        "dificultad": "facil",
        "audio": "assets/musica/shape_of_you.mp3",
        "pasos": _crear_pasos(
            [
                "brazos_arriba",
                "brazo_izq_lateral",
                "brazo_der_lateral",
                "manos_caderas",
                "brazos_en_cruz",
                "brazos_arriba"
            ],
            intervalo=3.7,
            duracion=2.8
        )
    },
    {
        "id": "la_bicicleta",
        "titulo": "La Bicicleta",
        "nivel": "Fácil",
        "dificultad": "facil",
        "audio": "assets/musica/la_bicicleta.mp3",
        "pasos": _crear_pasos(
            [
                "brazos_en_cruz",
                "manos_hombros",
                "brazo_izq_lateral",
                "brazo_der_lateral",
                "pies_juntos",
                "brazos_arriba"
            ],
            intervalo=3.7,
            duracion=2.8
        )
    },
    {
        "id": "moves_like_jagger",
        "titulo": "Moves Like Jagger",
        "nivel": "Medio",
        "dificultad": "medio",
        "audio": "assets/musica/moves_like_jagger.mp3",
        "pasos": _crear_pasos(
            [
                "brazos_arriba",
                "inclinacion_lateral",
                "brazo_izq_lateral",
                "brazo_der_lateral",
                "rodilla_arriba",
                "paso_lateral",
                "brazos_alternos",
                "estrella",
                "sentadilla",
                "brazos_en_cruz"
            ],
            intervalo=2.6,
            duracion=2.1
        )
    },
    {
        "id": "senorita",
        "titulo": "Señorita",
        "nivel": "Medio",
        "dificultad": "medio",
        "audio": "assets/musica/senorita.mp3",
        "pasos": _crear_pasos(
            [
                "brazos_en_cruz",
                "paso_lateral",
                "brazos_alternos",
                "rodilla_arriba",
                "inclinacion_lateral",
                "brazos_arriba",
                "sentadilla",
                "estrella",
                "brazo_izq_lateral",
                "brazo_der_lateral"
            ],
            intervalo=2.6,
            duracion=2.1
        )
    },
    {
        "id": "asereje",
        "titulo": "Aserejé",
        "nivel": "Difícil",
        "dificultad": "dificil",
        "audio": "assets/musica/asereje.mp3",
        "pasos": _crear_pasos(
            [
                "brazos_cruzados",
                "brazos_arriba",
                "paso_lateral",
                "rodilla_arriba",
                "brazos_en_cruz",
                "sentadilla",
                "mano_rodilla_contraria",
                "estrella",
                "inclinacion_lateral",
                "brazos_alternos",
                "toque_rodilla",
                "brazo_izq_lateral",
                "brazo_der_lateral",
                "brazos_arriba"
            ],
            intervalo=1.9,
            duracion=1.45
        )
    },
    {
        "id": "gasolina",
        "titulo": "Gasolina",
        "nivel": "Difícil",
        "dificultad": "dificil",
        "audio": "assets/musica/gasolina.mp3",
        "pasos": _crear_pasos(
            [
                "sentadilla",
                "brazos_arriba",
                "estrella",
                "rodilla_arriba",
                "mano_rodilla_contraria",
                "paso_lateral",
                "brazos_en_cruz",
                "toque_rodilla",
                "inclinacion_lateral",
                "brazos_alternos",
                "rodilla_arriba",
                "sentadilla",
                "estrella",
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
