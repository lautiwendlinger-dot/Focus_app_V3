import customtkinter as ctk
import json


# =========================
# CONFIGURACION GENERAL
# =========================
ctk.set_appearance_mode("dark")

BG = "#1e1e2e"
SURFACE = "#313244"
SURFACE_LIGHT = "#45475a"
ACCENT = "#89b4fa"
ACCENT_HOVER = "#74a7f7"
TEXT = "#cdd6f4"
MUTED = "#a6adc8"

ARCHIVO_TAREAS = "tareas_v2.json"


# =========================
# VENTANA PRINCIPAL
# =========================
ventana = ctk.CTk(fg_color=BG)
ventana.title("Focus app <3")
ventana.geometry("980x620")
ventana.minsize(900, 560)

# =========================
# VARIABLES DEL CRONOMETRO
# =========================

TIEMPO_INICIAL = 25 * 60
tiempo_restante = TIEMPO_INICIAL
timer_activo = False
timer_id = None

# =========================
# FUNCIONES DE TAREAS
# =========================
def guardar_tareas():
    tareas = []

    for widget in lista_tareas.winfo_children():
        if isinstance(widget, ctk.CTkCheckBox):
            tareas.append(
                {
                    "texto": widget.cget("text"),
                    "completada": bool(widget.get()),
                }
            )

    with open(ARCHIVO_TAREAS, "w", encoding="utf-8") as archivo:
        json.dump(tareas, archivo, ensure_ascii=False, indent=2)


def cambiar_estado_tarea():
    guardar_tareas()


def crear_tarea(texto, completada=False):
    checkbox = ctk.CTkCheckBox(
        lista_tareas,
        text=texto,
        text_color=TEXT,
        border_color=MUTED,
        fg_color=ACCENT,
        hover_color=ACCENT_HOVER,
        command=lambda:al_marcar_tarea(checkbox)
    )
    checkbox.pack(anchor="w", fill="x", padx=10, pady=6)

    if completada:
        checkbox.select()

    return checkbox

def al_marcar_tarea(checkbox):
    guardar_tareas()
    
    if checkbox.get()==1:
        ventana.after(2000, lambda: eliminar_tarea(checkbox))

def eliminar_tarea(checkbox):
    if checkbox.winfo_exists() and checkbox.get()==1:
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
    minutos = tiempo_restante//60
    segundos = tiempo_restante%60
    label_cronometro.configure(text=f"{minutos:02d}:{segundos:02d}")

def correr_cronometro():
    global tiempo_restante, timer_activo, timer_id

    if timer_activo:
        if tiempo_restante > 0:
            tiempo_restante -=1
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
# LAYOUT PRINCIPAL
# =========================
frame_left = ctk.CTkFrame(ventana, width=260, fg_color=SURFACE, corner_radius=0)
frame_left.pack(side="left", fill="y")
frame_left.pack_propagate(False)

frame_center = ctk.CTkFrame(ventana, fg_color=BG, corner_radius=0)
frame_center.pack(side="left", expand=True, fill="both")
frame_center.grid_columnconfigure(0, weight=1)
frame_center.grid_rowconfigure(0, weight=1)
frame_center.grid_rowconfigure(1, weight=0)
frame_center.grid_rowconfigure(2, weight=0)
frame_center.grid_rowconfigure(3, weight=0)
frame_center.grid_rowconfigure(4, weight=1)


frame_right = ctk.CTkFrame(ventana, width=150, fg_color=SURFACE, corner_radius=0)
frame_right.pack(side="right", fill="y")
frame_right.pack_propagate(False)

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
frame_botones_timer.grid(row=3, column=0, pady=(0,10))

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
# PANEL IZQUIERDO
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
# CARGA INICIAL
# =========================
cargar_tareas()
actualizar_texto_cronometro()


# =========================
# LOOP PRINCIPAL
# =========================
ventana.mainloop()
