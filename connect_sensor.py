# Import necessary libraries
import grovepi                # Import the GrovePi module to interface with Grove sensors and actuators
import grove_rgb_lcd as lcd   # Import the Grove RGB LCD library to display text on an LCD screen
import time                   # Import the time module to handle time-related tasks (e.g., delays)
import smtplib                # Import the SMTP library to send emails using the Simple Mail Transfer Protocol
from email.mime.text import MIMEText  # Import MIMEText to construct the body of the email
from send_email import send_email  # Import the custom 'send_email' function to send emails

# Port configuration for the GrovePi components
BUTTON_PORT = 3  # D3 for the button (the button is connected to digital pin D3 on the GrovePi)
BUZZER_PORT = 0  # D4 for the buzzer (the buzzer is connected to digital pin D4)
LED_PORT = 2     # D2 for the LED (the LED is connected to digital pin D2)

# Configure GrovePi ports
grovepi.pinMode(BUTTON_PORT, "INPUT")  # Set the button port as an INPUT (we are reading the button state)
grovepi.pinMode(BUZZER_PORT, "OUTPUT") # Set the buzzer port as an OUTPUT (we will control the buzzer)
grovepi.pinMode(LED_PORT, "OUTPUT")    # Set the LED port as an OUTPUT (we will control the LED)

# Morse code timing definitions
DOT_DURATION = 0.15         # Duration of a dot (short press) in seconds (a dot lasts 0.15 seconds)
DASH_DURATION = 0.25        # Minimum duration of a dash (long press) in seconds (a dash lasts 0.25 seconds)
LETTER_PAUSE_THRESHOLD = 1.0  # Pause threshold to indicate end of a letter in seconds (a pause of 1 second indicates the end of a letter)
FINISH_MESSAGE = 3.0        # Duration to indicate the end of the message (3 seconds indicates the end of the message)

# Morse code to text dictionary
MORSE_TO_TEXT = {   # A dictionary that maps Morse code sequences to corresponding alphabetic characters or digits
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E", "..-.": "F",
    "--.": "G", "....": "H", "..": "I", ".---": "J", "-.-": "K", ".-..": "L",
    "--": "M", "-.": "N", "---": "O", ".--.": "P", "--.-": "Q", ".-.": "R",
    "...": "S", "-": "T", "..-": "U", "...-": "V", ".--": "W", "-..-": "X",
    "-.--": "Y", "--..": "Z", "-----": "0", ".----": "1", "..---": "2",
    "...--": "3", "....-": "4", ".....": "5", "-....": "6", "--...": "7",
    "---..": "8", "----.": "9", "/": " "  # Slash represents space between words
}

def detect_morse_input():
    """
    Detects Morse code input from a button connected to the Raspberry Pi.

    Returns:
        str: The detected Morse code sequence as a string of dots (.) and dashes (-).
    """
    morse_code = ""  # Initialize an empty string to store the detected Morse code sequence
    press_start = None  # Variable to store the start time of a button press
    last_press_time = None  # Variable to track the last time the button was pressed
    message_finished = False  # Flag to indicate whether the message input is finished

    print("Morse input started. Press the button to input Morse code.")  # Inform the user to start pressing the button

    try:
        while not message_finished:  # Keep detecting Morse code until the message is finished
            button_state = grovepi.digitalRead(BUTTON_PORT)  # Read the state of the button (pressed or not)
            current_time = time.time()  # Get the current time

            if button_state:  # If the button is pressed
                if press_start is None:  # If the press start time is not recorded, record it
                    press_start = current_time
                grovepi.digitalWrite(BUZZER_PORT, 1)  # Turn on the buzzer
                grovepi.digitalWrite(LED_PORT, 1)     # Turn on the LED

                if (current_time - press_start) >= FINISH_MESSAGE:  # If the button is pressed for too long, finish the message
                    message_finished = True
                    print("\nMessage finished due to long press")  # Indicate that the message is finished due to a long press
            else:  # If the button is not pressed
                grovepi.digitalWrite(BUZZER_PORT, 0)  # Turn off the buzzer
                grovepi.digitalWrite(LED_PORT, 0)     # Turn off the LED

                if press_start is not None:  # If a press was previously detected
                    press_duration = current_time - press_start  # Calculate how long the button was pressed
                    press_start = None  # Reset the press start time

                    if press_duration < DOT_DURATION:  # If the press was short, it's a dot
                        morse_code += "."
                        print(".", end="", flush=True)
                    elif press_duration >= DASH_DURATION:  # If the press was long enough, it's a dash
                        morse_code += "-"
                        print("-", end="", flush=True)

                    last_press_time = current_time  # Record the time of the last press

            # If the pause between button presses is long enough, add a space (slash) to the Morse code
            if last_press_time is not None and ((current_time - last_press_time) > LETTER_PAUSE_THRESHOLD):
                if morse_code and not morse_code.endswith("/"):  # If there's Morse code and no space at the end
                    morse_code += "/"  # Add a space between letters
                    print("/", end="", flush=True)
                last_press_time = None

            # If there's a long pause, finish the message
            if last_press_time is not None and (current_time - last_press_time >= FINISH_MESSAGE):
                message_finished = True
                print("\nMessage finished due to inactivity")  # Indicate that the message finished due to inactivity

            time.sleep(0.05)  # Add a small delay to prevent excessive CPU usage

    except KeyboardInterrupt:
        print("\nProgram terminated by user.")  # Handle Ctrl+C interruption
    except IOError:
        print("Error reading the button.")  # Handle I/O errors (e.g., button or GrovePi issues)
    finally:
        grovepi.digitalWrite(BUZZER_PORT, 0)  # Ensure the buzzer is turned off when done
        grovepi.digitalWrite(LED_PORT, 0)     # Ensure the LED is turned off when done

    return morse_code  # Return the collected Morse code sequence

def morse_to_text(morse_code):
    """
    Converts a Morse code string into plain text.

    Args:
        morse_code (str): The Morse code string to decode.

    Returns:
        str: The decoded plain text message.
    """
    morse_code = morse_code.replace("/", " ")  # Replace slashes with spaces (to separate words)
    words = morse_code.split("   ")  # Split the Morse code into words (3 spaces represent a word separator)
    decoded_message = []  # Initialize an empty list to store the decoded words

    # Loop through each word in Morse code
    for word in words:
        symbols = word.split()  # Split each word into individual symbols (dots and dashes)
        decoded_word = "".join([MORSE_TO_TEXT.get(symbol, "") for symbol in symbols])  # Decode each symbol to a character
        decoded_message.append(decoded_word)  # Add the decoded word to the list

    return " ".join(decoded_message)  # Return the decoded message as a string

if __name__ == "__main__":  # If this script is being run directly (not imported)
    # Detect Morse code input
    morse_code = detect_morse_input()  # Call the function to detect Morse code input from the button
    print("\nInput Morse code:", morse_code)  # Print the Morse code sequence that was input

    # Convert Morse code to text
    text = morse_to_text(morse_code)  # Decode the Morse code into text
    print("Decoded text:", text)  # Print the decoded text

    # Display the decoded text on the LCD
    try:
        lcd.setText(text)  # Set the text on the LCD
        lcd.setRGB(0, 255, 0)  # Set the LCD's background color to green
    except OSError:
        print("Error displaying text on LCD.")  # Handle errors if the LCD is not connected or not functioning

    # Send the decoded text via email
    send_email(subject="Morse Code Message from Raspberry Pi", body=text)  # Send the decoded message via email
