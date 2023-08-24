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
import tkinter as tk
from tkinter.messagebox import showinfo as alert
from tkinter.messagebox import askyesno as question
from tkinter.simpledialog import askstring as prompt
import customtkinter
import warnings
import winsound
import re
from PIL import Image, ImageTk


class CountdownApp(customtkinter.CTk):
    """
    The `CountdownApp` class is a countdown timer GUI that displays the time left between a specified initial
    time and the current time.
    """

    def __init__(self):
        """
        This is the initialization function for a countdown timer GUI, which includes setting up the
        window, creating the main frame, displaying an image banner, and playing background music.
        """
        super().__init__()

        self.title(f"UTN FRA - countdown")
        self.minsize(320, 250)
        self.BACKGROUND_MUSIC = './assets/sound/bg_music_wav.wav'
        
        self.__frame_main = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.__frame_main.grid(row = 0, column = 0, padx = 20, pady = 5, columnspan = 2, rowspan = 3, sticky="nswe")

        self.__configure()

        self.__frame_player = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent", bg_color = 'transparent')
        self.__frame_player.grid(row = 3, column = 1, padx = 20, pady = 5, columnspan = 2, rowspan = 3, sticky="nswe")

        self.__lbl_time = tk.Label(master=self.__frame_main, relief=tk.RAISED, cursor='dot', font=("Arial", 50, "bold"), bg='black', fg='cyan', justify='left')
        self.__lbl_time.grid(row=2, column=0, columnspan=1, sticky='we')
        self.__lbl_time.place(x=50, y=420)

        self.__lbl_song_name = customtkinter.CTkLabel(master=self.__frame_player, text=f"TEST", font=("Arial", 20, "bold"))
        self.__lbl_song_name.grid(row=3, column=2, columnspan=2, padx=20, pady=10)

        self.__calculate_time_left()

    def __calculate_time_left(self):
        """
        The function calculates the time left between the current time and a specified initial time and
        updates a label with the formatted time.
        """
        seconds = (self.__initial_time - datetime.datetime.now()).total_seconds()
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h < 0:
            h = 0
            m = 0
            s = 0
        msg = f"  {h:02.0f}  :  {m:02.0f}  :  {s:02.0f}\nhour mins secs"
        self.__lbl_time.configure(text = f"{msg}")
        self.__lbl_time.after(1000, self.__calculate_time_left)
    
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
                time_pattern = '[0-2]{1}[0-9]{1}\:[0-5]{1}[0-9]{1}'
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
            if question('Initial or End?', 'Would you like an initial image? click NO for end image'):
                self.__image = Image.open('./assets/img/background_init.png')
            else:
                self.__image = Image.open('./assets/img/background_end.png')
            self.__image = ImageTk.PhotoImage(self.__image.resize((1191, 671)))
            print('rezised')
            self.__top_banner = customtkinter.CTkLabel(master = self.__frame_main, image = self.__image, text='')
            self.__top_banner.grid_configure(row = 0, column = 0, padx = 20, pady = 5, columnspan = 2, rowspan = 3, sticky = 'we')
            return True
        except Exception as e:
            print(e.with_traceback(None))
            return False

    def __play_loop_sound(self):
        """
        The function plays a looped sound in the background.
        """
        winsound.PlaySound(self.BACKGROUND_MUSIC, winsound.SND_LOOP + winsound.SND_ASYNC)

    def __activate_sound(self) -> bool:
        """
        The function activates sound and returns a boolean value indicating whether the sound was
        activated or not.
        :return: a boolean value. If the user chooses to activate the sound, the function returns True.
        If the user chooses not to activate the sound, the function returns False.
        """
        if question('Activate music?', 'Would you like to activate the sound?'):
            self.__play_loop_sound()
            return True
        else: return False

    def __configure(self) -> bool:
        """
        The function __configure() checks if the configuration date and background image are set, and if
        not, recursively calls itself until they are set, then activates sound and returns True.
        :return: a boolean value.
        """
        if not self.__configure_date() or not self.__configure_bg_image():
            return self.__configure()
        self.__activate_sound()
        return True

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    app = CountdownApp()
    app.mainloop()