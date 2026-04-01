import customtkinter as ctk
import json
import os
import pygame
from tkinter import filedialog

# =========================
# CONFIGURACION GENERAL              ##1e1e2e
# =========================
ctk.set_appearance_mode("dark")

BG = "#1e1e2e"
SURFACE = "#181825"
SURFACE_LIGHT = "#313244"
ACCENT = "#cba6f7"
ACCENT_HOVER = "#b4befe"
TEXT = "#cdd6f4"
MUTED = "#a6adc8"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_TAREAS = os.path.join(BASE_DIR, "tareas_v2.json")
ARCHIVO_CANCIONES = os.path.join(BASE_DIR, "canciones.json")
# =========================
# INIT PYGAME AUDIO
# =========================
pygame.mixer.init()

# =========================
# VENTANA PRINCIPAL
# =========================
ventana = ctk.CTk(fg_color=BG)
ventana.title("Focus app <3")
ventana.geometry("1160x620")
ventana.minsize(1060, 560)

# =========================
# VARIABLES DEL CRONOMETRO
# =========================
TIEMPO_INICIAL = 25 * 60 #se pone 25 * 60 porque el cronometro cuenta en segundos
tiempo_restante = TIEMPO_INICIAL #es tiempo restante porque el cronometro cuenta hacia atras
timer_activo = False #indica si el cronometro esta activo
timer_id = None #guarda el id del cronometro

# =========================
# VARIABLES DEL REPRODUCTOR 
# =========================
lista_canciones = []       # lista de rutas completas
cancion_actual_idx = None  # índice de la canción en reproducción
esta_pausado = False

# =========================
# VARIABLES DE MATERIAS
# =========================
notas_materias = {}   # diccionario: { "Matemáticas": "texto de notas..." }
ventana_notas_abierta = None # la ventana flotante que está abierta ahora
materia_activa = None  # nombre de la materia cuya ventana está abierta

# =========================
# FUNCIONES DE TAREAS
# =========================
def guardar_tareas():
    tareas = []
    for widget in lista_tareas.winfo_children():
        if isinstance(widget, ctk.CTkCheckBox):
            tareas.append({
                "texto": widget.cget("text"),
                "completada": bool(widget.get()),
            })
    with open(ARCHIVO_TAREAS, "w", encoding="utf-8") as archivo:
        json.dump(tareas, archivo, ensure_ascii=False, indent=2)


def crear_tarea(texto, completada=False):
    checkbox = ctk.CTkCheckBox(
        lista_tareas,
        text=texto,
        text_color=TEXT,
        border_color=MUTED,
        fg_color=ACCENT,
        hover_color=ACCENT_HOVER,
        command=lambda: al_marcar_tarea(checkbox)
    )
    checkbox.pack(anchor="w", fill="x", padx=10, pady=6)
    if completada:
        checkbox.select()
    return checkbox


def al_marcar_tarea(checkbox):
    guardar_tareas()
    if checkbox.get() == 1:
        ventana.after(2000, lambda: eliminar_tarea(checkbox))


def eliminar_tarea(checkbox):
    if checkbox.winfo_exists() and checkbox.get() == 1:
        checkbox.destroy()
        guardar_tareas()


def agregar_tarea():
    texto_tarea = entrada_tarea.get().strip()
    if texto_tarea == "":
        return
    crear_tarea(texto_tarea)
    entrada_tarea.delete(0, "end")
    guardar_tareas()


def cargar_tareas():
    try:
        with open(ARCHIVO_TAREAS, "r", encoding="utf-8") as archivo:
            tareas_guardadas = json.load(archivo)
        for tarea in tareas_guardadas:
            if not tarea["completada"]:
                crear_tarea(tarea["texto"], False)
        guardar_tareas()
    except FileNotFoundError:
        pass

# =========================
# FUNCIONES DEL CRONOMETRO
# =========================
def actualizar_texto_cronometro():
    minutos = tiempo_restante // 60
    segundos = tiempo_restante % 60
    label_cronometro.configure(text=f"{minutos:02d}:{segundos:02d}")



def correr_cronometro():
    global tiempo_restante, timer_activo, timer_id
    if timer_activo:
        if tiempo_restante > 0:
            tiempo_restante -= 1
            actualizar_texto_cronometro()
            timer_id = ventana.after(1000, correr_cronometro)
        else:
            ventana.bell()
            tiempo_restante = TIEMPO_INICIAL
            actualizar_texto_cronometro()
            timer_activo = False
            timer_id = None


def iniciar_cronometro():
    global timer_activo
    if not timer_activo:
        timer_activo = True
        correr_cronometro()


