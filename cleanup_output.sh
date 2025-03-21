#!/bin/bash
#
# Cleanup script for transcription output directory
# Safely removes all contents while handling permission issues
#

# Set the output directory - default is ./data/output
OUTPUT_DIR="./data/output"

# Allow custom output directory as first argument
if [ "$1" != "" ]; then
    OUTPUT_DIR="$1"
fi

# Print header
echo "========================================="
echo "CASPER OUTPUT DIRECTORY CLEANUP"
echo "========================================="
echo "Output directory: $OUTPUT_DIR"
echo

# Check if directory exists
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Error: Output directory '$OUTPUT_DIR' does not exist."
    echo "No cleanup needed."
    exit 0
fi

# Count files and directories to be removed
FILE_COUNT=$(find "$OUTPUT_DIR" -type f | wc -l)
DIR_COUNT=$(find "$OUTPUT_DIR" -mindepth 1 -type d | wc -l)
TOTAL_COUNT=$((FILE_COUNT + DIR_COUNT))

echo "Found:"
echo " - $FILE_COUNT files"
echo " - $DIR_COUNT subdirectories"
echo
echo "Total $TOTAL_COUNT items will be removed"
echo

# Confirm with user unless -y flag is passed
if [ "$2" != "-y" ]; then
    read -p "Do you want to proceed with cleanup? (y/N): " CONFIRM
    if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
        echo "Cleanup aborted."
        exit 0
    fi
fi

echo "Cleaning up output directory..."

# First check write permissions
if [ ! -w "$OUTPUT_DIR" ]; then
    echo "Warning: You don't have write permissions to $OUTPUT_DIR"
    echo "Attempting to fix permissions..."
    
    # Try with sudo if available
    if command -v sudo &>/dev/null; then
        sudo chmod -R u+w "$OUTPUT_DIR"
        if [ $? -ne 0 ]; then
            echo "Error: Failed to fix permissions. Please run this script with sudo."
            exit 1
        fi
        echo "Permissions fixed."
    else
        echo "Error: Cannot fix permissions. Please run this script with appropriate privileges."
        exit 1
    fi
fi

# Remove contents while keeping the main directory
find "$OUTPUT_DIR" -mindepth 1 -print0 | xargs -0 rm -rf 2>/dev/null

# Check if any items remain due to permission issues
REMAINING=$(find "$OUTPUT_DIR" -mindepth 1 | wc -l)

if [ $REMAINING -gt 0 ]; then
    echo "Warning: $REMAINING items could not be removed due to permission issues."
    echo "You may need to run this script with sudo:"
    echo "  sudo ./cleanup_output.sh \"$OUTPUT_DIR\""
else
    echo "Success! All contents of $OUTPUT_DIR have been removed."
    echo "The directory structure has been preserved."
fi

# Create a .gitkeep file to ensure the directory remains in git
touch "$OUTPUT_DIR/.gitkeep"

echo
echo "========================================="
echo "Cleanup completed at $(date)"
echo "========================================="
