"""
Música y efectos de sonido del juego (pygame.mixer).

  reproducir_musica(ruta, inicio)  -> empieza la canción de la rutina
  parar_musica()                   -> la apaga con un fundido
  efecto("acierto" | "fallo")      -> sonido corto de resultado

Si no hay tarjeta de sonido o falta un archivo, el juego sigue sin sonido
(solo se avisa por la consola).
"""
import os
import numpy as np
import pygame

VOLUMEN_MUSICA = 0.6    # 0-1: algo bajo para que se oigan los efectos
VOLUMEN_EFECTOS = 0.5
CARPETA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INICIO_CANCIONES = {
    "bailando": "1:02",
    "cant_stop_the_feeling": "0:15",
    "waka_waka": "0:30",
    "shape_of_you": "0:50",
    "la_bicicleta": "0:40",
    "moves_like_jagger": "0:42",
    "señorita": "0:38",
    "asereje": "0:12",
    "gasolina": "0:06",
}


_efectos = {}

def _a_segundos(tiempo):
    """'1:02' -> 62.0"""
    minutos, segundos = str(tiempo).split(":")
    return int(minutos) * 60 + float(segundos)

def _hay_sonido():
    return pygame.mixer.get_init() is not None


def reproducir_musica(ruta, inicio=0.0):
    """Reproduce el archivo de audio desde el segundo 'inicio'.
    La ruta es relativa a la carpeta del proyecto."""
    if not _hay_sonido():
        return False

    pygame.mixer.music.stop()   # por si sigue sonando la canción anterior
    if not ruta:
        return False

    ruta_completa = os.path.join(CARPETA, ruta)
    if not os.path.exists(ruta_completa):
        print(f"[sonido] No se encuentra la canción: {ruta}")
        return False

    try:
        pygame.mixer.music.load(ruta_completa)
        pygame.mixer.music.set_volume(VOLUMEN_MUSICA)
        # si la canción está en la tabla, empieza en su estribillo
        nombre = os.path.splitext(os.path.basename(ruta))[0]
        if nombre in INICIO_CANCIONES:
            inicio = _a_segundos(INICIO_CANCIONES[nombre])
        pygame.mixer.music.play(start=inicio, fade_ms=1000)
        return True
    except pygame.error as ex:
        print(f"[sonido] No se ha podido reproducir {ruta}: {ex}")
        return False


def parar_musica(fundido_ms=1500):
    """Baja el volumen poco a poco hasta parar la música."""
    if _hay_sonido():
        pygame.mixer.music.fadeout(fundido_ms)


def _crear_tono(notas, duracion_nota):
    """Crea un sonido con varias notas seguidas (frecuencias en Hz)."""
    frecuencia, _, canales = pygame.mixer.get_init()
    muestras = int(frecuencia * duracion_nota)
    t = np.arange(muestras) / frecuencia
    # Envolvente: sube rápido y se apaga suave (evita "clics")
    envolvente = np.minimum(1, t * 200) * np.exp(-t * 6)

    onda = np.concatenate([np.sin(2 * np.pi * f * t) * envolvente for f in notas])
    onda = (onda * 32767 * VOLUMEN_EFECTOS).astype(np.int16)
    if canales > 1:
        onda = np.repeat(onda[:, None], canales, axis=1)
    return pygame.sndarray.make_sound(np.ascontiguousarray(onda))


def efecto(nombre):
    """Reproduce un efecto: 'acierto' (dos notas que suben) o 'fallo' (dos que bajan)."""
    if not _hay_sonido():
        return
    if nombre not in _efectos:
        if nombre == "acierto":
            _efectos[nombre] = _crear_tono([660, 880], 0.12)
        else:
            _efectos[nombre] = _crear_tono([300, 200], 0.18)
    _efectos[nombre].play()