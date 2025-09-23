import csv
import os

# --- Configuration ---
# The big CSV file from EvtxECmd that we will search in
INPUT_CSV_FILE = '20250923091907_EvtxECmd_Output.csv'

# !!! IMPORTANT: Change this to the string you want to search for !!!
SEARCH_STRING = '2025-08-24'

# The new CSV file where we will save only the matching rows
OUTPUT_CSV_FILE = f'filtered_for_{SEARCH_STRING}.csv'
# --- End of Configuration ---

def filter_csv_by_string(input_filename, output_filename, search_term):
    """
    Reads a CSV file and creates a new one containing only the rows
    that include the specified search term in any column.
    """
    if search_term == 'PUT_YOUR_SEARCH_TERM_HERE':
        print("Please edit the script and change the SEARCH_STRING variable before running.")
        return

    script_dir = os.path.dirname(os.path.realpath(__file__))
    input_path = os.path.join(script_dir, input_filename)
    output_path = os.path.join(script_dir, output_filename)

    if not os.path.exists(input_path):
        print(f"Error: Input file not found at '{input_path}'")
        return

    print(f"Searching for the string '{search_term}' in '{input_path}'...")
    
    matching_rows = []

    with open(input_path, mode='r', encoding='utf-8', errors='ignore') as infile:
        reader = csv.reader(infile)
        
        # 1. Read the header and add it to our results
        header = next(reader)
        matching_rows.append(header)
        
        # 2. Loop through every data row
        for row in reader:
            # Join all columns into one searchable string (case-insensitive)
            full_row_text = ','.join(row).lower()
            
            # 3. Check if our search term is in the row's text
            if search_term.lower() in full_row_text:
                # 4. If it is, add the entire original row to our results
                matching_rows.append(row)

    # 5. Write the header and all matching rows to the new file
    if len(matching_rows) > 1:
        print(f"Found {len(matching_rows) - 1} rows containing '{search_term}'.")
        
        with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(matching_rows)
            
        print(f"Success! Filtered data has been saved to: {output_path}")
    else:
        print(f"No rows containing the string '{search_term}' were found.")


if __name__ == '__main__':
    filter_csv_by_string(INPUT_CSV_FILE, OUTPUT_CSV_FILE, SEARCH_STRING)