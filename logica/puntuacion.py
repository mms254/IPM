
class GestorPuntuacion:
    """
    Gestiona las puntuaciones de uno o dos jugadores.

    Cada jugador tiene sus propios aciertos, fallos
    y puntos. Las puntuaciones son independientes.
    """

    MAX_JUGADORES = 2
    PUNTOS_RESULTADO = {
        "perfecto": 100,
        "bien": 50,
        "fallo": 0
    }

    def __init__(self, num_jugadores=1):
        self.jugadores = {}

        self.iniciar_partida(num_jugadores)

    def iniciar_partida(self, num_jugadores):
        """
        Inicializa las puntuaciones de los jugadores.
        Se permite jugar con una o dos personas.
        """

        if num_jugadores < 1 or num_jugadores > self.MAX_JUGADORES:
            raise ValueError("El juego admite uno o dos jugadores.")

        self.jugadores = {}

        for id_jugador in range(1, num_jugadores + 1):
            self.jugadores[id_jugador] = {
                "puntos": 0,
                "aciertos": 0,
                "fallos": 0,
                "resultados": [],
                "pasos_registrados": set()
            }

    def registrar_evento(self, id_jugador, indice_paso,
                         movimiento, resultado):
        """
        Registra un resultado perfecto, bueno o fallido.

        Cada jugador solamente puede registrar una vez
        el resultado de cada paso de la coreografía.
        """

        if resultado not in self.PUNTOS_RESULTADO:
            raise ValueError("Resultado no válido")
        if id_jugador not in self.jugadores:
            raise ValueError("ID de jugador no válido")

        jugador = self.jugadores[id_jugador]

        if indice_paso in jugador["pasos_registrados"]:
            return None

        jugador["pasos_registrados"].add(indice_paso)
        correcto = resultado != "fallo"
        puntos = self.PUNTOS_RESULTADO[resultado]
        if correcto:
            jugador["aciertos"] += 1
        else:
            jugador["fallos"] += 1
        jugador["puntos"] += puntos

        evento = {
            "paso": indice_paso,
            "movimiento": movimiento,
            "resultado": resultado,
            "correcto": correcto,
            "puntos": puntos
        }
        jugador["resultados"].append(evento)
        return evento

    def registrar_resultado(self, id_jugador, indice_paso,
                            movimiento, correcto):
        """Mantiene la API anterior de registro basado en acierto/fallo."""
        resultado = "bien" if correcto else "fallo"
        return self.registrar_evento(
            id_jugador, indice_paso, movimiento, resultado
        ) is not None

    def obtener_puntuacion(self, id_jugador):
        """Devuelve los puntos de un jugador."""

        if id_jugador not in self.jugadores:
            return 0

        return self.jugadores[id_jugador]["puntos"]

    def obtener_resumen(self, id_jugador, total_pasos=None):
        """Devuelve las estadísticas finales de un jugador."""

        if id_jugador not in self.jugadores:
            return None

        jugador = self.jugadores[id_jugador]

        total = (
            total_pasos
            if total_pasos is not None
            else jugador["aciertos"] + jugador["fallos"]
        )

        porcentaje = 0

        if total > 0:
            porcentaje = min(jugador["aciertos"] / total * 100, 100)

        return {
            "puntos": jugador["puntos"],
            "aciertos": jugador["aciertos"],
            "fallos": jugador["fallos"],
            "total_pasos": total,
            "porcentaje": porcentaje,
            "resultados": list(jugador["resultados"])
        }

    def obtener_resumen_completo(self):
        """Devuelve los resultados de todos los jugadores."""

        resumen = {}

        for id_jugador in self.jugadores:
            resumen[id_jugador] = self.obtener_resumen(id_jugador)

        return resumen