def pausar_cronometro():
    global timer_activo, timer_id
    timer_activo = False
    if timer_id is not None:
        ventana.after_cancel(timer_id)
        timer_id = None


def resetear_cronometro():
    global tiempo_restante, timer_activo, timer_id
    timer_activo = False
    if timer_id is not None:
        ventana.after_cancel(timer_id)
        timer_id = None
    tiempo_restante = TIEMPO_INICIAL
    actualizar_texto_cronometro()

# =========================
# FUNCIONES DEL REPRODUCTOR
# =========================
def explorar_canciones():
    """Abre el explorador para seleccionar archivos de audio."""
    archivos = filedialog.askopenfilenames(
        title="Seleccionar canciones",
        filetypes=[("Archivos de audio", "*.mp3 *.wav *.ogg *.flac"), ("Todos", "*.*")]
    )
    se_agregaron_canciones = False
    for ruta in archivos:
        if ruta not in lista_canciones:
            lista_canciones.append(ruta)
            nombre = os.path.basename(ruta)
            agregar_item_lista(nombre, len(lista_canciones) - 1)
            se_agregaron_canciones = True
    if se_agregaron_canciones:
        guardar_canciones()


def agregar_item_lista(nombre, idx):
    """Agrega un botón a la lista visual de canciones."""
    btn = ctk.CTkButton(
        frame_lista_canciones,
        text=nombre,
        anchor="w",
        fg_color="transparent",
        hover_color=SURFACE_LIGHT,
        text_color=MUTED,
        font=("Arial", 12),
        height=32,
        command=lambda i=idx: reproducir_cancion(i)
    )
    btn.pack(fill="x", padx=4, pady=2)


def reproducir_cancion(idx):
    """Reproduce la canción en el índice dado."""
    global cancion_actual_idx, esta_pausado

    if idx < 0 or idx >= len(lista_canciones):
        return

    cancion_actual_idx = idx
    esta_pausado = False

    ruta = lista_canciones[idx]
    nombre = os.path.basename(ruta)

    pygame.mixer.music.stop()
    pygame.mixer.music.load(ruta)
    pygame.mixer.music.set_volume(slider_volumen.get() / 100)
    pygame.mixer.music.play()

    label_cancion_actual.configure(text=nombre)
    btn_play_pause.configure(text="⏸  Pausar")

    # Resaltar item activo en la lista
    for i, widget in enumerate(frame_lista_canciones.winfo_children()):
        if isinstance(widget, ctk.CTkButton):
            widget.configure(text_color=ACCENT if i == idx else MUTED)


def toggle_play_pause():
    """Alterna entre play y pausa."""
    global esta_pausado

    if cancion_actual_idx is None:
        # Si no hay nada cargado pero hay canciones, reproducir la primera
        if lista_canciones:
            reproducir_cancion(0)
        return

    if esta_pausado:
        pygame.mixer.music.unpause()
        esta_pausado = False
        btn_play_pause.configure(text="⏸  Pausar")
    else:
        pygame.mixer.music.pause()
        esta_pausado = True
        btn_play_pause.configure(text="▶  Play")


def stop_musica():
    """Detiene la reproducción."""
    global cancion_actual_idx, esta_pausado
    pygame.mixer.music.stop()
    cancion_actual_idx = None
    esta_pausado = False
    btn_play_pause.configure(text="▶  Play")
    label_cancion_actual.configure(text="Ninguna")


def cambiar_volumen(valor):
    """Actualiza el volumen del mixer."""
    pygame.mixer.music.set_volume(float(valor) / 100)
    label_vol.configure(text=f"{int(float(valor))}%")

def  guardar_canciones():
    with open(ARCHIVO_CANCIONES, "w", encoding="utf-8") as f:
        json.dump(lista_canciones, f, ensure_ascii=False, indent=2)

def cargar_canciones():
    try:
        with open(ARCHIVO_CANCIONES, "r", encoding="utf-8") as f:
            rutas = json.load(f)
        for ruta in rutas:
            if os.path.exists(ruta): # solo si el archivo todavía existe
                lista_canciones.append(ruta)
                nombre = os.path.basename(ruta)
                agregar_item_lista(nombre, len(lista_canciones) -1)
    except FileNotFoundError:
        pass


def al_cerrar_programa():
    guardar_tareas()
    guardar_canciones()
    guardar_materias()
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    ventana.destroy()

# =========================
# FUNCIONES DE MATERIAS
# =========================

def guardar_materias():
    with open("materias.json", "w", encoding="utf-8") as f:
        json.dump(notas_materias, f, ensure_ascii=False, indent=2)


