import grovepi
import time

# Port-Nummer des Buttons (Digitalport)
button = 3  # D3, der vierte digitale Port

# Button auf INPUT setzen
grovepi.pinMode(button, "INPUT")

# Morsecode-Zeiten definieren (angepasst an typische Morse-Geschwindigkeit)
DOT_DURATION = 0.2  # Dauer eines Punktes in Sekunden
DASH_DURATION = 0.6  # Dauer eines Strichs in Sekunden
SYMBOL_PAUSE = 0.5  # Pause zwischen Symbolen
LETTER_PAUSE = 1.5  # Pause zwischen Buchstaben

def detect_morse_input():
    morse_code = ""
    press_start = None

    print("Morsen gestartet. Drücken Sie den Button, um zu morsen.")
    
    try:
        while True:
            button_state = grovepi.digitalRead(button)
            
            if button_state == 1:  # Button wird gedrückt
                if press_start is None:
                    press_start = time.time()  # Startzeit des Drückens
            else:  # Button wird losgelassen
                if press_start is not None:
                    press_duration = time.time() - press_start
                    
                    # Dauer auswerten, ob Punkt oder Strich
                    if press_duration < (DOT_DURATION + DASH_DURATION) / 2:
                        morse_code += "."
                        print(".", end="", flush=True)
                    else:
                        morse_code += "-"
                        print("-", end="", flush=True)
                    
                    press_start = None
                    time.sleep(SYMBOL_PAUSE)  # Kurze Pause zwischen Symbolen
                
                # Pause zwischen Buchstaben erkennen
                if len(morse_code) > 0:
                    time.sleep(LETTER_PAUSE)
                    print(" ", end="", flush=True)  # Abstand für Klarheit
                
    except KeyboardInterrupt:
        print("\nProgramm beendet.")
        return morse_code

    except IOError:
        print("Fehler beim Lesen des Buttons.")

# Die Morsecode-Funktion aufrufen
morse_code = detect_morse_input()
print("\nEingehender Morsecode: ", morse_code)
