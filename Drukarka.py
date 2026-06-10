import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import re #potrzebne do obsługi pliku gcode
import numpy as np
from funkcje import *

file_name = 'CE3S1_3DBenchy.gcode' # Nazwa pliku gcode potrzebna do przedstawienia dzialania drukarki

# konfiguracja świateł
light_ambient = [0.3, 0.3, 0.3, 1.0]   
light_diffuse = [0.9, 0.9, 0.9, 1.0]   
light_specular = [0.5, 0.5, 0.5, 1.0]  

'''
Klasa Drukarka:

klasa zawiera komponenty takie jak: rama, os x, stół drukarki, ekstruder, stół na ktorym stoi drukarka oraz podłogę.
Każdy z tych komponentów został opisany jako zespól wspolzednych punktów oraz zespół połączonych punktów tworzących powierzchnie ścian brył.

'''
class Drukarka:
    parts_config = {
        'Rama': ['VERTICES_Calosc', 'SURFACES_Rama', 0.05],   
        'Oś X': ['VERTICES_osx', 'SURFACES_osx', 0.1],
        'bed': ['VERTICES_bed', 'SURFACES_bed', 0.01],
        'Ekstruder': ['VERTICES_Extruder', 'SURFACES_Extruder', 0.1],
        'Stół': ['VERTICES_Stol', 'SURFACES_Stol', 0.05],
        'Podloga': ['VERTICES_Podloga', 'SURFACES_Podloga', 0.05]
    }

    def __init__(self, part_name, texture_id, pos=None, rot=None):  # Konstruktor klasy, przechowuje on nazwe komponentu, jego teksture, pozycje oraz rotacje.
        self.vertices = getattr(self, self.parts_config[part_name][0]) # Mowi o vertices
        self.surfaces = getattr(self, self.parts_config[part_name][1]) # mówi o powierzchniach
        self.tex_scale = self.parts_config[part_name][2] # mówi o skali tekstur
        self.texture_id = texture_id  
        self.pos = pos if pos else [0.0, 0.0, 0.0]
        self.rot = rot if rot else [0.0, 0.0, 0.0]

    VERTICES_Calosc = (
    (0,0,0), (100,0,0), (100,100,0), (0,100,0), (0,0,10), (100,0,10), (100,100,10), (0,100,10), (10,10,10), (90,10,10), (90,90,10), 
    (10,90,10), (10,10,0), (90,10,0), (90,90,0), (10,90,0), (0,30,10), (10,30,10), (10,40,10), (0,40,10), (0,30,120), (10,30,120), (10,40,120), (0,40,120), 
    (90,30,10), (100,30,10), (100,40,10), (90,40,10), (90,30,120), (100,30,120), (100,40,120), (90,40,120), (0,30,120), (100,30,120), (100,40,120), (0,40,120), 
    (0,30,130), (100,30,130), (100,40,130), (0,40,130), (45,10,0), (55,10,0), (55,90,0), (45,90,0), (44,10,10), (55,10,10), (55,90,10), (45,90,10), (4,28,10), 
    (6,28,10), (6,30,10), (4,30,10), (4,28,130), (6,28,130), (6,30,130), (4,30,130), (94,28,10), (96,28,10), (96,30,10), (94,30,10), (94,28,130), (96,28,130), 
    (96,30,130), (94,30,130)
    )

    SURFACES_Rama = (
    (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7), (4,5,9,8), (5,6,10,9), (6,7,11,10), (7,4,8,11), (0,1,13,12), (1,2,14,13), (2,3,15,14), 
    (3,0,12,15), (8,9,13,12), (9,10,14,13), (10,11,15,14), (11,8,12,15), (40,41,42,43), (40,41,45,44), (43,40,44,47), (43,47,46,42), (42,46,45,41), 
    (44,45,46,47), (16,17,18,19), (16,17,21,20), (19,16,20,23), (19,23,22,18), (18,22,21,17), (20,21,22,23), (24,25,26,27), (24,25,29,28), (27,24,28,31), 
    (27,31,30,26), (26,30,29,25), (28,29,30,31), (32,33,34,35), (32,33,37,36), (35,32,36,39), (35,39,38,34), (34,38,37,33), (36,37,38,39), (48,49,50,51), 
    (52,53,54,55), (48,49,53,52), (49,50,54,53), (50,51,55,54), (51,48,52,55), (56,57,58,59), (60,61,62,63), (56,57,61,60), (57,58,62,61), (58,59,63,62), 
    (59,56,60,63)
    )
    
    VERTICES_osx = (
    (0,40,90), (100,40,90), (100,50,90), (0,50,90),(0,40,100), (100,40,100), (100,50,100), (0,50,100),(0,50,93), (100,50,93), (100,52,93), (0,52,93),
    (0,50,97), (100,50,97), (100,52,97), (0,52,97),(-4,24,85),(14,24,85),(14,42,85),(-4,42,85),(-4,24,122),(14,24,122),(14,42,122),(-4,42,122),
    (86,24,85),(104,24,85),(104,42,85),(86,42,85),(86,24,122),(104,24,122),(104,42,122),(86,42,122)
    )

    SURFACES_osx = (
    (0,1,2,3),(4,5,6,7),(0,1,5,4),(3,2,6,7),(1,2,6,5),(0,3,7,4),(8,9,10,11),(12,13,14,15),(8,9,13,12),(11,10,14,15),(9,10,14,13),(8,11,15,12),(16,17,18,19),
    (20,21,22,23),(16,17,21,20),(19,18,22,23),(17,18,22,21),(16,19,23,20),(24,25,26,27),(28,29,30,31),(24,25,29,28),(27,26,30,31),(25,26,30,29),(24,27,31,28)
    )

    VERTICES_bed = (
    (15,15,15), (85,15,15), (85,85,15), (15,85,15), (15,15,20), (85,15,20), (85,85,20), (15,85,20), (45,40,10), (55,40,10), (55,60,10), (45,60,10),
    (45,40,15), (55,40,15), (55,60,15), (45,60,15)
    )

    SURFACES_bed = (
    (0,1,2,3), (0,1,5,4), (3,0,4,7), (3,7,6,2), (2,6,5,1), (4,5,6,7), (8,9,10,11), (8,9,13,12), (11,8,12,15), (11,15,14,10), (10,14,13,9), (12,13,14,15)
    )
    
    VERTICES_Extruder = (
    (-10,50,97.5), (10,50,97.5), (10,53,97.5), (-10,53,97.5), (-10,50,110), (10,50,110), (10,53,110), (-10,53,110), (-10,50,86), (10,50,86), (10,53,86), 
    (-10,53,86), (-10,50,92.5), (10,50,92.5), (10,53,92.5), (-10,53,92.5), (-12,53,86), (12,53,86), (12,65,86), (-12,65,86), (-12,53,110), (12,53,110), 
    (12,65,110), (-12,65,110), (-4,58,86), (4,58,86), (4,62,86), (-4,62,86), (0,60,82)
    )
    
    SURFACES_Extruder = (
    (0,1,2,3), (4,5,6,7), (0,1,5,4), (3,2,6,7), (1,2,6,5), (0,3,7,4), (8,9,10,11), (12,13,14,15), (8,9,13,12), (11,10,14,15), (9,10,14,13), 
    (8,11,15,12), (16,17,18,19), (20,21,22,23), (16,17,21,20), (19,18,22,23), (17,18,22,21), (16,19,23,20), (24,25,28), (25,26,28), (26,27,28), 
    (27,24,28)
    )

    VERTICES_Stol = (
    (-150,-50,-5), (250,-50,-5), (250,150,-5), (-150,150,-5), (-150,-50,0), (250,-50,0), (250,150,0), (-150,150,0)
    )
    
    SURFACES_Stol = (
    (0,1,2,3), (4,5,6,7), (0,1,5,4), (2,3,7,6), (1,2,6,5), (0,3,7,4)
    )

    VERTICES_Stol = (
    (-150,-50,-5), (250,-50,-5), (250,150,-5), (-150,150,-5),(-150,-50,0), (250,-50,0), (250,150,0), (-150,150,0),(-145,-45,-80), (-135,-45,-80), (-135,-35,-80), 
    (-145,-35,-80),(-145,-45,-5), (-135,-45,-5), (-135,-35,-5), (-145,-35,-5),(235,-45,-80), (245,-45,-80), (245,-35,-80), (235,-35,-80),(235,-45,-5), (245,-45,-5), 
    (245,-35,-5), (235,-35,-5),(-145,135,-80), (-135,135,-80), (-135,145,-80), (-145,145,-80),(-145,135,-5), (-135,135,-5), (-135,145,-5), (-145,145,-5),(235,135,-80), 
    (245,135,-80), (245,145,-80), (235,145,-80),(235,135,-5), (245,135,-5), (245,145,-5), (235,145,-5)
    )

    SURFACES_Stol = (
    (0,1,2,3),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(8,9,10,11),(12,13,14,15),(8,9,13,12),(9,10,14,13),(10,11,15,14),(11,8,12,15),(16,17,18,19),
    (20,21,22,23),(16,17,21,20),(17,18,22,21),(18,19,23,22),(19,16,20,23),(24,25,26,27),(28,29,30,31),(24,25,29,28),(25,26,30,29),(26,27,31,30),(27,24,28,31),
    (32,33,34,35),(36,37,38,39),(32,33,37,36),(33,34,38,37),(34,35,39,38),(35,32,36,39)
    )

    VERTICES_Podloga = (
    (-1000, -1000, -81),(1000, -1000, -81),(1000, 1000, -81),(-1000, 1000, -81),(-1000, -1000, -83),(1000, -1000, -83),(1000, 1000, -83),(-1000, 1000, -83)
    )

    SURFACES_Podloga = (
    (0,1,2,3),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)
    )

    def draw(self):
        glPushMatrix() # zapamiętuje aktualny stan macierzy transformacji
        glTranslatef(*self.pos) # przesuwa caly uklad wspolzednych za pomoca operatora * do pozycji zadanej
        glRotatef(self.rot[0], 1, 0, 0)  # funkcje odpowiadaja za rotacje w danych osiach
        glRotatef(self.rot[1], 0, 1, 0)
        glRotatef(self.rot[2], 0, 0, 1)

        glEnable(GL_TEXTURE_2D) # zalacza uzycie tekstur 2D w openGL
        glBindTexture(GL_TEXTURE_2D, self.texture_id) # funkcja mowi o tym jaka teksture dodaje na powierzchnie bryly
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE) # funkcja mowi jak tekstura ma reagowac na swiatlo( 1. okresla obiekt konfiguracji, 2. wybiera tryb mieszania konfiguracji, 3. wybiera mnozenei jako mieszanie)
        glColor3f(1.0, 1.0, 1.0) # zmieniamy kolor na bialy zeby zdjecia nie zostaly znieksztalcone poprzez GL_MODULATE

        for surface in self.surfaces:
            v1 = self.vertices[surface[0]]
            v2 = self.vertices[surface[1]]
            v3 = self.vertices[surface[2]]
            normal = calculate_normal(v1, v2, v3) # obliczamy nromalna zeby wiedziec jak oswietlac teksture
            
            if len(surface) == 4:
                v4 = self.vertices[surface[3]] # jezeli ejst 4 wspolzedna to ją pobieramy
                glBegin(GL_QUADS) # otwieramy blok rysowania, wszystkie punkty wyslane az do glEnd() beda tworzyc czworoboczna sciane
                glNormal3fv(normal) # przekazuje wektor normlany dla sciany (kierunek padania swiatla)
                w = distance3d(v1, v2) * self.tex_scale
                h = distance3d(v2, v3) * self.tex_scale # obliczamy wysokosc i skalujemy wspolczynnikiem skalowania
                glTexCoord2f(0.0, 0.0); glVertex3fv(v1)
                glTexCoord2f(w, 0.0); glVertex3fv(v2)
                glTexCoord2f(w, h); glVertex3fv(v3)
                glTexCoord2f(0.0, h); glVertex3fv(v4) # paruje wierzcholki tekstury zeby dopasowaly sie do danej powierzchni
                glEnd() # zamykamy blok rysowania prostokatow
            elif len(surface) == 3:
                glBegin(GL_TRIANGLES) # otwieramy blok rysowania trojkatow
                glNormal3fv(normal) # przekazujemy normalna sciany (kierunek padania światła)
                w = distance3d(v1, v2) * self.tex_scale
                h = distance3d(v2, v3) * self.tex_scale # skalujemy
                glTexCoord2f(0.0, 0.0); glVertex3fv(v1)  
                glTexCoord2f(w, 0.0); glVertex3fv(v2)
                glTexCoord2f(w / 2.0, h); glVertex3fv(v3) # przypisujemy wierzcholki tekstury do powierzchni
                glEnd() # kończymy rysowanie trojkatow
        glDisable(GL_TEXTURE_2D) # konczymy mapowanie tekstur 
        glPopMatrix() # przywraca stan z przed uzycia glpushMatrix()


