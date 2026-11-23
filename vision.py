import time
from collections import deque

import cv2
import mediapipe as mp
from config import config


# Articulaciones que se devuelven (nombre -> índice de MediaPipe Pose)
ARTICULACIONES = {
    "hombro_izquierdo": 11,
    "hombro_derecho": 12,
    "codo_izquierdo": 13,
    "codo_derecho": 14,
    "muneca_izquierda": 15,
    "muneca_derecha": 16,
    "cadera_izquierda": 23,
    "cadera_derecha": 24,
    "rodilla_izquierda": 25,
    "rodilla_derecha": 26,
    "tobillo_izquierdo": 27,
    "tobillo_derecho": 28
}

JUGADORES = ("jugador_1", "jugador_2")

# Color del esqueleto de cada jugador (BGR)
COLORES_JUGADOR = {
    "jugador_1": (255, 150, 0),     # azul
    "jugador_2": (130, 50, 220)     # rosa
}

# Visibilidad mínima (media de los dos hombros) para contar a alguien como
# persona. Es baja a propósito: solo descarta detecciones fantasma, no a un
# jugador que está algo lejos o medio tapado.
VISIBILIDAD_PERSONA = 0.2

# Fotogramas (~1,5 s) que se recuerda dónde estaba un jugador que deja de verse
MEMORIA_JUGADOR = 45

# Distancia máxima (en anchura de imagen, 0-1) para reconocer a un jugador
# que vuelve a aparecer cerca de donde estaba
DISTANCIA_REAPARICION = 0.3


