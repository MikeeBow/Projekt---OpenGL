import re
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