def cargar_materias():
    try:
        with open("materias.json", "r", encoding="utf-8") as f:
            datos = json.load(f)
        for nombre, notas in datos.items():
            notas_materias[nombre] = notas
            crear_boton_materia(nombre)
    except FileNotFoundError:
        pass


def crear_boton_materia(nombre):
    btn = ctk.CTkButton(
        frame_botones_materias,
        text=nombre,
        height=30,
        fg_color=SURFACE_LIGHT,
        hover_color=ACCENT,
        text_color=TEXT,
        font=("Arial", 13),
        command=lambda n=nombre: toggle_ventana_notas(n, btn)
        # lambda n=nombre captura el nombre en ese momento
        # sin esto, todos los botones usarían el último nombre creado
    )
    btn.pack(side="left", padx=4, pady=4)
    return btn

def toggle_ventana_notas(nombre, boton):
    global ventana_notas_abiertas, materia_activa
    
    if materia_activa == nombre and ventana_notas_abiertas is not None:
        cerrar_ventana_notas()
        return
    
    if ventana_notas_abierta is not None:
        cerrar_ventana_notas()

    # Abrir la ventana de notas
    materia_activa = nombre
    boton.configure(fg_color=ACCENT, text_color="#11111b")  # resaltar botón activo
    
    win = ctk.CTkToplevel(ventana) # ventana flotante hija de la principal
    win.title(f'Notas - {nombre}')
    win.geometry("380x420")
    win.configure(fg_color = BG)
    
    ctk.CTkLabel(
        win,
        text=f'📓  {nombre}',
        font=("Arial", 18, "bold"),
        text_color=ACCENT,
    ).pack(anchor="w", padx=16, pady=(16, 8))

    caja_notas = ctk.CTkTextbox(
        win,
        fg_color=SURFACE_LIGHT,
        text_color=TEXT,
        border_color=MUTED,
        border_width=1,
        font=("Arial", 13),
        wrap="word"
    )
    caja_notas.pack(fill="both", expand=True, padx=16, pady=(0, 8))

    if notas_materias.get(nombre):
        caja_notas.insert("1.0", notas_materias[nombre])
    
    def al_escribir(event):
        notas_materias[nombre] = caja_notas.get("1.0", "end-1c")
        guardar_materias()
    
    caja_notas.bind("<KeyRelease>", al_escribir)
    
    ctk.CTkButton(
        win,
        text="Cerrar",
        height=34,
        fg_color=SURFACE_LIGHT,
        hover_color=SURFACE,
        text_color=TEXT,
        command=cerrar_ventana_notas,
    ).pack(fill="x", padx=16, pady=(0, 16))
    win.protocol("WM_DELETE_WINDOW", cerrar_ventana_notas)
    ventana_notas_abiertas = win

def cerrar_ventana_notas():
    global ventana_notas_abiertas, materia_activa
    guardar_materias()
    
    for widget in frame_botones_materias.winfo_children():
        if isinstance(widget, ctk.CTkButton) and widget.cget("text") == materia_activa:
            widget.configure(fg_color=SURFACE_LIGHT, text_color=TEXT)

        if ventana_notas_abiertas is not None:
            ventana_notas_abiertas.destroy()

        ventana_notas_abiertas = None
        materia_activa = None
    
def agregar_materia():
    nombre= entrada_materia.get().strip()
    if nombre == "" or nombre in notas_materias:
        entrada_materia.delete(0, "end")
        return
    notas_materias[nombre] = ""
    crear_boton_materia(nombre)
    entrada_materia.delete(0, "end")
    guardar_materias()

# =========================
# LAYOUT PRINCIPAL
# =========================
frame_left = ctk.CTkFrame(ventana, width=260, fg_color=SURFACE, corner_radius=0)
frame_left.pack(side="left", fill="y")
frame_left.pack_propagate(False)

frame_center = ctk.CTkFrame(ventana, fg_color=BG, corner_radius=0)
frame_center.pack(side="left", expand=True, fill="both")
frame_center.grid_columnconfigure(0, weight=1)
frame_center.grid_rowconfigure(0, weight=0)  # fila 0: barra de materias  ← antes era weight=1
frame_center.grid_rowconfigure(1, weight=1)  # fila 1: espacio             ← agregar esta línea
frame_center.grid_rowconfigure(2, weight=0)  # cronometro (era fila 1, ahora es 2)
frame_center.grid_rowconfigure(3, weight=0)  # botones timer (era fila 2)
frame_center.grid_rowconfigure(4, weight=1)  # espacio inferior (era fila 3)

