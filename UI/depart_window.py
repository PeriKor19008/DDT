import tkinter as tk
import subprocess
from tkinter import messagebox

def open_depart_window():
    depart_window = tk.Toplevel()
    depart_window.title("Depart Window")

    # Function to depart node
    def depart_node():
        node_ip = node_ip_entry.get()
        curl_command = f"curl -X POST -d '' http://{node_ip}:5000/depart"
        try:
            subprocess.run(curl_command, shell=True, check=True)
            print("Command executed successfully")
        except subprocess.CalledProcessError as e:
            print("Error executing command:", e)
        depart_window.destroy()

    # Function to display confirmation dialog
    def confirm_depart():
        confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to depart this node?",
                                        parent=depart_window)
        if confirmed:
            depart_node()

    # Create form elements
    node_ip_label = tk.Label(depart_window, text="Node IP:")
    node_ip_label.grid(row=0, column=0, padx=10, pady=5)
    node_ip_entry = tk.Entry(depart_window)
    node_ip_entry.grid(row=0, column=1, padx=10, pady=5)

    depart_button = tk.Button(depart_window, text="Depart", command=confirm_depart)
    depart_button.grid(row=1, columnspan=2, padx=10, pady=10)

    # Run the Depart window
    depart_window.mainloop()