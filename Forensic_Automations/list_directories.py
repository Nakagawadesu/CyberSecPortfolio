import os
import argparse

def list_all_files_and_dirs(root_dir):
    """
    Walks through a directory and prints a tree-like structure
    of all subdirectories and the files within them.
    """
    if not os.path.isdir(root_dir):
        print(f"Error: Directory not found at '{root_dir}'")
        return

    print(f"Directory and file tree for: {root_dir}\n")
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Calculate the depth for indentation
        level = dirpath.replace(root_dir, '', 1).count(os.sep)
        indent = ' ' * 4 * (level)
        
        # Print the current directory
        print(f'{indent}└── {os.path.basename(dirpath)}/')
        
        # This new part will print the files
        sub_indent = ' ' * 4 * (level + 1)
        for f in filenames:
            print(f'{sub_indent}├── {f}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List all subdirectories and files of a given directory.")
    parser.add_argument("target_directory", help="The path to the directory you want to scan.")
    
    args = parser.parse_args()
    
    list_all_files_and_dirs(args.target_directory)