frame_right = ctk.CTkFrame(ventana, width=220, fg_color=SURFACE, corner_radius=0)
frame_right.pack(side="right", fill="y")
frame_right.pack_propagate(False)

# =========================
# BARRA SUPERIOR DE MATERIAS
# =========================
frame_barra_materias = ctk.CTkFrame(frame_center, fg_color=SURFACE, corner_radius=0, height=50)
frame_barra_materias.grid(row=0, column=0, sticky="ew")
frame_barra_materias.grid_propagate(False)  # que no cambie de tamaño solo

ctk.CTkLabel(
    frame_barra_materias,
    text="Materias:",
    font=("Arial", 13),
    text_color=MUTED,
).pack(side="left", padx=(12, 6), pady=10)

entrada_materia = ctk.CTkEntry(
    frame_barra_materias,
    placeholder_text="Nueva materia...",
    width=150,
    height=30,
    fg_color=SURFACE_LIGHT,
    border_color=MUTED,
    text_color=TEXT,
)
entrada_materia.pack(side="left", padx=(0, 4), pady=10)
entrada_materia.bind("<Return>", lambda event: agregar_materia())

ctk.CTkButton(
    frame_barra_materias,
    text="＋",
    width=30,
    height=30,
    fg_color=ACCENT,
    hover_color=ACCENT_HOVER,
    text_color="#11111b",
    font=("Arial", 15, "bold"),
    command=agregar_materia,
).pack(side="left", padx=(0, 10), pady=10)

# Separador visual
ctk.CTkFrame(frame_barra_materias, width=2, height=30, fg_color=SURFACE_LIGHT).pack(side="left", padx=6)

# Acá se van a colocar los botones de cada materia
frame_botones_materias = ctk.CTkFrame(frame_barra_materias, fg_color="transparent")
frame_botones_materias.pack(side="left", fill="both", expand=True, padx=4)

# =========================
# PANEL CENTRAL - CRONOMETRO
# =========================
label_cronometro = ctk.CTkLabel(
    frame_center,
    text="25:00",
    font=("Arial", 72, "bold"),
    text_color=TEXT
)
label_cronometro.grid(row=2, column=0, pady=(40, 15))

frame_botones_timer = ctk.CTkFrame(frame_center, fg_color="transparent")
frame_botones_timer.grid(row=3, column=0, pady=(0, 10))

boton_iniciar = ctk.CTkButton(
    frame_botones_timer,
    text="Iniciar",
    width=110,
    fg_color=ACCENT,
    hover_color=ACCENT_HOVER,
    text_color="#11111b",
    command=iniciar_cronometro,
)
boton_iniciar.pack(side="left", padx=8)

boton_pausar = ctk.CTkButton(
    frame_botones_timer,
    text="Pausar",
    width=110,
    fg_color=SURFACE_LIGHT,
    hover_color=SURFACE,
    text_color=TEXT,
    command=pausar_cronometro
)
boton_pausar.pack(side="left", padx=8)

boton_reset = ctk.CTkButton(
    frame_botones_timer,
    text="Reset",
    width=110,
    fg_color=SURFACE_LIGHT,
    hover_color=SURFACE,
    text_color=TEXT,
    command=resetear_cronometro,
)
boton_reset.pack(side="left", padx=8)

# =========================
# PANEL IZQUIERDO - TAREAS
# =========================
titulo_tareas = ctk.CTkLabel(
    frame_left,
    text="Mis tareas",
    font=("Arial", 24, "bold"),
    text_color=TEXT,
)
titulo_tareas.pack(anchor="w", padx=16, pady=(20, 6))

subtitulo_tareas = ctk.CTkLabel(
    frame_left,
    text="Agrega tus tareas y marcalas cuando las completes.",
    font=("Arial", 13),
    text_color=MUTED,
    wraplength=220,
    justify="left",
)
subtitulo_tareas.pack(anchor="w", padx=16, pady=(0, 16))

entrada_tarea = ctk.CTkEntry(
    frame_left,
    placeholder_text="Escribe una tarea...",
    height=40,
    fg_color=SURFACE_LIGHT,
    border_color=MUTED,
    text_color=TEXT,
)
entrada_tarea.pack(fill="x", padx=16, pady=(0, 10))
entrada_tarea.bind("<Return>", lambda event: agregar_tarea())

boton_agregar = ctk.CTkButton(
    frame_left,
    text="Agregar tarea",
    height=40,
    fg_color=ACCENT,
    hover_color=ACCENT_HOVER,
    text_color="#11111b",
    command=agregar_tarea,
)
boton_agregar.pack(fill="x", padx=16, pady=(0, 16))

