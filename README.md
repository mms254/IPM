# MOVE & DANCE

Videojuego serio de baile controlado con el cuerpo mediante **visión por computador**.
La webcam detecta el esqueleto del jugador con **MediaPipe Pose Landmarker** y el juego
comprueba en tiempo real si imita los movimientos que aparecen en pantalla al ritmo de
la música. Se puede jugar **solo o con dos personas a la vez**, cada una con su propia
puntuación.

Pensado como juego de **actividad física y rehabilitación** (también para personas
mayores): movimientos sencillos de brazos, piernas y tronco, con tiempo suficiente para
cada ejercicio y tres niveles de dificultad.

Práctica del Bloque 2 de *Interacción Persona-Máquina* (IPM): IPM mediante visión por
computador.

**Autoras:** Sama Al Adib, Alba García Calvete, María Mestre Sánchez

---

## Requisitos

- Ordenador con **webcam**.
- **Conda** ([instalar Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install)).
- Altavoces para la música (opcional: sin sonido el juego funciona igual).

## Instalación (en un equipo nuevo)

Todos los comandos se ejecutan desde la carpeta del proyecto.

**1. Crear y activar el entorno de Python**

```bash
conda create -n IPM python=3.12
conda activate IPM
```

**2. Instalar las dependencias** (MediaPipe, OpenCV, pygame, NumPy...)

```bash
pip install -r requirements.txt
```

**3. Descargar el modelo de MediaPipe**

```bash
python download_models.py
```

Descarga los modelos *Pose Landmarker* en la carpeta `models/`. El juego usa
`models/pose_landmarker_full.task`.

**4. Añadir las canciones**

Los archivos MP3 no están en el repositorio (por tamaño y derechos de autor). Para descargar las canciones hay que poner estos comandos en la terminal:
```bash
yt-dlp -x --audio-format mp3 -o "assets/musica/bailando.%(ext)s" "https://www.youtube.com/watch?v=NUsoVlDFqZg"
yt-dlp -x --audio-format mp3 -o "assets/musica/cant_stop_the_feeling.%(ext)s" "https://www.youtube.com/watch?v=ru0K8uYEZWw"
yt-dlp -x --audio-format mp3 -o "assets/musica/waka_waka.%(ext)s" "https://www.youtube.com/watch?v=pRpeEdMmmQ0"
yt-dlp -x --audio-format mp3 -o "assets/musica/shape_of_you.%(ext)s" "ytsearch1:Ed Sheeran Shape of You official audio"
yt-dlp -x --audio-format mp3 -o "assets/musica/la_bicicleta.%(ext)s" "ytsearch1:Carlos Vives Shakira La Bicicleta audio oficial"
yt-dlp -x --audio-format mp3 -o "assets/musica/moves_like_jagger.%(ext)s" "ytsearch1:Maroon 5 Moves Like Jagger Christina Aguilera official audio"
yt-dlp -x --audio-format mp3 -o "assets/musica/señorita.%(ext)s" "ytsearch1:Abraham Mateo Señorita audio oficial"
yt-dlp -x --audio-format mp3 -o "assets/musica/asereje.%(ext)s" "ytsearch1:Las Ketchup Aserejé audio oficial"
yt-dlp -x --audio-format mp3 -o "assets/musica/gasolina.%(ext)s" "ytsearch1:Daddy Yankee Gasolina audio oficial"
```
La estructura de la carpeta debe verse así:
```
assets/musica/Se
entregan aparte en el `.zip` y hay que copiarlos en `assets/musica/` con estos nombres:
├── bailando.mp3
├── la_bicicleta.mp3
├── shape_of_you.mp3
├── cant_stop_the_feeling.mp3
├── moves_like_jagger.mp3
├── señorita.mp3
├── waka_waka.mp3
├── asereje.mp3
└── gasolina.mp3
```

Si falta alguna canción, la rutina se juega igual sin música (solo aparece un aviso en
la consola).

## Ejecución

```bash
conda activate IPM
python juego.py
```

Cada vez que se abre una terminal nueva hay que volver a hacer `conda activate IPM`.

## Estructura del proyecto

- `juego.py`: punto de entrada de la aplicación.
- `vision/`: cámara, detección corporal y configuración del modelo.
- `logica/`: coreografías, evaluación de movimientos, motor y puntuación.
- `interfaz/`: pantallas, estilo, figuras y sonido.
- `assets/fuentes/`: fuente y licencia incluidas.
- `assets/musica/`: canciones locales; los MP3 no se suben al repositorio.
- `models/`: modelos descargados con `python download_models.py`; no se suben al repositorio.

Para ejecutar las pruebas de la lógica:

```bash
python -m unittest -v logica.test_logica_juego
```

---

## Cómo se juega

