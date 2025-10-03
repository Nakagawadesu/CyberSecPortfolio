import csv
import sys
import os

def filter_logs_strict(csv_file, keywords):
    """
    Filters a CSV log file for rows containing ALL of the specified keywords
    and saves the results to a new CSV file.

    Args:
        csv_file (str): The path to the input CSV file.
        keywords (list): A list of strings to search for.
    """
    try:
        # Create a new filename for the filtered output
        base_name, ext = os.path.splitext(csv_file)
        filtered_keywords = "_".join(keywords).replace(" ", "_").replace(":", "").replace("\\", "_")
        output_file = f"{base_name}_filtered_{filtered_keywords}{ext}"
        
        # Open the input and output files
        with open(csv_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', newline='', encoding='utf-8') as f_out:
            reader = csv.reader(f_in)
            writer = csv.writer(f_out)
            
            header = next(reader)
            writer.writerow(header)
            
            for row in reader:
                # Convert row to a single lowercase string for case-insensitive search
                row_str = ' '.join(row).lower()
                
                # Check if ALL keywords are in the row string
                if all(keyword.lower() in row_str for keyword in keywords):
                    writer.writerow(row)
        
        print(f"Filtered data has been saved to '{output_file}'")
        print("\n\n" + "-"*50 + "\n")
        print("Here are the contents of the new file:")
        with open(output_file, 'r', encoding='utf-8') as f:
            print(f.read())
            
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python log_filter_strict.py <csv_file> <keyword1> <keyword2> ...")
        print("Example: python log_filter_strict.py powershell.csv \"2025-04-09 09:20:12\" \"WMI\"")
        sys.exit(1)

    csv_path = sys.argv[1]
    search_keywords = sys.argv[2:]

    print(f"Searching '{csv_path}' for ALL keywords: {', '.join(search_keywords)}\n")
    filter_logs_strict(csv_path, search_keywords)