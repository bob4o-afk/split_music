from pytube import YouTube
import pygame
from queue import Queue
from threading import Thread
from pydub import AudioSegment
import os
import tkinter as tk
from tkinter import filedialog

class MusicPlayerGUI:
    def __init__(self, master):
        self.play_left_thread = None
        self.play_right_thread = None
        self.play_both_thread = None

        self.master = master
        self.master.title("Music Player")

        self.url_entry = tk.Entry(self.master, width=40)
        self.url_entry.grid(row=0, column=0, padx=10, pady=10)

        self.choose_button = tk.Button(self.master, text="Choose File", command=self.choose_file)
        self.choose_button.grid(row=0, column=1, padx=10, pady=10)

        self.queue_left = Queue()
        self.queue_right = Queue()
        self.queue_both = Queue()

        self.add_left_button = tk.Button(self.master, text="Add to Left Queue", command=lambda: self.add_to_queue("left"))
        self.add_left_button.grid(row=1, column=0, padx=10, pady=10)

        self.add_right_button = tk.Button(self.master, text="Add to Right Queue", command=lambda: self.add_to_queue("right"))
        self.add_right_button.grid(row=1, column=1, padx=10, pady=10)

        self.add_both_button = tk.Button(self.master, text="Add to Both Queue", command=lambda: self.add_to_queue("both"))
        self.add_both_button.grid(row=1, column=2, padx=10, pady=10)

        self.play_left_button = tk.Button(self.master, text="Play Left", command=lambda: self.play_music("left"))
        self.play_left_button.grid(row=2, column=0, pady=10)

        self.play_right_button = tk.Button(self.master, text="Play Right", command=lambda: self.play_music("right"))
        self.play_right_button.grid(row=2, column=1, pady=10)

        self.play_both_button = tk.Button(self.master, text="Play Both", command=lambda: self.play_music("both"))
        self.play_both_button.grid(row=2, column=2, pady=10)

        self.stop_left_button = tk.Button(self.master, text="Stop Left", command=self.stop_left)
        self.stop_left_button.grid(row=3, column=0, pady=10)

        self.stop_right_button = tk.Button(self.master, text="Stop Right", command=self.stop_right)
        self.stop_right_button.grid(row=3, column=1, pady=10)

        self.stop_both_button = tk.Button(self.master, text="Stop Both", command=self.stop_both)
        self.stop_both_button.grid(row=3, column=2, pady=10)

        # Lists to store added songs for each channel
        self.added_songs_left = []
        self.added_songs_right = []
        self.added_songs_both = []

        # Listboxes to display added songs for each channel
        self.listbox_left = tk.Listbox(self.master, height=5)
        self.listbox_left.grid(row=4, column=0, padx=10, pady=10)

        self.listbox_right = tk.Listbox(self.master, height=5)
        self.listbox_right.grid(row=4, column=1, padx=10, pady=10)

        self.listbox_both = tk.Listbox(self.master, height=5)
        self.listbox_both.grid(row=4, column=2, padx=10, pady=10)

        # Create a folder named "songs" if it doesn't exist
        self.songs_folder = "songs"
        if not os.path.exists(self.songs_folder):
            os.makedirs(self.songs_folder)

        self.paused_pos_left = None
        self.paused_pos_right = None

    def add_to_queue(self, channel):
        url = self.url_entry.get()
        if not url:
            return

        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_file = audio_stream.download()

        # Convert audio to WAV format using pydub
        audio = AudioSegment.from_file(audio_file, format="mp4")
        wav_file = os.path.join(self.songs_folder, os.path.splitext(os.path.basename(audio_file))[0] + '.wav')
        audio.export(wav_file, format="wav")

        # Remove the original audio file (mp4)
        os.remove(audio_file)

        if channel == "left":
            self.queue_left.put(wav_file)
            self.added_songs_left.append(os.path.basename(wav_file))
            self.update_listbox(self.listbox_left, self.added_songs_left)
        elif channel == "right":
            self.queue_right.put(wav_file)
            self.added_songs_right.append(os.path.basename(wav_file))
            self.update_listbox(self.listbox_right, self.added_songs_right)
        elif channel == "both":
            self.queue_both.put(wav_file)
            self.added_songs_both.append(os.path.basename(wav_file))
            self.update_listbox(self.listbox_both, self.added_songs_both)

    def update_listbox(self, listbox, songs):
        listbox.delete(0, tk.END)
        for song in songs[:5]:
            listbox.insert(tk.END, song)
        if len(songs) > 5:
            listbox.insert(tk.END, "More")

    def play_music(self, channel):
        if channel == "left":
            if self.play_left_thread and self.play_left_thread.is_alive():
                return
            self.play_left_thread = Thread(target=self.play_audio, args=("left", self.paused_pos_left))
            self.play_left_thread.start()
        elif channel == "right":
            if self.play_right_thread and self.play_right_thread.is_alive():
                return
            self.play_right_thread = Thread(target=self.play_audio, args=("right", self.paused_pos_right))
            self.play_right_thread.start()
        elif channel == "both":
            if self.play_both_thread and self.play_both_thread.is_alive():
                return
            self.play_both_thread = Thread(target=self.play_audio, args=("both",))
            self.play_both_thread.start()

    def play_audio(self, channel, paused_pos=None):
        pygame.mixer.init()
        pygame.mixer.set_num_channels(2)  # Create two channels for left and right

        while not (self.queue_left.empty() and self.queue_right.empty() and self.queue_both.empty()):
            if not self.queue_left.empty() and channel == "left":
                left_channel = pygame.mixer.Channel(0)
                left_channel.set_volume(1.0, 0.0)
                self.play_channel(self.queue_left.get(), left_channel, paused_pos)

            if not self.queue_right.empty() and channel == "right":
                right_channel = pygame.mixer.Channel(1)
                right_channel.set_volume(0.0, 1.0)
                self.play_channel(self.queue_right.get(), right_channel, paused_pos)

            if not self.queue_both.empty() and channel == "both":
                self.play_channel(self.queue_both.get(), pygame.mixer.Channel(0), paused_pos)  # Play on both channels

                # If a song is added to both channels, reset the queues
                while not self.queue_left.empty():
                    self.queue_left.get()
                while not self.queue_right.empty():
                    self.queue_right.get()

                # Clear the added songs lists
                self.added_songs_left.clear()
                self.added_songs_right.clear()
                self.added_songs_both.clear()

                # Update listboxes
                self.update_listbox(self.listbox_left, self.added_songs_left)
                self.update_listbox(self.listbox_right, self.added_songs_right)
                self.update_listbox(self.listbox_both, self.added_songs_both)

        pygame.mixer.quit()

    def play_channel(self, wav_file, channel, paused_pos=None):
        sound = pygame.mixer.Sound(wav_file)
        channel.play(sound, fade_ms=1000)

        if paused_pos is not None:
            pygame.mixer.music.set_pos(paused_pos / 1000.0)

        length = sound.get_length() * 1000  # Convert to milliseconds
        pygame.time.delay(int(length))

    def stop_left(self):
        left_channel = pygame.mixer.Channel(0)
        left_channel.pause()  # Pause the sound
        self.paused_pos_left = pygame.mixer.music.get_pos()  # Store the paused position

    def stop_right(self):
        right_channel = pygame.mixer.Channel(1)
        right_channel.pause()  # Pause the sound
        self.paused_pos_right = pygame.mixer.music.get_pos()  # Store the paused position

    def stop_both(self):
        left_channel = pygame.mixer.Channel(0)
        right_channel = pygame.mixer.Channel(1)
        left_channel.pause()  # Pause the sound on the left channel
        right_channel.pause()  # Pause the sound on the right channel
        self.paused_pos_left = pygame.mixer.music.get_pos()  # Store the paused position on the left channel
        self.paused_pos_right = pygame.mixer.music.get_pos()


    def choose_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "audio/*.mp3;audio/*.wav")])
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, file_path)

def main():
    root = tk.Tk()
    app = MusicPlayerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