1. **Pantalla de inicio**: `ENTER` para empezar, `ESC` para salir.
2. **Elegir canción y jugadores**
   - `↑` / `↓`: elegir canción. Cada canción tiene su dificultad (fácil, medio o difícil).
   - `←` / `→`: elegir **1 o 2 jugadores**.
   - `ENTER`: jugar. `ESC`: volver.
   - La cámara cuenta cuántas personas hay delante. Si no coincide con lo elegido, avisa
     antes de empezar (por ejemplo, *"Se ven 2 personas. ¿Jugar a dobles?"*): `ENTER`
     para seguir igualmente, `2` para jugar a dobles o `ESC` para volver.
3. **Partida**: en pantalla aparece el movimiento que hay que hacer ahora, una figura de
   ayuda, el tiempo que queda y el siguiente movimiento. Hay que **mantener la postura**
   un momento para que cuente.
   - **¡Perfecto!** (100 puntos): en la primera mitad del tiempo del ejercicio.
   - **¡Bien!** (50 puntos): en la segunda mitad.
   - **Fallo** (0 puntos): si se acaba el tiempo.
   - `ESC` vuelve a la selección de canción.
4. **Resultados**: puntos, porcentaje de acierto, aciertos y fallos de cada jugador (y
   quién ha ganado si jugáis dos). `ENTER` para jugar otra, `ESC` para volver al menú.

### Canciones

| Fácil | Medio | Difícil |
|---|---|---|
| Bailando | Can't Stop the Feeling | Waka Waka |
| La Bicicleta | Moves Like Jagger | Aserejé |
| Shape of You | Señorita | Gasolina |

Los movimientos de cada partida se eligen al azar entre los de esa dificultad o inferior,
así que la coreografía cambia cada vez.

### Consejos para que la cámara te detecte bien

- Colócate a 2-3 metros, de forma que se te vea **el cuerpo entero** (al menos hasta las
  rodillas; para algunos movimientos, también los pies).
- Buena iluminación, mejor de frente que a contraluz.
- **Dos jugadores**: poneos uno a cada lado, sin taparos. El de la izquierda de la
  pantalla es el **Jugador 1** (esqueleto azul) y el de la derecha el **Jugador 2**
  (naranja). No os crucéis: se podrían intercambiar los jugadores.
- La imagen se muestra **en espejo**: tu brazo izquierdo aparece a la izquierda de la
  pantalla, como al mirarte en un espejo.

---

## Cómo está hecho

El proyecto se divide en tres partes que se comunican mediante funciones con nombres
y formatos acordados.

```
webcam ──► vision.py ──► puntos del cuerpo de cada jugador
                              │
                              ▼
            juego.py / pantallas.py  (interfaz, reloj de la canción)
                              │  tiempo + puntos
                              ▼
            motor_coreografia.py ──► movimiento correcto, eventos y puntuación
```

| Parte | Archivos | Qué hace |
|---|---|---|
| **Visión por computador** | `vision.py` | Abre la webcam, voltea la imagen en espejo, detecta hasta 2 personas con MediaPipe, asigna a cada una un jugador estable (J1/J2) y devuelve las coordenadas normalizadas de 12 articulaciones (hombros, codos, muñecas, caderas, rodillas y tobillos). También dibuja los esqueletos. |
| **Interfaz y jugabilidad** | `juego.py`, `pantallas.py`, `estilo.py`, `figuras.py`, `sonido.py` | Pantallas de inicio, selección, juego y resultados con pygame; muestra la cámara, el movimiento a imitar con su figura, temporizadores, música, efectos y mensajes. |
| **Lógica del juego y puntuación** | `coreografias.py`, `motor_coreografia.py`, `movimientos_logica_juego.py`, `puntuacion.py` | Catálogo de movimientos y canciones, generación de coreografías por dificultad, reconocimiento de cada movimiento a partir de las articulaciones, comparación con el paso esperado y puntuación independiente por jugador. |

Otros archivos:

- `config.py`: ruta del modelo de MediaPipe.
- `download_models.py`: descarga los modelos.
- `test_logica_juego.py`: pruebas automáticas de la lógica del juego.

### Reconocimiento de movimientos

Cada movimiento se reconoce comparando posiciones de las articulaciones **en proporción
al tamaño del cuerpo** (largo del torso y ancho de hombros), de modo que funciona igual
cerca o lejos de la cámara. Por ejemplo, *brazos arriba* se cumple cuando las dos
muñecas están por encima de los hombros una distancia mayor que el 30 % del torso. Solo
se usan los puntos que MediaPipe ve con suficiente visibilidad.

### Pruebas

```bash
python -m unittest test_logica_juego
```

---

Basado en el proyecto de ejemplo de la asignatura:
[CarloHSUA/IPM](https://github.com/CarloHSUA/IPM).
