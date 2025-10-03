import csv
import sys

def filter_logs(csv_file, keywords):
    """
    Filters a CSV log file for rows containing any of the specified keywords.

    Args:
        csv_file (str): The path to the input CSV file.
        keywords (list): A list of strings to search for.
    """
    try:
        with open(csv_file, 'r', encoding='utf-8') as f_in:
            reader = csv.reader(f_in)
            header = next(reader)
            
            # Print the header once
            print(','.join(header))

            for row in reader:
                row_str = ','.join(row).lower() # Convert row to a single lowercase string for case-insensitive search
                
                # Check if any keyword is in the row string
                if any(keyword.lower() in row_str for keyword in keywords):
                    print(','.join(row))

    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python log_filter.py <csv_file> <keyword1> <keyword2> ...")
        sys.exit(1)

    csv_path = sys.argv[1]
    search_keywords = sys.argv[2:]

    print(f"Searching '{csv_path}' for keywords: {', '.join(search_keywords)}\n")
    filter_logs(csv_path, search_keywords)