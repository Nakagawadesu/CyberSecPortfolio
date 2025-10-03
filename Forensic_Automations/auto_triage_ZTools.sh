#!/bin/bash

# --- CONFIGURATION ---
# Base directory where your analysis folder will be created.
DOWNLOADS_DIR="/home/nukitaro/Downloads"
# Path to your Zimmerman EZTools folder (e.g., the .NET 9 version).
EZTOOLS_DIR="/home/nukitaro/EZTools/net9"
# Full path to the dotnet executable.
DOTNET_PATH="/home/nukitaro/.dotnet/dotnet"
# Name of the main output folder for all analysis.
ANALYSIS_FOLDER_NAME="Analisys"
# --- END CONFIGURATION ---

# --- MAIN SCRIPT ---
# Get the triage directory from the first command-line argument
TRIAGE_DIR=$1
ANALYSIS_DIR="${DOWNLOADS_DIR}/${ANALYSIS_FOLDER_NAME}"

# Check if a triage directory was provided
if [ -z "$TRIAGE_DIR" ]; then
    echo "❌ Error: Please provide the path to the triage image directory."
    echo "Usage: ./auto_triage.sh /path/to/triage/image"
    exit 1
fi

echo "--- Starting Triage Process ---"

# Create the main analysis directory if it doesn't exist
mkdir -p "$ANALYSIS_DIR"
echo "Analysis output will be saved in: ${ANALYSIS_DIR}"

# --- Find Tools Automatically ---
echo "🔍 Searching for required tools in ${EZTOOLS_DIR}..."
EVTXECMD_DLL=$(find "$EZTOOLS_DIR" -name EvtxECmd.dll -print -quit)
RECMD_DLL=$(find "$EZTOOLS_DIR" -name RECmd.dll -print -quit)
MFTECMD_DLL=$(find "$EZTOOLS_DIR" -name MFTECmd.dll -print -quit)
AMCACHE_DLL=$(find "$EZTOOLS_DIR" -name AmcacheParser.dll -print -quit)

if [ -z "$EVTXECMD_DLL" ] || [ -z "$RECMD_DLL" ] || [ -z "$MFTECMD_DLL" ] || [ -z "$AMCACHE_DLL" ]; then
    echo "❌ Critical Error: Could not find all required tool DLLs in ${EZTOOLS_DIR}. Please check the path."
    exit 1
fi
echo "✅ All tools found."

# --- Process Artifacts ---
# This function finds an artifact and runs the specified tool against it
process_artifact() {
    local artifact_name=$1
    local tool_dll=$2
    local extra_args=$3
    
    echo ""
    echo "------------------------------------------------------------"
    echo "🔎 Searching for artifact: ${artifact_name}"
    
    # Find the artifact file within the triage directory
    ARTIFACT_PATH=$(find "$TRIAGE_DIR" -name "$artifact_name" -print -quit)
    
    if [ -z "$ARTIFACT_PATH" ]; then
        echo "   -> Artifact '${artifact_name}' not found. Skipping."
        return
    fi
    
    echo "   [+] Found at: ${ARTIFACT_PATH}"
    
    # Create a dedicated output folder for the artifact
    OUTPUT_SUBDIR="${ANALYSIS_DIR}/${artifact_name}_parsed"
    mkdir -p "$OUTPUT_SUBDIR"
    
    # Construct and run the command
    COMMAND=(sudo "$DOTNET_PATH" "$tool_dll" -f "$ARTIFACT_PATH" --csv "$OUTPUT_SUBDIR")
    # Add extra arguments if they exist
    if [ -n "$extra_args" ]; then
        COMMAND+=($extra_args)
    fi
    
    echo "▶️  Executing: ${COMMAND[@]}"
    echo "--- TOOL OUTPUT START ---"
    "${COMMAND[@]}"
    echo "--- TOOL OUTPUT END ---"
}

# Define which artifacts to process with which tools
process_artifact "Security.evtx" "$EVTXECMD_DLL"
process_artifact "System.evtx" "$EVTXECMD_DLL"
process_artifact "Application.evtx" "$EVTXECMD_DLL"
process_artifact "Microsoft-Windows-PowerShell%4Operational.evtx" "$EVTXECMD_DLL"

process_artifact "SYSTEM" "$RECMD_DLL" '--sa ".*"'
process_artifact "NTUSER.DAT" "$RECMD_DLL" '--sa ".*"'
process_artifact "Amcache.hve" "$AMCACHE_DLL"

process_artifact "\$MFT" "$MFTECMD_DLL"
process_artifact "\$UsnJrnl" "$MFTECMD_DLL" '--usnj --csvf UsnJrnl_parsed.csv'


echo ""
echo "------------------------------------------------------------"
echo "🎉 Triage Process Complete!"