# Petla glowna programu jako OOP

def main():
    pygame.init()  # funkcja uruchamia biblioteke numpy i wszystkie jej moduły
    pygame.mixer.set_num_channels(8)   # funkcja otwiera 8 kanałów miksera zeby puszczac dzeiwki osi X Y i Z 
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512) # ustawiamy probkowanie na 22050 hz, rozmiar na -16(oznacza zapis w kodzie u2), steroe oraz buffer dla zmienijszenia opoznienia
    
    display = (1200, 800) # ustawia rozmiar okna
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)   # tworzy okno z podwojnu renderowaniem oraz odpala zalacza renderowanie sprzetowe z opengl

    glMatrixMode(GL_PROJECTION) # przelaczenie na obsluge kamery od tej pory komendy definiuja sposob widzenia kamery 
    gluPerspective(45, (display[0]/display[1]), 0.1, 1000.0)# ustalamy kat widzenia w stopniach, proporcja szerokosci do wysokosci okna do wypelnienia kamery, oraz odleglosci odciecia
    glMatrixMode(GL_MODELVIEW) # przelaczamy znow na domyslna obsluge bryl

    # Ładowanie tekstur
    tekstura_podlogi = load_texture(r"img\podloga.jpg")
    tekstura_metalu = load_texture(r"img\metal.jpg")
    tekstura_belki = load_texture(r"img\osX.jpg")
    tekstura_ekstrudera = load_texture(r"img\ekstruder.jpg")
    tekstura_stolu = load_texture(r"img\stol.jpg")
    tekstura_drewna = load_texture(r"img\drewno.jpg")
    
    # Inicjalizacja modeli wraz z pozycjami
    rama = Drukarka('Rama', tekstura_metalu)
    os_x = Drukarka('Oś X', tekstura_belki, pos=[0.0, 0.0, -2])
    bed = Drukarka('bed', tekstura_stolu)
    extruder = Drukarka('Ekstruder', tekstura_ekstrudera, pos=[50.0, 0.0, 0.0])
    stol = Drukarka('Stół', tekstura_drewna)
    podloga = Drukarka('Podloga', tekstura_podlogi)
    
    # Konfiguracja renderowania
    glEnable(GL_DEPTH_TEST) # konfiguracja glebi - rysuje tylko sciany przed kamera a te za ta sciana widoczna nie
    glEnable(GL_LIGHTING) # wlacza światlo, dzieki czemu teraz kazdy kolor bedzie zalezec od zdefiniowanego swiatla
    glEnable(GL_NORMALIZE)   # skaluje wektory normalne 0potrzebne do globalnego skalowania obiektow glScalef
    glShadeModel(GL_SMOOTH)  # ustawia model cieniowania na gladki 
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.3, 0.3, 0.3, 1.0])  # Defniiuje globalne swiatlo, ktore dociera do kazdego zakamarka sceny z intenstywnoscia 30%( stawione w RGBA gdzie A to przezroczystosc)
    glEnable(GL_LIGHT0) # aktywuje pierwsze wbudwane zrodlo swiatla 
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient) # okresla skladowa rozproszona
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse) # skladowa kierunkowa
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular) # punktowe blaski i refleksy
    
    rotate_x, rotate_y = -70, 150   
    distance = -35  # stan kamery
    mouse_down = False  # flaga mowiaca o braku wcisnietego przycisku myszy   

    tryb_sterowania = 1 # domyslny tryb sterowania
    kolor_filamentu = [0.0, 0.7, 1.0]  # domyslne parametry filamentu kolor
    wydrukowane_sciezki = [] # sciezki historyczne 
    aktualna_sciezka = []     # sciezka aktualnie rysowana

    auto_drukowanie = False
    auto_indeks_punktu = 0 # indeks punktu w pliku gcode
    predkosc_mnoznik = 1.0  # wspolczynnik predkosci druku

    # Definiowanie dzwiekow dla osi i kanalow mixera pygame
    print("Generowanie brzmień osi do pamięci RAM...")
    dzwieki_osi = {
        "X": {
            "sound": dzwiek_wolny_ruch(f_bazowa=150, duration=1.0, sample_rate=50050),
            "channel": pygame.mixer.Channel(0)
        },
        "Y": {
            "sound": dzwiek_wolny_ruch(f_bazowa=110, duration=1.0, sample_rate=45050),
            "channel": pygame.mixer.Channel(1)
        },
        "Z": {
            "sound": dzwiek_wolny_ruch(f_bazowa=220, duration=1.0, sample_rate=40050),
            "channel": pygame.mixer.Channel(2)
        }
    }
    
    # operacja pobrania pliku gcode, ktora zwraca blad gdy plik sie nie odnajdzie
    punkty_gcode = []
    try:
        punkty_gcode = load_gcode_file(file_name)
        print(f"Pomyślnie załadowano plik G-code. Znaleziono punktów: {len(punkty_gcode)}")
    except FileNotFoundError:
        print(f"BŁĄD: Nie znaleziono pliku o nazwie '{file_name}'! Autodruk z G-code nie zadziała.")

    clock = pygame.time.Clock() # tworzenie obiektu zegara pygame
    
    while True:
        stary_x = extruder.pos[0]
        stary_y = bed.pos[1]
        stary_z = os_x.pos[2] # zapisanie aktualnych polozen w nieskonczonej petli 

        for event in pygame.event.get():    # sprawdzanie czy uzytkownik zamknal okno aplikacji
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: mouse_down = True  # ustawienie flagi rotacji obrazu
                if event.button == 4: distance += 1.0    # obsluga scrolla
                if event.button == 5: distance -= 1.0    

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: mouse_down = False # resetuje flage przez co marea sie dalej nie rusza
                
            elif event.type == pygame.MOUSEMOTION: # wykrywa ruch kursora myszy i adykwanie pododuje ruch przestrzeni 3D
                if mouse_down:
                    dx, dy = event.rel
                    rotate_y += dx  
                    rotate_x += dy  

        keys = pygame.key.get_pressed()     # pobeira stan wszytksich przyciskow klawiatury 
        
        if keys[K_1]: tryb_sterowania = 1
        if keys[K_2]: tryb_sterowania = 2 # przelaczenie tryby sterwoania 

        if keys[K_r] and not(keys[K_SPACE] or auto_drukowanie) : kolor_filamentu = [1.0, 0.0, 0.0]  
        if keys[K_g] and not(keys[K_SPACE] or auto_drukowanie): kolor_filamentu = [0.0, 1.0, 0.0]  
        if keys[K_b] and not(keys[K_SPACE] or auto_drukowanie): kolor_filamentu = [0.0, 0.0, 1.0]  # przelaczenie koloru filamentu
        
        # Sterowanie prędkością + zwieksza, - zmienjsza 
        if keys[K_KP_PLUS]: 
            predkosc_mnoznik += 0.1
            if predkosc_mnoznik > 3.0: predkosc_mnoznik = 3.0
            print(f"Mnożnik prędkości: {predkosc_mnoznik}x")
        if keys[K_KP_MINUS]: 
            predkosc_mnoznik -= 1.0
            if predkosc_mnoznik < 1.0: predkosc_mnoznik = 1.0
            print(f"Mnożnik prędkości: {predkosc_mnoznik}x")
        
        if keys[K_4] and not auto_drukowanie and len(punkty_gcode) > 0: # wlaczenie autdrukwoania 
            auto_drukowanie = True
            auto_indeks_punktu = 0


        # Ręczne sterowanie osiami
        if keys[K_UP] and os_x.pos[2] < -2: os_x.pos[2] += 0.5
        if keys[K_DOWN] and os_x.pos[2] > -62.0: os_x.pos[2] -= 0.5

        if tryb_sterowania == 1:
            if keys[K_LEFT] and extruder.pos[0] > 20: extruder.pos[0] -= 0.5
            if keys[K_RIGHT] and extruder.pos[0] < 80: extruder.pos[0] += 0.5
        elif tryb_sterowania == 2:
            if keys[K_LEFT] and bed.pos[1] > -20: bed.pos[1] -= 0.5
            if keys[K_RIGHT] and bed.pos[1] < 40: bed.pos[1] += 0.5

        # Autodrukowanie
        if auto_drukowanie:
            # Ustalamy budżet ruchu na tę klatkę obrazu:
            if auto_indeks_punktu == 0:
                # Jeśli jedziemy do pierwszego punktu, jedź bardzo wolno (np. prędkość 0.2)
                # Ta wartość nie jest mnożona przez predkosc_mnoznik, żeby dojazd zawsze był powolny i płynny.
                dystans_do_pokonania = 0.2  
            else:
                # NORMALNY DRUK: Dla kolejnych punktów używaj standardowej prędkości z mnożnikiem
                dystans_do_pokonania = 2.0 * predkosc_mnoznik 
            
            while dystans_do_pokonania > 0 and auto_drukowanie:
                cel = punkty_gcode[auto_indeks_punktu]
                
                # Obliczanie wektora kierunku w 3D
                dx = cel[0] - extruder.pos[0]
                dy = cel[1] - bed.pos[1]
                dz = cel[2] - os_x.pos[2]
                
                odleglosc_do_celu = math.sqrt(dx**2 + dy**2 + dz**2)
                
                if odleglosc_do_celu <= dystans_do_pokonania:
                    # Jeśli cel jest bliżej niż limit ruchu w tej klatce przemieszczamy tam osie
                    extruder.pos[0] = cel[0]
                    bed.pos[1] = cel[1]
                    os_x.pos[2] = cel[2]
                    
                    # Odejmujemy zużyty dystans i bierzemy kolejny punkt
                    dystans_do_pokonania -= odleglosc_do_celu
                    auto_indeks_punktu += 1
                    
                    if auto_indeks_punktu >= len(punkty_gcode):
                        auto_drukowanie = False
                        if aktualna_sciezka:
                            wydrukowane_sciezki.append((aktualna_sciezka, kolor_filamentu.copy()))
                            aktualna_sciezka = []
                            
                    # chcemy przerwać ruch w tej konkretnej klatce, aby druk nie wystartował "w ułamku sekundy".
                    if auto_indeks_punktu == 1:
                        dystans_do_pokonania = 0
                else:
                    # Przemieszczenie o wyliczony wektor, gdy cel jest dalej niż budżet na klatkę
                    proporcja = dystans_do_pokonania / odleglosc_do_celu
                    extruder.pos[0] += dx * proporcja
                    bed.pos[1] += dy * proporcja
                    os_x.pos[2] += dz * proporcja
                    
                    dystans_do_pokonania = 0  # Koniec budżetu na tę klatkę

        # Porownywanie wartosci wspolrzednych starych i dnowych do wydawania dzwieku
        ruch_x = (extruder.pos[0] != stary_x)
        ruch_y = (bed.pos[1] != stary_y)
        ruch_z = (os_x.pos[2] != stary_z)

        if ruch_x:
            if not dzwieki_osi["X"]["channel"].get_busy():  # konstrukcja zapewniajaca jednorazowe wlaczenie dzwieku zapobiegajaec zapetleniu nieskonczonosci sinusiod podczas dlugiego ruchu
                dzwieki_osi["X"]["channel"].play(dzwieki_osi["X"]["sound"], loops=-1)
        else:
            if dzwieki_osi["X"]["channel"].get_busy(): dzwieki_osi["X"]["channel"].stop()

        if ruch_y:
            if not dzwieki_osi["Y"]["channel"].get_busy():
                dzwieki_osi["Y"]["channel"].play(dzwieki_osi["Y"]["sound"], loops=-1)
        else:
            if dzwieki_osi["Y"]["channel"].get_busy(): dzwieki_osi["Y"]["channel"].stop()

        if ruch_z:
            if not dzwieki_osi["Z"]["channel"].get_busy():
                dzwieki_osi["Z"]["channel"].play(dzwieki_osi["Z"]["sound"], loops=-1)
        else:
            if dzwieki_osi["Z"]["channel"].get_busy(): dzwieki_osi["Z"]["channel"].stop()

        # logika rysowania filamentu
        if keys[K_SPACE] or auto_drukowanie:
            #obliczamy rzeczywistą lokalizację końcówki dyszy extrudera
            pozycja_dyszy_swiat_x = extruder.pos[0] + 0.0
            pozycja_dyszy_swiat_y = 60.0  
            pozycja_dyszy_swiat_z = extruder.pos[2] + 82.0  

            #graicę stołu w których przy spełnieniu odpowiednich warunków da się rysować 
            stol_min_x, stol_max_x = 15.0, 85.0
            stol_min_y, stol_max_y = 15.0 + bed.pos[1], 85.0 + bed.pos[1]
            stol_poziom_z = 20.0  

            nad_stolem = (stol_min_x <= pozycja_dyszy_swiat_x <= stol_max_x) and \
                         (stol_min_y <= pozycja_dyszy_swiat_y <= stol_max_y)

            na_powierzchni_stolu = nad_stolem and (abs(pozycja_dyszy_swiat_z - stol_poziom_z) <= 1.5)
            w_powietrzu_ale_na_plastiku = False
            w_powietrzu_ale_pod_plastikiem = False
            #przeliczenie współrzędnyej z uwagi na ruch stołu drukarki 
            pozycja_wzgledna_y = 60.0 - bed.pos[1]
            
            #uzupełnienie listy wydrukowanych ścieżek, plus dodanie aktualnej ścieżki 
            wszystkie_do_sprawdzenia = wydrukowane_sciezki.copy()
            if aktualna_sciezka: wszystkie_do_sprawdzenia.append(aktualna_sciezka)

            for element in wszystkie_do_sprawdzenia:
                #pobranie danych nie zależne of formatu aktualna_sciezka/wydrukownae_sciezki  
                sciezka_punkty = element[0] if isinstance(element, tuple) else element
                for pkt in sciezka_punkty:
                    dx = pozycja_dyszy_swiat_x - pkt[0]
                    dy = pozycja_wzgledna_y - pkt[1]
                    dz = pozycja_dyszy_swiat_z - pkt[2]
                    #czy rysujemy(jesteśmy) na plastiku?
                    if (dx**2 + dy**2) < 2.0 and (0.0 <= dz <= 2.0):
                        w_powietrzu_ale_na_plastiku = True; break
                    #czy rysujemy(jesteśmy) w bok od plastiku?
                    if abs(dz) <= 1.5 and (dx**2 + dy**2) < 2.0:
                        w_powietrzu_ale_na_plastiku = True; break
                    #czy rysujemy(jesteśmy) pod plastkiem?
                    if (dx**2 + dy**2) < 2.0 and (-2.0 <= dz <= 0.0):
                        w_powietrzu_ale_pod_plastikiem = True; break
                if w_powietrzu_ale_na_plastiku or w_powietrzu_ale_pod_plastikiem: break

            if na_powierzchni_stolu or w_powietrzu_ale_na_plastiku or w_powietrzu_ale_pod_plastikiem:
                pozycja_dyszy_wzgledna = (pozycja_dyszy_swiat_x, pozycja_wzgledna_y, pozycja_dyszy_swiat_z)
                if not aktualna_sciezka:  
                    aktualna_sciezka.append(pozycja_dyszy_wzgledna)
                else:
                    ostatni_punkt = aktualna_sciezka[-1]
                    dystans = (pozycja_dyszy_wzgledna[0] - ostatni_punkt[0])**2 + \
                              (pozycja_dyszy_wzgledna[1] - ostatni_punkt[1])**2 + \
                              (pozycja_dyszy_wzgledna[2] - ostatni_punkt[2])**2
                    #dodanie nowego punktu do listy tylko wtedy jak przesunimey się odpowiednio daleko 
                    if dystans > 0.5:
                        aktualna_sciezka.append(pozycja_dyszy_wzgledna)
            else:
                if aktualna_sciezka:
                    #przekazanie danych do listy punkty wraz z kolorem filamentu 
                    wydrukowane_sciezki.append((aktualna_sciezka, kolor_filamentu.copy()))
                    aktualna_sciezka = []
        else:
            if aktualna_sciezka:
                #zabezpieczednie 
                wydrukowane_sciezki.append((aktualna_sciezka, kolor_filamentu.copy()))
                aktualna_sciezka = []

        
        glClearColor(0.12, 0.12, 0.14, 1.0) # ustawia kolor scenerii w oknie oraz jego przezroczystosc
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # Wymazuje zawartość poprzedniej klatki obrazu z bufora koloru oraz resetuje bufor głębi, przygotowując czyste płótno pod nowe obliczenia rysunkowe.
        glLoadIdentity() # resetuje maceirz obrotu do maceirzy jednostkowej oraz usuwa wszystkie transformacje z poprzedniej kaltki i przywraca punkt odniesienia do srodka swiata
        
        glTranslatef(0, -3, distance) # ustawia kamere tak jak zadal uzytkownik
        #pochylenie kamery 
        glRotatef(rotate_x, 1, 0, 0) 
        glRotatef(rotate_y, 0, 0, 1) 

        glLightfv(GL_LIGHT0, GL_POSITION, [50.0, 50.0, 300.0, 1.0]) # definiuje pozycje swiatla. Wpsolczynnik 1.0 mowi ze jest to swiatlo sferyczne podobne do slonca

        glPushMatrix()
        #przeskalowanie świata
        glScalef(0.1, 0.1, 0.1)
        glTranslatef(-50, -50, -5) 
        
        #extruder porusza się z osią Z
        extruder.pos[2] = os_x.pos[2]  
        # ruch pród/tył odbywa się tylko za pomocą stołu drukarki 
        os_x.pos[1] = 0.0
        extruder.pos[1] = 0.0
        
        #narysowanie elemntów drukarki 
        rama.draw()
        os_x.draw()
        extruder.draw()
        bed.draw()
        stol.draw()
        podloga.draw()

        #rysowanie linii filamentu
        glDisable(GL_LIGHTING)  # wyłaczeie świtła dla filamentu, żeby kolor był jednolity i nie zależał od oświetlenia
        glLineWidth(6.0)        
        glPushMatrix()
        glTranslatef(0.0, bed.pos[1], 0.0)#filament porusza sie razem ze stołem, bo przeciez na nim jest drukowany

        for sciezka, kolor_sciezki in wydrukowane_sciezki:
            glColor3fv(kolor_sciezki)
            glBegin(GL_LINE_STRIP)
            for punkt in sciezka: glVertex3fv(punkt)
            glEnd()
            
        if aktualna_sciezka:
            glColor3fv(kolor_filamentu)
            glBegin(GL_LINE_STRIP)
            for punkt in aktualna_sciezka: glVertex3fv(punkt)
            glEnd()
            
        glPopMatrix() 
        glEnable(GL_LIGHTING) 
        glPopMatrix() 
        
        pygame.display.flip()#orzekazanie nowej klatki dla użytkownika
        clock.tick(60)

if __name__ == "__main__":
    main()
