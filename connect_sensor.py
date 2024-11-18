import grovepi
import time

# Port-Nummer des Buttons (Digitalport)
button = 3  # D3, der vierte digitale Port

# Button auf INPUT setzen
grovepi.pinMode(button, "INPUT")

# Morsecode-Zeiten definieren
DOT_DURATION = 0.2  # Dauer eines Punktes in Sekunden
DASH_DURATION = 0.6  # Dauer eines Strichs in Sekunden
SYMBOL_PAUSE = 0.5  # Pause zwischen Symbolen (zwischen Punkt und Strich)
LETTER_PAUSE_THRESHOLD = 1.0  # Pause für Buchstaben (längerer Abstand)
FINISH_MESSAGE = 4.0
def detect_morse_input():
    morse_code = ""
    press_start = None
    last_press_time = None
    message_finished = False

    print("Morsen gestartet. Drücken Sie den Button, um zu morsen.")
    
    try:
        while not message_finished:
            button_state = grovepi.digitalRead(button)
            current_time = time.time()

            if button_state == 1:  # Button gedrückt
                if press_start is None:
                    press_start = current_time  # Startzeit des Drückens
            else:  # Button nicht gedrückt
                if press_start is not None:  # Button wurde losgelassen
                    press_duration = current_time - press_start
                    press_start = None

                    # Punkt oder Strich bestimmen
                    if press_duration < DOT_DURATION:
                        morse_code += "."
                        print(".", end="", flush=True)
                    elif press_duration >= FINISH_MESSAGE:
                        message_finished = True

                    else:
                        morse_code += "-"
                        print("-", end="", flush=True)
                    
                    last_press_time = current_time

            # Überprüfen, ob genug Pause vergangen ist, um einen neuen Buchstaben zu beginnen
            if last_press_time is not None and (current_time - last_press_time > LETTER_PAUSE_THRESHOLD):
                if morse_code:
                    print(" ", end="", flush=True)
                    last_press_time = None

            time.sleep(0.05)  # Kurze Wartezeit für CPU-Entlastung
                
    except KeyboardInterrupt:
        print("\nProgramm beendet.")
        return morse_code

    except IOError:
        print("Fehler beim Lesen des Buttons.")

    if message_finished:
        return morse_code

# Die Morsecode-Funktion aufrufen
morse_code = detect_morse_input()
print("\nEingehender Morsecode: ", morse_code)

