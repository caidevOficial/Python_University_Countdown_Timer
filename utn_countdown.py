# Copyright (C) 2023 <UTN FRA>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import re
import random as rd
import tkinter as tk
import warnings
from tkinter import Button, filedialog
from tkinter.messagebox import (
    askyesno as question, showinfo as alert
)
from tkinter.simpledialog import askstring as prompt

import customtkinter
import mutagen
from PIL import Image, ImageTk
from pygame import mixer


class CountdownApp(customtkinter.CTk):
    """
    The `CountdownApp` class is a countdown timer GUI that displays the time left between a specified initial
    time and the current time.
    """

    def __init__(self) -> None:
        """
        This is the initialization function for a countdown timer GUI, which includes setting up the
        window, creating the main frame, displaying an image banner, and playing background music.
        """
        super().__init__()
        mixer.init(frequency=44100)
        self.title(f"UTN FRA - countdown")
        self.minsize(320, 250)
        self.BACKGROUND_MUSIC = '.'
        self.__actual_song = None
        self.__actual_song_name = None
        self.__actual_position = 0
        self.__is_playing = False
        self.__is_paused = False
        self.__is_stopped = False
        self.__is_random_activated = False
        self.__time_done = False
        self.__alert_show = False
        self.__final_snd_path = './assets/sound/closs.mp3'
        self.__songs = list()
        self.__configure_frames()
        self.__configure_date_bg_img()
        self.__configure_labels()
        self.__configure_buttons()
        self.__configure_sound()
        self.__lbl_update_song = ''
        self.__calculate_time_left()

    #! #### CONFIGURATIONS #### !#
    def __configure_frames(self) -> None:
        """
        The function configures two frames with specific properties and grid positions.
        """
        self.__frame_main = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.__frame_main.grid(row = 0, column = 0, padx = 10, pady = 5, columnspan = 1, rowspan = 1, sticky="nswe")

        self.__frame_player = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent", bg_color = 'transparent', width=600, height=50)
        self.__frame_player.grid(row = 1, column = 0, padx = 20, pady = 5, columnspan = 1, rowspan = 1, sticky="nswe")

    def __configure_buttons(self) -> None:
        """
        The function `__configure_buttons` creates and configures buttons for a music player interface.
        """
        self.__configure_icons()
        self.__btn_open_song = customtkinter.CTkButton(master=self.__frame_player, width = 100, image=self.__icon_open_logo, text='', command=self.__open_songs)
        self.__btn_open_song.grid(row=0, column = 0, padx=5, pady=5)

        self.__btn_prev_song = customtkinter.CTkButton(master=self.__frame_player, width = 100, image=self.__icon_previous_logo, text='', command=self.__prev_song)
        self.__btn_prev_song.grid(row=0, column = 1, padx=5, pady=5)

        self.__btn_play_song = customtkinter.CTkButton(master=self.__frame_player, width = 100, image=self.__icon_play_logo, text='', command=self.__init_music_player)
        self.__btn_play_song.grid(row=0, column = 2, padx=5, pady=5)

        self.__btn_pause_song = customtkinter.CTkButton(master=self.__frame_player, width = 100, image=self.__icon_pause_logo, text='', command=self.__pause_song)
        self.__btn_pause_song.grid(row=0, column = 3, padx=5, pady=5)

        self.__btn_stop_song = customtkinter.CTkButton(master=self.__frame_player, width = 100, image=self.__icon_stop_logo, text='', command=self.__stop_song)
        self.__btn_stop_song.grid(row=0, column = 4, padx=5, pady=5)

        self.__btn_next_song = customtkinter.CTkButton(master=self.__frame_player, width = 100, image=self.__icon_next_logo, text='', command=self.__next_song)
        self.__btn_next_song.grid(row=0, column = 5, padx=5, pady=5)

        self.__btn_shuffle_song = customtkinter.CTkButton(master=self.__frame_player, width = 100, image=self.__icon_shuffle_logo, text='', command=self.__activate_random_mode)
        self.__btn_shuffle_song.grid(row=0, column = 6, padx=5, pady=5)

    def __configure_labels(self) -> None:
        """
        The function configures two labels, one for displaying the time and one for displaying the song
        name.
        """
        self.__lbl_time = tk.Label(master=self.__frame_main, relief=tk.RAISED, cursor='dot', font=("Arial", 50, "bold"), bg='black', fg='cyan', justify='left')
        self.__lbl_time.grid(row=2, column=0, columnspan=1, sticky='we')
        self.__lbl_time.place(x=50, y=420)

        self.__lbl_song_name = customtkinter.CTkLabel(master=self.__frame_player, text=f"Select songs and clic Play to listen music", font=("Arial", 15, "bold"), width=35)
        self.__lbl_song_name.grid(row=1, column=0, columnspan=6, padx=10, pady=10)

    def __calculate_time_left(self) -> None:
        """
        The function calculates the time left between the current time and a specified initial time and
        updates a label with the formatted time.
        """
        seconds = (self.__initial_time - datetime.datetime.now()).total_seconds()
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if not self.__time_done:
            if h < 0:
                h = 0
                m = 0
                s = 0
                self.__time_done = True
                self.__play_closs_voice()
            msg = f"  {h:02.0f}  :  {m:02.0f}  :  {s:02.0f}\nhour mins secs"
            self.__lbl_time.configure(text = f"{msg}")
            self.__lbl_time.after(1000, self.__calculate_time_left)
        elif not self.__alert_show and self.__time_done:
            self.__alert_show = True
            alert('GET READY!', 'TIME DONE, GET READY FOR THE CLASS!')
    
    def __configure_date(self) -> bool:
        """
        The function __configure_date prompts the user to enter a valid hour in the format HH:MM for the
        current date, and then converts it into a datetime object.
        :return: a boolean value. If the configuration of the date is successful, it returns True. If
        there is an exception or error during the configuration, it returns False.
        """
        try:
            complete_hour = None
            actual_date = datetime.datetime.today().date()
            while not complete_hour:
                complete_hour = prompt('Activate', f'Enter Hour in format: HH:MM for date {actual_date}')
                time_pattern = r'[0-2]{1}[0-9]{1}:[0-5]{1}[0-9]{1}'
                if not re.match(f'^{time_pattern}$', complete_hour):
                    complete_hour = None
            self.__initial_time = datetime.datetime.strptime(f'{actual_date} {complete_hour}:00', '%Y-%m-%d %H:%M:%S')
            alert('Datetime', f'Datetime configured: {self.__initial_time}')
            return True
        except Exception as e:
            print(e.with_traceback(None))
            return False

    def __configure_bg_image(self) -> bool:
        """
        This function configures the background image based on user input.
        :return: a boolean value.
        """
        try:
            img_path = './assets/img/background_init.png'
            if question('Initial image?', 'Would you like an initial image?'):
                img_path = './assets/img/background_init.png'
                #self.__image = Image.open('./assets/img/background_init.png')
            elif question('Back image?', 'Would you like a back image?'):
                img_path = './assets/img/background_back.png'
            elif question('End image?', 'Would you like a end image?'):
                img_path = './assets/img/background_end.png'
            
            self.__image = ImageTk.PhotoImage(
                Image.open(img_path).resize((1191, 671)))
            self.__top_banner = customtkinter.CTkLabel(master = self.__frame_main, image = self.__image, text='')
            self.__top_banner.grid_configure(row = 0, column = 0, padx = 10, pady = 5, columnspan = 1, rowspan = 1, sticky = 'we')
            return True
        except Exception as e:
            print(e.with_traceback(None))
            return False

    def __configure_shuffle_button_icon(self, color: str = 'yellow') -> None:
        """
        The function configures the icon for a shuffle button with a specified color.
        
        :param color: The "color" parameter is a string that specifies the color of the shuffle button
        icon. It is set to 'yellow' by default, defaults to yellow
        """
        self.__icon_shuffle_logo = ImageTk.PhotoImage(Image.open(f'./assets/icons/{color}/shuffle.png'))

    def __update_shuffle_icon(self, color: str = 'yellow') -> None:
        """
        This function updates the shuffle icon and button color in a music player interface.
        
        :param color: The color parameter is a string that represents the color of the shuffle icon. It
        is set to 'yellow' by default, defaults to yellow
        """
        self.__configure_shuffle_button_icon(color)
        self.__btn_shuffle_song.configure(image=self.__icon_shuffle_logo)

    def __configure_icons(self) -> None:
        """
        The function configures icons by loading and assigning image files to different variables.
        """
        self.__icon_open_logo = ImageTk.PhotoImage(Image.open('./assets/icons/yellow/folder.png'))
        self.__icon_play_logo = ImageTk.PhotoImage(Image.open('./assets/icons/yellow/play.png'))
        self.__icon_pause_logo = ImageTk.PhotoImage(Image.open('./assets/icons/yellow/pause.png'))
        self.__icon_previous_logo = ImageTk.PhotoImage(Image.open('./assets/icons/yellow/back.png'))
        self.__icon_next_logo = ImageTk.PhotoImage(Image.open('./assets/icons/yellow/next.png'))
        self.__icon_stop_logo = ImageTk.PhotoImage(Image.open('./assets/icons/yellow/stop.png'))
        self.__configure_shuffle_button_icon('yellow')

    def __configure_date_bg_img(self) -> bool:
        """
        The function __configure() checks if the configuration date and background image are set, and if
        not, recursively calls itself until they are set, then activates sound and returns True.
        :return: a boolean value.
        """
        if not self.__configure_date() or not self.__configure_bg_image():
            return self.__configure_date_bg_img()
        return True

    def __configure_sound(self) -> None:
        """
        The function configures the sound by activating it.
        """
        self.__activate_sound()

    def __activate_sound(self) -> bool:
        """
        The function activates sound and returns a boolean value indicating whether the sound was
        activated or not.
        :return: a boolean value. If the user chooses to activate the sound, the function returns True.
        If the user chooses not to activate the sound, the function returns False.
        """
        if question('Activate music?', 'Would you like to activate the sound?'):
            self.__open_songs()
            self.__init_music_player()
            return True
        else: return False
    
    def __start_music_timer(self) -> None:
        """
        The function initializes a music player and calculates the time left for the music to finish.
        """
        self.__init_music_player()
        self.__calculate_time_left()

    #! #### MUSIC PLAYER #### !#
    def __prev_song(self) -> None:
        """
        The function __prev_song() is used to go to the previous song in a music player, either by
        selecting a random song or by decrementing the actual position if random mode is not activated.
        """
        match self.__is_random_activated:
            case True:
                self.__set_random_song()
            case False:
                if self.__actual_position > 0:
                    self.__actual_position -= 1
                else:
                    self.__actual_position = 0
        self.after(100, self.__start_music_timer)
    
    def __next_song(self) -> None:
        """
        The function `__next_song` selects the next song to play based on whether random mode is
        activated or not.
        """
        match self.__is_random_activated:
            case True:
                self.__set_random_song()
            case False:
                if self.__actual_position < len(self.__songs) - 1:
                    self.__actual_position += 1
                else:
                    self.__actual_position = 0
        self.after(100, self.__start_music_timer)
    
    def __stop_song(self) -> None:
        """
        The function stops the currently playing song and cancels any scheduled updates to the song
        label.
        """
        if self.__is_playing:
            self.__is_stopped = True
            self.__is_playing = False
            mixer.music.stop()
            self.__actual_song_name = 'Nothing `cause it`s stopped!'
            if self.__lbl_update_song:
                self.after_cancel(self.__lbl_update_song)
                self.__lbl_song_name.configure(text = f'🎧Now Playing: {self.__actual_song_name}')
    
    def __pause_song(self) -> None:
        """
        The function toggles between pausing and unpausing a song using the mixer.music module in
        Python.
        """
        if not self.__is_stopped and self.__is_playing and self.__lbl_update_song:
            if self.__is_paused:
                mixer.music.unpause()
                self.__actual_song_name = self.__actual_song_name.split(' | ')[0]
            else: 
                mixer.music.pause()
                self.__actual_song_name += ' | (but it`s paused!)'
            self.__is_paused = not self.__is_paused
            self.after_cancel(self.__lbl_update_song)
            self.__lbl_song_name.configure(text = f'🎧Now Playing: {self.__actual_song_name}')
    
    def __set_on_off_random(self, on_off: str) -> None:
        """
        The function sets a boolean variable to True or False based on the input string 'on' or 'off'.
        
        :param on_off: The `on_off` parameter is a string that specifies whether to turn on or off a
        random feature. It can have two possible values: 'on' or 'off'
        """
        match on_off.lower():
            case 'on':
                if not self.__is_random_activated:
                    self.__is_random_activated = True
                    self.__update_shuffle_icon('gray')
                self.__set_random_song()
            case 'off':
                if self.__is_random_activated:
                    self.__is_random_activated = False
                    self.__update_shuffle_icon('yellow')
    
    def __set_random_song(self) -> None:
        """
        The function sets the actual position of a random song in a list of songs.
        """
        amount_songs = len(self.__songs)
        random_song = rd.choice(list(range(amount_songs)))
        self.__actual_position = random_song
    
    def __play_random_mode(self) -> None:
        """
        The function sets the random mode of a music player to "on" and initializes the music player.
        """
        self.__set_on_off_random('on')
        self.__init_music_player()

    def __activate_random_mode(self) -> None:
        """
        The function activates or deactivates the random mode based on its current state.
        """
        if not self.__is_random_activated:
            self.__play_random_mode()
        else: self.__set_on_off_random('off')

    def __init_music_player(self) -> None:
        """
        The `__init_music_player` function initializes the music player by loading and playing the first
        song in the list of songs.
        """
        if self.__songs and not self.__time_done:
            self.__is_stopped = False
            self.__is_playing = True
            mixer.music.load(self.__songs[self.__actual_position])
            mixer.music.play()
            self.__play_songs()

    def __play_songs(self) -> None:
        """
        The function plays songs from a list and updates the song name label accordingly.
        """
        if self.__songs:
            amount_songs = len(self.__songs)
            self.__actual_song = self.__songs[self.__actual_position]
            self.__actual_song_name = self.__actual_song.split('/')[-1]
            time = mixer.music.get_pos()
            x = int(time * 0.001)
            mixer.music.set_volume(1)
            audio = mutagen.File(self.__songs[self.__actual_position])
            log = audio.info.length
            minutes, seconds = divmod(log, 60)
            minutes, seconds = int(minutes), int(seconds)
            tt = minutes * 60 + seconds
            self.__lbl_song_name.configure(text = f'🎧Now Playing: {self.__actual_song_name}')
            self.__lbl_update_song = self.after(100, self.__play_songs)

            if x == tt:
                self.after_cancel(self.__lbl_update_song)
                self.__lbl_song_name.configure(text = '')
                if self.__is_random_activated:
                    self.__play_random_mode()
                else:
                    if self.__actual_position < amount_songs -1 :
                        self.__actual_position += 1
                        self.after(500, self.__play_songs)
                        mixer.music.play()
                    else: self.__actual_position = 0
                self.after(500, self.__init_music_player)
                mixer.music.play()
    
    def __play_closs_voice(self) -> None:
        """
        The function stops all the playing music and plays the sound of Mariano Closs.
        """
        self.__stop_song()
        mixer.music.load(self.__final_snd_path)
        mixer.music.play()

    def __open_songs(self) -> None:
        """
        The function opens a file dialog to select multiple songs with the file extensions .mp3 or .wav.
        """
        self.__songs = filedialog.askopenfilenames(
            initialdir=self.BACKGROUND_MUSIC, title='Select songs to open',
            filetypes=(('MP3 Files', '*.mp3'), ('WAV Files', '*.wav'), ('OGG Files', '*.ogg'))
        )

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    app = CountdownApp()
    app.mainloop()