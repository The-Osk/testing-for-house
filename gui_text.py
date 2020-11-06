import tkinter
from tkinter import filedialog
import cv2
import json
from PIL import Image, ImageTk
from modules import reco
from modules import MusicSearch
import pafy               
import vlc
from time import sleep

class MainWindow:
    def __init__(self, window, cap):
        self.window = window
        self.window.resizable(False,False)
        self.cap = cap
        self.width = 500
        self.height = 400
        self.canvas = tkinter.Canvas(self.window, width=self.width, height=self.height)
        self.canvas.pack()
        self.Snap_Button = tkinter.Button(self.window, text="snapshot", command=self.get_image_details).pack()
        self.Camera_update()

    def Camera_update(self):
        self.frame = self.cap.read()[1]
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.frame = Image.fromarray(self.frame)
        self.frame = ImageTk.PhotoImage(self.frame)
        self.canvas.create_image(self.width//2, self.height//2, image=self.frame)
        self.window.after(20, self.Camera_update)
    
    def get_image_details(self):
        reco.main((cv2.imencode(".jpg", self.cap.read()[1])[1]).tobytes())
        cv2.destroyAllWindows()
        self.window.destroy()

class MusicPlayer:
    def __init__(self, window):
        self.window = window
        self.window.resizable(False, False)
        self.window.geometry("320x100")
        with open("log.json", "r") as file: 
            music = json.load(file)
        self.Music_list = []
        self.Music_name_list = []
        for I in music:
            self.Music_list.append(MusicSearch.find_song(I["name"]))
            self.Music_name_list.append(I["name"])

        self.Volume = tkinter.Scale(self.window, from_=0, to=100, orient=tkinter.HORIZONTAL)
        self.Volume.set(50)
        self.Next = tkinter.Button(self.window, text = '>>',  width = 4, font = ('Times', 10), command = self.next)
        self.Previuos = tkinter.Button(self.window, text = '<<',  width = 4, font = ('Times', 10), command = self.previuos)
        Stop = tkinter.Button(self.window, text = 'Stop',  width = 10, font = ('Times', 10), command = self.stop)
        Play = tkinter.Button(self.window, text = 'Play',  width = 10, font = ('Times', 10), command = self.play)
        Pause = tkinter.Button(self.window, text = 'Pause',  width = 10, font = ('Times', 10), command = self.pause)
        Exit = tkinter.Button(self.window, text = 'Exit',  width = 10, font = ('Times', 10), command = self.Exit)
        self.Music_label = tkinter.Label(self.window, text=self.Music_name_list[0], justify=tkinter.CENTER)
        Stop.place(x=10 ,y=20);Play.place(x=120,y=20);Pause.place(x=230,y=20);Exit.place(x=10,y=60);self.Volume.place(x=210, y=40);self.Next.place(x=160, y=60);self.Previuos.place(x=120, y=60)
        self.Music_label.place(x=120, y=0)
        self.Previuos['state'] = tkinter.DISABLED
        if(len(self.Music_list) == 1):
            self.Next['state'] = tkinter.DISABLED
        self.pause_status = False
        self.stop_status = False
        self.music_pointer = 0 
        self.Music_Player = vlc.MediaPlayer(pafy.new(self.Music_list[0]).getbestaudio().url)
        self.Music_Player.audio_set_volume(self.Volume.get())
        self.Music_Player.play()
        sleep(2)
        self.song_selector()

    def song_selector(self):
        self.Music_Player.audio_set_volume(self.Volume.get())
        if((not self.Music_Player.is_playing()) and not(self.pause_status or self.stop_status)):
            self.music_pointer = self.music_pointer + 1
            if(self.music_pointer <= len(self.Music_list) - 1):
                self.Music_label['text'] = self.Music_name_list[self.music_pointer]
                self.Music_Player = vlc.MediaPlayer(pafy.new(self.Music_list[self.music_pointer]).getbestaudio().url)
                self.Music_Player.play()
                sleep(0.5)
            else:
                self.window.destroy()
                return
        self.window.after(20, self.song_selector)

    def Exit(self):
        self.Music_Player.stop()
        self.window.destroy()

    def play(self):
        if(not self.Music_Player.is_playing()):
            self.Music_label['text'] = self.Music_name_list[self.music_pointer]
            self.Music_Player.play()
            self.pause_status = False
            self.stop_status = False
            sleep(0.5)

    def pause(self):
        self.Music_label['text'] = "Pause"
        self.pause_status = True
        self.stop_status = False
        self.Music_Player.pause()

    def stop(self):
        self.Music_label['text'] = "Stop"
        self.pause_status = False
        self.stop_status = True
        self.Music_Player.stop()
    
    def next(self):
        if(self.music_pointer < len(self.Music_list) - 1):
            self.Music_Player.stop()
            self.music_pointer = self.music_pointer + 1
            self.Music_label['text'] = self.Music_name_list[self.music_pointer]
            self.Music_Player = vlc.MediaPlayer(pafy.new(self.Music_list[self.music_pointer]).getbestaudio().url)
            self.Music_Player.play()
            self.Previuos['state'] = tkinter.NORMAL
            sleep(0.5)
        if(self.music_pointer == (len(self.Music_list) - 1)):
            self.Next['state'] = tkinter.DISABLED

    def previuos(self):
        if(self.music_pointer > 0):
            self.Music_Player.stop()
            self.music_pointer = self.music_pointer - 1
            self.Music_label['text'] = self.Music_name_list[self.music_pointer]
            self.Music_Player = vlc.MediaPlayer(pafy.new(self.Music_list[self.music_pointer]).getbestaudio().url)
            self.Music_Player.play()
            self.Next['state'] = tkinter.NORMAL
            sleep(0.5)
        if(self.music_pointer == 0):
            self.Previuos['state'] = tkinter.DISABLED            

if __name__ == "__main__":
    MainPage = tkinter.Tk(className="Camera")
    MainWindow(MainPage, cv2.VideoCapture(0))
    MainPage.mainloop()
    MusicPlayer_window = tkinter.Tk(className="Music Player")
    MusicPlayer(MusicPlayer_window)
    MusicPlayer_window.mainloop()