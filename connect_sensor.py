import grovepi
import grove_rgb_lcd as lcd
import time

# Port number for the button (digital port)
button = 3  # D3, the fourth digital port

# Port number for the buzzer (digital port)
buzzer = 0  # D4, the fifth digital port

# Port number for the LED (digital port)
led = 2  # D2, the sixth digital port

# Set the button to input mode, buzzer and LED to output mode
grovepi.pinMode(button, "INPUT")
grovepi.pinMode(buzzer, "OUTPUT")
grovepi.pinMode(led, "OUTPUT")

# Morse code timing definitions
DOT_DURATION = 0.2  # Duration of a dot in seconds
DASH_DURATION = 0.5  # Duration of a dash in seconds
LETTER_PAUSE_THRESHOLD = 1.0  # Pause to recognize the start of a new letter
FINISH_MESSAGE = 3.0  # Duration of pause to signal the end of the message


def detect_morse_input():
    """
    This function captures user input via a button to generate Morse code.
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
                grovepi.digitalWrite(buzzer, 1)  # Activate the buzzer
                grovepi.digitalWrite(led, 1)  # Turn on the LED

                # Check if the button has been held longer than FINISH_MESSAGE
                if (current_time - press_start) >= FINISH_MESSAGE:
                    message_finished = True
                    print("\nMessage finished due to long press")

            else:  # Button is not pressed
                grovepi.digitalWrite(buzzer, 0)  # Deactivate the buzzer
                grovepi.digitalWrite(led, 0)  # Turn off the LED

                if press_start is not None:  # If the button was previously pressed
                    press_duration = current_time - press_start  # Calculate press duration
                    press_start = None  # Reset for the next press

                    # Determine if the input is a dot or a dash
                    if press_duration < DOT_DURATION:
                        morse_code += "."  # Short press → dot
                        print(".", end="", flush=True)
                    elif press_duration >= DASH_DURATION:
                        morse_code += "-"  # Longer press → dash
                      
                        print("-", end="", flush=True)

                    last_press_time = current_time  # Save the time of the last input

            # Check if enough pause has passed to recognize a new letter
            if last_press_time is not None and ((current_time - last_press_time) > LETTER_PAUSE_THRESHOLD):
                if morse_code and not morse_code.endswith(" "):  # Prevent repeated spaces
                    morse_code += "/"  # Add a slash for letter pause
                    print("/", end="", flush=True)
                last_press_time = None  # Reset to detect a new letter pause

            # Check for end of message due to inactivity
            if last_press_time is not None and (current_time - last_press_time >= FINISH_MESSAGE):
                message_finished = True
                print("\nMessage finished due to inactivity")

            # Short delay to reduce CPU usage
            time.sleep(0.05)

    except KeyboardInterrupt:
        # End the program on keyboard interrupt (CTRL + C)
        grovepi.digitalWrite(buzzer, 0)  # Ensure the buzzer is turned off
        grovepi.digitalWrite(led, 0)  # Ensure the LED is turned off
        print("\nProgram terminated.")
        return morse_code

    except IOError:
        # Error handling for button read issues
        grovepi.digitalWrite(buzzer, 0)  # Ensure the buzzer is turned off
        grovepi.digitalWrite(led, 0)  # Ensure the LED is turned off
        print("Error reading the button.")

    # Return the Morse code when the message is finished
    if message_finished:
        grovepi.digitalWrite(buzzer, 0)  # Ensure the buzzer is turned off
        grovepi.digitalWrite(led, 0)  # Ensure the LED is turned off
        return morse_code

# Wörterbuch zur Umwandlung von Morsecode in Klartext
MORSE_TO_TEXT = {
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E", "..-.": "F",
    "--.": "G", "....": "H", "..": "I", ".---": "J", "-.-": "K", ".-..": "L",
    "--": "M", "-.": "N", "---": "O", ".--.": "P", "--.-": "Q", ".-.": "R",
    "...": "S", "-": "T", "..-": "U", "...-": "V", ".--": "W", "-..-": "X",
    "-.--": "Y", "--..": "Z", "-----": "0", ".----": "1", "..---": "2",
    "...--": "3", "....-": "4", ".....": "5", "-....": "6", "--...": "7",
    "---..": "8", "----.": "9", "/": " "  # Slash for spaces between letters
}

def morse_to_text(morse_code):
    """
    Wandelt Morsecode in Klartext um.
    
    Args:
        morse_code (str): Die Morsecode-Zeichenkette, z.B. "... --- ..."
    
    Returns:
        str: Der umgewandelte Klartext
    """
    # Replace "/" with a space for letter pauses
    morse_code = morse_code.replace("/", " ")

    # Split Morsecode into words based on triple spaces
    words = morse_code.split("   ")
    decoded_message = []

    for word in words:
        # Split word into Morse symbols based on single spaces
        symbols = word.split()
        decoded_word = "".join([MORSE_TO_TEXT.get(symbol, "") for symbol in symbols])
        decoded_message.append(decoded_word)

    return " ".join(decoded_message)


# Main program
if __name__ == "__main__":
    morse_code = detect_morse_input()  # Get the Morse code input
    print("\nInput Morse code: ", morse_code)

    # Convert Morse code to text and display it
    text = morse_to_text(morse_code)
    print("Decoded text: ", text)

    try:
        lcd.setText(text)  # Setzt den Text auf dem Display
        time.sleep(0.2)  # Kurze Verzögerung
        lcd.setRGB(0, 255, 0)  # Setzt den Hintergrund auf grün
    except OSError as e:
        # error during setting background color
        # this can pass silently
        pass
        lcd.setText(text)  # Setzt den Text trotzdem

