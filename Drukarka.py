import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# --- KONFIGURACJA ŚWIATŁA ---
light_ambient = [0.5, 0.5, 0.5, 1.0]
light_diffuse = [1.0, 1.0, 1.0, 1.0]

class Drukarka:
    parts_config = {
        'Podstawa': ['VERTICES_Calosc', 'SURFACES_Calosc'],
        'Oś X': ['VERTICES_osx', 'SURFACES_osx'],
        'Stół': ['VERTICES_bed', 'SURFACES_bed'],
        'Ekstruder': ['VERTICES_Extruder', 'SURFACES_Extruder']
    }

    def __init__(self, part_name, color, pos=None, rot=None):
        self.vertices = getattr(self, self.parts_config[part_name][0])
        self.surfaces = getattr(self, self.parts_config[part_name][1])
        self.color = color
        self.pos = pos if pos else [0.0, 0.0, 0.0]
        self.rot = rot if rot else [0.0, 0.0, 0.0]

    VERTICES_Calosc = (
        (0,0,0), (100,0,0), (100,100,0), (0,100,0),
        (0,0,10), (100,0,10), (100,100,10), (0,100,10),
        (10,10,10), (90,10,10), (90,90,10), (10,90,10),
        (10,10,0), (90,10,0), (90,90,0), (10,90,0),
        (0,30,10), (10,30,10), (10,40,10), (0,40,10),
        (0,30,120), (10,30,120), (10,40,120), (0,40,120),
        (90,30,10), (100,30,10), (100,40,10), (90,40,10),
        (90,30,120), (100,30,120), (100,40,120), (90,40,120),
        (0,30,120), (100,30,120), (100,40,120), (0,40,120),
        (0,30,130), (100,30,130), (100,40,130), (0,40,130),
        (45,10,0), (55,10,0), (55,90,0), (45,90,0),
        (45,10,10), (55,10,10), (55,90,10), (45,90,10)
    )

    SURFACES_Calosc = (
        (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
        (4, 5, 9, 8), (5, 6, 10, 9), (6, 7, 11, 10), (7, 4, 8, 11),
        (0, 1, 13, 12), (1, 2, 14, 13), (2, 3, 15, 14), (3, 0, 12, 15),
        (8, 9, 13, 12), (9, 10, 14, 13), (10, 11, 15, 14), (11, 8, 12, 15),
        (16, 17, 18, 19), (16, 17, 21, 20), (19, 16, 20, 23), 
        (19, 23, 22, 18), (18, 22, 21, 17), (20, 21, 22, 23),
        (24, 25, 26, 27), (24, 25, 29, 28), (27, 24, 28, 31), 
        (27, 31, 30, 26), (26, 30, 29, 25), (28, 29, 30, 31),
        (32, 33, 34, 35), (32, 33, 37, 36), (35, 32, 36, 39), 
        (35, 39, 38, 34), (34, 38, 37, 33), (36, 37, 38, 39),
        (40, 41, 42, 43), (40, 41, 45, 44), (43, 40, 44, 47), 
        (43, 47, 46, 42), (42, 46, 45, 41), (44, 45, 46, 47)
    )

    VERTICES_osx = (
        (0,40,90), (100,40,90), (100,50,90), (0,50,90),
        (0,40,100), (100,40,100), (100,50,100), (0,50,100)
    )
   
    SURFACES_osx = (
        (0, 1, 2, 3), (0, 1, 5, 4), (3, 0, 4, 7), (3, 7, 6, 2), (2, 6, 5, 1), (4, 5, 6, 7)
    )

    VERTICES_bed = (
        (15,15,15), (85,15,15), (85,85,15), (15,85,15),
        (15,15,20), (85,15,20), (85,85,20), (15,85,20),
        (45,40,10), (55,40,10), (55,60,10), (45,60,10),
        (45,40,15), (55,40,15), (55,60,15), (45,60,15)
    )
    SURFACES_bed = (
        (0, 1, 2, 3), (0, 1, 5, 4), (3, 0, 4, 7), (3, 7, 6, 2), (2, 6, 5, 1), (4, 5, 6, 7),
        (8, 9, 10, 11), (8, 9, 13, 12), (11, 8, 12, 15), (11, 15, 14, 10), (10, 14, 13, 9), (12, 13, 14, 15)
    )

    VERTICES_Extruder = (
        (-10, 50, 90),  (10, 50, 90),  (10, 70, 90),  (-10, 70, 90),
        (-10, 50, 110), (10, 50, 110), (10, 70, 110), (-10, 70, 110),
        (-5, 55, 90),    (5, 55, 90),    (5, 65, 90),    (-5, 65, 90),     
        (0, 60, 82)
    )

    SURFACES_Extruder = (
        (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
        (4, 5, 6, 7),
        (8, 9, 12, 12), (9, 10, 12, 12), (10, 11, 12, 12), (11, 8, 12, 12)
    )

    def draw(self, material):
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, material['ambient'])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, material['diffuse'])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, material['specular'])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, material['shininess'])
        
        glPushMatrix()
        glTranslatef(*self.pos)
        glRotatef(self.rot[0], 1, 0, 0)
        glRotatef(self.rot[1], 0, 1, 0)
        glRotatef(self.rot[2], 0, 0, 1)

        glBegin(GL_QUADS)
        for surface in self.surfaces:
            for vertex in surface:
                glVertex3fv(self.vertices[vertex])
        glEnd()
        glPopMatrix()

