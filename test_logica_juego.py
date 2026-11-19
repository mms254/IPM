import unittest

from coreografias import CANCIONES, MOVIMIENTOS
from motor_coreografia import MotorCoreografia, PartidaCoreografia
from puntuacion import GestorPuntuacion


class CoreografiasTests(unittest.TestCase):
    def test_canciones_tienen_el_numero_de_pasos_y_niveles_acordados(self):
        self.assertEqual(
            [(cancion["titulo"], len(cancion["pasos"]), cancion["dificultad"])
             for cancion in CANCIONES],
            [
                ("Bailando", 6, "facil"),
                ("Can't Stop the Feeling", 10, "medio"),
                ("Waka Waka", 14, "dificil")
            ]
        )
        for cancion in CANCIONES:
            for paso in cancion["pasos"]:
                self.assertIn(paso["movimiento"], MOVIMIENTOS)

    def test_cancion_conserva_sus_tiempos_y_su_nivel_es_fijo(self):
        cancion = CANCIONES[0]
        motor = MotorCoreografia(cancion)
        self.assertEqual(motor.pasos, cancion["pasos"])
        self.assertEqual(motor.dificultad, "facil")
        with self.assertRaises(ValueError):
            MotorCoreografia(cancion, "dificil")

    def test_puntuaciones_de_dos_jugadores_son_independientes(self):
        cancion = {
            "dificultad": "medio",
            "pasos": [
                {"inicio": 1.0, "duracion": 1.0, "movimiento": "brazos_arriba"}
            ]
        }
        partida = PartidaCoreografia(cancion, ("jugador_1", "jugador_2"))
        puntos_correctos = {
            "hombro_izquierdo": {"x": 0.4, "y": 0.3, "visibilidad": 1.0},
            "hombro_derecho": {"x": 0.6, "y": 0.3, "visibilidad": 1.0},
            "cadera_izquierda": {"x": 0.4, "y": 0.6, "visibilidad": 1.0},
            "cadera_derecha": {"x": 0.6, "y": 0.6, "visibilidad": 1.0},
            "muneca_izquierda": {"x": 0.3, "y": 0.1, "visibilidad": 1.0},
            "muneca_derecha": {"x": 0.7, "y": 0.1, "visibilidad": 1.0}
        }

        partida.actualizar(
            1.1,
            {"jugador_1": puntos_correctos, "jugador_2": None},
            0.2
        )
        eventos = partida.actualizar(
            1.4,
            {"jugador_1": puntos_correctos, "jugador_2": None},
            0.3
        )
        self.assertEqual(eventos["jugador_1"]["resultado"], "perfecto")
        self.assertNotIn("jugador_2", eventos)

        eventos = partida.actualizar(2.0, {}, 0.6)
        self.assertEqual(eventos["jugador_2"]["resultado"], "fallo")
        self.assertEqual(
            partida.puntuaciones(),
            {"jugador_1": 100, "jugador_2": 0}
        )
        self.assertEqual(partida.resumen()["jugador_2"]["fallos"], 1)

    def test_partida_rechaza_mas_de_dos_jugadores(self):
        with self.assertRaises(ValueError):
            PartidaCoreografia(CANCIONES[0], ("jugador_1", "jugador_2", "jugador_3"))

    def test_partida_admite_un_jugador(self):
        partida = PartidaCoreografia(CANCIONES[0], ("jugador_1",))
        self.assertEqual(partida.puntuaciones(), {"jugador_1": 0})

    def test_puntuacion_perfecto_bien_y_fallo(self):
        puntuacion = GestorPuntuacion(1)
        puntuacion.registrar_evento(1, 0, "brazos_arriba", "perfecto")
        puntuacion.registrar_evento(1, 1, "sentadilla", "bien")
        puntuacion.registrar_evento(1, 2, "rodilla_arriba", "fallo")

        resumen = puntuacion.obtener_resumen(1)
        self.assertEqual(resumen["puntos"], 150)
        self.assertEqual(resumen["aciertos"], 2)
        self.assertEqual(resumen["fallos"], 1)


if __name__ == "__main__":
    unittest.main()
