
"""
Motor de coreografías de Move & Dance.
"""

from collections.abc import Mapping

from coreografias import DIFICULTADES, crear_coreografia_aleatoria
from movimientos_logica_juego import comprobar_movimiento
from puntuacion import GestorPuntuacion


class MotorCoreografia:

    def __init__(
        self,
        cancion,
        dificultad=None,
        puntuacionador=None,
        id_jugador=1,
        aleatorizar=True,
        rng=None
    ):
        pasos = cancion.get("pasos")
        if not pasos:
            raise ValueError("La coreografía no tiene pasos")

        dificultad_cancion = cancion.get("dificultad")
        dificultad_solicitada = self._normalizar_dificultad(dificultad)

        if dificultad_cancion is None:
            dificultad_cancion = dificultad_solicitada or "medio"
        else:
            dificultad_cancion = self._normalizar_dificultad(
                dificultad_cancion
            )

        if dificultad_cancion not in DIFICULTADES:
            raise ValueError("La canción tiene una dificultad no válida")
        if (
            dificultad_solicitada is not None
            and dificultad_solicitada != dificultad_cancion
        ):
            raise ValueError(
                "La dificultad de esta canción es fija y no se puede cambiar"
            )

        self.dificultad = dificultad_cancion
        if aleatorizar:
            cancion = crear_coreografia_aleatoria(cancion, rng)
        self.cancion = cancion
        # Los tiempos pertenecen al audio y no se deben escalar según el nivel.
        self.pasos = [dict(paso) for paso in cancion["pasos"]]

        ultimo = self.pasos[-1]
        self.duracion_total = ultimo["inicio"] + ultimo["duracion"] + 1.0

        self.indice = 0
        self.puntuacionador = puntuacionador or GestorPuntuacion(1)
        self.id_jugador = id_jugador
        self.tiempo_correcto = 0.0
        self.tiempo_estable = 0.25

    @staticmethod
    def _normalizar_dificultad(dificultad):
        if dificultad == "normal":
            return "medio"
        return dificultad

    def paso_actual(self, t):
        """Devuelve el paso que está activo en el instante t."""

        if self.indice >= len(self.pasos):
            return None

        paso = self.pasos[self.indice]

        if paso["inicio"] <= t < paso["inicio"] + paso["duracion"]:
            return paso

        return None

    def siguiente_paso(self, t):
        """Devuelve el próximo paso pendiente."""

        if self.indice >= len(self.pasos):
            return None

        paso = self.pasos[self.indice]

        if t < paso["inicio"]:
            return paso

        return (
            self.pasos[self.indice + 1]
            if self.indice + 1 < len(self.pasos)
            else None
        )

    def actualizar(self, t, correcto, dt=0.0):
        """
        Actualiza el estado de la coreografía.

        t: segundos transcurridos desde el inicio.
        correcto: True si el jugador realiza el movimiento esperado.
        dt: tiempo transcurrido desde la última actualización, en segundos.
        """

        if dt < 0:
            raise ValueError("dt no puede ser negativo")
        if self.terminado():
            return None

        paso = self.pasos[self.indice]
        fin_paso = paso["inicio"] + paso["duracion"]

        if t < paso["inicio"]:
            return None

        transcurrido = t - paso["inicio"]

        if t >= fin_paso:
            return self._registrar("fallo", paso)

        if correcto:
            inicio_muestra = max(t - dt, paso["inicio"])
            fin_muestra = min(t, fin_paso)
            self.tiempo_correcto += max(0.0, fin_muestra - inicio_muestra)
        else:
            self.tiempo_correcto = 0.0

        if self.tiempo_correcto >= self.tiempo_estable:
            if transcurrido < paso["duracion"] / 2:
                resultado = "perfecto"
            else:
                resultado = "bien"
            return self._registrar(resultado, paso)

        return None

    def _registrar(self, resultado, paso):
        """Registra el resultado y pasa al siguiente movimiento."""

        evento = self.puntuacionador.registrar_evento(
            self.id_jugador,
            self.indice,
            paso["movimiento"],
            resultado
        )
        if evento is None:
            raise RuntimeError("El paso ya tenía un resultado registrado")

        self.indice += 1
        self.tiempo_correcto = 0.0

        return evento

    def terminado(self):
        """Comprueba si se han completado todos los pasos."""

        return self.indice >= len(self.pasos)

    def puntuacion(self):
        """Devuelve los puntos acumulados."""
        return self.puntuacionador.obtener_puntuacion(self.id_jugador)

    def resumen(self):
        """Devuelve el resumen de la partida."""
        return self.puntuacionador.obtener_resumen(
            self.id_jugador,
            total_pasos=len(self.pasos)
        )


class PartidaCoreografia:
    """Coordina una coreografía con puntuaciones independientes por jugador."""

    MAX_JUGADORES = 2

    def __init__(self, cancion, jugadores, aleatorizar=True, rng=None):
        if isinstance(jugadores, str):
            raise ValueError("Indica los jugadores como una colección de IDs")

        ids = tuple(jugadores)
        if not 1 <= len(ids) <= self.MAX_JUGADORES:
            raise ValueError("La partida debe tener uno o dos jugadores")
        if any(
            not isinstance(id_jugador, str) or not id_jugador
            for id_jugador in ids
        ):
            raise ValueError("Cada jugador debe tener un ID de texto no vacío")
        if len(set(ids)) != len(ids):
            raise ValueError("Los IDs de jugador deben ser únicos")

        self.cancion = (
            crear_coreografia_aleatoria(cancion, rng)
            if aleatorizar
            else cancion
        )
        self.puntuacionador = GestorPuntuacion(len(ids))
        self._indices_jugador = {
            id_jugador: indice
            for indice, id_jugador in enumerate(ids, start=1)
        }
        self.motores = {
            id_jugador: MotorCoreografia(
                self.cancion,
                puntuacionador=self.puntuacionador,
                id_jugador=self._indices_jugador[id_jugador],
                aleatorizar=False
            )
            for id_jugador in ids
        }

    def actualizar(self, t, puntos_por_jugador, dt):
        """
        Actualiza cada jugador usando su propio conjunto de puntos corporales.

        Los IDs deben mantenerse estables durante la partida. Si un jugador no
        aparece en un fotograma, se considera que no está haciendo el paso.
        """
        if not isinstance(puntos_por_jugador, Mapping):
            raise TypeError("Los puntos deben ser un mapeo de ID a articulaciones")

        desconocidos = set(puntos_por_jugador) - set(self.motores)
        if desconocidos:
            raise ValueError("Se recibieron IDs de jugador no registrados")

        eventos = {}
        for id_jugador, motor in self.motores.items():
            paso = motor.paso_actual(t)
            puntos = puntos_por_jugador.get(id_jugador)
            correcto = (
                paso is not None
                and comprobar_movimiento(puntos, paso["movimiento"])
            )
            evento = motor.actualizar(t, correcto, dt)
            if evento is not None:
                eventos[id_jugador] = {
                    **evento,
                    "jugador_id": id_jugador
                }

        return eventos

    def puntuaciones(self):
        """Devuelve los puntos acumulados de cada jugador."""
        return {
            id_jugador: motor.puntuacion()
            for id_jugador, motor in self.motores.items()
        }

    def resumen(self):
        """Devuelve un resumen independiente para cada jugador."""
        return {
            id_jugador: motor.resumen()
            for id_jugador, motor in self.motores.items()
        }

    def terminado(self):
        """Indica si todos los jugadores han completado la coreografía."""
        return all(motor.terminado() for motor in self.motores.values())