materials = {
    'red': {'ambient': [0.4, 0.1, 0.1, 1], 'diffuse': [0.9, 0.1, 0.1, 1], 'specular': [0.5,0.5,0.5,1], 'shininess': 32},
    'blue': {'ambient': [0.1, 0.1, 0.4, 1], 'diffuse': [0.1, 0.1, 0.9, 1], 'specular': [0.5,0.5,0.5,1], 'shininess': 32}
}

def main():
    pygame.init()
    display = (1200, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0]/display[1]), 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)
    
    podstawa = Drukarka('Podstawa', [1.0, 0.0, 0.0])
    os_x = Drukarka('Oś X', [0.0, 0.0, 1.0])
    bed = Drukarka('Stół', [0.0, 1.0, 0.0])
    extruder = Drukarka('Ekstruder', [1.0, 1.0, 0.0])
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_NORMALIZE)   
    glShadeModel(GL_SMOOTH) 
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.4, 0.4, 0.4, 1.0])
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    
    # --- ZMIENNE KAMERY ---
    rotate_x, rotate_y = -70, 150  # Początkowa rotacja
    distance = -15                 # Początkowe przybliżenie
    mouse_down = False             # Czy lewy przycisk myszy jest wciśnięty

    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            # Obsługa myszy
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: mouse_down = True  # Lewy przycisk
                if event.button == 4: distance += 1.0    # Scroll w górę (przybliż)
                if event.button == 5: distance -= 1.0    # Scroll w dół (oddal)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: mouse_down = False
            
            elif event.type == pygame.MOUSEMOTION:
                if mouse_down:
                    dx, dy = event.rel
                    rotate_y += dx  # Obrót wokół osi Z (horyzontalnie)
                    rotate_x += dy  # Obrót góra/dół

        keys = pygame.key.get_pressed()
        if keys[K_UP] and os_x.pos[2] < 20: os_x.pos[2] += 2.0 
        if keys[K_DOWN] and os_x.pos[2] > -70: os_x.pos[2] -= 2.0

        glClearColor(0.15, 0.15, 0.15, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # --- ZASTOSOWANIE TRANSFORMACJI KAMERY ---
        glTranslatef(0, 0, distance)  # Przybliżenie
        glRotatef(rotate_x, 1, 0, 0)  # Obrót góra/dół
        glRotatef(rotate_y, 0, 0, 1)  # Obrót 360 wokół drukarki

        glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 10, 1])

        glPushMatrix()
        glScalef(0.05, 0.05, 0.05)
        glTranslatef(-50, -50, -5) 
        
        podstawa.draw(materials['red'])
        
        # Przesunięcie ekstrudera wraz z osią X
        glPushMatrix()
        glTranslatef(0, 0, os_x.pos[2])
        os_x.draw(materials['blue'])
        extruder.draw(materials['blue'])
        glPopMatrix()
        
        bed.draw(materials['blue'])
        glPopMatrix()
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()