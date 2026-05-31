import re
import math
import pygame
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def load_gcode_file(file_name):
    points = []
    X, Y, Z = 0.0, 0.0, 0.0

    with open(file_name, "r", encoding='utf-8') as file:
        for line in file:
            # Prawidłowe usuwanie komentarzy po średniku
            line = line.split(";")[0].strip()
            if not line:
                continue

            if line.startswith('G0') or line.startswith('G1'):
                X_match = re.search(r'X([-+]?[0-9]*\.?[0-9]+)', line)
                Y_match = re.search(r'Y([-+]?[0-9]*\.?[0-9]+)', line)
                Z_match = re.search(r'Z([-+]?[0-9]*\.?[0-9]+)', line)

                if X_match: X = float(X_match.group(1))
                if Y_match: Y = float(Y_match.group(1))
                if Z_match: Z = float(Z_match.group(1))

                # Dodajemy punkt przesunięty o offset Twojej drukarki
                points.append([X, Y, Z - 62.0])
                
    return points

def load_texture(filename):
    try:
        texture_surface = pygame.image.load(filename)
        texture_surface = texture_surface.convert()
        texture_data = pygame.image.tostring(texture_surface, "RGB", True)
        width = texture_surface.get_width()
        height = texture_surface.get_height()

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGB, width, height, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
        return tex_id
    except pygame.error:
        # Rezerwowy mechanizm tworzenia pustej tekstury w razie braku pliku graficznego
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 1, 1, 0, GL_RGB, GL_UNSIGNED_BYTE, b'\x80\x80\x80')
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        return tex_id


def calculate_normal(v1, v2, v3):
    u = [v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]]
    v = [v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]]
    nx = u[1] * v[2] - u[2] * v[1]
    ny = u[2] * v[0] - u[0] * v[2]
    nz = u[0] * v[1] - u[1] * v[0]
    dlugosc = (nx**2 + ny**2 + nz**2)**0.5
    if dlugosc == 0: return [0.0, 0.0, 1.0]
    return [nx / dlugosc, ny / dlugosc, nz / dlugosc]

def distance3d(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)

def generuj_audio_id(audio_data):
    """Konwertuje jednowymiarową tablicę NumPy na format 16-bit stereo Sound dla Pygame"""
    odciecie = int(len(audio_data) * 0.05)
    fade = np.linspace(0, 1, odciecie)
    audio_data[:odciecie] *= fade
    audio_data[-odciecie:] *= fade[::-1]
    
    audio_data = (audio_data / np.max(np.abs(audio_data)) * 20000).astype(np.int16)
    stereo_data = np.vstack((audio_data, audio_data)).T
    return pygame.sndarray.make_sound(stereo_data)

def dzwiek_wolny_ruch(f_bazowa, duration=1.0, sample_rate=22050):
    """Generuje chropowaty pomruk silnika krokowego o zadanej częstotliwości bazowej"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    fala = np.sin(2 * np.pi * f_bazowa * t) + 0.4 * np.sin(4 * np.pi * f_bazowa * t)
    szum = np.random.normal(0, 0.05, len(t))
    return generuj_audio_id(fala + szum)

