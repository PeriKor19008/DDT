import tkinter as tk
import subprocess
import json
import pandas as pd


def open_search_data_window():
    search_data_window = tk.Toplevel()
    search_data_window.title("Search Data Window")

    education_label = tk.Label(search_data_window, text="Education:")
    education_label.grid(row=0, column=1, padx=10, pady=5)
    education_entry = tk.Entry(search_data_window)
    education_entry.grid(row=0, column=2, padx=10, pady=5)

    ip_prefix_label = tk.Label(search_data_window, text="IP Prefix:")
    ip_prefix_label.grid(row=1, column=1, padx=10, pady=5)
    ip_prefix_entry = tk.Entry(search_data_window)
    ip_prefix_entry.grid(row=1, column=2, padx=10, pady=5)

    result_text = tk.Text(search_data_window, height=20, width=180)
    result_text.grid(row=2, column=1, columnspan=2, padx=10, pady=5)

    def search_data():
        try:
            education = education_entry.get()
            prefix = ip_prefix_entry.get()
            for i in range(2,4):
                try:
                    curl_command = f"curl -X GET http://172.{prefix}.0.{i}:5000/retrieve_data -H 'Content-Type: application/json' -d '{{\"Education\": \"{education}\"}}'"
                    print(curl_command)

                    # Capture the output of the command
                    result = subprocess.run(curl_command, shell=True, check=True, stdout=subprocess.PIPE)
                    output = result.stdout.decode('utf-8')
                    break
                except subprocess.CalledProcessError as e:
                    print("Error executing script:", e)
                    continue
                
            # Parse JSON response
            entries = json.loads(output)
            num_results = len(entries)
            representation = ""
            representation += f"Number of results: {num_results}\n"

            for entry in entries:
                for key, value in entry.items():
                    representation += f"{key}: {value}, "
                representation += "\n"

            representation = representation.rstrip(", \n")

            result_text.delete(1.0, tk.END)  # Clear previous content
            result_text.insert(tk.END, representation)

        except subprocess.CalledProcessError as e:
            print("Error executing script:", e)


    search_data_button = tk.Button(search_data_window, text="Search Data", command=search_data)
    search_data_button.grid(row=3, column=1, columnspan=2, padx=10, pady=10)

    search_data_window.mainloop()


