"""
Estilo visual: tamaño de la ventana, colores, fuentes
"""

import pygame

ANCHO, ALTO = 1280, 720
FPS = 30
TITULO = "MOVE & DANCE"

# colores
FONDO = (18, 14, 38)
FONDO_CLARO = (40, 32, 80)
TEXTO = (245, 245, 255)
TEXTO_SUAVE = (170, 165, 200)
ACENTO = (180, 90, 255)      
ACENTO_2 = (255, 90, 170)    
VERDE = (80, 230, 140)
AMARILLO = (255, 210, 80)
ROJO = (255, 90, 90)

_fuentes = {}

def fuente(tamaño):
    if tamaño not in _fuentes:
        _fuentes[tamaño] = pygame.font.Font(None, tamaño)
    return _fuentes[tamaño]

def texto(superficie, mensaje, tamano, color, centro=None, topleft=None):
    render = fuente(tamano).render(str(mensaje), True, color)
    rect = render.get_rect()
    if centro is not None:
        rect.center = centro
    elif topleft is not None:
        rect.topleft = topleft
    superficie.blit(render, rect)
    return rect