lista_tareas = ctk.CTkScrollableFrame(
    frame_left,
    fg_color=SURFACE_LIGHT,
    border_width=1,
    border_color=MUTED,
)
lista_tareas.pack(fill="both", expand=True, padx=16, pady=(0, 16))

# =========================
# PANEL DERECHO - MUSICA
# =========================
titulo_musica = ctk.CTkLabel(
    frame_right,
    text="♫  Música",
    font=("Arial", 20, "bold"),
    text_color=TEXT,
)
titulo_musica.pack(anchor="w", padx=16, pady=(20, 4))

subtitulo_musica = ctk.CTkLabel(
    frame_right,
    text="Cargá canciones para escuchar mientras trabajás.",
    font=("Arial", 12),
    text_color=MUTED,
    wraplength=190,
    justify="left",
)
subtitulo_musica.pack(anchor="w", padx=16, pady=(0, 12))

boton_explorar = ctk.CTkButton(
    frame_right,
    text="＋  Agregar canciones",
    height=36,
    fg_color=ACCENT,
    hover_color=ACCENT_HOVER,
    text_color="#11111b",
    font=("Arial", 13, "bold"),
    command=explorar_canciones,
)
boton_explorar.pack(fill="x", padx=16, pady=(0, 10))

# Lista scrollable de canciones
frame_lista_canciones = ctk.CTkScrollableFrame(
    frame_right,
    fg_color=SURFACE_LIGHT,
    border_width=1,
    border_color=MUTED,
    label_text="",
)
frame_lista_canciones.pack(fill="both", expand=True, padx=16, pady=(0, 10))

# Separador visual
ctk.CTkLabel(frame_right, text="", height=2, fg_color=SURFACE_LIGHT).pack(fill="x", padx=16)

# Canción actual
ctk.CTkLabel(
    frame_right,
    text="Reproduciendo:",
    font=("Arial", 11),
    text_color=MUTED,
).pack(anchor="w", padx=16, pady=(8, 0))

label_cancion_actual = ctk.CTkLabel(
    frame_right,
    text="Ninguna",
    font=("Arial", 12, "bold"),
    text_color=ACCENT,
    wraplength=190,
    justify="left",
)
label_cancion_actual.pack(anchor="w", padx=16, pady=(2, 10))

# Botones play/pause y stop
frame_controles = ctk.CTkFrame(frame_right, fg_color="transparent")
frame_controles.pack(fill="x", padx=16, pady=(0, 8))

btn_play_pause = ctk.CTkButton(
    frame_controles,
    text="▶  Play",
    height=34,
    fg_color=ACCENT,
    hover_color=ACCENT_HOVER,
    text_color="#11111b",
    font=("Arial", 13, "bold"),
    command=toggle_play_pause,
)
btn_play_pause.pack(side="left", expand=True, fill="x", padx=(0, 4))

btn_stop = ctk.CTkButton(
    frame_controles,
    text="⏹",
    width=36,
    height=34,
    fg_color=SURFACE_LIGHT,
    hover_color=SURFACE,
    text_color=TEXT,
    font=("Arial", 14),
    command=stop_musica,
)
btn_stop.pack(side="left")

# Volumen
frame_vol = ctk.CTkFrame(frame_right, fg_color="transparent")
frame_vol.pack(fill="x", padx=16, pady=(0, 16))

ctk.CTkLabel(
    frame_vol,
    text="Vol",
    font=("Arial", 12),
    text_color=MUTED,
    width=28,
).pack(side="left")

slider_volumen = ctk.CTkSlider(
    frame_vol,
    from_=0,
    to=100,
    command=cambiar_volumen,
    button_color=ACCENT,
    button_hover_color=ACCENT_HOVER,
    progress_color=ACCENT,
)
slider_volumen.set(70)
slider_volumen.pack(side="left", expand=True, fill="x", padx=6)

label_vol = ctk.CTkLabel(
    frame_vol,
    text="70%",
    font=("Arial", 12),
    text_color=MUTED,
    width=36,
)
label_vol.pack(side="left")

# Volumen inicial
pygame.mixer.music.set_volume(0.7)

# =========================
# CARGA INICIAL
# =========================
cargar_tareas()
actualizar_texto_cronometro()
cargar_canciones()
cargar_materias()
ventana.protocol("WM_DELETE_WINDOW", al_cerrar_programa)

# =========================
# LOOP PRINCIPAL
# =========================
ventana.mainloop()
