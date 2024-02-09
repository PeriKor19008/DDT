import tkinter as tk
import subprocess

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


    def search_data():
        try:
            education = education_entry.get()
            prefix = ip_prefix_entry.get()
            curl_command = f"curl -X GET http://172.{prefix}.0.2:5000/retrieve_data -H 'Content-Type: application/json' -d '{{\"Education\": [\"{education}\"]}}'"            
            subprocess.run(curl_command, shell=True, check=True)

        except subprocess.CalledProcessError as e:
             print("Error executing script:", e)
             

        search_data_window.destroy()
    
    search_data_button = tk.Button(search_data_window, text="Search Data", command=search_data)
    search_data_button.grid(row=3, column=1, columnspan=2, padx=10, pady=10)
    
    search_data_window.mainloop()