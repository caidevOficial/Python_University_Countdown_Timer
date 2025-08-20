import flet as ft
import datetime
import asyncio
import os
import random as rd
import pygame # Importamos la biblioteca Pygame
from pygame import mixer # Importamos el módulo mixer de Pygame

# Nota importante: Asegúrate de tener Pygame instalado:
# pip install pygame

# Inicializamos el mezclador de Pygame antes de la clase principal
# para asegurar que esté listo para su uso.
pygame.init()
mixer.init()

# Definimos la clase principal de la aplicación.
# No hereda de ft.Column, sino que es el contenido de una vista.
class CountdownAppContent(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
        self.page = page

        # --- Controles de la Interfaz de Usuario (UI) ---
        self.time_label = ft.Text(
            value="00:00:00", 
            size=50, 
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        self.song_name_label = ft.Text(
            "Selecciona canciones y presiona Play", 
            size=16,
            text_align=ft.TextAlign.CENTER
        )
        self.shuffle_button = ft.IconButton(
            icon=ft.Icons.SHUFFLE,
            tooltip="Modo aleatorio",
            on_click=self.toggle_random_mode,
        )

        # Los controles se añaden directamente aquí
        self.controls = [
            ft.Row(
                [self.time_label],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.FOLDER_OPEN,
                        tooltip="Abrir canciones",
                        on_click=self.open_songs_dialog
                    ),
                    ft.IconButton(
                        icon=ft.Icons.SKIP_PREVIOUS,
                        tooltip="Canción anterior",
                        on_click=self.prev_song
                    ),
                    ft.IconButton(
                        icon=ft.Icons.PLAY_ARROW,
                        tooltip="Reproducir",
                        on_click=self.play_music
                    ),
                    ft.IconButton(
                        icon=ft.Icons.PAUSE,
                        tooltip="Pausar / Reanudar",
                        on_click=self.pause_or_resume_song
                    ),
                    ft.IconButton(
                        icon=ft.Icons.STOP,
                        tooltip="Detener",
                        on_click=self.stop_song
                    ),
                    ft.IconButton(
                        icon=ft.Icons.SKIP_NEXT,
                        tooltip="Siguiente canción",
                        on_click=self.next_song
                    ),
                    self.shuffle_button,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                wrap=True,
            ),
            ft.Row([self.song_name_label], alignment=ft.MainAxisAlignment.CENTER)
        ]

        # --- Estado de la aplicación ---
        self.target_time = None
        self.songs = []
        self.current_song_index = 0
        self.is_random_activated = False
        self.is_paused = False # Estado para rastrear si la música está pausada

        # Establecemos un evento de fin de canción para Pygame
        mixer.music.set_endevent(pygame.USEREVENT)
        self.page.run_task(self.check_end_of_song_event)


    # --- Lógica de la Cuenta Regresiva ---

    # El método show_time_picker se movió a la función principal,
    # ya que pertenece a la vista de selección.
    # El método handle_time_change también se movió por la misma razón.

    async def update_countdown(self):
        if not self.target_time:
            return
            
        while (self.target_time - datetime.datetime.now()).total_seconds() > 0:
            seconds_left = (self.target_time - datetime.datetime.now()).total_seconds()
            m, s = divmod(seconds_left, 60)
            h, m = divmod(m, 60)
            
            self.time_label.value = f"{h:02.0f}:{m:02.0f}:{s:02.0f}"
            self.update()
            await asyncio.sleep(1)
        
        self.time_label.value = "¡TIEMPO CUMPLIDO!"
        self.update()

    # --- Lógica del Reproductor de Música (Pygame.mixer) ---

    async def check_end_of_song_event(self):
        # Esta tarea se ejecuta en segundo plano para escuchar eventos de Pygame
        while True:
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT:
                    self.next_song() # Llama a la siguiente canción al finalizar
            await asyncio.sleep(0.1) # Esperamos un poco para no saturar la CPU

    def on_files_selected(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.songs = [file.path for file in e.files]
            self.song_name_label.value = f"{len(self.songs)} canciones seleccionadas. ¡Listo para reproducir!"
            self.current_song_index = 0
        else:
            self.song_name_label.value = "No se seleccionaron canciones."
        self.update()

    def open_songs_dialog(self, e):
        # Accedemos al file_picker a través de la página
        self.page.file_picker.pick_files(
            allow_multiple=True,
            allowed_extensions=["mp3", "MP3", "wav", "WAV", "ogg", "OGG"]
        )

    def play_music(self, e=None):
        if not self.songs:
            self.song_name_label.value = "¡No hay canciones! Abre una carpeta primero."
            self.update()
            return

        if self.is_random_activated:
            self.set_random_song()
        
        self.play_current_song()

    def play_current_song(self):
        if not self.songs:
            return
        
        song_path = self.songs[self.current_song_index]
        
        try:
            # Usamos mixer.music para cargar y reproducir el archivo directamente
            mixer.music.load(song_path)
            mixer.music.play()
            self.is_paused = False
            self.song_name_label.value = f"🎧 {os.path.basename(song_path)}"
        except Exception as e:
            self.song_name_label.value = f"Error al reproducir: {e}"
        
        self.update()

    def pause_or_resume_song(self, e):
        if mixer.music.get_busy() and not self.is_paused:
            mixer.music.pause()
            self.is_paused = True
            self.song_name_label.value += " (Pausado)"
        elif self.is_paused:
            mixer.music.unpause()
            self.is_paused = False
            self.song_name_label.value = self.song_name_label.value.replace(" (Pausado)", "")
        self.update()

    def stop_song(self, e):
        if mixer.music.get_busy():
            mixer.music.stop()
            pygame.event.clear()
            self.is_paused = False
        self.song_name_label.value = "Música detenida."
        self.update()

    def next_song(self, e=None):
        if not self.songs: return
        if self.is_random_activated:
            self.set_random_song()
        else:
            self.current_song_index = (self.current_song_index + 1) % len(self.songs)
        self.play_current_song()

    def prev_song(self, e):
        if not self.songs: return
        if self.is_random_activated:
            self.set_random_song()
        else:
            self.current_song_index = (self.current_song_index - 1 + len(self.songs)) % len(self.songs)
        self.play_current_song()

    def toggle_random_mode(self, e):
        self.is_random_activated = not self.is_random_activated
        self.shuffle_button.icon_color = ft.Colors.PINK_ACCENT_400 if self.is_random_activated else None
        self.update()
        
    def set_random_song(self):
        if self.songs:
            self.current_song_index = rd.randint(0, len(self.songs) - 1)
    
def main(page: ft.Page):
    page.title = "UTN FRA - Countdown App"
    page.window_width = 500
    page.window_height = 400
    page.window_min_width = 450
    page.window_min_height = 350
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.app_content = CountdownAppContent(page)

    # Creamos las instancias de los controles que se compartirán entre vistas
    page.file_picker = ft.FilePicker(on_result=page.app_content.on_files_selected)
    page.time_picker = ft.TimePicker(
        confirm_text="Confirmar",
        error_invalid_text="Hora fuera de rango",
        help_text="Elige la hora para la cuenta regresiva",
    )
    page.overlay.extend([page.file_picker, page.time_picker])

    def route_change(route):
        page.views.clear()

        # --- Vista de Selección de Hora ---
        if page.route == "/":
            def handle_time_change(e):
                selected_time = page.time_picker.value
                if selected_time:
                    today = datetime.datetime.now().date()
                    target_time = datetime.datetime.combine(today, selected_time)
                    if target_time <= datetime.datetime.now():
                        target_time += datetime.timedelta(days=1)
                    
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"Cuenta regresiva iniciada para las {target_time.strftime('%H:%M')}"),
                        open=True
                    )
                    
                    # Navegamos a la vista principal
                    page.go(f"/app?target_time={target_time.isoformat()}")
                else:
                    page.snack_bar = ft.SnackBar(
                        ft.Text("Selección de hora cancelada."),
                        open=True
                    )
                page.update()

            page.time_picker.on_change = handle_time_change

            page.views.append(
                ft.View(
                    "/",
                    [
                        ft.AppBar(title=ft.Text("Seleccionar Hora"), bgcolor=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Column(
                            [
                                ft.Text(
                                    "Configura la hora para la cuenta regresiva",
                                    size=16,
                                    text_align=ft.TextAlign.CENTER
                                ),
                                ft.ElevatedButton(
                                    "Seleccionar Hora",
                                    icon=ft.Icons.TIMER_SHARP,
                                    on_click=lambda e: page.open(page.time_picker)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=True
                        ),
                    ],
                )
            )

        # --- Vista de la Aplicación Principal ---
        elif page.route.startswith("/app"):
            # app_content = CountdownAppContent(page)
            app_content = page.app_content
            
            # Pasamos la hora objetivo a la vista principal
            target_time_str = page.route.split('?')[1].split('=')[1]
            app_content.target_time = datetime.datetime.fromisoformat(target_time_str)
            page.run_task(app_content.update_countdown)

            page.views.append(
                ft.View(
                    "/app",
                    [
                        ft.AppBar(title=ft.Text("Reproductor y Temporizador"), bgcolor=ft.Colors.ON_SURFACE_VARIANT),
                        app_content,
                    ],
                )
            )

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)
    
if __name__ == "__main__":
    ft.app(target=main)
