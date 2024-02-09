import tkinter as tk
import subprocess


def open_log_window():
    log_window = tk.Toplevel()
    log_window.title("Log Window")

    # Function to handle logging node
    import subprocess

    # Function to handle logging node
    def log_node():
        node_ip = node_ip_entry.get()
        curl_command = f"curl -X POST -d '' http://{node_ip}/show_routes"
        try:
            subprocess.run(curl_command, shell=True, check=True)
            print("Command executed successfully")
        except subprocess.CalledProcessError as e:
            print("Error executing command:", e)
        log_window.destroy()

    # Function to handle logging all
    # Function to handle logging all
    def log_all():
        try:
            subprocess.run(["./log.sh"], check=True)
            print("Script executed successfully")
        except subprocess.CalledProcessError as e:
            print("Error executing script:", e)
        log_window.destroy()

    # Create form elements
    node_ip_label = tk.Label(log_window, text="Node IP:")
    node_ip_label.grid(row=0, column=0, padx=10, pady=5)
    node_ip_entry = tk.Entry(log_window)
    node_ip_entry.grid(row=0, column=1, padx=10, pady=5)

    log_node_button = tk.Button(log_window, text="Log Node", command=log_node)
    log_node_button.grid(row=1, column=0, padx=10, pady=10)

    log_all_button = tk.Button(log_window, text="Log All", command=log_all)
    log_all_button.grid(row=1, column=1, padx=10, pady=10)

    # Run the Log window
    log_window.mainloop()