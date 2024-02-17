import tkinter as tk
import subprocess

def open_stabilize_window():
    stab_window = tk.Toplevel()
    stab_window.title("Stabilize Window")


    def stab_all():
        try:
            ip_prefix = ip_prefix_entry.get()
            node_amount = int(node_amount_entry.get())
            subprocess.run(["../stabilize.sh", f"{ip_prefix}", str(node_amount)], check=True)
            print("Script executed successfully")
        except ValueError:
            print("Node amount must be an integer")
        except subprocess.CalledProcessError as e:
            print("Error executing script:", e)
        #log_window.destroy()


    ip_prefix_label = tk.Label(stab_window, text="IP Prefix:")
    ip_prefix_label.grid(row=0, column=2, padx=10, pady=5)
    ip_prefix_entry = tk.Entry(stab_window)
    ip_prefix_entry.grid(row=0, column=3, padx=10, pady=5)

    node_amount_label = tk.Label(stab_window, text="Node Amount:")
    node_amount_label.grid(row=1, column=2, padx=10, pady=5)
    node_amount_entry = tk.Entry(stab_window)
    node_amount_entry.grid(row=1, column=3, padx=10, pady=5)

    stab_all_button = tk.Button(stab_window, text="Stabilize All", command=stab_all)
    stab_all_button.grid(row=2, column=3, padx=10, pady=10)

    stab_window.mainloop()