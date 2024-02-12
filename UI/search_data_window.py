import tkinter as tk
import subprocess
import json

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

    result_text = tk.Text(search_data_window, height=20, width=120)
    result_text.grid(row=2, column=1, columnspan=2, padx=10, pady=5)

    def search_data():
        try:
            education = education_entry.get()
            prefix = ip_prefix_entry.get()
            curl_command = f"curl -X GET http://172.{prefix}.0.2:5000/retrieve_data -H 'Content-Type: application/json' -d '{{\"Education\": \"{education}\"}}'"
            print(curl_command)

            # Capture the output of the command
            result = subprocess.run(curl_command, shell=True, check=True, stdout=subprocess.PIPE)
            output = result.stdout.decode('utf-8')

            # Format the output
            formatted_output = ""
            encountered_names = set()  # Set to keep track of encountered names
            for entry in json.loads(output):
                name = entry['Name']
                if name not in encountered_names:
                    formatted_output += f"Name: {name}, Education: {', '.join(entry['Education'])}, Awards: {entry['Awards']}\n\n"
                    encountered_names.add(name)


            # Display the output in the UI
            result_text.delete(1.0, tk.END)  # Clear previous content
            result_text.insert(tk.END, formatted_output)

        except subprocess.CalledProcessError as e:
            print("Error executing script:", e)

    search_data_button = tk.Button(search_data_window, text="Search Data", command=search_data)
    search_data_button.grid(row=3, column=1, columnspan=2, padx=10, pady=10)

    search_data_window.mainloop()

