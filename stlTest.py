import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from stl import mesh
import sys

class STLPart:
    """
    Klasa reprezentująca pojedynczą część STL z własną pozycją i obrotem.
    """
    def __init__(self, filename, color):
        self.vertices = self._load_stl(filename)
        self.color = color
        self.pos = [0.0, 0.0, 0.0]
        self.rot = [0.0, 0.0, 0.0]

    def _load_stl(self, filename):
        try:
            m = mesh.Mesh.from_file(filename)
            return m.vectors.reshape(-1, 3)
        except Exception as e:
            print(f"Błąd ładowania {filename}: {e}")
            return None

    def draw(self):
        if self.vertices is None: return
        
        glPushMatrix()
        glTranslatef(*self.pos)
        glRotatef(self.rot[0], 1, 0, 0)
        glRotatef(self.rot[1], 0, 1, 0)
        glRotatef(self.rot[2], 0, 0, 1)
        
        glBegin(GL_TRIANGLES)
        glColor3fv(self.color)
        for vertex in self.vertices:
            glVertex3fv(vertex)
        glEnd()
        glPopMatrix()

def main():
    pygame.init()
    display = (1024, 768)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Drukarka 3D - Sterowanie częściami")

    gluPerspective(45, (display[0] / display[1]), 0.1, 1000.0)
    glTranslatef(0.0, 0.0, -200)
    glEnable(GL_DEPTH_TEST)

    # --- KONFIGURACJA CZĘŚCI ---
    parts = {
        'extruder': STLPart('profilAlu.stl', [0.2, 0.6, 1.0]),
        'bed':      STLPart('profilAlu.stl', [1.0, 0.5, 0.0]),
        'frame':    STLPart('profilAlu.stl', [0.5, 0.5, 0.5])
    }

    # Ustawienie początkowe
    parts['extruder'].pos[0] = -40
    parts['bed'].pos[0] = 40

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # --- LOGIKA STEROWANIA ---
        keys = pygame.key.get_pressed()
        
        # Sterowanie Extruderem (Strzałki i W)
        if keys[K_LEFT]:  parts['extruder'].pos[0] -= 1.5
        if keys[K_RIGHT]: parts['extruder'].pos[0] += 1.5
        if keys[K_w]:     parts['extruder'].rot[0] += 2.0
        
        # Sterowanie Stołem (Góra/Dół i E)
        if keys[K_UP]:    parts['bed'].pos[1] += 1.5
        if keys[K_DOWN]:  parts['bed'].pos[1] -= 1.5
        if keys[K_e]:     parts['bed'].rot[1] += 2.0

        # --- RENDEROWANIE ---
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for part in parts.values():
            part.draw()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()