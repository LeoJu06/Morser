import grovepi
import grove_rgb_lcd as lcd
import time
import sqlite3
import smtplib
from email.mime.text import MIMEText
import requests
from send_email import send_email


# Port configuration
button = 3  # D3
buzzer = 0 # D4
led = 2  # D2

# Set the button to input mode, buzzer and LED to output mode
grovepi.pinMode(button, "INPUT")
grovepi.pinMode(buzzer, "OUTPUT")
grovepi.pinMode(led, "OUTPUT")

# Morse code timing definitions
DOT_DURATION = 0.15
DASH_DURATION = 0.25
LETTER_PAUSE_THRESHOLD = 1.0
FINISH_MESSAGE = 3.0

# Telegram configuration
TELEGRAM_BOT_TOKEN = "DEIN_BOT_TOKEN"
TELEGRAM_CHAT_ID = "DEIN_CHAT_ID"

# Morse-to-text dictionary
MORSE_TO_TEXT = {
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E", "..-.": "F",
    "--.": "G", "....": "H", "..": "I", ".---": "J", "-.-": "K", ".-..": "L",
    "--": "M", "-.": "N", "---": "O", ".--.": "P", "--.-": "Q", ".-.": "R",
    "...": "S", "-": "T", "..-": "U", "...-": "V", ".--": "W", "-..-": "X",
    "-.--": "Y", "--..": "Z", "-----": "0", ".----": "1", "..---": "2",
    "...--": "3", "....-": "4", ".....": "5", "-....": "6", "--...": "7",
    "---..": "8", "----.": "9", "/": " "  # Slash for spaces between letters
}

def detect_morse_input():
    morse_code = ""
    press_start = None
    last_press_time = None
    message_finished = False
    print("Morse input started. Press the button to input Morse code.")
    try:
        while not message_finished:
            button_state = grovepi.digitalRead(button)
            current_time = time.time()
            if button_state:
                if press_start is None:
                    press_start = current_time
                grovepi.digitalWrite(buzzer, 1)
                grovepi.digitalWrite(led, 1)
                if (current_time - press_start) >= FINISH_MESSAGE:
                    message_finished = True
                    print("\nMessage finished due to long press")
            else:
                grovepi.digitalWrite(buzzer, 0)
                grovepi.digitalWrite(led, 0)
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
                if morse_code and not morse_code.endswith(" "):
                    morse_code += "/"
                    print("/", end="", flush=True)
                last_press_time = None
            if last_press_time is not None and (current_time - last_press_time >= FINISH_MESSAGE):
                message_finished = True
                print("\nMessage finished due to inactivity")
            time.sleep(0.05)
    except KeyboardInterrupt:
        grovepi.digitalWrite(buzzer, 0)
        grovepi.digitalWrite(led, 0)
        print("\nProgram terminated.")
        return morse_code
    except IOError:
        grovepi.digitalWrite(buzzer, 0)
        grovepi.digitalWrite(led, 0)
        print("Error reading the button.")
    if message_finished:
        grovepi.digitalWrite(buzzer, 0)
        grovepi.digitalWrite(led, 0)
        return morse_code

def morse_to_text(morse_code):
    morse_code = morse_code.replace("/", " ")
    words = morse_code.split("   ")
    decoded_message = []
    for word in words:
        symbols = word.split()
        decoded_word = "".join([MORSE_TO_TEXT.get(symbol, "") for symbol in symbols])
        decoded_message.append(decoded_word)
    return " ".join(decoded_message)





# Main program
if __name__ == "__main__":
    morse_code = detect_morse_input()
    
    print("\nInput Morse code: ", morse_code)
    text = morse_to_text(morse_code)
    print("Decoded text: ", text)
    try:
        lcd.setText(text)
        time.sleep(0.2)
        lcd.setRGB(0, 255, 0)
    except OSError:
        lcd.setText(text)

    send_email(subject="Morse Code send from Rasbpy", body=text)  