class DetectorCorporal:
    """
    Detecta la postura corporal de hasta dos personas utilizando
    MediaPipe Pose Landmarker.

    Cada persona se identifica como "jugador_1" (la de la izquierda de la
    pantalla) o "jugador_2" (la de la derecha), y mantiene su identificador
    aunque se mueva o deje de verse un momento.
    """

    def __init__(self, max_personas=2):
        # Configurar MediaPipe
        self.mp_pose = mp.solutions.pose

        opciones = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=config.model_path
            ),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_poses=max_personas
        )

        # Crear el detector
        self.detector = (
            mp.tasks.vision.PoseLandmarker.create_from_options(
                opciones
            )
        )

        self.timestamp = 0
        self.poses_mediapipe = 0    # poses que devolvió MediaPipe (sin filtrar)
        self.poses = []             # landmarks de cada persona detectada
        self.puntos = None          # landmarks del jugador principal

        self._poses_jugador = {}    # "jugador_1" -> landmarks
        self._ultima_x = {}         # posición horizontal de cada jugador
        self._sin_ver = {}          # fotogramas que lleva sin verse

    # ------------------------------------------------------------------
    # Detección
    # ------------------------------------------------------------------

    def detectar(self, frame):
        """
        Detecta los cuerpos en un fotograma de OpenCV.
        Devuelve los landmarks del jugador principal o None.
        """

        # Convertir BGR a RGB
        frame_rgb = cv2.cvtColor(
            frame, cv2.COLOR_BGR2RGB
        )

        imagen_mp = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame_rgb
        )

        # Marca de tiempo real en milisegundos (MediaPipe la usa para seguir
        # a las personas entre fotogramas; tiene que ir siempre creciendo)
        self.timestamp = max(
            self.timestamp + 1,
            time.monotonic_ns() // 1_000_000
        )

        resultado = self.detector.detect_for_video(
            imagen_mp,
            self.timestamp
        )

        poses = list(resultado.pose_landmarks or [])
        self.poses_mediapipe = len(poses)

        # Se descartan solo las detecciones sin hombros (fantasmas)
        self.poses = [pose for pose in poses if self._es_persona(pose)]

        self._asignar_jugadores()

        self.puntos = (
            self._poses_jugador.get("jugador_1")
            or self._poses_jugador.get("jugador_2")
        )

        return self.puntos

    @staticmethod
    def _es_persona(pose):
        visibilidad = (
            pose[ARTICULACIONES["hombro_izquierdo"]].visibility
            + pose[ARTICULACIONES["hombro_derecho"]].visibility
        ) / 2
        return visibilidad >= VISIBILIDAD_PERSONA

    @staticmethod
    def _centro_x(pose):
        """Posición horizontal de la persona (punto medio de los hombros)."""
        return (
            pose[ARTICULACIONES["hombro_izquierdo"]].x
            + pose[ARTICULACIONES["hombro_derecho"]].x
        ) / 2

    def _recientes(self):
        """Jugadores que se han visto hace poco."""
        return [
            jugador for jugador in JUGADORES
            if jugador in self._ultima_x
            and self._sin_ver[jugador] < MEMORIA_JUGADOR
        ]

    def _asignar_jugadores(self):
        """Decide qué pose es el jugador 1 y cuál el jugador 2."""

        poses = sorted(self.poses, key=self._centro_x)[:2]
        recientes = self._recientes()
        asignacion = {}

        if len(poses) == 2:
            # Por defecto: izquierda = jugador 1, derecha = jugador 2.
            izquierda, derecha = poses
            asignacion = {"jugador_1": izquierda, "jugador_2": derecha}

            if len(recientes) == 1:
                # Ya había alguien jugando y entra otra persona: el que estaba
                # conserva su número y el nuevo recibe el otro.
                conocido = recientes[0]
                otro = "jugador_2" if conocido == "jugador_1" else "jugador_1"
                x = self._ultima_x[conocido]
                cercana, lejana = sorted(
                    poses, key=lambda p: abs(self._centro_x(p) - x)
                )
                asignacion = {conocido: cercana, otro: lejana}

            elif len(recientes) == 2:
                # Ya se conocían los dos: se elige el reparto en el que menos
                # se han movido (así no se intercambian si se cruzan).
                x1 = self._ultima_x["jugador_1"]
                x2 = self._ultima_x["jugador_2"]
                xi = self._centro_x(izquierda)
                xd = self._centro_x(derecha)
                if abs(xi - x2) + abs(xd - x1) < abs(xi - x1) + abs(xd - x2):
                    asignacion = {"jugador_1": derecha, "jugador_2": izquierda}

        elif len(poses) == 1:
            # Una sola persona: es el jugador que estaba más cerca, si alguno
            # se ha visto hace poco; si no, es el jugador 1.
            pose = poses[0]
            x = self._centro_x(pose)
            jugador = "jugador_1"

            if recientes:
                cercano = min(recientes, key=lambda j: abs(self._ultima_x[j] - x))
                if abs(self._ultima_x[cercano] - x) < DISTANCIA_REAPARICION:
                    jugador = cercano

            asignacion = {jugador: pose}

        # Actualizar la memoria de cada jugador
        for jugador in JUGADORES:
            if jugador in asignacion:
                self._ultima_x[jugador] = self._centro_x(asignacion[jugador])
                self._sin_ver[jugador] = 0
            elif jugador in self._sin_ver:
                self._sin_ver[jugador] += 1

        self._poses_jugador = asignacion

    # ------------------------------------------------------------------
    # Resultados
    # ------------------------------------------------------------------

    @staticmethod
    def _convertir(pose):
        """Convierte los landmarks de una pose en el diccionario de puntos."""
        puntos = {}

        for nombre, indice in ARTICULACIONES.items():
            landmark = pose[indice]

            puntos[nombre] = {
                "x": landmark.x,
                "y": landmark.y,
                "z": landmark.z,
                "visibilidad": landmark.visibility
            }

        return puntos

    def obtener_puntos(self):
        """
        Devuelve las coordenadas normalizadas de las principales
        articulaciones del jugador principal (el jugador 1, o el único
        que se ve), o None si no se ve a nadie.
        """

        if self.puntos is None:
            return None

        return self._convertir(self.puntos)

    def obtener_jugadores(self):
        """
        Devuelve los puntos de cada jugador que se ve ahora mismo:
            {"jugador_1": {...}, "jugador_2": {...}}
        Un jugador que no se ve no aparece en el diccionario.
        """

        return {
            jugador: self._convertir(pose)
            for jugador, pose in self._poses_jugador.items()
        }

    def num_personas(self):
        """Número de personas detectadas en el último fotograma (0, 1 o 2)."""
        return len(self._poses_jugador)

    # ------------------------------------------------------------------
    # Dibujo
    # ------------------------------------------------------------------

    def dibujar_esqueleto(self, frame):
        """
        Dibuja el esqueleto de cada jugador sobre la imagen, cada uno
        de un color. Si hay dos personas, escribe J1 y J2 encima.
        """

        if not self._poses_jugador:
            return frame

        alto, ancho = frame.shape[:2]
        varios = len(self._poses_jugador) > 1

        for jugador, pose in self._poses_jugador.items():
            color = COLORES_JUGADOR[jugador]

            # Dibujar conexiones
            for inicio, fin in self.mp_pose.POSE_CONNECTIONS:
                punto1 = pose[inicio]
                punto2 = pose[fin]

                x1 = int(punto1.x * ancho)
                y1 = int(punto1.y * alto)
                x2 = int(punto2.x * ancho)
                y2 = int(punto2.y * alto)

                cv2.line(frame, (x1, y1), (x2, y2), color, 2)

            # Dibujar articulaciones
            for landmark in pose:
                x = int(landmark.x * ancho)
                y = int(landmark.y * alto)

                cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

            # Etiqueta encima de la cabeza
            if varios:
                nariz = pose[0]
                x = int(nariz.x * ancho) - 20
                y = max(30, int(nariz.y * alto) - 40)
                etiqueta = "J1" if jugador == "jugador_1" else "J2"
                cv2.putText(frame, etiqueta, (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        return frame

    def cerrar(self):
        """Libera los recursos del detector."""
        self.detector.close()


class Camara:
    """
    Abre la webcam y, en cada lectura, devuelve el fotograma en espejo
    con los esqueletos dibujados y los puntos del cuerpo.

    No lanza excepciones: si algo falla, guarda el motivo en
    self.error y las lecturas devuelven (None, None).

    Un jugador:
        camara = Camara()
        frame, puntos = camara.leer()

    Dos jugadores a la vez:
        frame, jugadores = camara.leer_jugadores()
        # jugadores = {"jugador_1": {...}, "jugador_2": {...}}
        camara.num_jugadores      # 0, 1 o 2 (estable, sin parpadeos)

    camara.cerrar()
    """

    # Fotogramas (~1 s) que se usan para decidir cuántas personas hay
    VENTANA_PERSONAS = 30

    def __init__(self, indice=0, dibujar=True, max_personas=2):
        self.error = None
        self.dibujar = dibujar
        self.detector = None
        self.captura = None

        self.personas = 0       # personas en el último fotograma
        self._historial = deque(maxlen=self.VENTANA_PERSONAS)

        # Crear detector corporal
        try:
            self.detector = DetectorCorporal(max_personas)
        except Exception as ex:
            self.error = f"No se ha podido cargar MediaPipe: {ex}"
            return

        # Abrir webcam
        self.captura = cv2.VideoCapture(indice)

        if not self.captura.isOpened():
            self.error = "No se ha podido abrir la webcam"

    def _procesar(self):
        """Lee un fotograma, lo voltea, detecta y dibuja.
        Devuelve el frame, o None si hay error."""

        if self.error is not None:
            return None

        # Leer imagen de la webcam
        correcto, frame = self.captura.read()

        if not correcto or frame is None:
            self.error = "Error al leer la webcam"
            return None

        # Voltear imagen como un espejo
        frame = cv2.flip(frame, 1)

        try:
            # Detectar los cuerpos
            self.detector.detectar(frame)

            self.personas = self.detector.num_personas()
            self._historial.append(self.personas)

            # Dibujar esqueletos
            if self.dibujar:
                frame = self.detector.dibujar_esqueleto(frame)
        except Exception as ex:
            self.error = f"Error al detectar el cuerpo: {ex}"
            self.personas = 0
            return frame

        return frame

    def leer(self):
        """
        Modo un jugador. Devuelve (frame, puntos):
          - frame: imagen BGR de OpenCV (con esqueleto si dibujar=True) o None
          - puntos: diccionario del jugador principal o None
        """

        frame = self._procesar()

        if frame is None or self.error is not None:
            return frame, None

        return frame, self.detector.obtener_puntos()

    def leer_jugadores(self):
        """
        Modo dos jugadores. Devuelve (frame, jugadores):
          - frame: imagen BGR de OpenCV o None
          - jugadores: {"jugador_1": puntos, "jugador_2": puntos}; solo
            aparecen los jugadores que se ven en este fotograma
        """

        frame = self._procesar()

        if frame is None or self.error is not None:
            return frame, {}

        return frame, self.detector.obtener_jugadores()

    @property
    def num_jugadores(self):
        """
        Cuántas personas hay delante de la cámara (0, 1 o 2), mirando
        el último segundo para que no cambie por un fallo de un fotograma.
        """

        if not self._historial:
            return 0

        total = len(self._historial)
        con_dos = sum(1 for n in self._historial if n >= 2)
        con_alguien = sum(1 for n in self._historial if n >= 1)

        if con_dos >= total / 2:
            return 2
        if con_alguien >= total / 2:
            return 1
        return 0

    def cerrar(self):
        """Cierra la webcam y libera el detector."""

        if self.captura is not None:
            self.captura.release()
            self.captura = None

        if self.detector is not None:
            self.detector.cerrar()
            self.detector = None