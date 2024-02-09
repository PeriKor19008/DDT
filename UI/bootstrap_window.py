import tkinter as tk
import subprocess

def open_bootstrap_window():
    bootstrap_window = tk.Toplevel()
    bootstrap_window.title("Bootstrap Window")

    # Function to retrieve data from the form and execute curl command
    def send_data():
        sender_ip = sender_ip_entry.get()
        receiver_ip = receiver_ip_entry.get()
        ip_prefix = ip_prefix_entry.get()
        node_amount = node_amount_entry.get()
        if not receiver_ip.startswith("http://"):
            receiver_ip = "http://" + receiver_ip
        curl_command = f"curl -X POST -d '{receiver_ip}' http://{sender_ip}/bootstrap"
        try:
            subprocess.run(curl_command, shell=True, check=True)
            command_label.config(text="Command sent: " + curl_command)
        except subprocess.CalledProcessError as e:
            command_label.config(text="Error executing command: " + str(e))
        bootstrap_window.destroy()  # Close the window after sending the command

    # Create the first form elements
    sender_ip_label = tk.Label(bootstrap_window, text="Sender IP:")
    sender_ip_label.grid(row=0, column=0, padx=10, pady=5)
    sender_ip_entry = tk.Entry(bootstrap_window)
    sender_ip_entry.grid(row=0, column=1, padx=10, pady=5)

    receiver_ip_label = tk.Label(bootstrap_window, text="Receiver IP:")
    receiver_ip_label.grid(row=1, column=0, padx=10, pady=5)
    receiver_ip_entry = tk.Entry(bootstrap_window)
    receiver_ip_entry.grid(row=1, column=1, padx=10, pady=5)

    # Create the second form elements
    ip_prefix_label = tk.Label(bootstrap_window, text="IP Prefix:")
    ip_prefix_label.grid(row=0, column=2, padx=10, pady=5)
    ip_prefix_entry = tk.Entry(bootstrap_window)
    ip_prefix_entry.grid(row=0, column=3, padx=10, pady=5)

    node_amount_label = tk.Label(bootstrap_window, text="Node Amount:")
    node_amount_label.grid(row=1, column=2, padx=10, pady=5)
    node_amount_entry = tk.Entry(bootstrap_window)
    node_amount_entry.grid(row=1, column=3, padx=10, pady=5)

    # Function to bootstrap all
    def bootstrap_all():
        ip_prefix = ip_prefix_entry.get()
        try:
            # Convert node amount to an integer
            node_amount = int(node_amount_entry.get())
            subprocess.run(["./bootstrap.sh", ip_prefix, str(node_amount)], check=True)
            command_label.config(text="Bootstrap script executed successfully")
        except ValueError:
            command_label.config(text="Node amount must be an integer")
        except subprocess.CalledProcessError as e:
            command_label.config(text="Error executing bootstrap script: " + str(e))
        bootstrap_window.destroy()  # Close the window after sending the command

    # Create Bootstrap All button
    bootstrap_all_button = tk.Button(bootstrap_window, text="Bootstrap All", command=bootstrap_all)
    bootstrap_all_button.grid(row=2, column=2, columnspan=2, padx=10, pady=10)

    submit_button = tk.Button(bootstrap_window, text="Send", command=send_data)
    submit_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    # Label to display the command
    command_label = tk.Label(bootstrap_window, text="")
    command_label.grid(row=3, columnspan=4, padx=10, pady=5)

    # Run the Bootstrap window
    bootstrap_window.mainloop()
