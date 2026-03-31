import os
import pygame


class MusicPlayer:
    def __init__(self, music_folder):
        self.music_folder = music_folder
        self.playlist = self.load_playlist()
        self.current_index = 0
        self.is_playing = False

    def load_playlist(self):
        supported_formats = (".mp3", ".wav")
        files = []

        for file_name in os.listdir(self.music_folder):
            if file_name.lower().endswith(supported_formats):
                full_path = os.path.join(self.music_folder, file_name)
                files.append(full_path)

        files.sort()
        return files

    def get_current_track_name(self):
        if not self.playlist:
            return "No tracks found"
        return os.path.basename(self.playlist[self.current_index])

    def load_current_track(self):
        if self.playlist:
            pygame.mixer.music.load(self.playlist[self.current_index])

    def play(self):
        if self.playlist:
            try:
                self.load_current_track()
                pygame.mixer.music.play()
                self.is_playing = True
            except pygame.error as e:
                print(f"Error playing track: {e}")
                self.is_playing = False

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False

    def next_track(self):
        if self.playlist:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.play()

    def previous_track(self):
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)
            self.play()

    def get_position_seconds(self):
        pos_ms = pygame.mixer.music.get_pos()
        if pos_ms < 0:
            return 0
        return pos_ms // 1000