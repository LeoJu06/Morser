import smtplib  # Import the SMTP library for sending emails
from email.mime.text import MIMEText  # Import MIMEText to format the email body as plain text
from email.mime.multipart import MIMEMultipart  # Import MIMEMultipart to allow sending email with multiple parts
import yaml  # Import the yaml library to read YAML configuration files


# Load the configuration from the YAML file to retrieve email credentials
with open("config.yaml", "r") as file:  # Open the config.yaml file in read mode
    config = yaml.safe_load(file)  # Load the YAML content into a Python dictionary

# Extract email credentials from the loaded configuration
email_credentials = config["email_credentials"]  # Get the email credentials section from the config
leo_mail = email_credentials["email"]  # Extract the sender's email from the credentials
leos_password = email_credentials["password"]  # Extract the sender's email password from the credentials

# Default email settings (recipient and content of the email)
recipient_email = "Andrin.hugentobler@hotmail.com"  # Define the recipient's email address
subject = "Mail send from my Raspby"  # Define the subject of the email
body = "Second mail from my raspby"  # Define the body content of the email

def send_email(subject, body, sender_email=leo_mail, sender_password=leos_password, recipient_email=recipient_email, smtp_server="smtp.gmail.com", smtp_port=587):
    """
    Sends an email using the provided SMTP server and authentication details.
    
    :param sender_email: The email address of the sender (default is the value loaded from the config.yaml file)
    :param sender_password: The password for the sender's email account (default is the value loaded from the config.yaml file)
    :param recipient_email: The recipient's email address
    :param subject: The subject line of the email
    :param body: The body content of the email
    :param smtp_server: The SMTP server address to use for sending the email (default is "smtp.gmail.com")
    :param smtp_port: The SMTP server port to use (default is 587, for TLS encryption)
    """
    try:
        # Create the email message as a multipart message
        msg = MIMEMultipart()  # This allows us to send an email with multiple parts (like text and attachments)
        msg['From'] = sender_email  # Set the "From" field to the sender's email
        msg['To'] = recipient_email  # Set the "To" field to the recipient's email
        msg['Subject'] = subject  # Set the subject line of the email

        # Attach the body text of the email (in plain text format)
        msg.attach(MIMEText(body, 'plain'))  # 'plain' indicates the email body will be plain text

        # Establish a connection to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)  # Connect to the SMTP server on the specified port
        server.starttls()  # Start TLS encryption for the connection to make it secure

        # Log in to the SMTP server using the sender's email and password
        server.login(sender_email, sender_password)  # Authenticate the sender

        # Send the email from the sender to the recipient
        server.sendmail(sender_email, recipient_email, msg.as_string())  # Send the email as a string

        print("E-Mail wurde erfolgreich gesendet!")  # Print a success message if the email was sent

    except Exception as e:  # Catch any errors that occur during the email sending process
        print(f"Fehler beim Senden der E-Mail: {e}")  # Print the error message if something goes wrong

    finally:
        # Close the connection to the SMTP server
        server.quit()  # This ensures the server connection is closed even if an error occurs


# The following example demonstrates how to use the `send_email` function:
# Example call of the `send_email` function
# send_email(
#     sender_email="deine.email@gmail.com",  # Specify the sender's email
#     sender_password="dein_passwort",       # Specify the sender's email password
#     recipient_email="empfaenger.email@example.com",  # Specify the recipient's email address
#     subject="Test-E-Mail",  # Specify the subject of the email
#     body="Das ist eine Testnachricht."  # Specify the body content of the email
# )

if __name__ == "__main__":  # If this script is being run directly (not imported)
    # Send the email using the credentials and content defined earlier
    send_email(leo_mail, leos_password, recipient_email, subject, body)  # Call the send_email function with the appropriate arguments
