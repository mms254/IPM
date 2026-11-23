"""
Estilo visual: tamaño de la ventana, colores, fuentes y fondo
"""

import os
import pygame

ANCHO, ALTO = 1280, 720
FPS = 30
TITULO = "MOVE & DANCE"

# colores
FONDO = (12, 16, 46)
FONDO_CLARO = (30, 40, 92)   
TEXTO = (240, 245, 255)
TEXTO_SUAVE = (150, 170, 210)
ACENTO = (220, 50, 130)     
ACENTO_2 = (30, 130, 220)     
VERDE = (60, 220, 150)
AMARILLO = (255, 205, 60)
ROJO = (255, 90, 110)
COLOR_TITULO = (80, 210, 255) 
SOMBRA = (220, 50, 130)     

COLOR_JUGADOR = {
    "jugador_1": (0, 150, 255),     # azul
    "jugador_2": (220, 50, 130),    # rosa
}
NOMBRE_JUGADOR = {"jugador_1": "Jugador 1", "jugador_2": "Jugador 2"}

CARPETA_FUENTES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fuentes")
FUENTE_TITULO = os.path.join(CARPETA_FUENTES, "KaushanScript-Regular.ttf")

_fuentes = {}

def fuente(tamaño, titulo=False):
    if (tamaño, titulo) not in _fuentes:
        if titulo:
            _fuentes[(tamaño, titulo)] = pygame.font.Font(FUENTE_TITULO, tamaño)
        else:
            _fuentes[(tamaño, titulo)] = pygame.font.Font(None, tamaño)
    return _fuentes[(tamaño, titulo)]

def texto(superficie, mensaje, tamaño, color, centro=None, topleft=None, titulo=False, sombra=False):
    render = fuente(tamaño, titulo).render(str(mensaje), True, color)
    rect = render.get_rect()
    if centro is not None:
        rect.center = centro
    elif topleft is not None:
        rect.topleft = topleft
    if sombra:
        # el mismo texto en otro color y un poco desplazado
        render_sombra = fuente(tamaño, titulo).render(str(mensaje), True, SOMBRA)
        superficie.blit(render_sombra, (rect.x + 5, rect.y + 5))
    superficie.blit(render, rect)
    return rect

def dibujar_fondo(pantalla):
    """Fondo azul con una franja azul arriba y otra rosa abajo."""
    pantalla.fill(FONDO)
    pygame.draw.rect(pantalla, ACENTO_2, (0, 0, ANCHO, 6))
    pygame.draw.rect(pantalla, ACENTO, (0, ALTO - 6, ANCHO, 6))