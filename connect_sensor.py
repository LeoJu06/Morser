"""
Module for detecting Morse code input via a Raspberry Pi using GrovePi components.
This module converts the Morse code into text, displays the text on an LCD,
and sends the message via email.
"""

import grovepi
import grove_rgb_lcd as lcd
import time
import smtplib
from email.mime.text import MIMEText
from send_email import send_email

# Port configuration
BUTTON_PORT = 3  # D3 for the button
BUZZER_PORT = 0  # D4 for the buzzer
LED_PORT = 2     # D2 for the LED

# Configure GrovePi ports
# Set button to input mode, buzzer and LED to output mode
grovepi.pinMode(BUTTON_PORT, "INPUT")
grovepi.pinMode(BUZZER_PORT, "OUTPUT")
grovepi.pinMode(LED_PORT, "OUTPUT")

# Morse code timing definitions
DOT_DURATION = 0.15         # Duration of a dot (short press) in seconds
DASH_DURATION = 0.25        # Minimum duration of a dash (long press) in seconds
LETTER_PAUSE_THRESHOLD = 1.0  # Pause threshold to indicate end of a letter in seconds
FINISH_MESSAGE = 3.0        # Duration to indicate the end of the message

# Morse-to-text dictionary
MORSE_TO_TEXT = {
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E", "..-.": "F",
    "--.": "G", "....": "H", "..": "I", ".---": "J", "-.-": "K", ".-..": "L",
    "--": "M", "-.": "N", "---": "O", ".--.": "P", "--.-": "Q", ".-.": "R",
    "...": "S", "-": "T", "..-": "U", "...-": "V", ".--": "W", "-..-": "X",
    "-.--": "Y", "--..": "Z", "-----": "0", ".----": "1", "..---": "2",
    "...--": "3", "....-": "4", ".....": "5", "-....": "6", "--...": "7",
    "---..": "8", "----.": "9", "/": " "  # Slash for spaces between words
}

def detect_morse_input():
    """
    Detects Morse code input from a button connected to the Raspberry Pi.

    Returns:
        str: The detected Morse code sequence as a string of dots (.) and dashes (-).
    """
    morse_code = ""
    press_start = None
    last_press_time = None
    message_finished = False

    print("Morse input started. Press the button to input Morse code.")
    try:
        while not message_finished:
            button_state = grovepi.digitalRead(BUTTON_PORT)
            current_time = time.time()

            if button_state:
                if press_start is None:
                    press_start = current_time
                grovepi.digitalWrite(BUZZER_PORT, 1)
                grovepi.digitalWrite(LED_PORT, 1)

                if (current_time - press_start) >= FINISH_MESSAGE:
                    message_finished = True
                    print("\nMessage finished due to long press")
            else:
                grovepi.digitalWrite(BUZZER_PORT, 0)
                grovepi.digitalWrite(LED_PORT, 0)

                if press_start is not None:
                    press_duration = current_time - press_start
                    press_start = None

                    if press_duration < DOT_DURATION:
                        morse_code += "."
                        print(".", end="", flush=True)
                    elif press_duration >= DASH_DURATION:
                        morse_code += "-"
                        print("-", end="", flush=True)

                    last_press_time = current_time

            if last_press_time is not None and ((current_time - last_press_time) > LETTER_PAUSE_THRESHOLD):
                if morse_code and not morse_code.endswith("/"):
                    morse_code += "/"
                    print("/", end="", flush=True)
                last_press_time = None

            if last_press_time is not None and (current_time - last_press_time >= FINISH_MESSAGE):
                message_finished = True
                print("\nMessage finished due to inactivity")

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except IOError:
        print("Error reading the button.")
    finally:
        grovepi.digitalWrite(BUZZER_PORT, 0)
        grovepi.digitalWrite(LED_PORT, 0)

    return morse_code

def morse_to_text(morse_code):
    """
    Converts a Morse code string into plain text.

    Args:
        morse_code (str): The Morse code string to decode.

    Returns:
        str: The decoded plain text message.
    """
    morse_code = morse_code.replace("/", " ")  # Replace slashes with spaces
    words = morse_code.split("   ")  # Split Morse code into words
    decoded_message = []

    for word in words:
        symbols = word.split()
        decoded_word = "".join([MORSE_TO_TEXT.get(symbol, "") for symbol in symbols])
        decoded_message.append(decoded_word)

    return " ".join(decoded_message)

if __name__ == "__main__":
    # Detect Morse code input
    morse_code = detect_morse_input()
    print("\nInput Morse code:", morse_code)

    # Convert Morse code to text
    text = morse_to_text(morse_code)
    print("Decoded text:", text)

    # Display the decoded text on the LCD
    try:
        lcd.setText(text)
        lcd.setRGB(0, 255, 0)
    except OSError:
        print("Error displaying text on LCD.")

    # Send the decoded text via email
    send_email(subject="Morse Code Message from Raspberry Pi", body=text)
