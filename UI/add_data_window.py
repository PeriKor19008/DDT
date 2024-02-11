import tkinter as tk
import subprocess
import csv
import json
def open_add_data_window():
    add_data_window = tk.Toplevel()
    add_data_window.title("Add Data Window")

    name_label = tk.Label(add_data_window, text="Name:")
    name_label.grid(row=0, column=0, padx=10, pady=5)
    name_entry = tk.Entry(add_data_window)
    name_entry.grid(row=1, column=0, padx=10, pady=5)

    education_label = tk.Label(add_data_window, text="Education:")
    education_label.grid(row=0, column=1, padx=10, pady=5)
    education_entry = tk.Entry(add_data_window)
    education_entry.grid(row=1, column=1, padx=10, pady=5)

    award_label = tk.Label(add_data_window, text="Awards:")
    award_label.grid(row=0, column=2, padx=10, pady=5)
    award_entry = tk.Entry(add_data_window)
    award_entry.grid(row=1, column=2, padx=10, pady=5)

    ip_prefix_label = tk.Label(add_data_window, text="IP Prefix:")
    ip_prefix_label.grid(row=2, column=0, padx=10, pady=5)
    ip_prefix_entry = tk.Entry(add_data_window)
    ip_prefix_entry.grid(row=2, column=1, padx=10, pady=5)

    data_count_label = tk.Label(add_data_window, text="Number of entries:")
    data_count_label.grid(row=4, column=0, padx=10, pady=5)
    data_count_entry = tk.Entry(add_data_window)
    data_count_entry.grid(row=4, column=1, padx=10, pady=5)


    def add_data():
        try:
            name = name_entry.get()
            education = education_entry.get()
            awards = int(award_entry.get())
            prefix = ip_prefix_entry.get()

            curl_command = f"curl -X POST http://172.{prefix}.0.2:5000/insert_data -H 'Content-Type: application/json' -d '{{\"Name\": \"{name}\", \"Education\": [\"{education}\"], \"Awards\": {awards}}}'"
            subprocess.run(curl_command, shell=True, check=True)
            
        except subprocess.CalledProcessError as e:
            print("Error executing script:", e)
             
        add_data_window.destroy()

    

    add_data_button = tk.Button(add_data_window, text="Add Data", command=add_data)
    add_data_button.grid(row=2, column=2, padx=10, pady=10)


    def add_data_all():
        try:
            prefix = ip_prefix_entry.get()
            count = data_count_entry.get()
            with open('web_crawler/computer_scientists.csv', mode='r') as file:
                csv_reader = csv.DictReader(file)
                counter = 0
                for row in csv_reader:
                    if len(count) != 0:
                        if counter > int(count):
                            break
                    name = row['Name'].replace('"', r'\"')
                    row['Education'] = row['Education'].replace("'s","")
                    row['Education'] = row['Education'].replace('""',"'")
                    education = json.dumps(eval(row['Education']))
                    awards = json.dumps(row['Awards'])

                    # Constructing the curl command with proper escaping
                    curl_command = f'curl -X POST http://172.{prefix}.0.2:5000/insert_data -H "Content-Type: application/json" -d \'{{\"Name\": "{name}", \"Education\": {education}, \"Awards\": {awards}}}\''
                    subprocess.run(curl_command, shell=True, check=True)
                    counter += 1
        except subprocess.CalledProcessError as e:
            print("Error executing script:", e)

        add_data_window.destroy()


    add_data_all_button = tk.Button(add_data_window, text="Add Crawler Data", command=add_data_all)
    add_data_all_button.grid(row=4, column=2, padx=10, pady=10)

    add_data_window.mainloop()