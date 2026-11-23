"""
4 pantallas del juego
"""

import math
import cv2
import pygame
import estilo as e
import sonido
from coreografias import MOVIMIENTOS, CANCIONES
from motor_coreografia import PartidaCoreografia
from figuras import dibujar_figura


NIVELES = {"facil": "Fácil", "medio": "Medio", "dificil": "Difícil"}
COLOR_NIVEL = {"facil": e.VERDE, "medio": e.AMARILLO, "dificil": e.ROJO}
DESCRIPCION_NIVEL = {
    "facil": "Movimientos sencillos y ritmo tranquilo",
    "medio": "Más movimientos y algo más de ritmo",
    "dificil": "Todo el cuerpo y ritmo rápido",
}
ORDEN_NIVELES = ("facil", "medio", "dificil")

def dibujar_frame(superficie, frame, rect):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    alto, ancho = rgb.shape[:2]
    imagen = pygame.image.frombuffer(rgb.tobytes(), (ancho, alto), "RGB")
    escala = min(rect.width / ancho, rect.height / alto)
    imagen = pygame.transform.smoothscale(imagen, (int(ancho * escala), int(alto * escala)))
    superficie.blit(imagen, imagen.get_rect(center=rect.center))

def caja_texto(superficie, mensaje, tamaño, color_texto, color_fondo, centro, margen=16):
    """Dibuja un texto centrado en un rectángulo"""
    render = e.fuente(tamaño).render(mensaje, True, color_texto)
    rect = render.get_rect(center=centro)
    pygame.draw.rect(superficie, color_fondo, rect.inflate(margen * 2, margen * 2), border_radius=12)
    superficie.blit(render, render.get_rect(center=centro))

