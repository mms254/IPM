"""
4 pantallas del juego
"""

import pygame
import estilo as e
from simulacion import (comprobar_movimiento, MOVIMIENTOS, CANCIONES, 
DIFICULTADES, MotorCoreografia)

class Pantalla:
    def __init__(self, juego):
        self.juego = juego

    def manejar_evento(self, evento):
        pass

    def actualizar(self, dt):
        pass

    def dibujar(self, pantalla):
        pass


class PantallaInicio(Pantalla):
    def __init__(self, juego):
        super().__init__(juego)
        self.tiempo = 0.0

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                self.juego.cambiar_pantalla("seleccion")
            elif evento.key == pygame.K_ESCAPE:
                self.juego.salir()

    def actualizar(self, dt):
        self.tiempo += dt

    def dibujar(self, pantalla):
        pantalla.fill(e.FONDO)
        e.texto(pantalla, e.TITULO, 140, e.ACENTO, centro=(e.ANCHO//2, 250))
        e.texto(pantalla, "Baila para sumar puntos", 44, e.TEXTO_SUAVE, centro=(e.ANCHO//2, 340))
        if int(self.tiempo * 2) % 2 == 0:
            e.texto(pantalla, "Pulsa ENTER para empezar", 48, e.TEXTO, centro=(e.ANCHO//2, 520))
        e.texto(pantalla, "Pulsa ESC para salir", 32, e.TEXTO_SUAVE, centro=(e.ANCHO//2, 640))

    
class PantallaSeleccion(Pantalla):
    def __init__(self, juego):
        super().__init__(juego)
        self.cancion = 0
        self.dificultad = 1

    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return
        if evento.key == pygame.K_UP:
            self.cancion = (self.cancion - 1) % len(CANCIONES)
        elif evento.key == pygame.K_DOWN:
            self.cancion = (self.cancion + 1) % len(CANCIONES)
        elif evento.key == pygame.K_LEFT:
            self.dificultad = max(0, self.dificultad - 1)
        elif evento.key == pygame.K_RIGHT:
            self.dificultad = min(len(DIFICULTADES) - 1, self.dificultad + 1)
        elif evento.key == pygame.K_RETURN:
            self.juego.cambiar_pantalla(
                "juego",
                cancion=CANCIONES[self.cancion],
                dificultad=DIFICULTADES[self.dificultad],
            )
        elif evento.key == pygame.K_ESCAPE:
            self.juego.cambiar_pantalla("inicio")

    def dibujar(self, pantalla):
        pantalla.fill(e.FONDO)
        e.texto(pantalla, "Elige canción", 80, e.TEXTO, centro=(e.ANCHO // 2, 90))

        for i, cancion in enumerate(CANCIONES):
            seleccionada = i == self.cancion
            rect = pygame.Rect(0, 0, 700, 80)
            rect.center = (e.ANCHO // 2, 220 + i * 100)
            color = e.ACENTO if seleccionada else e.FONDO_CLARO
            pygame.draw.rect(pantalla, color, rect, border_radius=16)
            info = f'{cancion["titulo"]}   ({len(cancion["pasos"])} pasos)'
            e.texto(pantalla, info, 44, e.TEXTO, centro=rect.center)

        nombre_dif = DIFICULTADES[self.dificultad].upper()
        e.texto(pantalla, f"Dificultad:  <  {nombre_dif}  >", 48, e.AMARILLO,
                centro=(e.ANCHO // 2, 560))
        e.texto(pantalla, "Flechas: elegir   ENTER: jugar   ESC: volver", 32,
                e.TEXTO_SUAVE, centro=(e.ANCHO // 2, 660))


class PantallaJuego(Pantalla):
    COLOR_RESULTADO = {
        "perfecto": e.VERDE,
        "bien": e.AMARILLO,
        "fallo": e.ROJO
    }
    
    TEXTO_RESULTADO = {
        "perfecto": "¡PERFECTO!",
        "bien": "¡BIEN!",
        "fallo": "FALLO"
    }

    def __init__(self, juego, cancion, dificultad):
        super().__init__(juego)
        self.cancion = cancion
        self.dificultad = dificultad
        self.motor = MotorCoreografia(cancion, dificultad)
        self.t = 0.0 # segundos desde el inicio de la canción
        self.mensaje = None # último resultado
        self.tiempo_mensaje = 0.0

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.juego.cambiar_pantalla("seleccion")

    def actualizar(self, dt):
        self.t += dt
        self.tiempo_mensaje -= dt

        puntos = None 
        paso = self.motor.paso_actual(self.t)
        correcto = paso is not None and comprobar_movimiento(puntos, paso["movimiento"])

        evento = self.motor.actualizar(self.t, correcto)
        if evento is not None:
            self.mensaje = evento
            self.tiempo_mensaje = 1.0  # se muestra durante 1 segundo

        if self.motor.terminado() and self.tiempo_mensaje <= 0:
            self.juego.cambiar_pantalla(
                "resultados", resumen=self.motor.resumen(), cancion=self.cancion
            )

    def dibujar(self, pantalla):
        pantalla.fill(e.FONDO)

        # zona cámara
        camara = pygame.Rect(40, 100, 760, 570)
        pygame.draw.rect(pantalla, e.FONDO_CLARO, camara, border_radius=12)
        e.texto(pantalla, "[ aquí irá la webcam ]", 36, e.TEXTO_SUAVE,
                centro=camara.center)

        # barra superior: canción, puntos y progreso de la canción
        e.texto(pantalla, self.cancion["titulo"], 40, e.TEXTO, topleft=(40, 25))
        e.texto(pantalla, f"Puntos: {self.motor.puntuacion()}", 48, e.AMARILLO,
                topleft=(1000, 25))
        progreso = min(1.0, self.t / self.motor.duracion_total)
        pygame.draw.rect(pantalla, e.FONDO_CLARO, (40, 70, 1200, 10), border_radius=5)
        pygame.draw.rect(pantalla, e.ACENTO_2, (40, 70, int(1200 * progreso), 10),
                         border_radius=5)

        # panel derecho: movimientos actual y siguiente
        x = 1020
        paso = self.motor.paso_actual(self.t)
        if paso is not None:
            e.texto(pantalla, "¡Ahora!", 40, e.TEXTO_SUAVE, centro=(x, 180))
            nombre = MOVIMIENTOS[paso["movimiento"]]["nombre"]
            e.texto(pantalla, nombre, 44, e.TEXTO, centro=(x, 240))
            # Barra de tiempo restante del paso
            restante = 1 - (self.t - paso["inicio"]) / paso["duracion"]
            restante = max(0.0, restante)
            pygame.draw.rect(pantalla, e.FONDO_CLARO, (x - 180, 290, 360, 18),
                             border_radius=9)
            pygame.draw.rect(pantalla, e.ACENTO, (x - 180, 290, int(360 * restante), 18),
                             border_radius=9)
        else:
            e.texto(pantalla, "Prepárate...", 44, e.TEXTO_SUAVE, centro=(x, 240))

        siguiente = self.motor.siguiente_paso(self.t)
        if siguiente is not None:
            e.texto(pantalla, "A continuación:", 32, e.TEXTO_SUAVE, centro=(x, 400))
            e.texto(pantalla, MOVIMIENTOS[siguiente["movimiento"]]["nombre"], 36,
                    e.TEXTO, centro=(x, 440))

        # mensaje de resultado
        if self.mensaje is not None and self.tiempo_mensaje > 0:
            res = self.mensaje["resultado"]
            e.texto(pantalla, self.TEXTO_RESULTADO[res], 80,
                    self.COLOR_RESULTADO[res], centro=(x, 560))

        e.texto(pantalla, "(simulación: mantén ESPACIO para 'hacer' el movimiento)",
                24, e.TEXTO_SUAVE, centro=(x, 690))


class PantallaResultados(Pantalla):
    def __init__(self, juego, resumen, cancion):
        super().__init__(juego)
        self.resumen = resumen
        self.cancion = cancion

    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return
        if evento.key == pygame.K_RETURN:
            self.juego.cambiar_pantalla("seleccion")
        elif evento.key == pygame.K_ESCAPE:
            self.juego.cambiar_pantalla("inicio")

    def dibujar(self, pantalla):
        pantalla.fill(e.FONDO)
        r = self.resumen
        centro_x = e.ANCHO // 2
        e.texto(pantalla, "Resultados", 90, e.ACENTO, centro=(centro_x, 110))
        e.texto(pantalla, self.cancion["titulo"], 44, e.TEXTO_SUAVE,
                centro=(centro_x, 180))
        e.texto(pantalla, f'{r["puntos"]} puntos', 100, e.AMARILLO,
                centro=(centro_x, 300))
        e.texto(pantalla, f'Acierto: {r["porcentaje"]:.0f} %', 56, e.TEXTO,
                centro=(centro_x, 410))
        e.texto(pantalla, f'Aciertos: {r["aciertos"]}    Fallos: {r["fallos"]}', 44,
                e.TEXTO, centro=(centro_x, 480))
        e.texto(pantalla, "ENTER: jugar otra   ESC: menú principal", 32,
                e.TEXTO_SUAVE, centro=(centro_x, 640))