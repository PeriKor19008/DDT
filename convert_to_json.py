import csv
import json

csv_file_path = 'web_crawler/computer_scientists.csv'  # Replace with the path to your CSV file
json_file_path = 'cs_to.json'  # Replace with the desired output JSON file path

data = []

with open(csv_file_path, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    header = next(csv_reader)  # Read the header

    for row in csv_reader:
        name = row[0]
        education = eval(row[1])  # Using eval to convert the string representation of the list to an actual list
        awards = int(row[2])

        entry = {
            'Name': name,
            'Education': education,
            'Awards': awards
        }

        data.append(entry)

# Write the JSON data to a file
with open(json_file_path, 'w') as json_file:
    json.dump(data, json_file, indent=2)

print(f'Conversion successful. JSON file saved to {json_file_path}')
