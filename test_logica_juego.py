import unittest
from random import Random

from coreografias import (
    CANCIONES,
    MOVIMIENTOS,
    crear_coreografia_aleatoria
)
from motor_coreografia import MotorCoreografia, PartidaCoreografia
from movimientos_logica_juego import DETECTORES, comprobar_movimiento
from puntuacion import GestorPuntuacion


class CoreografiasTests(unittest.TestCase):
    def test_canciones_tienen_el_numero_de_pasos_y_niveles_acordados(self):
        self.assertEqual(
            [(cancion["titulo"], len(cancion["pasos"]), cancion["dificultad"])
             for cancion in CANCIONES],
            [
                ("Bailando", 6, "facil"),
                ("Can't Stop the Feeling", 10, "medio"),
                ("Waka Waka", 14, "dificil"),
                ("Shape of You", 6, "facil"),
                ("La Bicicleta", 6, "facil"),
                ("Moves Like Jagger", 10, "medio"),
                ("Señorita", 10, "medio"),
                ("Aserejé", 14, "dificil"),
                ("Gasolina", 14, "dificil")
            ]
        )
        for cancion in CANCIONES:
            for paso in cancion["pasos"]:
                self.assertIn(paso["movimiento"], MOVIMIENTOS)

    def test_cancion_conserva_sus_tiempos_y_su_nivel_es_fijo(self):
        cancion = CANCIONES[0]
        motor = MotorCoreografia(cancion, rng=Random(10))
        self.assertEqual(
            [(paso["inicio"], paso["duracion"]) for paso in motor.pasos],
            [(paso["inicio"], paso["duracion"]) for paso in cancion["pasos"]]
        )
        self.assertEqual(motor.dificultad, "facil")
        with self.assertRaises(ValueError):
            MotorCoreografia(cancion, "dificil")

    def test_coreografias_aleatorias_respetan_cantidad_y_cambian_secuencia(self):
        for cancion in CANCIONES:
            primera = crear_coreografia_aleatoria(cancion, Random(10))
            segunda = crear_coreografia_aleatoria(cancion, Random(20))
            self.assertEqual(len(primera["pasos"]), len(cancion["pasos"]))
            self.assertEqual(len(segunda["pasos"]), len(cancion["pasos"]))
            self.assertNotEqual(
                [paso["movimiento"] for paso in primera["pasos"]],
                [paso["movimiento"] for paso in segunda["pasos"]]
            )
            for paso in primera["pasos"] + segunda["pasos"]:
                self.assertIn(paso["movimiento"], MOVIMIENTOS)
            self.assertEqual(
                len({paso["movimiento"] for paso in primera["pasos"]}),
                len(primera["pasos"])
            )
            rango = {"facil": 0, "medio": 1, "dificil": 2}
            for paso in primera["pasos"]:
                self.assertLessEqual(
                    rango[MOVIMIENTOS[paso["movimiento"]]["dificultad"]],
                    rango[cancion["dificultad"]]
                )

    def test_no_repite_la_ultima_secuencia_de_una_cancion(self):
        cancion = {
            **CANCIONES[0],
            "id": "test_no_repetir_secuencia"
        }
        primera = crear_coreografia_aleatoria(cancion, Random(5))
        segunda = crear_coreografia_aleatoria(cancion, Random(5))
        self.assertNotEqual(
            [paso["movimiento"] for paso in primera["pasos"]],
            [paso["movimiento"] for paso in segunda["pasos"]]
        )

    def test_detectores_cubren_todos_los_movimientos_del_catalogo(self):
        self.assertEqual(set(MOVIMIENTOS), set(DETECTORES))

    def test_detecta_los_movimientos_nuevos(self):
        puntos = {
            "hombro_izquierdo": {"x": 0.4, "y": 0.3, "visibilidad": 1.0},
            "hombro_derecho": {"x": 0.6, "y": 0.3, "visibilidad": 1.0},
            "cadera_izquierda": {"x": 0.4, "y": 0.6, "visibilidad": 1.0},
            "cadera_derecha": {"x": 0.6, "y": 0.6, "visibilidad": 1.0},
            "muneca_izquierda": {"x": 0.4, "y": 0.6, "visibilidad": 1.0},
            "muneca_derecha": {"x": 0.6, "y": 0.6, "visibilidad": 1.0},
            "rodilla_izquierda": {"x": 0.4, "y": 0.8, "visibilidad": 1.0},
            "rodilla_derecha": {"x": 0.6, "y": 0.8, "visibilidad": 1.0},
            "tobillo_izquierdo": {"x": 0.49, "y": 0.95, "visibilidad": 1.0},
            "tobillo_derecho": {"x": 0.51, "y": 0.95, "visibilidad": 1.0}
        }
        self.assertTrue(comprobar_movimiento(puntos, "manos_caderas"))
        self.assertTrue(comprobar_movimiento(puntos, "pies_juntos"))

        puntos["muneca_izquierda"] = {"x": 0.6, "y": 0.3, "visibilidad": 1.0}
        puntos["muneca_derecha"] = {"x": 0.4, "y": 0.3, "visibilidad": 1.0}
        self.assertTrue(comprobar_movimiento(puntos, "brazos_cruzados"))

        puntos["muneca_izquierda"] = {"x": 0.4, "y": 0.3, "visibilidad": 1.0}
        puntos["muneca_derecha"] = {"x": 0.6, "y": 0.3, "visibilidad": 1.0}
        self.assertTrue(comprobar_movimiento(puntos, "manos_hombros"))

        puntos["muneca_izquierda"] = {"x": 0.4, "y": 0.8, "visibilidad": 1.0}
        puntos["muneca_derecha"] = {"x": 0.6, "y": 0.8, "visibilidad": 1.0}
        self.assertTrue(comprobar_movimiento(puntos, "toque_rodilla"))

        puntos["muneca_izquierda"] = {"x": 0.4, "y": 0.7, "visibilidad": 1.0}
        puntos["muneca_derecha"] = {"x": 0.6, "y": 0.7, "visibilidad": 1.0}
        self.assertTrue(comprobar_movimiento(puntos, "brazos_abajo"))

    def test_detecta_estrella_con_brazos_arriba_y_pies_separados(self):
        puntos = {
            "hombro_izquierdo": {"x": 0.4, "y": 0.3, "visibilidad": 1.0},
            "hombro_derecho": {"x": 0.6, "y": 0.3, "visibilidad": 1.0},
            "cadera_izquierda": {"x": 0.4, "y": 0.6, "visibilidad": 1.0},
            "cadera_derecha": {"x": 0.6, "y": 0.6, "visibilidad": 1.0},
            "muneca_izquierda": {"x": 0.3, "y": 0.1, "visibilidad": 1.0},
            "muneca_derecha": {"x": 0.7, "y": 0.1, "visibilidad": 1.0},
            "tobillo_izquierdo": {"x": 0.3, "y": 0.95, "visibilidad": 1.0},
            "tobillo_derecho": {"x": 0.7, "y": 0.95, "visibilidad": 1.0}
        }
        self.assertTrue(comprobar_movimiento(puntos, "estrella"))

        puntos["tobillo_derecho"]["x"] = 0.55
        self.assertFalse(comprobar_movimiento(puntos, "estrella"))

    def test_detecta_mano_a_rodilla_contraria(self):
        puntos = {
            "hombro_izquierdo": {"x": 0.4, "y": 0.3, "visibilidad": 1.0},
            "hombro_derecho": {"x": 0.6, "y": 0.3, "visibilidad": 1.0},
            "cadera_izquierda": {"x": 0.4, "y": 0.6, "visibilidad": 1.0},
            "cadera_derecha": {"x": 0.6, "y": 0.6, "visibilidad": 1.0},
            "rodilla_izquierda": {"x": 0.35, "y": 0.85, "visibilidad": 1.0},
            "rodilla_derecha": {"x": 0.65, "y": 0.85, "visibilidad": 1.0},
            "muneca_izquierda": {"x": 0.64, "y": 0.86, "visibilidad": 1.0},
            "muneca_derecha": {"x": 0.45, "y": 0.45, "visibilidad": 1.0}
        }
        self.assertTrue(
            comprobar_movimiento(puntos, "mano_rodilla_contraria")
        )

        puntos["muneca_izquierda"]["x"] = 0.35
        puntos["muneca_izquierda"]["y"] = 0.85
        self.assertFalse(
            comprobar_movimiento(puntos, "mano_rodilla_contraria")
        )

    def test_una_partida_comparte_la_misma_coreografia_entre_jugadores(self):
        partida = PartidaCoreografia(
            CANCIONES[0],
            ("jugador_1", "jugador_2")
        )
        self.assertEqual(
            partida.motores["jugador_1"].pasos,
            partida.motores["jugador_2"].pasos
        )
        self.assertEqual(partida.cancion["pasos"], partida.motores["jugador_1"].pasos)

    def test_puntuaciones_de_dos_jugadores_son_independientes(self):
        cancion = {
            "dificultad": "medio",
            "pasos": [
                {"inicio": 1.0, "duracion": 1.0, "movimiento": "brazos_arriba"}
            ]
        }
        partida = PartidaCoreografia(
            cancion,
            ("jugador_1", "jugador_2"),
            aleatorizar=False
        )
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
