"""
python3 csv2json.py ads.csv ads.adv
python3 csv2json.py categories.csv ads.category
"""
import codecs
import csv
import json
import sys

ENCODING = 'UTF-8'
CSV_DELIMITER = ','

# _, input_name, model_name = sys.argv
input_name = "user.csv"
model_name = "user.adv"


with codecs.open(input_name, 'r', encoding=ENCODING) as f:
    reader = csv.reader(f, delimiter=CSV_DELIMITER)

    header_row = []
    entries = []

    for row in reader:

        if not header_row:
            header_row = row
            continue

        pk = row[0]
        model = model_name
        fields = {}
        for i in range(len(row) - 1):
            active_field = row[i + 1] if row[i + 1] != '' else '0'

            if active_field.isdigit():
                try:
                    new_number = int(active_field)
                except ValueError:
                    new_number = float(active_field)
                fields[header_row[i + 1]] = new_number
            elif active_field == 'TRUE':
                fields[header_row[i + 1]] = True
            elif active_field == 'FALSE':
                fields[header_row[i + 1]] = False
            else:
                fields[header_row[i + 1]] = active_field.strip()

        entries.append({
            'pk': int(pk),
            'model': model_name,
            'fields': fields
        })

out_file = ''.join(input_name.split('.')[:-1]) + '.json'
with open(out_file, 'w') as fo:
    json.dump(entries, fo, indent=4, ensure_ascii=False)
