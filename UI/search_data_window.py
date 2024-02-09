import tkinter as tk

def open_search_data_window():
    search_data_window = tk.Toplevel()
    search_data_window.title("Search Data Window")
    label = tk.Label(search_data_window, text="This is the Search Data window")
    label.pack()