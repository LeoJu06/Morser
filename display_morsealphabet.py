import tkinter as tk
from PIL import Image, ImageTk

# Initialisiere das Tkinter-Hauptfenster
root = tk.Tk()
root.title("Morse Code Image Display")

# Bildschirmgröße ermitteln
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Bild laden
image_path = "./Morsecode.jpeg"
image = Image.open(image_path)

# Bildgröße an Bildschirm anpassen
image = image.resize((screen_width, screen_height), Image.LANCZOS)

# Konvertiere das Bild für Tkinter
photo = ImageTk.PhotoImage(image)

# Erstelle ein Label, um das Bild anzuzeigen
label = tk.Label(root, image=photo)
label.pack()

# Tkinter-Schleife starten
root.mainloop()
