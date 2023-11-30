import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from tkinter import PhotoImage
from PIL import Image, ImageTk
import pygame
from tkinter import messagebox

def custom_alert(sound_file):
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    messagebox.showinfo("Title", "Message")
    while pygame.mixer.music.get_busy():  # Wait for audio to finish playing
        pygame.time.Clock().tick(10)

_main_root_created = False

def setup_root():
    global _main_root_created
    if not _main_root_created:
        root = ThemedTk(theme="arc")
        root.title("Product Configurator")
        root.geometry("800x400")
        _main_root_created = True
    else:
        root = tk.Toplevel()
        root.title("Product Configurator - Additional Window")
        root.geometry("800x400")
    return root

# Constants
IMAGE_PATH = r"C:\Users\rasmu\Desktop\Micro matic\micromaticlogo.jpg"
DESIRED_SIZE = 100
HEADER_FONT = ("Arial", 16, "bold")
HEADER_OFFSET = 80  # Based on the logo's size

def load_and_resize_image(path, desired_size):
    """Load an image and resize it to the desired size."""
    image = Image.open(path)
    image = image.resize((desired_size, desired_size), Image.ANTIALIAS)
    return image

def setup_header(root, combo_frame):
    """Set up the header for the application."""
    
    # Setup logo
    logo_image = load_and_resize_image(IMAGE_PATH, DESIRED_SIZE)
    logo = ImageTk.PhotoImage(logo_image)
    
    # Display the logo at the top left corner
    logo_label = ttk.Label(root, image=logo)
    logo_label.image = logo  # Prevent image object from being garbage collected
    logo_label.place(relx=0, rely=0, anchor=tk.NW)

    # Display the text header
    header_text = "Micro Matic Product Configurator"
    header = ttk.Label(root, text=header_text, font=HEADER_FONT)
    place_header_based_on_combo_frame_position(header, combo_frame, root)

def place_header_based_on_combo_frame_position(header, combo_frame, root):
    """Position the header based on the combo_frame's position."""
    combo_frame_y = combo_frame.winfo_y()
    header_x = root.winfo_width() // 2
    header_y = combo_frame_y - HEADER_OFFSET
    
    # Debug print statements
    print(f"Root width: {root.winfo_width()}")
    print(f"Header position: x={header_x}, y={header_y}")
    
    header.place(x=header_x, y=header_y, anchor=tk.N)

def setup_combobox_frame(root, categories, update_combos, reset_combos, show_code_number, toggle_description, sort_by_system, df):
    global updated_dropdown_values
    updated_dropdown_values = categories  # Initially set to the full categories

    combo_frame = ttk.Frame(root, padding="10")
    combo_frame.pack(pady=100)

    combos = {}

    # Create the 'System' dropdown first
    if 'System' in categories:
        ttk.Label(combo_frame, text="System").grid(row=0, column=0, padx=5, pady=2)
        system_items = categories['System']
        selected_system = tk.StringVar()
        system_combobox = ttk.Combobox(combo_frame, textvariable=selected_system, values=system_items, width=15)
        system_combobox.grid(row=1, column=0, padx=5, pady=2)
        selected_system.set(system_items[0])  # Set initial value
        system_combobox.bind("<<ComboboxSelected>>", lambda event: sort_by_system(selected_system.get(), df, combos, categories))
        combos['System'] = system_combobox

    start_row_index = 2  # Adjust the starting row index for other categories

    # Create dropdowns for each of the other categories
    for idx, (category, items) in enumerate(categories.items()):
        if category != 'System':
            ttk.Label(combo_frame, text=category).grid(row=start_row_index, column=idx, padx=5, pady=2)
            combo = ttk.Combobox(combo_frame, values=items, width=15)
            combo.grid(row=start_row_index + 1, column=idx, padx=5, pady=2)
            combo.bind("<<ComboboxSelected>>", lambda event, c=combo: update_combos(combos, df, categories))
            combos[category] = combo

    reset_button = ttk.Button(combo_frame, text="Reset All Choices", command=reset_combos)
    reset_button.grid(row=start_row_index + 2, columnspan=len(categories), pady=10, padx=10, sticky="ew")

    show_code_button = ttk.Button(combo_frame, text="Show Code Number", command=lambda: show_code_number(combos, df))
    show_code_button.grid(row=start_row_index + 3, columnspan=len(categories), pady=10, padx=10, sticky="ew")

    description_button = ttk.Button(combo_frame, text="Show Descriptions", command=toggle_description)
    description_button.grid(row=start_row_index + 4, columnspan=len(categories), pady=10, padx=10, sticky="ew")

    return combos, combo_frame, description_button

def setup_controls(root, reset_combos, show_code_number):
    control_frame = ttk.Frame(root, padding="20")
    control_frame.pack(fill=tk.X, expand=True, pady=10)

    control_frame.columnconfigure(0, weight=1)
    control_frame.columnconfigure(1, weight=1)