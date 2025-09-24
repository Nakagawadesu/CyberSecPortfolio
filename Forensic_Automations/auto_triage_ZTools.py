import os
import subprocess
import argparse

# --- CONFIGURATION ---
# Base directory where your challenge files are.
DOWNLOADS_DIR = "/home/nukitaro/Downloads"

# Path to your Zimmerman EZTools folder (specifically the .NET 9 version).
EZTOOLS_DIR = "/home/nukitaro/EZTools/net9"

# Full path to the dotnet executable.
DOTNET_PATH = "/home/nukitaro/.dotnet/dotnet"

# Name of the main output folder for all analysis.
ANALYSIS_FOLDER_NAME = "Analisys"
# --- END CONFIGURATION ---

# This dictionary maps artifact filenames to the correct tool and arguments.
# This makes it easy to add more artifacts to process in the future.
ARTIFACT_TOOL_MAP = {
    # Registry Hives (parsed with RECmd)
    'SYSTEM': {'tool': 'RECmd/RECmd.dll', 'args': ['--sa', '.*']},
    'NTUSER.DAT': {'tool': 'RECmd/RECmd.dll', 'args': ['--sa', '.*']},
    'Amcache.hve': {'tool': 'AmcacheParser.dll', 'args': []},
    # Event Logs (parsed with EvtxECmd)
    'Security.evtx': {'tool': 'EvtxECmd/EvtxECmd.dll', 'args': []},
    'System.evtx': {'tool': 'EvtxECmd/EvtxECmd.dll', 'args': []},
    'Application.evtx': {'tool': 'EvtxECmd/EvtxECmd.dll', 'args': []},
    'Microsoft-Windows-PowerShell%4Operational.evtx': {'tool': 'EvtxECmd/EvtxECmd.dll', 'args': []},
    'Microsoft-Windows-User Profile Service%4Operational.evtx': {'tool': 'EvtxECmd/EvtxECmd.dll', 'args': []},
    # File System Artifacts (parsed with MFTECmd)
    '$MFT': {'tool': 'MFTECmd.dll', 'args': []},
    '$UsnJrnl': {'tool': 'MFTECmd.dll', 'args': ['--usnj', '--csvf', 'UsnJrnl_parsed.csv']} # Special args for UsnJrnl
}

def run_command(command_parts):
    """Executes a command and prints its output."""
    try:
        print(f"\n▶️  Running command: {' '.join(command_parts)}")
        subprocess.run(command_parts, check=True, capture_output=True, text=True)
        print("✅ Command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {' '.join(command_parts)}")
        print(f"   Error message: {e.stderr}")
    except FileNotFoundError:
        print(f"❌ Error: The program '{command_parts[0]}' was not found. Please check paths in the script.")

def process_triage_image(triage_dir, output_base_dir):
    """
    Scans a triage image directory and runs the appropriate tools on found artifacts.
    """
    print(f"--- Starting Triage Process ---")
    print(f"Triage Image Directory: {triage_dir}")
    print(f"Analysis Output Directory: {output_base_dir}")

    if not os.path.isdir(triage_dir):
        print(f"❌ Error: Triage directory not found at '{triage_dir}'")
        return

    # Create the main analysis directory if it doesn't exist
    os.makedirs(output_base_dir, exist_ok=True)

    # Walk through the entire triage directory to find artifacts
    for dirpath, dirnames, filenames in os.walk(triage_dir):
        for filename in filenames:
            # Check if the found file is one of the artifacts we know how to process
            if filename in ARTIFACT_TOOL_MAP:
                artifact_info = ARTIFACT_TOOL_MAP[filename]
                artifact_path = os.path.join(dirpath, filename)
                
                print(f"\nFound artifact: '{filename}' at '{artifact_path}'")
                
                # Build the command
                tool_dll_path = os.path.join(EZTOOLS_DIR, artifact_info['tool'])
                
                # Create a dedicated output folder for each artifact to keep results clean
                output_subdir = os.path.join(output_base_dir, f"{filename}_parsed")
                os.makedirs(output_subdir, exist_ok=True)

                command = [
                    'sudo',
                    DOTNET_PATH,
                    tool_dll_path,
                    '-f',
                    artifact_path,
                    '--csv',
                    output_subdir
                ]
                
                # Add any special arguments for the tool
                if artifact_info['args']:
                    command.extend(artifact_info['args'])
                
                # Run the command for the artifact
                run_command(command)

    print("\n--- Triage Process Complete ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automatically run Zimmerman's EZ Tools against a forensic triage image.")
    parser.add_argument("triage_directory", help="The path to the root of the triage image directory.")
    
    args = parser.parse_args()
    
    analysis_dir = os.path.join(DOWNLOADS_DIR, ANALYSIS_FOLDER_NAME)
    
    process_triage_image(args.triage_directory, analysis_dir)