def nombre_movimiento(id_movimiento):
    return MOVIMIENTOS.get(id_movimiento, {}).get("nombre", id_movimiento)

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
    """Dos pasos:
      1. "nivel":   elegir Fácil, Medio o Difícil
      2. "cancion": elegir una canción de ese nivel y 1 o 2 jugadores
    Se puede abrir directamente en el paso 2 pasándole el nivel (al volver
    de una partida) y la canción que estaba elegida."""

    VISIBLES = 4 # canciones que caben a la vez en la lista

    def __init__(self, juego, nivel=None, id_cancion=None):
        super().__init__(juego)
        self.frame = None
        self.aviso = None
        self.paso = "cancion" if nivel in ORDEN_NIVELES else "nivel"
        self.nivel = ORDEN_NIVELES.index(nivel) if nivel in ORDEN_NIVELES else 0
        self.cancion = 0
        self.primera = 0 # primera canción visible de la lista
        for i, cancion in enumerate(self.canciones()):
            if cancion.get("id") == id_cancion:
                self.cancion = i
        self.ajustar_lista()

    def canciones(self, nivel=None):
        """Canciones del nivel indicado (o del elegido)."""
        nivel = nivel or ORDEN_NIVELES[self.nivel]
        return [c for c in CANCIONES if c.get("dificultad") == nivel]

    def ajustar_lista(self):
        """Mueve la lista para que la canción elegida siempre se vea."""
        if self.cancion < self.primera:
            self.primera = self.cancion
        elif self.cancion >= self.primera + self.VISIBLES:
            self.primera = self.cancion - self.VISIBLES + 1

    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return

        # con un aviso en pantalla solo se puede confirmar o volver
        if self.aviso is not None:
            if evento.key == pygame.K_RETURN:
                self.empezar()
            elif evento.key in (pygame.K_2, pygame.K_KP2) and self.juego.camara.num_jugadores == 2:
                self.juego.num_jugadores = 2
                self.empezar()
            elif evento.key == pygame.K_ESCAPE:
                self.aviso = None
            return

        if self.paso == "nivel":
            self.evento_nivel(evento.key)
        else:
            self.evento_cancion(evento.key)

    def evento_nivel(self, tecla):
        if tecla == pygame.K_UP:
            self.nivel = (self.nivel - 1) % len(ORDEN_NIVELES)
        elif tecla == pygame.K_DOWN:
            self.nivel = (self.nivel + 1) % len(ORDEN_NIVELES)
        elif tecla == pygame.K_RETURN and self.canciones():
            self.paso = "cancion"
            self.cancion = 0
            self.primera = 0
        elif tecla == pygame.K_ESCAPE:
            self.juego.cambiar_pantalla("inicio")

    def evento_cancion(self, tecla):
        lista = self.canciones()
        if tecla == pygame.K_UP:
            self.cancion = (self.cancion - 1) % len(lista)
            self.ajustar_lista()
        elif tecla == pygame.K_DOWN:
            self.cancion = (self.cancion + 1) % len(lista)
            self.ajustar_lista()
        elif tecla in (pygame.K_LEFT, pygame.K_RIGHT):
            self.juego.num_jugadores = 2 if self.juego.num_jugadores == 1 else 1
        elif tecla == pygame.K_RETURN:
            self.aviso = self.comprobar_jugadores()
            if self.aviso is None:
                self.empezar()
        elif tecla == pygame.K_ESCAPE:
            self.paso = "nivel"

    def comprobar_jugadores(self):
        """Compara los jugadores elegidos con las personas que ve la cámara.
        Devuelve el texto del aviso, o None si todo coincide."""
        camara = self.juego.camara
        elegidos = self.juego.num_jugadores
        if camara.error is not None:
            return f"La cámara no funciona: {camara.error}"
        detectados = camara.num_jugadores
        if detectados == 0:
            return "No se ve a nadie delante de la cámara"
        if elegidos == 2 and detectados == 1:
            return "Falta el Jugador 2: poneos los dos delante de la cámara"
        if elegidos == 1 and detectados == 2:
            return "Se ven 2 personas. ¿Jugar a dobles?"
        return None

    def empezar(self):
        cancion = self.canciones()[self.cancion]
        self.juego.cambiar_pantalla("juego", cancion=cancion, num_jugadores=self.juego.num_jugadores)

    def actualizar(self, dt):
        # se lee la cámara también aquí para saber cuántas personas hay
        self.frame, _ = self.juego.camara.leer_jugadores()

    def dibujar(self, pantalla):
        pantalla.fill(e.FONDO)
        if self.paso == "nivel":
            self.dibujar_niveles(pantalla)
        else:
            self.dibujar_canciones(pantalla)
        if self.aviso is not None:
            self.dibujar_aviso(pantalla)

    def dibujar_niveles(self, pantalla):
        e.texto(pantalla, "Elige el nivel", 80, e.TEXTO, centro=(e.ANCHO // 2, 70))

        for i, nivel in enumerate(ORDEN_NIVELES):
            seleccionado = i == self.nivel
            color = COLOR_NIVEL[nivel]
            rect = pygame.Rect(0, 0, 900, 140)
            rect.midtop = (e.ANCHO // 2, 140 + i * 165)
            pygame.draw.rect(pantalla, e.ACENTO if seleccionado else e.FONDO_CLARO, rect,
                             border_radius=20)
            pygame.draw.rect(pantalla, color, (rect.x, rect.y, 24, rect.height),
                             border_top_left_radius=20, border_bottom_left_radius=20)
            if seleccionado:
                pygame.draw.rect(pantalla, color, rect, width=5, border_radius=20)

            e.texto(pantalla, NIVELES[nivel], 64, e.TEXTO if seleccionado else color,
                    topleft=(rect.x + 60, rect.y + 22))
            e.texto(pantalla, DESCRIPCION_NIVEL[nivel], 34, e.TEXTO,
                    topleft=(rect.x + 60, rect.y + 88))
            num = len(self.canciones(nivel))
            texto_num = f"{num} canciones" if num != 1 else "1 canción"
            e.texto(pantalla, texto_num if num else "Sin canciones", 36, e.TEXTO,
                    centro=(rect.right - 130, rect.centery))

        e.texto(pantalla, "Arriba/abajo: elegir nivel   ENTER: continuar   ESC: volver", 30,
                e.TEXTO_SUAVE, centro=(e.ANCHO // 2, 680))

    def dibujar_canciones(self, pantalla):
        nivel = ORDEN_NIVELES[self.nivel]
        caja_texto(pantalla, f"NIVEL {NIVELES[nivel].upper()}", 34, COLOR_NIVEL[nivel],
                   e.FONDO_CLARO, (150, 60))
        e.texto(pantalla, "Elige canción", 80, e.TEXTO, centro=(e.ANCHO // 2, 70))

        # lista de canciones del nivel (se desplaza si hay más de las que caben)
        lista = self.canciones()
        for fila, i in enumerate(range(self.primera, min(len(lista), self.primera + self.VISIBLES))):
            cancion = lista[i]
            rect = pygame.Rect(40, 140 + fila * 130, 720, 110)
            color = e.ACENTO if i == self.cancion else e.FONDO_CLARO
            pygame.draw.rect(pantalla, color, rect, border_radius=16)
            pygame.draw.rect(pantalla, COLOR_NIVEL[nivel], (rect.x, rect.y, 14, rect.height),
                             border_top_left_radius=16, border_bottom_left_radius=16)
            e.texto(pantalla, cancion["titulo"], 50, e.TEXTO, topleft=(rect.x + 40, rect.y + 18))
            e.texto(pantalla, f'{len(cancion["pasos"])} ejercicios', 32, e.TEXTO,
                    topleft=(rect.x + 40, rect.y + 68))

        # flechas si hay canciones por encima o por debajo
        if self.primera > 0:
            pygame.draw.polygon(pantalla, e.TEXTO_SUAVE, [(400, 118), (385, 132), (415, 132)])
        if self.primera + self.VISIBLES < len(lista):
            y = 140 + self.VISIBLES * 130 - 8
            pygame.draw.polygon(pantalla, e.TEXTO_SUAVE, [(400, y + 14), (385, y), (415, y)])

        # cámara y número de jugadores
        zona = pygame.Rect(800, 140, 440, 330)
        pygame.draw.rect(pantalla, e.FONDO_CLARO, zona, border_radius=12)
        camara = self.juego.camara
        if self.frame is not None:
            dibujar_frame(pantalla, self.frame, zona)
        else:
            e.texto(pantalla, "Cámara no disponible", 30, e.TEXTO_SUAVE, centro=zona.center)
        if camara.error is None:
            e.texto(pantalla, f"Personas delante: {camara.num_jugadores}", 34, e.TEXTO_SUAVE,
                    centro=(zona.centerx, zona.bottom + 30))

        jugadores = "1 JUGADOR" if self.juego.num_jugadores == 1 else "2 JUGADORES"
        e.texto(pantalla, f"<  {jugadores}  >", 52, e.AMARILLO, centro=(zona.centerx, 570))

        e.texto(pantalla, "Arriba/abajo: canción   Izq/der: jugadores   ENTER: jugar   ESC: cambiar nivel",
                28, e.TEXTO_SUAVE, centro=(e.ANCHO // 2, 680))

    def dibujar_aviso(self, pantalla):
        velo = pygame.Surface((e.ANCHO, e.ALTO), pygame.SRCALPHA)
        velo.fill((0, 0, 0, 170))
        pantalla.blit(velo, (0, 0))
        caja = pygame.Rect(0, 0, 1000, 260)
        caja.center = (e.ANCHO // 2, e.ALTO // 2)
        pygame.draw.rect(pantalla, e.FONDO_CLARO, caja, border_radius=20)
        pygame.draw.rect(pantalla, e.AMARILLO, caja, width=4, border_radius=20)
        e.texto(pantalla, self.aviso, 44, e.TEXTO, centro=(caja.centerx, caja.y + 80))
        opciones = "ENTER: jugar igualmente   ESC: volver"
        if self.juego.num_jugadores == 1 and self.juego.camara.num_jugadores == 2:
            opciones = "2: jugar a dobles   ENTER: jugar solo   ESC: volver"
        e.texto(pantalla, opciones, 36, e.AMARILLO, centro=(caja.centerx, caja.y + 180))


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

    def __init__(self, juego, cancion, num_jugadores):
        super().__init__(juego)
        self.cancion = cancion
        self.ids = ("jugador_1", "jugador_2") if num_jugadores == 2 else ("jugador_1",)
        self.partida = PartidaCoreografia(cancion, self.ids)
        self.pasos = self.partida.cancion["pasos"]
        self.duracion_total = self.pasos[-1]["inicio"] + self.pasos[-1]["duracion"] + 1.0
        self.t = 0.0
        self.frame = None
        self.jugadores = {} # puntos de cada jugador
        self.mensajes = {} # último resultado de cada uno
        self.tiempo_mensaje = {}

        sonido.reproducir_musica(cancion.get("audio"), 
        cancion.get("inicio_audio", 0.0))

    @property
    def dobles(self):
        return len(self.ids) == 2

    def salir(self, nombre, **datos):
        sonido.parar_musica()
        self.juego.cambiar_pantalla(nombre, **datos)

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.salir("seleccion", nivel=self.cancion.get("dificultad"),
                id_cancion=self.cancion.get("id"))

    def actualizar(self, dt):
        self.t += dt
        for jugador in self.tiempo_mensaje:
            self.tiempo_mensaje[jugador] -= dt

        self.frame, jugadores = self.juego.camara.leer_jugadores()
        if not self.dobles:
            puntos = jugadores.get("jugador_1") or jugadores.get("jugador_2")
            jugadores = {"jugador_1": puntos} if puntos else {}
        jugadores = {j: p for j, p in jugadores.items() if j in self.ids}
        self.jugadores = jugadores

        eventos = self.partida.actualizar(self.t, jugadores, dt)
        for jugador, evento in eventos.items():
            self.mensajes[jugador] = evento
            self.tiempo_mensaje[jugador] = 1.0 
        if eventos:
            acierto = any(ev["resultado"] != "fallo" for ev in eventos.values())
            sonido.efecto("acierto" if acierto else "fallo")

        mensajes_activos = any(t > 0 for t in self.tiempo_mensaje.values())
        if self.partida.terminado() and not mensajes_activos:
            self.salir("resultados", resumen=self.partida.resumen(), cancion=self.cancion)

    def paso_en_curso(self):
        for paso in self.pasos:
            if paso["inicio"] <= self.t < paso["inicio"] + paso["duracion"]:
                return paso
        return None

    def siguiente_paso(self):
        for paso in self.pasos:
            if paso["inicio"] > self.t:
                return paso
        return None


    def dibujar(self, pantalla):
        pantalla.fill(e.FONDO)
        zona = pygame.Rect(40, 100, 760, 570)
        self.dibujar_camara(pantalla, zona)
        self.dibujar_marcador(pantalla)
        self.dibujar_panel(pantalla)
        self.dibujar_mensajes(pantalla, zona)

    def dibujar_camara(self, pantalla, zona):
        pygame.draw.rect(pantalla, e.FONDO_CLARO, zona, border_radius=12)
        if self.frame is None:
            # sin imagen: se muestra el motivo que da la Camara de la persona 1
            e.texto(pantalla, self.juego.camara.error or "Conectando cámara...", 30,
                    e.TEXTO_SUAVE, centro=zona.center)
            return

        dibujar_frame(pantalla, self.frame, zona)

        # avisos de jugadores que no se ven
        if not self.dobles:
            if "jugador_1" not in self.jugadores:
                caja_texto(pantalla, "No te veo: ponte delante de la cámara", 36, e.TEXTO,
                           e.ROJO, (zona.centerx, zona.y + 40))
        else:
            for jugador, x in (("jugador_1", zona.x + zona.width // 4),
                               ("jugador_2", zona.x + 3 * zona.width // 4)):
                if jugador not in self.jugadores:
                    caja_texto(pantalla, f"No se ve al {e.NOMBRE_JUGADOR[jugador]}", 30,
                               e.TEXTO, e.ROJO, (x, zona.y + 40))

    def dibujar_marcador(self, pantalla):
        e.texto(pantalla, self.cancion["titulo"], 40, e.TEXTO, topleft=(40, 25))
        puntos = self.partida.puntuaciones()
        if self.dobles:
            e.texto(pantalla, f'J1: {puntos["jugador_1"]}', 48, e.COLOR_JUGADOR["jugador_1"],
                    topleft=(760, 25))
            e.texto(pantalla, f'J2: {puntos["jugador_2"]}', 48, e.COLOR_JUGADOR["jugador_2"],
                    topleft=(1010, 25))
        else:
            e.texto(pantalla, f'Puntos: {puntos["jugador_1"]}', 48, e.AMARILLO,
                    topleft=(1000, 25))

        progreso = min(1.0, self.t / self.duracion_total)
        pygame.draw.rect(pantalla, e.FONDO_CLARO, (40, 70, 1200, 10), border_radius=5)
        pygame.draw.rect(pantalla, e.ACENTO_2, (40, 70, int(1200 * progreso), 10),
                         border_radius=5)


    def dibujar_panel(self, pantalla):
        """Panel derecho: movimiento actual con su imagen de referencia,
        tiempo que queda y el siguiente movimiento."""
        x = 1020
        paso = self.paso_en_curso()
        siguiente = self.siguiente_paso()
        figura = pygame.Rect(0, 0, 230, 230)
        figura.midtop = (x, 185)

        if paso is not None:
            e.texto(pantalla, "¡Ahora!", 36, e.TEXTO_SUAVE, centro=(x, 120))
            e.texto(pantalla, nombre_movimiento(paso["movimiento"]), 46, e.TEXTO,
                    centro=(x, 158))
            dibujar_figura(pantalla, paso["movimiento"], figura)
            instruccion = MOVIMIENTOS.get(paso["movimiento"], {}).get("instruccion")
            if instruccion:
                e.texto(pantalla, instruccion, 28, e.TEXTO_SUAVE, centro=(x, 440))
            restante = 1 - (self.t - paso["inicio"]) / paso["duracion"]
            restante = max(0.0, restante)
            pygame.draw.rect(pantalla, e.FONDO_CLARO, (x - 180, 462, 360, 18),
                             border_radius=9)
            pygame.draw.rect(pantalla, e.ACENTO, (x - 180, 462, int(360 * restante), 18),
                             border_radius=9)

            # quién lo ha hecho ya (el motor de cada jugador pasa al siguiente paso)
            if self.dobles:
                for i, jugador in enumerate(self.ids):
                    hecho = self.partida.motores[jugador].paso_actual(self.t) is None
                    estado = "¡hecho!" if hecho else "..."
                    e.texto(pantalla, f"J{i + 1}: {estado}", 34, e.COLOR_JUGADOR[jugador],
                            centro=(x - 90 + i * 180, 510))
            elif self.partida.motores["jugador_1"].paso_actual(self.t) is None:
                e.texto(pantalla, "¡Hecho! Espera al siguiente", 34, e.VERDE, centro=(x, 510))

            # el siguiente, en pequeño
            if siguiente is not None:
                e.texto(pantalla, "A continuación:", 30, e.TEXTO_SUAVE, centro=(x, 562))
                mini = pygame.Rect(850, 585, 80, 80)
                dibujar_figura(pantalla, siguiente["movimiento"], mini, resaltar=False)
                e.texto(pantalla, nombre_movimiento(siguiente["movimiento"]), 32, e.TEXTO,
                        topleft=(945, 612))

        elif siguiente is not None:
            # entre movimientos: se enseña ya el próximo para ir preparándose
            e.texto(pantalla, "Prepárate para...", 36, e.TEXTO_SUAVE, centro=(x, 120))
            e.texto(pantalla, nombre_movimiento(siguiente["movimiento"]), 46, e.TEXTO,
                    centro=(x, 158))
            dibujar_figura(pantalla, siguiente["movimiento"], figura)
            instruccion = MOVIMIENTOS.get(siguiente["movimiento"], {}).get("instruccion")
            if instruccion:
                e.texto(pantalla, instruccion, 28, e.TEXTO_SUAVE, centro=(x, 440))
            falta = siguiente["inicio"] - self.t
            e.texto(pantalla, f"Empieza en {math.ceil(falta)}...", 40, e.AMARILLO,
                    centro=(x, 500))
        else:
            e.texto(pantalla, "¡Último movimiento!", 40, e.TEXTO_SUAVE, centro=(x, 300))

    def dibujar_mensajes(self, pantalla, zona):
        """Resultado del último paso: con 1 jugador en el panel derecho;
        con 2, el de cada uno encima de su mitad de la cámara."""
        for jugador, evento in self.mensajes.items():
            if self.tiempo_mensaje.get(jugador, 0) <= 0:
                continue
            res = evento["resultado"]
            if self.dobles:
                x = zona.x + zona.width // 4 if jugador == "jugador_1" else zona.x + 3 * zona.width // 4
                caja_texto(pantalla, self.TEXTO_RESULTADO[res], 56, self.COLOR_RESULTADO[res],
                           e.FONDO, (x, zona.bottom - 60))
            else:
                caja_texto(pantalla, self.TEXTO_RESULTADO[res], 80, self.COLOR_RESULTADO[res],
                    e.FONDO, (zona.centerx, zona.bottom - 70))


class PantallaResultados(Pantalla):
    def __init__(self, juego, resumen, cancion):
        super().__init__(juego)
        self.resumen = resumen
        self.cancion = cancion

    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return
        if evento.key == pygame.K_RETURN:
            self.juego.cambiar_pantalla("seleccion", nivel=self.cancion.get("dificultad"),
                id_cancion=self.cancion.get("id"))        
        elif evento.key == pygame.K_ESCAPE:
            self.juego.cambiar_pantalla("inicio")

   
    def dibujar(self, pantalla):
        pantalla.fill(e.FONDO)
        centro_x = e.ANCHO // 2
        e.texto(pantalla, "Resultados", 90, e.ACENTO, centro=(centro_x, 90))
        e.texto(pantalla, self.cancion["titulo"], 44, e.TEXTO_SUAVE, centro=(centro_x, 155))

        if len(self.resumen) == 1:
            r = self.resumen["jugador_1"]
            e.texto(pantalla, f'{r["puntos"]} puntos', 100, e.AMARILLO, centro=(centro_x, 300))
            e.texto(pantalla, f'Acierto: {r["porcentaje"]:.0f} %', 56, e.TEXTO,
                    centro=(centro_x, 410))
            e.texto(pantalla, f'Aciertos: {r["aciertos"]}    Fallos: {r["fallos"]}', 44,
                    e.TEXTO, centro=(centro_x, 480))
        else:
            self.dibujar_dobles(pantalla)

        e.texto(pantalla, "ENTER: jugar otra   ESC: menú principal", 32,
                e.TEXTO_SUAVE, centro=(centro_x, 650))

    def dibujar_dobles(self, pantalla):
        p1 = self.resumen["jugador_1"]["puntos"]
        p2 = self.resumen["jugador_2"]["puntos"]
        if p1 == p2:
            e.texto(pantalla, "¡Empate!", 70, e.AMARILLO, centro=(e.ANCHO // 2, 235))
        else:
            ganador = "jugador_1" if p1 > p2 else "jugador_2"
            e.texto(pantalla, f"¡Gana el {e.NOMBRE_JUGADOR[ganador]}!", 70,
                    e.COLOR_JUGADOR[ganador], centro=(e.ANCHO // 2, 235))

        for jugador, x in (("jugador_1", 340), ("jugador_2", 940)):
            r = self.resumen[jugador]
            color = e.COLOR_JUGADOR[jugador]
            tarjeta = pygame.Rect(0, 0, 460, 300)
            tarjeta.midtop = (x, 290)
            pygame.draw.rect(pantalla, e.FONDO_CLARO, tarjeta, border_radius=20)
            pygame.draw.rect(pantalla, color, tarjeta, width=4, border_radius=20)
            e.texto(pantalla, e.NOMBRE_JUGADOR[jugador], 50, color, centro=(x, 335))
            e.texto(pantalla, f'{r["puntos"]} puntos', 70, e.AMARILLO, centro=(x, 410))
            e.texto(pantalla, f'Acierto: {r["porcentaje"]:.0f} %', 40, e.TEXTO, centro=(x, 475))
            e.texto(pantalla, f'Aciertos: {r["aciertos"]}   Fallos: {r["fallos"]}', 34,
                    e.TEXTO, centro=(x, 530))
