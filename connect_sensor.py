import grovepi
import time

# Port number of the button (digital port)
button = 3  # D3, the fourth digital port

# Set the button to input mode
grovepi.pinMode(button, "INPUT")

# Morse code timing definitions
DOT_DURATION = 0.2  # Duration of a dot in seconds
DASH_DURATION = 0.6  # Duration of a dash in seconds
SYMBOL_PAUSE = 0.5  # Pause between symbols (dot or dash)
LETTER_PAUSE_THRESHOLD = 1.0  # Pause to recognize the start of a new letter
FINISH_MESSAGE = 4.0  # Duration of pause to signal the end of the message


def detect_morse_input():
    """
    This function captures user input via a button to generate Morse code.
    The user can press the button for short or long durations to create dots (.)
    or dashes (-). A long pause signals the end of the input.

    Function details:
    - A short press (< DOT_DURATION) registers as a dot.
    - A longer press (>= DOT_DURATION and < FINISH_MESSAGE) registers as a dash.
    - A pause greater than LETTER_PAUSE_THRESHOLD between inputs adds a space
      for a new letter.
    - A very long pause (>= FINISH_MESSAGE) signals the end of the message.

    Returns:
        str: The Morse code string generated from the input.
    """
    morse_code = ""
    press_start = None  # Time when the button press started
    last_press_time = None  # Time of the last button press
    message_finished = False  # Flag to indicate the message is complete

    print("Morse input started. Press the button to input Morse code.")

    try:
        while not message_finished:
            # Read the button status (1 = pressed, 0 = not pressed)
            button_state = grovepi.digitalRead(button)
            current_time = time.time()  # Get the current time

            if button_state:  # Button is pressed
                if press_start is None:
                    press_start = current_time  # Record the start time of the press
            else:  # Button is not pressed
                if press_start is not None:  # If the button was previously pressed
                    press_duration = current_time - press_start  # Calculate press duration
                    press_start = None  # Reset for the next press

                    # Determine if the input is a dot or a dash
                    if press_duration < DOT_DURATION:
                        morse_code += "."  # Short press → dot
                        print(".", end="", flush=True)
                    elif press_duration >= FINISH_MESSAGE:
                        message_finished = True  # Long pause → end of message
                    else:
                        morse_code += "-"  # Longer press → dash
                        print("-", end="", flush=True)

                    last_press_time = current_time  # Save the time of the last input

            # Check if enough pause has passed to recognize a new letter
            if last_press_time is not None and (current_time - last_press_time > LETTER_PAUSE_THRESHOLD):
                if morse_code:  # If there is already a part of Morse code
                    print("/", end="", flush=True)  # Print a space for a new letter
                    last_press_time = None  # Reset to detect a new letter pause

            # Short delay to reduce CPU usage
            time.sleep(0.05)

    except KeyboardInterrupt:
        # End the program on keyboard interrupt (CTRL + C)
        print("\nProgram terminated.")
        return morse_code

    except IOError:
        # Error handling for button read issues
        print("Error reading the button.")

    # Return the Morse code when the message is finished
    if message_finished:
        return morse_code




# Wörterbuch zur Umwandlung von Morsecode in Klartext
MORSE_TO_TEXT = {
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E", "..-.": "F",
    "--.": "G", "....": "H", "..": "I", ".---": "J", "-.-": "K", ".-..": "L",
    "--": "M", "-.": "N", "---": "O", ".--.": "P", "--.-": "Q", ".-.": "R",
    "...": "S", "-": "T", "..-": "U", "...-": "V", ".--": "W", "-..-": "X",
    "-.--": "Y", "--..": "Z", "-----": "0", ".----": "1", "..---": "2",
    "...--": "3", "....-": "4", ".....": "5", "-....": "6", "--...": "7",
    "---..": "8", "----.": "9", "/": " "  # Schrägstrich für Leerzeichen
}

def morse_to_text(morse_code):
    """
    Wandelt Morsecode in Klartext um.
    
    Args:
        morse_code (str): Die Morsecode-Zeichenkette, z.B. "... --- ..."
    
    Returns:
        str: Der umgewandelte Klartext
    """
    # Teilen der Morsecode-Zeichenkette in Wörter anhand von "   " (drei Leerzeichen)
    words = morse_code.split("   ")
    decoded_message = []

    for word in words:
        # Teilen in einzelne Morsecode-Zeichen anhand von " " (ein Leerzeichen)
        symbols = word.split(" ")
        decoded_word = "".join([MORSE_TO_TEXT.get(symbol, "") for symbol in symbols])
        decoded_message.append(decoded_word)

    return " ".join(decoded_message)


# Beispiel zur Umwandlung
morse_code = detect_morse_input()  # Diese Funktion liefert den Morsecode
print("\nInput Morse code: ", morse_code)

# Konvertiere Morsecode in Text und gebe ihn aus
text = morse_to_text(morse_code)
print("Decoded text: ", text)
