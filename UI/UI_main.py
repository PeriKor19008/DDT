import tkinter as tk
from bootstrap_window import open_bootstrap_window
from depart_window import open_depart_window
from log_window import open_log_window
from add_data_window import open_add_data_window
from search_data_window import open_search_data_window

# Create the main application window
root = tk.Tk()
root.title("Simple UI")



# Create buttons
labels = ["Bootstrap", "Depart", "Log", "Add Data", "Search Data"]
commands = [open_bootstrap_window, open_depart_window, open_log_window, open_add_data_window, open_search_data_window]


# Create a label for information
info_text = "This is a simple UI that helps the user perform all the basic functions of the network"
info_label = tk.Label(root, text=info_text, wraplength=600, justify="center")
info_label.grid(row=0, columnspan=len(labels), padx=10, pady=5)



for i, command in enumerate(commands):
    button = tk.Button(root, text=labels[i], command=command)
    button.grid(row=1, column=i, padx=10, pady=5, sticky="ew")  # sticky="ew" to make buttons expand horizontally

# Run the application
root.mainloop()