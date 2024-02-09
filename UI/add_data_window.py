import tkinter as tk

def open_add_data_window():
    add_data_window = tk.Toplevel()
    add_data_window.title("Add Data Window")
    label = tk.Label(add_data_window, text="This is the Add Data window")
    label.pack()