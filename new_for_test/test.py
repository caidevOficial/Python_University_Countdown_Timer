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

# --- CAMBIO PRINCIPAL ---
# Ahora se hereda de un control de diseño como ft.Column.
# Ya no se usa UserControl ni el método build().
class CountdownApp(ft.Column):
    def __init__(self):
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

        # La llamada a super().__init__() se hace al final, pasando los controles
        # y las propiedades del layout.
        super().__init__(
            controls=[
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
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )

        # --- Estado de la aplicación ---
        self.target_time = None
        self.songs = []
        self.current_song_index = 0
        self.is_random_activated = False
        self.is_paused = False # Estado para rastrear si la música está pausada
        self.is_stopped = True

        # --- Controles no visuales ---
        # Eliminamos flet_audio y usamos pygame.mixer.music
        self.file_picker = ft.FilePicker(on_result=self.on_files_selected)
        self.time_picker = ft.TimePicker(
            confirm_text="Confirmar",
            error_invalid_text="Hora fuera de rango",
            help_text="Elige la hora para la cuenta regresiva",
            on_change=self.handle_time_change,
        )

        # Establecemos un evento de fin de canción para Pygame
        # Esto nos permite saber cuándo una canción ha terminado de reproducirse
        mixer.music.set_endevent(pygame.USEREVENT)

    def did_mount(self):
        # Extendemos la página con los controles
        self.page.overlay.extend([self.file_picker, self.time_picker])
        self.show_time_picker()
        # Este page.update() es crucial para que los controles del overlay existan.
        self.page.update()
        # Iniciamos la tarea en segundo plano para escuchar el evento de fin de canción
        self.page.run_task(self.check_end_of_song_event)

    # --- Lógica de la Cuenta Regresiva ---

    def show_time_picker(self, e=None):
        self.time_picker.open = True
        if self.page:
            self.page.update()

    def handle_time_change(self, e):
        selected_time = self.time_picker.value
        if selected_time:
            today = datetime.datetime.now().date()
            self.target_time = datetime.datetime.combine(today, selected_time)
            
            if self.target_time <= datetime.datetime.now():
                self.target_time += datetime.timedelta(days=1)

            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Cuenta regresiva iniciada para las {self.target_time.strftime('%H:%M')}"),
                open=True
            )
            self.page.run_task(self.update_countdown)
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Selección de hora cancelada."),
                open=True
            )
        self.page.update()

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
        self.file_picker.pick_files(
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
        self.is_stopped = False

    def play_current_song(self):
        if not self.songs:
            return
        song_path = self.songs[self.current_song_index]
        
        try:
            # Usamos mixer.music para cargar y reproducir el archivo directamente
            mixer.music.load(song_path)
            mixer.music.play()
            self.is_paused = False
            self.is_stopped = False
            self.song_name_label.value = f"🎧 {os.path.basename(song_path)}"
        except Exception as e:
            self.song_name_label.value = f"Error al reproducir: {e}"
        
        self.update()

    def pause_or_resume_song(self, e):
        if mixer.music.get_busy() and not self.is_paused:
            mixer.music.pause()
            self.is_paused = True
            self.song_name_label.value += " (Pausado)"
        elif self.is_paused and not self.is_stopped:
            mixer.music.unpause()
            self.is_paused = False
            self.song_name_label.value = self.song_name_label.value.replace(" (Pausado)", "")
        self.update()

    def stop_song(self, e):
        if mixer.music.get_busy():
            mixer.music.stop()
            # Se ha añadido esta línea para limpiar la cola de eventos.
            # Esto previene que el evento de "fin de canción" active la siguiente.
            pygame.event.clear()
            self.is_paused = False
            self.is_stopped = True
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
    
    app = CountdownApp()
    page.add(app)
    
if __name__ == "__main__":
    ft.app(target=main)
