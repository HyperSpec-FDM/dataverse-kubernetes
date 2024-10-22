import os
import csv
import pandas as pd

# Function to convert CSV to TSV
def csv_to_tsv(input_csv_file, output_tsv_file):
    # Open the CSV file for reading
    with open(input_csv_file, 'r', newline='') as csv_file:
        # Open the TSV file for writing
        with open(output_tsv_file, 'w', newline='') as tsv_file:
            # Create CSV reader and TSV writer objects
            csv_reader = csv.reader(csv_file, delimiter=";")
            tsv_writer = csv.writer(tsv_file, delimiter='\t')

            # Write all rows from the CSV file to the TSV file
            for row in csv_reader:
                tsv_writer.writerow(row)

# Function to convert Excel (xlsx) to TSV
def xlsx_to_tsv(input_xlsx_file, output_tsv_file):
    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel(input_xlsx_file)

    # Write the DataFrame to a TSV file
    df.to_csv(output_tsv_file, sep='\t', index=False)

def convert_to_tsv(input_file):
    # Determine the output file name by changing the extension to .tsv
    output_file = os.path.splitext(input_file)[0] + '.tsv'

    if input_file.endswith('.csv'):
        csv_to_tsv(input_file, output_file)
    elif input_file.endswith('.xlsx'):
        xlsx_to_tsv(input_file, output_file)
    else:
        raise ValueError("Unsupported file format. Please provide a .csv or .xlsx file.")

    print(f'Converted {input_file} to {output_file}')


input_file = "../metadata/test.xlsx"
convert_to_tsv(input_file)

