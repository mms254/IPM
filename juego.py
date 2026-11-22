"""
En este archivo se actualizan los estados del juego a la pantalla activa en cada momento
"""

import sys
import pygame
import estilo as e
from vision import Camara
from pantallas import (PantallaInicio, PantallaSeleccion, PantallaJuego, PantallaResultados)

class Juego:
    PANTALLAS = {
        "inicio": PantallaInicio,
        "seleccion": PantallaSeleccion,
        "juego": PantallaJuego,
        "resultados": PantallaResultados
    }

    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((e.ANCHO, e.ALTO))
        pygame.display.set_caption(e.TITULO)
        self.reloj = pygame.time.Clock()
        self.ejecutando = True
        self.camara = Camara()
        self.num_jugadores = 1
        self.actual = PantallaInicio(self)

    def cambiar_pantalla(self, nombre, **datos):
        """
        Crea una nueva pantalla con los datos necesarios, 
        como un resumen o la canción elegida
        """
        self.actual = self.PANTALLAS[nombre](self, **datos)

    def salir(self):
        self.ejecutando = False

    def ejecutar(self):
        while self.ejecutando:
            dt = self.reloj.tick(e.FPS) / 1000 # desde el último fotograma
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.salir()
                self.actual.manejar_evento(evento)

            self.actual.actualizar(dt)
            self.actual.dibujar(self.pantalla)
            pygame.display.flip()

        self.camara.cerrar()
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    Juego().ejecutar()